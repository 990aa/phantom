# Phantom

Phantom is a local-first AI assistant that idles at under 15 MB RAM, surfaces as a tiny floating overlay on any active window, and loads an AI model on demand only when triggered. The entire stack is offline, private, and GPU-optional. 

It works seamlessly with your existing workflow, giving you contextual AI capabilities exactly when and where you need them without hogging system resources.

## Features

- **Local & Private:** Everything runs on your machine. No data is sent to external servers.
- **Resource Efficient:** Idles at < 15 MB RAM. The AI model is only loaded into memory when requested.
- **Context-Aware:** Grabs context from the active window or clipboard automatically. If UI accessibility fails, it transparently falls back to taking localized screenshots for vision processing.
- **Floating Overlay & System Tray:** Provides a non-intrusive UI that appears over your current application and runs quietly in the system tray. Auto-starts natively with Windows.
- **Task-Specific Models:** Assign and persist specific models for precise tasks (e.g. use a lightweight 0.8B model for text completion, but instantly switch to a larger vision model for captions).
- **GPU-Optional:** Works on CPU-only machines but can leverage GPU acceleration via `llama-cpp-python`.
- **Customizable:** Load your own GGUF models and tweak style distillation rules.

## Architecture Stack

Phantom is built using a modern, multi-language stack to optimize for performance and development speed.

| Layer | Technology | Purpose |
|-------|------------|---------|
| **The Watcher** | Rust (Windows) / Tauri IPC | Clipboard monitor, hotkey listener, UIAutomation context grab |
| **The Interface** | Tauri + React/TS (Windows) | Floating overlay UI, model management, streaming output |
| **The Brain** | Python + llama-cpp-python (uv) | GGUF model loader, inference engine, style pipeline |
| **The Memory** | SQLite (rusqlite + Python) | Style rulebook, message logs, model config, custom model URLs |

## Prerequisites

Before building Phantom, ensure you have the following installed:

- **Rust & Cargo:** Required for compiling the Watcher and Tauri backend.
- **Node.js:** Recommended Node 20+ for building the Vite + React frontend.
- **Python 3.14+:** Required for the Python AI Engine. (Or use `uv` for python version management).
- **uv:** A fast Python package and project manager. (Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or pip).

## Installation & Build Instructions

You'll need to build the three main components of the application. 

### 1. The Watcher (Rust)

The Watcher monitors your clipboard and active window context.

```bash
cd watcher
cargo build --release
```

### 2. The Brain (Python)

The Brain is the inference engine that runs the GGUF models.

```bash
cd engine
uv sync
```

### 3. The Interface (Tauri)

The Interface is the React-based floating overlay. 

```bash
cd ui
npm install
npm run tauri build
```

## Usage

Once all components are built, you can run the application by launching the built Tauri executable from `ui/src-tauri/target/release/`.

1. Run Phantom. The Watcher process will start in the background.
2. The UI overlay remains hidden until invoked.
3. Trigger the assistant (via hotkey or copying text) to display the overlay.
4. Input your prompt. The Brain will start up, process the request with the loaded model, stream the response back, and then shut down the heavy model.

## Configuration

Phantom stores its memory, including model configuration and message logs, in an SQLite database (typically in your user directory `.phantom/phantom.db`).

You can configure models by opening the Interface settings, where you can paste Hugging Face URLs for GGUF models to have the engine download and run them automatically.

## Project Structure

- `engine/` - Python FastAPI/subprocess backend for model inference and downloading.
- `scripts/` - Utility scripts (e.g., version bumping).
- `shared/` - Shared assets and database schemas.
- `ui/` - Tauri application and React frontend.
- `watcher/` - Rust process for OS-level context grabbing and hotkeys.

## Testing

To run the automated tests:
- **Rust (Watcher):** `cd watcher && cargo test`
- **UI (React/Vite):** `cd ui && npm run test`
- **Python (Engine):** `cd engine && uv run pytest ../tests`

## Contributing

Pull requests are welcome! Please ensure you test your changes locally and adhere to the formatting guidelines of each language (e.g., `cargo fmt` for Rust, `eslint` for TS, and `ruff`/`black` for Python).

## License

MIT License
