# studylog

A command-line tool for logging and tracking your study sessions. Start a session and
get a live timer in your terminal while studylog quietly tracks which apps you spend
time in — so at the end you can see exactly how focused you actually were.

## Installation

```bash
uv add "git+https://github.com/Lbangayan/studylog.git"
```

> **Note:** App tracking uses `pywin32` and is only supported on Windows.

## Usage

### Start a session

```bash
studylog start DSC190
```

Displays a live timer in your terminal. Press **Ctrl+C** to end the session.
When the session ends, your total time and a per-app usage breakdown are shown.

```
╭─ studylog ───────────────────────────────╮
│                                          │
│  Subject:  DSC190                        │
│  Time:     00:23:45                      │
│                                          │
│  Press Ctrl+C to stop                    │
╰──────────────────────────────────────────╯
```

### Start a session with focus mode

```bash
studylog start DSC190 --focus Discord,YouTube
```

Same as above, but prints a warning in the terminal any time one of the listed
apps comes to the foreground — a nudge to get back on track.

### View session history

```bash
studylog history
```

Prints a table of all past sessions with the subject, date, duration, and the
app you spent the most time in.

### View a summary by subject

```bash
studylog summary
```

Shows total time spent per subject over the past 7 days with a bar chart.

```bash
studylog summary --days 30
```

Pass `--days` to change the lookback window (default is 7).

### Emergency stop

```bash
studylog stop
```

If a session was left running (e.g. your terminal closed before Ctrl+C), this
saves it with the current time as the end time.
