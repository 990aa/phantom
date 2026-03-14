# Phantom

Phantom is a local-first AI assistant that idles at under 15 MB RAM, surfaces as a tiny floating overlay on any active window, and loads an AI model on demand only when triggered. The entire stack is offline, private, and GPU-optional. 

It works seamlessly with your existing workflow, giving you contextual AI capabilities exactly when and where you need them without hogging system resources.

## Features

- **Local & Private:** Everything runs on your machine. No data is sent to external servers.
- **Resource Efficient:** Idles at < 15 MB RAM. The AI model is only loaded into memory when requested.
- **Context-Aware:** Grabs context from the active window or clipboard automatically. If UI accessibility fails, it transparently falls back to taking localized screenshots for vision processing.
- **Floating Overlay & System Tray:** Provides a non-intrusive UI that appears over your current application and runs quietly in the system tray. Auto-starts natively with Windows.
- **Task-Specific Models:** Assign and persist specific models for precise tasks (e.g. use a lightweight 0.8B model for text completion, but instantly switch to a larger vision model for captions).
- **GPU-Optional:** Works on CPU-only machines but can leverage GPU acceleration via `llama-cpp-python` (Windows) or `llama.cpp` native (Android).
- **Customizable:** Load your own GGUF models and tweak style distillation rules.

## Architecture Stack

Phantom is built using a modern, multi-language stack to optimize for performance and development speed.

| Layer | Technology | Purpose |
|-------|------------|---------|
| **The Watcher** | Rust (Windows) / Kotlin (Android) | Clipboard monitor, hotkey listener, UIAutomation/Accessibility |
| **The Interface** | Tauri + React (Windows) / Flutter (Android) | Floating overlay UI, model management, streaming output |
| **The Brain** | Python + llama-cpp (Windows) / Dart FFI + C++ (Android) | GGUF model loader, inference engine, style pipeline |
| **The Memory** | SQLite (Shared via sql script) | Style rulebook, message logs, model config, custom URLs |

## Prerequisites

Before building Phantom, ensure you have the following installed:

### For Windows:
- **Rust & Cargo:** Required for compiling the Watcher and Tauri backend.
- **Node.js:** Recommended Node 20+ for building the Vite + React frontend.
- **Python 3.14+ & uv:** Required for the Python AI Engine.

### For Android:
- **Flutter:** Stable channel.
- **Android Studio & NDK:** NDK version 26.1.10909125 is required to compile `llama.cpp` for Android.

## Installation & Build Instructions

### Windows Build

1. **The Watcher (Rust):** `cd watcher && cargo build --release`
2. **The Brain (Python):** `cd engine && uv sync`
3. **The Interface (Tauri):** `cd ui && npm install && npm run tauri build`

### Android Build

1. Enter the Android directory: `cd android_app`
2. Initialize Flutter submodules and native NDK build: `flutter pub get`
3. Build the APK: `flutter build apk --release`
4. **Permissions Post-Install:** After installing, you must open Android Settings to grant **"Display over other apps"** (SYSTEM_ALERT_WINDOW) and **"Accessibility"** (BIND_ACCESSIBILITY_SERVICE) for Phantom to read text and inject responses.

## Usage

### Windows
1. Run Phantom. The Watcher process will start in the background.
2. The UI overlay remains hidden until invoked.
3. Trigger the assistant (via hotkey or copying text) to display the overlay.
4. Input your prompt. The Brain will start up, process the request with the loaded model, stream the response back, and then shut down.

### Android
1. Launch the Phantom app to manage models and download a lightweight GGUF (e.g., Qwen3.5-0.8B).
2. Tap the floating bubble or persistent notification to summon the Phantom overlay.
3. Generate text or hit **Insert** to paste the generated output directly into your current chat app via Accessibility Services.

## Troubleshooting

- **Windows Hotkey Fails:** If the hotkey doesn't work in certain apps, you may need to run Phantom as Administrator due to Windows UAC restrictions.
- **Android Overlay Doesn't Appear:** Ensure the "Display over other apps" permission is granted.
- **Android Model Crashes:** Your device may lack sufficient RAM. Use models under 2GB (like Qwen3.5-0.8B or Llama-3.2-1B) for mid-range phones.

## Testing

To run the automated tests:
- **Rust (Watcher):** `cd watcher && cargo test`
- **UI (React/Vite):** `cd ui && npm run test`
- **Python (Engine):** `cd engine && uv run pytest ../tests`
- **Android (Flutter):** `cd android_app && flutter test test/unit/`

## Contributing

Pull requests are welcome! Please ensure you test your changes locally and adhere to the formatting guidelines of each language.

## License

MIT License
