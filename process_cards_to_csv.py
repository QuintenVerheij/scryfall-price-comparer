import pandas as pd
from pathlib import Path
import datetime
import os

MAX_HISTORY = 5

def print_progress_bar(progress, total, bar_length=40, label=""):
    percent = 100 * (progress / total)
    filled = int(bar_length * progress / total)
    bar = "█" * filled + "-" * (bar_length - filled)
    print(f"\r{label} |{bar}| {percent:5.1f}%", end="")

def process_and_export_to_csv(filtered_json_path):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    output_dir = Path("data/exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"filtered_cards_with_diff_{timestamp}.csv"

    print(f"📊 Processing {filtered_json_path} ...")
    df = pd.read_json(filtered_json_path)

    # Flatten the nested "prices" dictionary
    prices_df = pd.json_normalize(df['prices'])
    df = pd.concat([df, prices_df], axis=1)

    # Convert price columns to numeric
    for col in ["eur", "usd", "eur_foil", "usd_foil"]:
        df[col] = pd.to_numeric(df.get(col), errors="coerce")

    # Compute differences safely
    df["diff_abs"] = (df["eur"] - df["usd"]).round(2)
    df["diff_pct"] = ((df["eur"] - df["usd"]) / df["usd"] * 100).round(2)
    df["diff_abs_foil"] = (df["eur_foil"] - df["usd_foil"]).round(2)
    df["diff_pct_foil"] = ((df["eur_foil"] - df["usd_foil"]) / df["usd_foil"] * 100).round(2)


    columns_to_keep = ["name", "set", "collector_number", "usd", "usd_foil", "eur", "eur_foil", "diff_abs", "diff_pct","diff_abs_foil","diff_pct_foil"]
    df = df[columns_to_keep]

    print("💾 Writing CSV file...")
    df.to_csv(output_file, index=False, float_format="%.2f")
    print(f"\n✅ Exported {output_file}")

    cleanup_old_exports(output_dir)
    return output_file

def cleanup_old_exports(output_dir: Path):
    files = sorted(output_dir.glob("filtered_cards_with_diff_*.csv"), reverse=True)
    if len(files) > MAX_HISTORY:
        for old_file in files[MAX_HISTORY:]:
            try:
                os.remove(old_file)
                print(f"🧹 Removed old file: {old_file.name}")
            except OSError as e:
                print(f"⚠️ Could not remove {old_file}: {e}")

if __name__ == "__main__":
    latest_file = sorted(Path("data").glob("default-cards-*.json"), reverse=True)[0]
    process_and_export_to_csv(latest_file)
