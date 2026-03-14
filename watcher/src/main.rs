use global_hotkey::{
    hotkey::{Code, HotKey, Modifiers},
    GlobalHotKeyEvent, GlobalHotKeyManager,
};
use phantom_watcher::{clipboard, context_grabber, logger, scheduler, AppContext, IpcEvent};
use std::process::Command;
use std::time::Duration;
use tokio::io::AsyncWriteExt;
use tokio::net::windows::named_pipe::ServerOptions;
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    env_logger::init();

    // Auto-start
    if let Ok(exe_path) = std::env::current_exe() {
        let _ = std::process::Command::new("reg")
            .args([
                "add",
                "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "/v",
                "PhantomWatcher",
                "/t",
                "REG_SZ",
                "/d",
                &exe_path.to_string_lossy(),
                "/f",
            ])
            .output();
    }

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
            if let Ok(_event) = receiver.try_recv() {
                // If we received an event, it means the hotkey was triggered.
                let _ = tx_hotkey
                    .send(IpcEvent::HotkeyTriggered(AppContext {
                        process_name: String::new(),
                        window_title: String::new(),
                        text_before: String::new(),
                        text_after: String::new(),
                        screenshot_path: None,
                    }))
                    .await;
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
            use windows::Win32::UI::WindowsAndMessaging::{
                DispatchMessageW, GetMessageW, TranslateMessage, MSG,
            };
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
                .create("\\\\.\\pipe\\phantom-ipc")
            {
                Ok(mut server) => {
                    if server.connect().await.is_ok() {
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
            IpcEvent::HotkeyTriggered(_) => {
                println!("Hotkey triggered. Grabbing context...");
                let ctx = context_grabber::grab_context().await;
                println!("Context: {:?}", ctx);
                // Send to Tauri frontend via named pipe
                let _ = pipe_tx_clone.send(IpcEvent::HotkeyTriggered(ctx)).await;
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
                    let mut stmt = conn
                        .prepare("SELECT content FROM message_log ORDER BY id DESC LIMIT 300")
                        .unwrap();
                    let rows = stmt.query_map([], |row| row.get::<_, String>(0)).unwrap();
                    let mut messages = Vec::new();
                    for m in rows.flatten() {
                        messages.push(m);
                    }
                    messages.reverse();
                    let text_log = messages.join("\n");

                    // Spawn python engine
                    let _ = Command::new("uv")
                        .args(["run", "phantom-engine"])
                        .env("TASK", "distill")
                        .env("TEXT", text_log)
                        .spawn();
                }
            }
        }
    }
}
