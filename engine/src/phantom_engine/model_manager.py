import gc
import sqlite3
from pathlib import Path
from typing import Iterator, Optional
from .schemas import InferenceRequest, InferenceResponse
from . import tasks

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

def init_db(db_path: Path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='models'")
        if not cursor.fetchone():
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "shared" / "schema.sql",
                Path.cwd() / "shared" / "schema.sql",
                Path.cwd().parent / "shared" / "schema.sql"
            ]
            for p in possible_paths:
                if p.exists():
                    with open(p, 'r') as f:
                        conn.executescript(f.read())
                    break
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_default_model(model_type: str = "text") -> tuple[str, str]:
    db_path = Path.home() / ".phantom" / "phantom.db"
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    init_db(db_path)

    if not db_path.exists():
        return "qwen3.5-0.8b", ""

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        col = "is_default_vision" if model_type == "vision" else "is_default_text"
        cursor.execute(f"SELECT id, local_path FROM models WHERE {col} = 1 LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row and row[1]:
            return row[0], row[1]
    except Exception:
        pass
    return "qwen3.5-0.8b", ""


def get_preferred_model(task: str) -> Optional[str]:
    db_path = Path.home() / ".phantom" / "phantom.db"
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (f"preferred_model_{task}",))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return None


def check_compatibility(model_id: str, task: str) -> bool:
    text_tasks = [
        "summarize",
        "simplify",
        "explain",
        "reply",
        "continue",
        "custom",
        "distill",
    ]
    vision_tasks = ["caption", "navigate"]

    is_vision_model = (
        "moondream" in model_id.lower()
        or "-vl-" in model_id.lower()
        or "vlm" in model_id.lower()
    )

    if task in text_tasks and is_vision_model:
        return False
    if task in vision_tasks and not is_vision_model:
        return False
    return True


def generate_response(req: InferenceRequest) -> Iterator[InferenceResponse]:
    model_type = "vision" if req.task in ["caption", "navigate"] else "text"
    
    model_id = req.model_override
    if not model_id:
        model_id = get_preferred_model(req.task)

    local_path = ""

    if not model_id:
        model_id, local_path = get_default_model(model_type)
    else:
        # User requested override, we could query for its path, but keeping it simple for now
        db_path = Path.home() / ".phantom" / "phantom.db"
        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT local_path FROM models WHERE id = ?", (model_id,)
                )
                row = cursor.fetchone()
                conn.close()
                if row and row[0]:
                    local_path = row[0]
            except Exception:
                pass

    if not check_compatibility(model_id, req.task):
        yield InferenceResponse(
            type="error",
            content=f"Model {model_id} is not compatible with task {req.task}",
            model_used=model_id,
            elapsed_ms=0,
        )
        return

    model = None
    if local_path and Llama is not None:
        try:
            model = Llama(model_path=local_path, verbose=False, n_ctx=2048)
        except Exception as e:
            yield InferenceResponse(
                type="error",
                content=f"Failed to load model: {str(e)}",
                model_used=model_id,
                elapsed_ms=0,
            )
            return

    style_rules = get_style_context()

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
        if req.task in [
            "summarize",
            "simplify",
            "explain",
            "caption",
            "navigate",
            "distill",
            "custom",
        ]:
            yield from handler(model, req, "")
        else:
            yield from handler(model, req, style_rules)
    else:
        yield InferenceResponse(
            type="error",
            content=f"Unknown task: {req.task}",
            model_used=model_id,
            elapsed_ms=0,
        )

    # Unload
    if model is not None:
        del model
    gc.collect()


def get_style_context() -> str:
    import sqlite3
    from pathlib import Path

    db_path = Path.home() / ".phantom" / "phantom.db"
    if not db_path.exists():
        return ""

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT rules_json FROM style_rules ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""
    except Exception:
        return ""
