use std::time::Duration;
use tokio::sync::mpsc::Sender;
use arboard::Clipboard;
use crate::IpcEvent;

pub async fn watch_clipboard(tx: Sender<IpcEvent>) {
    let mut clipboard = match Clipboard::new() {
        Ok(c) => c,
        Err(_) => return,
    };
    
    let mut last_text = String::new();
    
    loop {
        if let Ok(text) = clipboard.get_text() {
            if text != last_text && !text.trim().is_empty() {
                last_text = text.clone();
                let _ = tx.send(IpcEvent::ClipboardChanged(text)).await;
            }
        }
        tokio::time::sleep(Duration::from_millis(300)).await;
    }
}
