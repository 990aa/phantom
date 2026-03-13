use std::sync::Arc;
use tokio::sync::mpsc;
use phantom_watcher::{AppContext, IpcEvent, context_grabber, logger, clipboard, scheduler};
use global_hotkey::{GlobalHotKeyManager, hotkey::{HotKey, Modifiers, Code}, GlobalHotKeyEvent};
use tokio::net::windows::named_pipe::ServerOptions;
use tokio::io::AsyncWriteExt;
use std::process::Command;
use std::time::Duration;

#[tokio::main]
async fn main() {
    env_logger::init();
    let (tx, mut rx) = mpsc::channel::<IpcEvent>(100);
    let (pipe_tx, mut pipe_rx) = mpsc::channel::<IpcEvent>(100); // Channel to send events to pipe

    // Task 1: Clipboard Watcher
    let tx_clip = tx.clone();
    tokio::spawn(async move {
        clipboard::watch_clipboard(tx_clip).await;
    });

    // Task 2: Hotkey Listener
    let tx_hotkey = tx.clone();
    
    // The hotkey receiver loop
    tokio::spawn(async move {
        let receiver = GlobalHotKeyEvent::receiver();
        loop {
            if let Ok(event) = receiver.try_recv() {
                // If we received an event, it means the hotkey was triggered.
                let _ = tx_hotkey.send(IpcEvent::HotkeyTriggered).await;
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
    });

    // The thread with message loop
    tokio::task::spawn_blocking(move || {
        let manager = GlobalHotKeyManager::new().unwrap();
        let hotkey = HotKey::new(Some(Modifiers::CONTROL), Code::Space);
        manager.register(hotkey).unwrap();
        
        #[cfg(target_os = "windows")]
        unsafe {
            use windows::Win32::UI::WindowsAndMessaging::{GetMessageW, TranslateMessage, DispatchMessageW, MSG};
            let mut msg: MSG = std::mem::zeroed();
            while GetMessageW(&mut msg, None, 0, 0).into() {
                TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
    });

    let tx_sched = tx.clone();
    tokio::spawn(async move {
        scheduler::run_scheduler(tx_sched).await;
    });

    // Task 3: IPC Server (Named Pipe)
    let pipe_tx_clone = pipe_tx.clone();
    tokio::spawn(async move {
        println!("IPC server listening...");
        loop {
            match ServerOptions::new()
                .first_pipe_instance(true)
                .create("\\\\.\\pipe\\phantom-ipc") {
                Ok(mut server) => {
                    if let Ok(_) = server.connect().await {
                        println!("Client connected to pipe!");
                        while let Some(event) = pipe_rx.recv().await {
                            if let Ok(json) = serde_json::to_string(&event) {
                                let line = format!("{}\n", json);
                                if server.write_all(line.as_bytes()).await.is_err() {
                                    break; // Client disconnected
                                }
                            }
                        }
                    }
                }
                Err(e) => {
                    println!("Error creating pipe: {:?}", e);
                    tokio::time::sleep(Duration::from_secs(1)).await;
                }
            }
        }
    });

    // Dispatcher
    while let Some(event) = rx.recv().await {
        match event {
            IpcEvent::HotkeyTriggered => {
                println!("Hotkey triggered. Grabbing context...");
                let ctx = context_grabber::grab_context().await;
                println!("Context: {:?}", ctx);
                // Send to Tauri frontend via named pipe
                let _ = pipe_tx_clone.send(IpcEvent::HotkeyTriggered).await;
            }
            IpcEvent::ClipboardChanged(text) => {
                println!("Clipboard changed");
                logger::log_message(&text, "outgoing", "unknown").await;
            }
            IpcEvent::TriggerStyleDistillation => {
                println!("Triggering Style Distillation");
                let mut path = dirs::home_dir().unwrap_or_else(|| std::path::PathBuf::from("."));
                path.push(".phantom");
                path.push("phantom.db");
                
                if let Ok(conn) = rusqlite::Connection::open(&path) {
                    let mut stmt = conn.prepare("SELECT text FROM message_log ORDER BY id DESC LIMIT 300").unwrap();
                    let rows = stmt.query_map([], |row| row.get::<_, String>(0)).unwrap();
                    let mut messages = Vec::new();
                    for msg in rows {
                        if let Ok(m) = msg {
                            messages.push(m);
                        }
                    }
                    messages.reverse();
                    let text_log = messages.join("\n");
                    
                    // Spawn python engine
                    let _ = Command::new("uv")
                        .args(&["run", "phantom-engine"])
                        .env("TASK", "distill")
                        .env("TEXT", text_log)
                        .spawn();
                }
            }
            _ => {}
        }
    }
}
