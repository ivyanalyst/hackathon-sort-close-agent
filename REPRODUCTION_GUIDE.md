# Reproduction Guide

This guide walks through running this project from a completely clean environment.

## Prerequisites
- Python 3.10+ (developed and tested on Python 3.12)
- A Gemini API key (free tier is sufficient) — get one at https://aistudio.google.com/apikey
- ~10 minutes, no cost on the free tier for a run of this size

## 1. Clone the repository
```bash
git clone https://github.com/ivyanalyst/hackathon-sort-close-agent.git
cd hackathon-sort-close-agent
```

## 2. Set up a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```
This installs `google-genai` (Gemini API client) and `python-dotenv` (for loading the API key).

## 4. Configure your API key
```bash
cp .env.example .env
```
Open `.env` in any text editor and replace the placeholder with your real key:
GEMINI_API_KEY=your_actual_key_here

## 5. Run the baseline (no API calls, instant)
```bash
python3 baseline/sort_baseline.py
```
**Expected output:** 20 files copied from `data/raw_downloads/` into `data/Sorted_Baseline/{Extension}/{Date}/`, grouped purely by file type — no task awareness. Takes under 1 second.

## 6. Run the sort agent
```bash
python3 agent/sort_agent.py
```
**Expected output:** each of the 22 test files is classified one at a time, printed to the terminal with the assigned task and reasoning. Files are copied into `data/Sorted_Agent/{Task}/{Date}/filename`, or `data/Sorted_Agent/_Needs_Review/` if the model isn't confident.

**Expected runtime:** ~2-3 minutes (includes a built-in delay between API calls to respect free-tier rate limits).

**Note on quota:** the free tier allows a limited number of requests per day. If you see `429 RESOURCE_EXHAUSTED` errors partway through, this is expected behavior on a fresh free-tier key under heavy testing — the script has a skip-logic that lets you simply re-run the same command later (or the next day) to pick up where it left off; already-classified files won't be re-processed.

## 7. Run the evaluation
```bash
python3 eval/run_eval.py
```
**Expected output:** a file-by-file comparison against `data/ground_truth.json`, ending in an accuracy score. On our test run: **22/22 (100%)**. Results are also saved to `eval/eval_results.json`.

## 8. Run the close agent (rule-based + 2 LLM calls for ambiguous cases)
```bash
python3 agent/close_agent.py
```
**Expected output:** 10 simulated open items evaluated — expect 4 marked CLOSE, 4 marked KEEP_OPEN, and 2 marked NEEDS_CONFIRMATION with a generated human-readable summary. Results saved to `trajectories/close_agent_run.json`.

## What "success" looks like end to end
- `data/Sorted_Baseline/` populated, organized only by file type
- `data/Sorted_Agent/` populated, organized by task, with `_Needs_Review/` containing the 2 genuinely ambiguous files
- `eval/eval_results.json` showing accuracy at or near 100% on the 22-file test set
- `trajectories/sort_agent_run.json` and `trajectories/close_agent_run.json` containing full reasoning logs for every decision

## Model & cost notes
- Model used: `gemini-3.5-flash-lite` (see `TAXONOMY_SPEC.md` for why this was chosen over the full `flash` model)
- Total API calls for a full run: ~24 (22 sort classifications + 2 close-agent summaries)
- Cost: effectively $0 on the free tier for a run this size

## Resetting to a clean state
To re-run everything from scratch (e.g. to test a modified prompt or taxonomy):
```bash
rm -rf data/Sorted_Baseline data/Sorted_Agent trajectories/*.json eval/eval_results.json
python3 baseline/sort_baseline.py
python3 agent/sort_agent.py
python3 eval/run_eval.py
python3 agent/close_agent.py
```
