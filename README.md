# studylog

A command-line tool for logging and tracking your study sessions. Start a session and
get a live timer in your terminal while studylog quietly tracks which apps you spend
time in — so at the end you can see exactly how focused you actually were. A procedural
bonsai tree grows in the timer panel as you study, getting more branches the longer you go.

> **Note:** App tracking and the animated bonsai require Windows (`pywin32`). The timer,
> history, and summary commands work on any platform.

## Installation

**Install as a standalone command (recommended):**
```bash
uv tool install "git+https://github.com/Lbangayan/studylog.git"
```
After this, `studylog` works as a command from anywhere in your terminal.

**Or clone and run locally:**
```bash
git clone https://github.com/Lbangayan/studylog.git
cd studylog
uv sync
uv tool install .   # makes `studylog` available system-wide
```

To run without installing (from inside the cloned folder):
```bash
uv run studylog --help
```

**For use as a dependency in another project:**
```bash
uv add "git+https://github.com/Lbangayan/studylog.git"
```

## Usage

### Start a session

```bash
studylog start DSC190
```

Displays a live timer alongside a growing bonsai tree. The tree gains new branches
at 5, 10, 20, 35, 50, and 70 minutes. Press **Ctrl+C** to end the session — your
total time and a per-app usage breakdown are saved automatically.

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

## Data

Sessions are stored in `~/.studylog/sessions.json`. You can back this file up or
delete it at any time.
