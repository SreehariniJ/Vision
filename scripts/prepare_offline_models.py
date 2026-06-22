import os
from pathlib import Path
from huggingface_hub import snapshot_download

def prepare_model(repo_id: str, output_dir: str):
    print(f"\n[{repo_id}] Downloading model...")
    # Download to local directory
    snapshot_download(
        repo_id=repo_id,
        local_dir=output_dir,
        local_dir_use_symlinks=False, # We want actual files
        resume_download=True
    )
    
    print(f"[{repo_id}] Download complete.")

if __name__ == "__main__":
    vision_dir = Path(r"c:\Users\Sreeharini\vision")
    models_dir = vision_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Model 1: 7B
    prepare_model(
        repo_id="Qwen/Qwen2.5-VL-7B-Instruct",
        output_dir=str(models_dir / "Qwen2.5-VL-7B-Instruct")
    )
    
    # Model 2: 32B AWQ
    prepare_model(
        repo_id="Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
        output_dir=str(models_dir / "Qwen2.5-VL-32B-Instruct-AWQ")
    )
    
    print("\nAll models have been downloaded successfully.")
