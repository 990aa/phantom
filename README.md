# Phantom

Phantom is a local-first AI assistant that idles at under 15 MB RAM, surfaces as a tiny floating overlay on any active window, and loads an AI model on demand only when triggered. The entire stack is offline, private, and GPU-optional.

It works seamlessly with your existing workflow, giving you contextual AI capabilities exactly when and where you need them without hogging system resources.

## Multi-Language Stack

Phantom leverages the best tool for each specific platform and task:

| Language | Layer | Purpose | Key Implementation |
| :--- | :--- | :--- | :--- |
| **Rust** | [Watcher](./watcher) | OS Monitoring | Hotkey listener, UIAutomation, IPC Named Pipes. |
| **Python** | [Engine](./engine) | AI Brain | GGUF inference (`llama-cpp`), Style distillation, Model management. |
| **TypeScript** | [UI](./ui) | Desktop Interface | React-based overlay window, state sync via `Zustand`. |
| **Dart** | [Android App](./android_app) | Mobile Assist | Flutter UI, Accessibility Service, `llama.cpp` native bridge. |
| **Kotlin** | [Android Native](./android_app) | Mobile Hooks | Background WorkManager, Accessibility node tree traversal. |
| **SQL** | [Shared Memory](./shared) | Persistence | SQLite schemas for message logs and model tracking. |

## Features

- **Local & Private:** Everything runs on your machine. No data is sent to external servers.
- **Resource Efficient:** Idles at < 15 MB RAM. Models are loaded only on demand.
- **Context-Aware:** Grabs context from the active window or clipboard automatically. 
- **Floating Overlays:** Compact panels that appear over any app on Windows and Android.
- **Style Learning:** Automatically extracts 50-word rulebooks from your outgoing messages to mirror your writing style.
- **GPU Acceleration:** Leverages GPU via `llama-cpp-python` (Windows) or runs optimized C++ natively (Android).

## Run / Build Instructions

### [Windows (Desktop)](./ui/README.md)
1. Build the Watcher: `cd watcher && cargo build --release`
2. Sync the Engine: `cd engine && uv sync`
3. Build the UI: `cd ui && npm install && npm run tauri build`

### [Android (Mobile)](./android_app/README.md)
1. Initialize: `cd android_app && flutter pub get`
2. Build: `flutter build apk --release`

## Deployment & Distribution
- **Windows**: Distributed via Standalone Installer (`.exe`) or **WinGet**.
- **Android**: Distributed via **F-Droid** compatible APKs. 
- *Note: Not intended for Google Play Store.*

## Automated Testing
Run the unified test suite to verify the entire stack:
```bash
python test_all.py
```

## Contributing
See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Author
**990aa**

## License
MIT License
