import time
import gc
from typing import Iterator
from .schemas import InferenceRequest, InferenceResponse
from . import tasks

def check_compatibility(model_id: str, task: str) -> bool:
    text_tasks = ["summarize", "simplify", "explain", "reply", "continue", "custom", "distill"]
    vision_tasks = ["caption", "navigate"]
    
    is_vision_model = "moondream" in model_id.lower() or "-vl-" in model_id.lower() or "vlm" in model_id.lower()
    
    if task in text_tasks and is_vision_model:
        return False
    if task in vision_tasks and not is_vision_model:
        return False
    return True

def generate_response(req: InferenceRequest) -> Iterator[InferenceResponse]:
    model_id = req.model_override or "qwen3.5-0.8b"
    
    if not check_compatibility(model_id, req.task):
        yield InferenceResponse(
            type="error",
            content=f"Model {model_id} is not compatible with task {req.task}",
            model_used=model_id,
            elapsed_ms=0
        )
        return

    # In a real implementation:
    # 1. Resolve model via SQLite
    # 2. Download if missing via downloader.py
    # 3. Load llama_cpp.Llama
    # 4. Fetch style_rules from SQLite
    
    model = None # Stub for the loaded model
    style_rules = "Be concise and clear." # Stub
    
    task_handlers = {
        "summarize": tasks.summarize,
        "simplify": tasks.simplify,
        "explain": tasks.explain,
        "custom": tasks.custom,
        "reply": tasks.reply,
        "continue": tasks.continue_text,
        "caption": tasks.caption,
        "navigate": tasks.navigate,
        "distill": tasks.distill_style,
    }
    
    handler = task_handlers.get(req.task)
    if handler:
        yield from handler(model, req, style_rules)
    else:
        yield InferenceResponse(
            type="error",
            content=f"Unknown task: {req.task}",
            model_used=model_id,
            elapsed_ms=0
        )
    
    # Unload
    del model
    gc.collect()
