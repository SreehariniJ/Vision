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
    print("Downloading BGE-M3 embedding model (~2.2 GB)...")
    just_download(
        repo_id="BAAI/bge-m3",
        output_dir=str(models_dir / "bge-m3")
    )
    
    print("\nDownloading BGE-Reranker-v2-M3 reranker model (~2.2 GB)...")
    just_download(
        repo_id="BAAI/bge-reranker-v2-m3",
        output_dir=str(models_dir / "bge-reranker-v2-m3")
    )
    
    print("\n=== ALL SUPPORT MODELS DOWNLOADED ===")
