# W4GNS General Logger

A desktop contact logging app for amateur radio operators with SKCC award tracking.

## Requirements
- Python 3.12+
- pip

## Install
1. (Optional) Create a virtual environment.
   - Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `py -m venv .venv && .venv\\Scripts\\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`

## Run
- `python3 main.py`
- Windows: `py main.py`

## First run setup
- Open Settings and enter your callsign, SKCC number, and station info.
- Configure QRZ and other integrations if you use them.
- The database is stored in `logger.db` in the project directory.
- Download SKCC rosters from the Awards tab when prompted.

## Basic use
- Logging tab: enter QSO details and press Log (or Ctrl+Enter).
- Contacts tab: search and edit existing QSOs.
- Awards tab: view progress and export applications.
