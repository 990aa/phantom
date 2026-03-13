import typer
import sys
import json
from .schemas import InferenceRequest, InferenceResponse
from .model_manager import generate_response
from .downloader import download_model

app = typer.Typer(no_args_is_help=True)

@app.command("download")
def download(repo: str, filename: str = ""):
    try:
        download_model(repo, filename)
    except Exception as e:
        print(json.dumps({"type": "error", "content": str(e)}))

@app.command("run")
def run():
    # Read single line of JSON from stdin
    try:
        input_data = sys.stdin.readline().strip()
        if not input_data:
            return
        
        req = InferenceRequest.model_validate_json(input_data)
        
        # Stream response back
        for token_resp in generate_response(req):
            print(token_resp.model_dump_json())
            sys.stdout.flush()
            
    except Exception as e:
        err = InferenceResponse(type="error", content=str(e), model_used="", elapsed_ms=0)
        print(err.model_dump_json())
        sys.stdout.flush()

if __name__ == "__main__":
    app()
