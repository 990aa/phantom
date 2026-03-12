import os
from pathlib import Path
from huggingface_hub import hf_hub_download

def download_model(repo_id: str, filename: str) -> str:
    target_dir = Path.home() / ".phantom" / "models"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # In a real implementation, we stream progress back as JSON
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=target_dir,
        show_progress=False
    )
    return local_path
