import requests
import datetime
from pathlib import Path

def download_scryfall_data(output_dir="data"):
    meta_url = "https://api.scryfall.com/bulk-data/default-cards"
    r = requests.get(meta_url)
    r.raise_for_status()
    info = r.json()
    download_url = info["download_uri"]

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"default-cards-{timestamp}.json"
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📥 Downloading Scryfall data to {output_path} ...")
    with requests.get(download_url, stream=True) as resp:
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    print("✅ Download complete.")
    return output_path

if __name__ == "__main__":
    download_scryfall_data()
