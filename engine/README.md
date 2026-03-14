# Phantom AI Engine (Brain)

The Python sidecar that handles the AI logic, model lifecycle, and style distillation.

## Purposes
- **Inference**: Uses `llama-cpp-python` to run GGUF models on CPU or GPU.
- **Model Management**: Handles downloading models from HuggingFace and tracking their local state.
- **Style Pipeline**: Distills user writing styles from message logs into 50-word rulebooks.
- **API**: Provides a CLI interface via `Typer` for task execution.

## Implementation Details
- **`src/phantom_engine/model_manager.py`**: Singleton that manages loading/unloading models into VRAM/RAM on demand to keep the idle footprint low.
- **`src/phantom_engine/tasks.py`**: Defines the prompt templates for Summarize, Simplify, Explain, Reply, Continue, Caption, and Navigate.
- **`src/phantom_engine/downloader.py`**: Multi-threaded downloader with progress tracking for HuggingFace GGUF files.
- **`src/phantom_engine/schemas.py`**: Pydantic models for IPC data validation.

## Run / Build Instructions

### Prerequisites
- Python 3.14+
- `uv` package manager

### Development
1. `cd engine`
2. `uv sync`
3. `uv run phantom-engine --help`

### Build (Standalone)
The engine is bundled into a single executable for the Windows Tauri app:
```bash
uv run pyinstaller --onefile --name phantom-engine src/phantom_engine/__main__.py
```
This executable is placed in `ui/src-tauri/binaries/` during the release build.

## Linting & Testing
- **Linting**: `uv run ruff check .`
- **Type Checking**: `uv run pyright src`
- **Testing**: `uv run pytest ../tests`
