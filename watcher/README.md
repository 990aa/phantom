# Phantom Watcher

The background daemon for Windows that monitors system events and grabs context.

## Purposes
- **System Monitoring**: Listens for global hotkeys (Ctrl+Space) and clipboard changes.
- **Context Grabbing**: Uses Windows UIAutomation to read text from the active window or takes screenshots as fallback.
- **Message Logging**: Persists clipboard history to SQLite for style distillation.
- **IPC Server**: Hosts a Named Pipe (`\\.\pipe\phantom-ipc`) to relay events to the Tauri UI.

## Implementation Details
- **`src/main.rs`**: Main dispatcher loop and IPC server.
- **`src/context_grabber.rs`**: Core logic for UIAutomation text extraction and fallback screen capture.
- **`src/clipboard.rs`**: Polls the system clipboard for new entries.
- **`src/scheduler.rs`**: Monitors user idle time and triggers weekly style distillation.
- **`src/logger.rs`**: Database writer for message logs.

## Run / Build Instructions

### Prerequisites
- Rust & Cargo (1.75+)
- Windows 10/11

### Development
1. `cd watcher`
2. `cargo run`

### Build (Release)
```bash
cargo build --release
```
The binary will be located at `target/release/phantom-watcher.exe`.

## Testing
- **Unit & Integration Tests**: `cargo test`
- **Linting**: `cargo clippy`
