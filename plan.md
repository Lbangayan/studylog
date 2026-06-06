# studylog – Project Plan

## Overview
A Python CLI tool for logging study sessions. Displays a live timer while you study,
tracks which apps you have in focus (Windows only, via pywin32), and stores session
history so you can review how you've been spending your time.

---

## Assignment Requirements Checklist
- [ ] Solves a non-trivial problem
- [ ] Hosted in a public GitHub repository with organic commit history
- [ ] Written as a Python command-line tool
- [ ] Managed with `uv`, installable via `uv add "git+https://github.com/<user>/studylog"`
- [ ] README.md with description and usage sections

---

## Features

### Core Commands
| Command | Description |
|---|---|
| `studylog start <subject>` | Start a study session with a live timer |
| `studylog stop` | Stop the active session and save it |
| `studylog history` | List all past sessions |
| `studylog summary` | Show time spent per subject (past 7 days by default) |

### Live Timer Display (rich)
- When `studylog start` is running, show a live-updating panel:
  ```
  Studying: DSC190
  Time:     00:23:45
  Press Ctrl+C to stop
  ```

### App Tracking (pywin32, Windows only)
- While a session is active, poll the foreground window every 2 seconds
- Record app name + cumulative time spent in each app
- On session end, show a breakdown:
  ```
  App usage during session:
    VS Code     32m  ████████████░░
    Chrome      10m  ████░░░░░░░░░░
    Discord      3m  █░░░░░░░░░░░░░
  ```

### Focus Mode (optional stretch goal)
- `studylog start <subject> --focus Discord,YouTube`
- Print a warning in the terminal if a blocked app comes to the foreground

---

## Data Storage
- Sessions stored in `~/.studylog/sessions.json`
- Each session record:
  ```json
  {
    "id": "uuid",
    "subject": "DSC190",
    "start": "2026-06-05T14:00:00",
    "end": "2026-06-05T14:45:00",
    "duration_seconds": 2700,
    "app_usage": {
      "Code.exe": 1920,
      "chrome.exe": 600,
      "Discord.exe": 180
    }
  }
  ```

---

## Tech Stack
| Library | Purpose |
|---|---|
| `typer` | CLI argument parsing and subcommands |
| `rich` | Live timer display, colored tables, progress bars |
| `pywin32` | Foreground window tracking (Windows only) |

---

## File Structure
```
studylog/
├── plan.md
├── pyproject.toml
├── README.md
└── src/
    └── studylog/
        ├── __init__.py       # entry point → main()
        ├── cli.py            # typer app, all commands
        ├── tracker.py        # live timer + app tracking loop
        ├── storage.py        # read/write sessions.json
        └── display.py        # rich tables, summary charts
```

---

## Build Order (2-day plan)

### Day 1
1. Set up repo, uv project, dependencies
2. `storage.py` — load/save sessions
3. `tracker.py` — live timer with rich, app polling with pywin32
4. `studylog start` + `studylog stop` working end-to-end

### Day 2
1. `studylog history` — table of past sessions
2. `studylog summary` — per-subject breakdown with bar chart
3. Focus mode (`--focus` flag) if time allows
4. README.md, final cleanup, push to GitHub
