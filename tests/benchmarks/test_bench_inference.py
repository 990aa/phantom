import pytest
import subprocess
import sys
import json
import time
import psutil

def run_summarize(model_name: str):
    from phantom_engine.schemas import InferenceRequest, AppContext
    req = InferenceRequest(
        task="summarize",
        text="The quick brown fox jumps over the lazy dog. " * 10,
        model_override=model_name,
        context=AppContext(process_name="bench", window_title="bench", text_before="", text_after="")
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
    
    first_token_time = None
    start_time = time.time()
    
    # Track RAM usage
    p = psutil.Process(proc.pid)
    peak_rss = 0
    
    token_count = 0
    for line in proc.stdout:
        try:
            current_rss = p.memory_info().rss
            if current_rss > peak_rss:
                peak_rss = current_rss
        except psutil.NoSuchProcess:
            pass
            
        line = line.strip()
        if not line:
            continue
            
        resp = json.loads(line)
        if resp.get("type") == "token":
            if first_token_time is None:
                first_token_time = time.time() - start_time
            token_count += 1
        elif resp.get("type") == "done":
            break
            
    proc.wait()
    total_time = time.time() - start_time
    
    return {
        "ttft": first_token_time,
        "tokens_per_sec": token_count / total_time if total_time > 0 else 0,
        "peak_rss_mb": peak_rss / (1024 * 1024)
    }

@pytest.mark.benchmark(group="inference")
def test_bench_qwen_0_8b(benchmark):
    # This benchmarks the TTFT and speeds.
    # We use a dummy model for architecture stubs, but in real environment it tests the actual GGUF
    result = benchmark(run_summarize, "qwen3.5-0.8b")
    assert result is not None

@pytest.mark.benchmark(group="inference")
def test_bench_llama_1b(benchmark):
    result = benchmark(run_summarize, "llama-3.2-1b")
    assert result is not None
