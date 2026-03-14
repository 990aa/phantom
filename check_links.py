import requests
import sys

models = [
    ("unsloth/Qwen3.5-0.8B-GGUF", "Qwen3.5-0.8B-Q4_K_M.gguf"),
    ("bartowski/Llama-3.2-1B-Instruct-GGUF", "Llama-3.2-1B-Instruct-Q4_K_M.gguf"),
    ("moondream/moondream2-gguf", "moondream2-text-model-f16.gguf"),
    ("moondream/moondream2-gguf", "moondream2-mmproj-f16.gguf"),
    ("bartowski/SmolVLM2-2.2B-Instruct-GGUF", "SmolVLM2-2.2B-Instruct-Q4_K_M.gguf"),
]

for repo, filename in models:
    url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
    print(f"Checking {url}...")
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        if resp.status_code == 200:
            print(f"  OK: {resp.status_code}")
        else:
            print(f"  FAILED: {resp.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
