# Phantom

Phantom is a local-first AI assistant that idles at under 15 MB RAM, surfaces as a tiny floating overlay on any active window, and loads an AI model on demand only when triggered. The entire stack is offline, private, and GPU-optional.

## Architecture Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| The Watcher | Rust (Windows) / Tauri IPC | Clipboard monitor, hotkey listener, UIAutomation context grab |
| The Interface | Tauri + React/TS (Windows) | Floating overlay UI, model management, streaming output |
| The Brain | Python + llama-cpp-python (uv) | GGUF model loader, inference engine, style pipeline |
| The Memory | SQLite (rusqlite + Python) | Style rulebook, message logs, model config, custom model URLs |

## Building the Components

### 1. The Watcher (Rust)
```bash
cd watcher
cargo build --release
```

### 2. The Interface (Tauri)
```bash
cd ui
npm install
npm run tauri build
```

### 3. The Brain (Python)
```bash
cd engine
uv sync
```
