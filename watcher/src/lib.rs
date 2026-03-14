pub mod clipboard;
pub mod context_grabber;
pub mod logger;
pub mod scheduler;

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub struct AppContext {
    pub process_name: String,
    pub window_title: String,
    pub text_before: String,
    pub text_after: String,
    pub screenshot_path: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum IpcEvent {
    HotkeyTriggered(AppContext),
    ClipboardChanged(String),
    TriggerStyleDistillation,
}
