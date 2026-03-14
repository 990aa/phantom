import os
import json
import threading
import sys
import time
from pathlib import Path
from typing import Optional
from huggingface_hub import hf_hub_download


def download_model(repo_id: str, filename: str) -> str:
    target_dir = Path.home() / ".phantom" / "models"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Handle custom URL parsing (e.g. huggingface.co/author/repo/resolve/main/filename)
    if repo_id.startswith("http"):
        parts = repo_id.replace("https://", "").replace("http://", "").split("/")
        if "huggingface.co" in parts:
            idx = parts.index("huggingface.co")
            repo_id = f"{parts[idx + 1]}/{parts[idx + 2]}"
            if not filename and "resolve" in parts:
                filename = parts[-1]

    if not filename:
        raise ValueError("Filename could not be determined")

    local_path: Optional[str] = None
    exc: Optional[Exception] = None

    def _do_download():
        nonlocal local_path, exc
        try:
            # hf_hub_download returns the local path as a string
            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=target_dir,
            )
            local_path = str(path)
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

    if local_path is None:
        raise RuntimeError("Download failed: local_path is None")

    print(
        json.dumps(
            {
                "type": "progress",
                "downloaded_bytes": -1,
                "status": "complete",
                "local_path": local_path,
            }
        )
    )
    sys.stdout.flush()
    return local_path
