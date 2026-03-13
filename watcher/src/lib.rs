pub mod context_grabber;
pub mod logger;
pub mod clipboard;
pub mod scheduler;

use serde::{Serialize, Deserialize};

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