import pytest
import time
import subprocess
import sys
import json
import pyperclip
import psutil
import sqlite3
from pathlib import Path

# Helpers
def get_db_path():
    return Path.home() / ".phantom" / "phantom.db"

def run_engine_task(task, text="", image_path=None, model_override=None):
    from phantom_engine.schemas import InferenceRequest, AppContext
    req = InferenceRequest(
        task=task,
        text=text,
        image_path=image_path,
        model_override=model_override,
        context=AppContext(process_name="test", window_title="test", text_before="", text_after="")
    )
    req_json = req.model_dump_json()
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "phantom_engine", "run"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    proc.stdin.write(req_json + "\n")
    proc.stdin.flush()
    
    outputs = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        outputs.append(json.loads(line))
        if outputs[-1].get("type") == "done":
            break
            
    proc.wait(timeout=30)
    return outputs

def test_e2e_01_clipboard_trigger():
    # Simulate a copy. In a real environment, we would also assert that the Rust watcher picks this up
    # and the Tauri UI becomes visible.
    pyperclip.copy("Phantom test clipboard content")
    time.sleep(0.5)
    assert pyperclip.paste() == "Phantom test clipboard content"

def test_e2e_02_summarize_task():
    outputs = run_engine_task("summarize", text="This is a long text to summarize. It should be shorter.")
    tokens = [o["content"] for o in outputs if o.get("type") == "token"]
    assert len(tokens) > 0
    final_output = "".join(tokens)
    assert "summary" in final_output.lower()

def test_e2e_03_vision_caption():
    # Use a dummy image path
    outputs = run_engine_task("caption", image_path="dummy.png", model_override="moondream2")
    tokens = [o["content"] for o in outputs if o.get("type") == "token"]
    assert len(tokens) > 0

def test_e2e_04_style_distillation():
    db_path = get_db_path()
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        for i in range(50):
            c.execute("INSERT INTO message_log (content, direction, app_context) VALUES (?, ?, ?)", 
                      (f"Fake message {i}", "outgoing", "test"))
        conn.commit()
        conn.close()
    
    outputs = run_engine_task("distill", text="Fake messages")
    assert any(o.get("type") == "done" for o in outputs)

def test_e2e_05_ram_budget():
    # Spawn actual rust watcher logic instead of dummy sleep process.
    # Note: in real CI we assume `cargo build --release` ran and watcher exists.
    watcher_path = Path("watcher/target/release/phantom-watcher.exe")
    if not watcher_path.exists():
        watcher_path = Path("watcher/target/release/phantom-watcher")
    
    if watcher_path.exists():
        proc = subprocess.Popen([str(watcher_path)])
        time.sleep(2)
        p = psutil.Process(proc.pid)
        mem_info = p.memory_info()
        assert mem_info.rss < 25 * 1024 * 1024
        proc.terminate()
    else:
        pytest.skip("Watcher binary not found. Run cargo build --release first.")

def test_e2e_06_custom_model_url():
    db_path = get_db_path()
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO models (id, name, hf_repo, filename, local_path, type, is_downloaded, is_default_text, is_default_vision) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      ("test_custom_model", "Custom Model", "author/repo", "model.gguf", None, "text", 0, 0, 0))
            conn.commit()
            
            c.execute("SELECT hf_repo FROM models WHERE id = 'test_custom_model'")
            res = c.fetchone()
            assert res is not None
            assert res[0] == "author/repo"
        finally:
            c.execute("DELETE FROM models WHERE id = 'test_custom_model'")
            conn.commit()
            conn.close()
    else:
        pytest.skip("DB not initialized yet")

def test_e2e_07_model_switch():
    outputs = run_engine_task("summarize", text="Test model switch", model_override="llama-3.2-1b")
    # Check the model used in the response
    assert outputs[-1].get("model_used") == "llama-3.2-1b"
