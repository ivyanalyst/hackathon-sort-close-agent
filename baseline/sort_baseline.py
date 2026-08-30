"""
Simple baseline: sorts files by extension + creation date only.
No task reasoning, no LLM. This is the comparison point for the agent.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

SOURCE_DIR = Path("data/raw_downloads")
OUTPUT_DIR = Path("data/Sorted_Baseline")


def get_creation_date(filepath: Path) -> str:
    """Return the file's creation/modified date as YYYY-MM-DD."""
    timestamp = filepath.stat().st_mtime
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def sort_baseline():
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source folder not found: {SOURCE_DIR}")

    files = [f for f in SOURCE_DIR.iterdir() if f.is_file()]
    print(f"Found {len(files)} files to sort.\n")

    results = []

    for file in files:
        extension = file.suffix.lstrip(".").upper() or "NO_EXTENSION"
        date_str = get_creation_date(file)

        dest_folder = OUTPUT_DIR / extension / date_str
        dest_folder.mkdir(parents=True, exist_ok=True)

        dest_path = dest_folder / file.name
        shutil.copy2(file, dest_path)

        results.append({
            "file": file.name,
            "extension": extension,
            "date": date_str,
            "destination": str(dest_path)
        })
        print(f"  {file.name:45s} -> {dest_path}")

    print(f"\nDone. {len(results)} files copied to {OUTPUT_DIR}/")
    return results


if __name__ == "__main__":
    sort_baseline()
