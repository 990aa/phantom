import time
import gc
from typing import Iterator
from .schemas import InferenceRequest, InferenceResponse

def generate_response(req: InferenceRequest) -> Iterator[InferenceResponse]:
    start = time.time()
    model_id = req.model_override or "qwen3.5-0.8b"
    
    # In a real implementation:
    # 1. Resolve model via SQLite
    # 2. Check compatibility (text vs vision)
    # 3. Download if missing via downloader.py
    # 4. Load llama_cpp.Llama
    # 5. Generate stream
    
    # Dummy stream for architecture stub
    words = ["Phantom", "acknowledges", "your", "request:", req.task]
    if req.text:
        words.append(f"({req.text[:20]}...)")
        
    for word in words:
        yield InferenceResponse(
            type="token",
            content=word + " ",
            model_used=model_id,
            elapsed_ms=int((time.time() - start) * 1000)
        )
        time.sleep(0.1)
        
    yield InferenceResponse(
        type="done",
        content="",
        model_used=model_id,
        elapsed_ms=int((time.time() - start) * 1000)
    )
    
    # Unload
    gc.collect()
