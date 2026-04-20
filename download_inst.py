import requests
import os
import json

def download_json_file(url, save_path):
    try:
        # Create folder if not exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Download file
        response = requests.get(url)
        response.raise_for_status()

        # Parse JSON
        data = response.json()

        # Save with indent=4
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ File downloaded & formatted → {save_path}")

    except Exception as e:
        print(f"❌ Error downloading file: {e}")


def download_json_file(url, save_path):
    try:
        # Create folder if not exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Download file
        response = requests.get(url)
        response.raise_for_status()

        # Parse JSON
        data = response.json()

        # Save with indent=4
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ File downloaded & formatted → {save_path}")

    except Exception as e:
        print(f"❌ Error downloading file: {e}")

url = "https://github.com/acc0012/instrument-list-backup/raw/refs/heads/main/data/api-scrip-master-1.json"
save_path = "downloads/api-scrip-master-1.json"

download_json_file(url, save_path)        