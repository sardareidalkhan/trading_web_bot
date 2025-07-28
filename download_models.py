import os
import gdown
import zipfile

# ⚠️ CHANGE THIS TO YOUR ZIP FILE ID (not folder!)
file_id = "1T-wQFIpBHvFthlC_-y0hoaDN9C999-hM"

zip_path = "model.zip"
extract_path = os.path.join("EXTRA_THINGS", "all_dataset")
os.makedirs(extract_path, exist_ok=True)

def download_and_extract_zip():
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        print("⬇️ Downloading model ZIP...")
        gdown.download(url, zip_path, quiet=False)

        print("📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        print(f"✅ Models extracted to: {extract_path}")
    except Exception as e:
        print("❌ Failed to download or extract model zip:", e)

if __name__ == "__main__":
    download_and_extract_zip()
