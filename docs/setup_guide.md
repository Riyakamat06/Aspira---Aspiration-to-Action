# Aspira – Backend Setup Guide

## Purpose
This guide shows a new team member how to run the Aspira backend on their
own machine or in a GitHub Codespace, from a fresh copy of the repository.

## Requirements
- Python 3.10 or newer
- Git
- A GitHub Codespace, or a local terminal

## Steps

### 1. Open the project
Open the repository in a Codespace, or clone it locally:

    git clone https://github.com/Riyakamat06/Aspira---Aspiration-to-Action
    cd Aspira---Aspiration-to-Action

### 2. Create a virtual environment
A virtual environment keeps the project's packages separate from the rest
of the machine.

    python -m venv .venv
    source .venv/bin/activate

On Windows (PowerShell), activate with `.venv\Scripts\Activate.ps1`.
When it works, the prompt starts with `(.venv)`.

### 3. Install the packages

    pip install -r backend/requirements.txt

### 4. Run the server
    cd backend
    uvicorn app.main:app --reload

The server runs at http://127.0.0.1:8000. In a Codespace, open the forwarded
port in the browser.

### 5. Check that it works
- Open `/health` at the end of the address. The reply should be
  `{"status":"ok"}`.
- Open `/docs` to see the automatically generated list of endpoints.

### 6. Run the tests
    cd backend
    pytest

All tests should pass.

## Common problems
| Problem | Cause | Fix |
|---|---|---|
| `uvicorn: command not found` | Packages not installed, or the virtual environment is not active | Activate `.venv`, then run `pip install -r requirements.txt` |
| `No module named 'app...'` | A folder is missing, or a file is empty | Check that the folder has an `__init__.py`, and check the file's size with `wc -l` |
| 404 Not Found at the home address | The app has no page at `/` | Add `/health` or `/docs` to the address |
| Terminal shows `(END)` or `:` | Git opened its reader | Press `q` |

## Notes
- Never commit the `.venv` folder. It is listed in `.gitignore`.
- The database engine (SQLite or PostgreSQL) is not final. Setup steps for
  it will be added once it is chosen.