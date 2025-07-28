import os
import subprocess

# Your Google Drive folder ID for `all_dataset`
FOLDER_ID = "1gbkQveWb_fepsCmC0r5oif7ecy7LrZNz"

# Output directory inside your project
TARGET_DIR = os.path.join("EXTRA_THINGS", "all_dataset")
os.makedirs(TARGET_DIR, exist_ok=True)

def download_all_models():
    print("⬇️ Downloading all_dataset folder from Google Drive...")
    try:
        subprocess.run([
            "gdown",
            f"--folder https://drive.google.com/drive/folders/{FOLDER_ID}",
            "--output", TARGET_DIR,
            "--quiet"
        ], check=True)
        print("✅ Models downloaded successfully to:", TARGET_DIR)
    except subprocess.CalledProcessError as e:
        print("❌ Failed to download model folder:", e)

if __name__ == "__main__":
    download_all_models()
