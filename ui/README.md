# Phantom UI (Interface)

The desktop frontend for Phantom on Windows, built with Tauri and React.

## Purposes
- **User Interface**: Provides the floating overlay, model manager, and settings screens.
- **Inter-Process Communication (IPC)**: Communicates with the Rust Watcher via Named Pipes and triggers the Python Engine sidecar.
- **State Management**: Uses `Zustand` to manage app settings and inference streaming states.

## Implementation Details
- **`src/App.tsx`**: Main UI layout and routing logic.
- **`src/components/Overlay.tsx`**: The compact assistant panel that appears on hotkey triggers.
- **`src/components/ModelManager.tsx`**: Interface for downloading and setting default models.
- **`src/store.ts`**: Unified state store for the frontend.
- **`src-tauri/src/main.rs`**: Tauri backend that manages system tray and named pipe clients.

## Run / Build Instructions

### Prerequisites
- Node.js 22+
- Rust & Cargo (1.75+)

### Development
1. `cd ui`
2. `npm install`
3. `npm run tauri dev`

### Build (Installer)
```bash
npm run tauri build
```
This will produce an `.exe` installer in `src-tauri/target/release/bundle/nsis/`.

## Testing
- **Component Tests**: `npm run test` (Vitest + React Testing Library)
- **Type Checking**: `npx tsc`
