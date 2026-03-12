use std::sync::Arc;
use tokio::sync::mpsc;
use phantom_watcher::{AppContext, IpcEvent, context_grabber, logger, clipboard, scheduler};

#[tokio::main]
async fn main() {
    env_logger::init();
    let (tx, mut rx) = mpsc::channel::<IpcEvent>(100);

    // Task 1: Clipboard Watcher
    let tx_clip = tx.clone();
    tokio::spawn(async move {
        clipboard::watch_clipboard(tx_clip).await;
    });

    // Task 2: Hotkey Listener
    let tx_hotkey = tx.clone();
    tokio::spawn(async move {
        // Dummy implementation since global-hotkey requires a proper event loop
        // In a real app we would use global_hotkey::GlobalHotKeyEvent
        println!("Hotkey listener started.");
        // tx_hotkey.send(IpcEvent::HotkeyTriggered).await.unwrap();
    });

    let tx_sched = tx.clone();
    tokio::spawn(async move {
        scheduler::run_scheduler(tx_sched).await;
    });

    // Task 3: IPC Server (Named Pipe)
    tokio::spawn(async move {
        println!("IPC server listening...");
    });

    // Dispatcher
    while let Some(event) = rx.recv().await {
        match event {
            IpcEvent::HotkeyTriggered => {
                println!("Hotkey triggered. Grabbing context...");
                let ctx = context_grabber::grab_context().await;
                println!("Context: {:?}", ctx);
            }
            IpcEvent::ClipboardChanged(text) => {
                println!("Clipboard changed: {}", text);
                logger::log_message(&text, "outgoing", "unknown").await;
            }
            _ => {}
        }
    }
}
