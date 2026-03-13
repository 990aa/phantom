import pytest
import sys
import subprocess
from pydantic import ValidationError
from phantom_engine.schemas import InferenceRequest, AppContext
from phantom_engine.model_manager import check_compatibility

def test_validation_missing_fields():
    with pytest.raises(ValidationError):
        # Missing context
        InferenceRequest(task="summarize", text="Hello")

def test_check_compatibility():
    assert check_compatibility("qwen3.5-0.8b", "summarize") == True
    assert check_compatibility("moondream2", "caption") == True
    assert check_compatibility("qwen3.5-0.8b", "caption") == False
    assert check_compatibility("moondream2", "summarize") == False

def test_distill_style():
    from phantom_engine.tasks import distill_style
    req = InferenceRequest(
        task="distill",
        text="Msg 1\nMsg 2",
        context=AppContext(process_name="", window_title="", text_before="", text_after="")
    )
    
    # Normally we'd use a mock, but since the test currently executes the actual or mocked function:
    # Let's ensure the output passes word count and basic types
    tokens = list(distill_style(None, req, ""))
    final_output = "".join(t.content for t in tokens if t.type == "token")
    assert len(final_output.split()) < 500  # Reasonable rulebook size
    # Check that at least something was generated
    assert len(final_output.strip()) > 0

def test_downloader_mock(monkeypatch):
    import phantom_engine.downloader as dl
    
    def mock_download(*args, **kwargs):
        return "/fake/path/model.gguf"
        
    monkeypatch.setattr(dl, "hf_hub_download", mock_download)
    res = dl.download_model("unsloth/Qwen3.5-0.8B", "qwen.gguf")
    assert res == "/fake/path/model.gguf"

def test_engine_subprocess():
    import json
    req = InferenceRequest(
        task="summarize",
        text="Test string.",
        context=AppContext(process_name="test", window_title="test", text_before="", text_after="")
    )
    req_json = req.model_dump_json()
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "phantom_engine", "run"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    proc.stdin.write(req_json + "\n")
    proc.stdin.flush()
    
    tokens_received = 0
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        resp = json.loads(line)
        if resp["type"] == "token":
            tokens_received += 1
        elif resp["type"] == "done":
            break
            
    proc.wait()
    assert tokens_received > 0
    assert proc.returncode == 0
