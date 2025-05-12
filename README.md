# Vanta Ledger

This project is a ledger application with a Python Kivy-based desktop/mobile UI.

## Setup

1. Create and activate a Python virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the backend API server (if applicable):

```bash
uvicorn src.vanta_ledger.main:app --reload
```

4. Run the Kivy UI app:

```bash
./run.sh
```

or on Windows:

```bash
run.bat
```

## Removed Frontends

- The old Vue.js frontend and Tkinter UI app have been removed.
- The current UI is implemented using Kivy for better mobile and desktop support.

## Notes

- The Kivy app requires system clipboard utilities `xclip` and `xsel` on Linux.
- If you encounter crashes or segmentation faults, it may be related to graphics drivers or Kivy compatibility.
- Consider running the app with debug logging enabled for troubleshooting.

## Project Cleanup

- Unused frontend files and dependencies have been removed.
- The project is cleaned up to focus on the Kivy UI app and backend API.
