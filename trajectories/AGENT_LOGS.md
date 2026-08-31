# Agent Trajectory Writeup

This document walks through representative examples of the sort agent's 
reasoning, covering a normal case, both intentionally ambiguous test cases, 
and both adversarial test cases. Full raw logs for all 22 files are in 
`sort_agent_run.json` and `close_agent_run.json` in this same folder.

## Sort Agent — Instructions Given

Every file is classified using the same prompt template: the filename, 
the first 300 characters of file content, and the file's creation date are 
provided, along with the fixed list of 4 valid task names. The model is told 
to return `task: null` rather than guess if it isn't confident. See 
`agent/sort_agent.py` (PROMPT_TEMPLATE) for the exact wording.

## Representative Cases

### `Client_A_Proposal_Draft.docx`
- **Model output:** task = `Client Proposal`, confidence = `high`
- **Reasoning given:** The filename and content explicitly indicate a proposal draft for a client engagement.
- **Destination:** `data/Sorted_Agent/Client Proposal/2026-08-03/Client_A_Proposal_Draft.docx`
- **Model used:** `gemini-3.5-flash-lite`

### `Notes.docx`
- **Model output:** task = `None`, confidence = `low`
- **Reasoning given:** The filename and content are too generic to confidently map the notes to any specific task.
- **Destination:** `data/Sorted_Agent/_Needs_Review/Notes.docx`
- **Model used:** `gemini-3.5-flash-lite`

### `Meeting_Summary.pdf`
- **Model output:** task = `None`, confidence = `low`
- **Reasoning given:** The filename and content are too generic to confidently map to any of the specific task categories.
- **Destination:** `data/Sorted_Agent/_Needs_Review/Meeting_Summary.pdf`
- **Model used:** `gemini-3.5-flash-lite`

### `Proposal_Feedback.docx`
- **Model output:** task = `Conference Prep`, confidence = `high`
- **Reasoning given:** The file content explicitly discusses feedback from conference organizers on a submitted talk proposal and preparations for the event.
- **Destination:** `data/Sorted_Agent/Conference Prep/2026-08-23/Proposal_Feedback.docx`
- **Model used:** `gemini-3.5-flash-lite`

### `Demo_Prep_Notes.docx`
- **Model output:** task = `Conference Prep`, confidence = `high`
- **Reasoning given:** The file content explicitly mentions preparing a demo for an upcoming conference presentation.
- **Destination:** `data/Sorted_Agent/Conference Prep/2026-08-27/Demo_Prep_Notes.docx`
- **Model used:** `gemini-3.5-flash-lite`

## Close Agent — Full Run

Unlike the sort agent, the close agent uses rule-based logic for standard 
decisions (deterministic, based on task status) and only calls the LLM for 
the 2 ambiguous items, to generate a human-readable summary for the user.

### `Client_A_Proposal_Draft.docx`
- **Decision:** KEEP_OPEN
- **Reasoning:** Task 'Client Proposal' is still in progress — must not close.

### `Google Sheets - Client Proposal Pricing`
- **Decision:** CLOSE
- **Reasoning:** Task 'Client Proposal' is marked done — safe to close.

### `W2_Statement_2025.pdf`
- **Decision:** CLOSE
- **Reasoning:** Task 'Tax Filing' is marked done — safe to close.

### `TurboTax - 2025 Tax Return Filing`
- **Decision:** KEEP_OPEN
- **Reasoning:** Task 'Tax Filing' is still in progress — must not close.

### `Figma - Web Redesign - Wireframe v2`
- **Decision:** KEEP_OPEN
- **Reasoning:** Task 'Website Redesign' is still in progress — must not close.

### `logo_revised_transparent.png`
- **Decision:** CLOSE
- **Reasoning:** Task 'Website Redesign' is marked done — safe to close.

### `Presentation_Slides_Final.pptx`
- **Decision:** CLOSE
- **Reasoning:** Task 'Conference Prep' is marked done — safe to close.

### `Conference Registration & Schedule`
- **Decision:** KEEP_OPEN
- **Reasoning:** Task 'Conference Prep' is still in progress — must not close.

### `Untitled Document`
- **Decision:** NEEDS_CONFIRMATION
- **Reasoning:** Task is unclear or unassigned — flagging for human review rather than guessing.
- **Generated summary for user:** This untitled document doesn't match any active tasks; review it to decide whether to keep or close.

### `New Tab`
- **Decision:** NEEDS_CONFIRMATION
- **Reasoning:** Task is unclear or unassigned — flagging for human review rather than guessing.
- **Generated summary for user:** This unassigned tab has no clear context, so you can safely close it if not needed.
