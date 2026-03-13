from pydantic import BaseModel
from typing import Optional, Literal


class AppContext(BaseModel):
    process_name: str
    window_title: str
    text_before: str
    text_after: str


class InferenceRequest(BaseModel):
    task: Literal[
        "summarize",
        "simplify",
        "explain",
        "reply",
        "continue",
        "caption",
        "navigate",
        "custom",
        "distill",
    ]
    text: Optional[str] = None
    image_path: Optional[str] = None
    model_override: Optional[str] = None
    custom_prompt: Optional[str] = None
    context: AppContext
    stream: bool = True


class InferenceResponse(BaseModel):
    type: Literal["token", "done", "error"]
    content: str
    model_used: str
    elapsed_ms: int


class ModelInfo(BaseModel):
    id: str
    name: str
    hf_repo: str
    filename: str
    local_path: Optional[str] = None
    type: str
    size_bytes: Optional[int] = None
    is_downloaded: bool
    is_default_text: bool
    is_default_vision: bool
