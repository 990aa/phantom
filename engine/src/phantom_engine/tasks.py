import time
from typing import Iterator
from .schemas import InferenceRequest, InferenceResponse

def _llm_stream(model, system_msg: str, user_msg: str, model_id: str) -> Iterator[InferenceResponse]:
    start = time.time()
    if model is None:
        # Fallback if model failed to load, to avoid crashing tests or missing model
        yield InferenceResponse(
            type="error",
            content="Model not loaded",
            model_used=model_id,
            elapsed_ms=int((time.time() - start) * 1000)
        )
        return

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    try:
        stream = model.create_chat_completion(messages=messages, stream=True)
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield InferenceResponse(
                    type="token",
                    content=delta["content"],
                    model_used=model_id,
                    elapsed_ms=int((time.time() - start) * 1000)
                )
        
        yield InferenceResponse(
            type="done",
            content="",
            model_used=model_id,
            elapsed_ms=int((time.time() - start) * 1000)
        )
    except Exception as e:
        yield InferenceResponse(
            type="error",
            content=str(e),
            model_used=model_id,
            elapsed_ms=int((time.time() - start) * 1000)
        )

def summarize(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = "Produce a concise 3-sentence summary."
    user_msg = f"{req.text}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")

def simplify(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = "Rewrite the input in simpler, plain language."
    user_msg = f"{req.text}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")

def explain(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = "Provide a clear explanation."
    user_msg = f"{req.text}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")

def custom(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = req.custom_prompt or "Follow the user instructions."
    user_msg = f"{req.text}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")

def reply(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = f"User writing style rules (follow exactly): {style_rules}\nGenerate the next message."
    user_msg = f"Context:\n{req.context.text_before}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")

def continue_text(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = f"User writing style rules (follow exactly): {style_rules}\nContinue writing in the same tone."
    user_msg = f"Text:\n{req.context.text_before}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")

def caption(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = "Provide a short, descriptive caption for the image."
    user_msg = f"Image: {req.image_path}"
    # In a real multimodal, we would encode the image. Here we just mock or pass path if supported.
    return _llm_stream(model, system_msg, user_msg, req.model_override or "vision-model")

def navigate(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = "Describe where to click next based on the user question."
    user_msg = f"Image: {req.image_path}\nQuestion: {req.text}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "vision-model")

def distill_style(model, req: InferenceRequest, style_rules: str = "") -> Iterator[InferenceResponse]:
    system_msg = "Extract a 50-word communication style rulebook from the messages."
    user_msg = f"Messages:\n{req.text}"
    return _llm_stream(model, system_msg, user_msg, req.model_override or "default-model")
