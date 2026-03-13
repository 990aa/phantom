import os
import json
import threading
import sys
import time
from pathlib import Path
from huggingface_hub import hf_hub_download

def download_model(repo_id: str, filename: str) -> str:
    target_dir = Path.home() / ".phantom" / "models"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle custom URL parsing (e.g. huggingface.co/author/repo/resolve/main/filename)
    if repo_id.startswith("http"):
        parts = repo_id.replace("https://", "").replace("http://", "").split("/")
        if "huggingface.co" in parts:
            idx = parts.index("huggingface.co")
            repo_id = f"{parts[idx+1]}/{parts[idx+2]}"
            if not filename and "resolve" in parts:
                filename = parts[-1]

    if not filename:
        raise ValueError("Filename could not be determined")
        
    # Start download in a thread so we can stream progress
    download_thread = None
    local_path = None
    exc = None
    
    def _do_download():
        nonlocal local_path, exc
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=target_dir,
                show_progress=False
            )
        except Exception as e:
            exc = e

    t = threading.Thread(target=_do_download)
    t.start()
    
    partial_path = target_dir / f".{filename}.incomplete"
    while t.is_alive():
        # Polling file size
        if partial_path.exists():
            size = os.path.getsize(partial_path)
            # We don't know total size natively without a HEAD request, so just send bytes downloaded
            print(json.dumps({"type": "progress", "downloaded_bytes": size}))
            sys.stdout.flush()
        time.sleep(0.5)
        
    t.join()
    
    if exc:
        raise exc
        
    print(json.dumps({"type": "progress", "downloaded_bytes": -1, "status": "complete", "local_path": str(local_path)}))
    sys.stdout.flush()
    return local_path
