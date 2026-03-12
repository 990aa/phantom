import time
from typing import Iterator
from .schemas import InferenceRequest, InferenceResponse

def _dummy_stream(words: list[str], model_id: str) -> Iterator[InferenceResponse]:
    """Helper to simulate streaming output for testing."""
    start = time.time()
    for word in words:
        yield InferenceResponse(
            type="token",
            content=word + " ",
            model_used=model_id,
            elapsed_ms=int((time.time() - start) * 1000)
        )
        time.sleep(0.05)
    
    yield InferenceResponse(
        type="done",
        content="",
        model_used=model_id,
        elapsed_ms=int((time.time() - start) * 1000)
    )

def summarize(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: Produce a concise 3-sentence summary. Style: {style_rules}\n\nUser: {req.text}"
    return _dummy_stream(["Here", "is", "a", "concise", "summary", "of", "the", "provided", "text."], req.model_override or "default-model")

def simplify(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: Rewrite the input in simpler, plain language.\n\nUser: {req.text}"
    return _dummy_stream(["This", "means", "something", "very", "simple."], req.model_override or "default-model")

def explain(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: Provide a clear explanation.\n\nUser: {req.text}"
    return _dummy_stream(["The", "explanation", "is", "that", "it", "works", "like", "this."], req.model_override or "default-model")

def custom(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    # text will hold the context, req_custom could be parsed if we extended schemas, let's assume text has it
    prompt = f"System: {style_rules}\n\nUser: {req.text}"
    return _dummy_stream(["Custom", "response", "generated."], req.model_override or "default-model")

def reply(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: User writing style rules (follow exactly): {style_rules}\nGenerate the next message.\n\nContext:\n{req.context.text_before}"
    return _dummy_stream(["Sounds", "good,", "I", "will", "do", "that!"], req.model_override or "default-model")

def continue_text(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: User writing style rules (follow exactly): {style_rules}\nContinue writing in the same tone.\n\nText:\n{req.context.text_before}"
    return _dummy_stream(["And", "then", "the", "next", "thing", "happened."], req.model_override or "default-model")

def caption(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: Provide a short, descriptive caption for the image.\n\nImage: {req.image_path}"
    return _dummy_stream(["A", "screenshot", "showing", "an", "app", "interface."], req.model_override or "vision-model")

def navigate(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: Describe where to click next based on the user question.\n\nImage: {req.image_path}\nQuestion: {req.text}"
    return _dummy_stream(["Click", "the", "button", "on", "the", "top", "right."], req.model_override or "vision-model")

def distill_style(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    prompt = f"System: Extract a 50-word communication style rulebook from the messages.\n\nMessages:\n{req.text}"
    return _dummy_stream(["Use", "short", "sentences.", "No", "emojis.", "Lowercase", "only."], req.model_override or "default-model")
