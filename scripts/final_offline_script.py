import shutil
from pathlib import Path
from huggingface_hub import snapshot_download

vision_dir = Path(r"c:\Users\Sreeharini\vision")
models_dir = vision_dir / "models"

def download_and_zip(repo_id: str, output_dir: str, zip_filename: str):
    print(f"\n--- Processing {repo_id} ---")
    print("1. Downloading (this skips files already downloaded)...")
    snapshot_download(
        repo_id=repo_id,
        local_dir=output_dir,
        local_dir_use_symlinks=False,
        resume_download=True
    )
    
    print(f"2. Packaging to {zip_filename}...")
    print("   (Note: Using .tar format because it handles massive files perfectly on Windows")
    print("    and is the native extraction format on your RHEL VM!)")
    
    base_name = zip_filename.replace('.tar', '')
    shutil.make_archive(
        base_name=base_name,
        format='tar',
        root_dir=output_dir,
        base_dir='.'
    )
    print(f"[{repo_id}] Finished successfully!")

if __name__ == "__main__":
    download_and_zip(
        repo_id="Qwen/Qwen2.5-VL-7B-Instruct",
        output_dir=str(models_dir / "Qwen2.5-VL-7B-Instruct"),
        zip_filename=str(vision_dir / "Qwen2.5-VL-7B-Instruct.tar")
    )
    
    download_and_zip(
        repo_id="Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
        output_dir=str(models_dir / "Qwen2.5-VL-32B-Instruct-AWQ"),
        zip_filename=str(vision_dir / "Qwen2.5-VL-32B-Instruct-AWQ.tar")
    )
    
    print("\nALL MODELS DOWNLOADED AND ZIPPED SAFELY!")
