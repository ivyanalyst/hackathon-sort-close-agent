"""
Agent: classifies files into tasks using filename + content + date,
following the rules in TAXONOMY_SPEC.md. Copies files into
data/Sorted_Agent/{TaskName}/{Date}/filename, or _Needs_Review if uncertain.
Logs every decision + reasoning to trajectories/ for later review.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SOURCE_DIR = Path("data/raw_downloads")
OUTPUT_DIR = Path("data/Sorted_Agent")
TRAJECTORY_LOG = Path("trajectories/sort_agent_run.json")

TASKS = ["Client Proposal", "Tax Filing", "Website Redesign", "Conference Prep"]
MODEL_NAME = "gemini-3.5-flash-lite"

PROMPT_TEMPLATE = """You are a file-sorting assistant. Classify the following file into exactly ONE of these tasks: {tasks}

If you cannot confidently determine the task from the filename and content, respond with task: null instead of guessing.

Filename: {filename}
File content: {content}
File date: {date}

Respond ONLY with valid JSON in this exact format, no markdown fences, no explanation outside the JSON:
{{"task": "<one of the task names or null>", "confidence": "<high|medium|low>", "reasoning": "<one sentence explaining your decision>"}}
"""


def get_creation_date(filepath: Path) -> str:
    timestamp = filepath.stat().st_mtime
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def read_content(filepath: Path, max_chars: int = 300) -> str:
    try:
        return filepath.read_text(errors="ignore")[:max_chars]
    except Exception:
        return "(binary or unreadable content)"


def classify_file(filepath: Path) -> dict:
    content = read_content(filepath)
    date_str = get_creation_date(filepath)

    prompt = PROMPT_TEMPLATE.format(
        tasks=", ".join(TASKS),
        filename=filepath.name,
        content=content,
        date=date_str
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {"task": None, "confidence": "low", "reasoning": f"Failed to parse model response: {raw_text[:100]}"}

    result["date"] = date_str
    return result


def sort_agent():
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source folder not found: {SOURCE_DIR}")

    files = [f for f in SOURCE_DIR.iterdir() if f.is_file()]
    print(f"Found {len(files)} files to classify.\n")

    trajectory = []

    already_processed = set()
    for existing in OUTPUT_DIR.rglob("*"):
        if existing.is_file():
            already_processed.add(existing.name)

    for file in files:
        if file.name in already_processed:
            print(f"Skipping (already processed): {file.name}")
            continue
        print(f"Classifying: {file.name} ...")
        try:
            result = classify_file(file)
        except Exception as e:
            print(f"  ERROR: {e}")
            dest_folder = OUTPUT_DIR / "_Needs_Review"
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / file.name
            shutil.copy2(file, dest_path)
            trajectory.append({
                "file": file.name,
                "task": None,
                "confidence": "error",
                "reasoning": f"API error: {str(e)[:150]}",
                "destination": str(dest_path),
                "model_used": MODEL_NAME
            })
            print(f"  -> NEEDS REVIEW (error): {str(e)[:80]}")
            continue

        task = result.get("task")
        date_str = result.get("date")

        if task in TASKS:
            dest_folder = OUTPUT_DIR / task / date_str
        else:
            dest_folder = OUTPUT_DIR / "_Needs_Review"

        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / file.name
        shutil.copy2(file, dest_path)

        log_entry = {
            "file": file.name,
            "task": task,
            "confidence": result.get("confidence"),
            "reasoning": result.get("reasoning"),
            "date": date_str,
            "destination": str(dest_path),
            "model_used": MODEL_NAME
        }
        trajectory.append(log_entry)
        print(f"  -> {task or 'NEEDS REVIEW'} ({result.get('confidence')}): {result.get('reasoning')}")

    TRAJECTORY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TRAJECTORY_LOG, "w") as f:
        json.dump(trajectory, f, indent=2)

    print(f"\nDone. {len(trajectory)} files processed.")
    print(f"Trajectory log saved to {TRAJECTORY_LOG}")
    return trajectory


if __name__ == "__main__":
    sort_agent()
