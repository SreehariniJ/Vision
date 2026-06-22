from pathlib import Path
from huggingface_hub import snapshot_download

vision_dir = Path(r"c:\Users\Sreeharini\vision")
models_dir = vision_dir / "models"

def just_download(repo_id: str, output_dir: str):
    print(f"\n--- Downloading {repo_id} ---")
    snapshot_download(
        repo_id=repo_id,
        local_dir=output_dir,
        local_dir_use_symlinks=False,
        resume_download=True
    )
    print(f"[{repo_id}] Download 100% complete!")

if __name__ == "__main__":
    print("Starting strictly download-only process. No compression will occur.")
    
    # 7B Model (Should already be finished)
    just_download(
        repo_id="Qwen/Qwen2.5-VL-7B-Instruct",
        output_dir=str(models_dir / "Qwen2.5-VL-7B-Instruct")
    )
    
    # 32B Model
    just_download(
        repo_id="Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
        output_dir=str(models_dir / "Qwen2.5-VL-32B-Instruct-AWQ")
    )
    
    print("\nALL MODELS SUCCESSFULLY DOWNLOADED!")
