"""cli.py – typer command definitions."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from studylog import storage
from studylog.tracker import SessionTracker
from studylog import display

app = typer.Typer(
    name="studylog",
    help="Log and track your study sessions with a live timer and app usage stats.",
    add_completion=False,
)
console = Console()


# ---------------------------------------------------------------------------
# start
# ---------------------------------------------------------------------------

@app.command()
def start(
    subject: str = typer.Argument(..., help="Subject or class you are studying (e.g. DSC190)"),
    focus: Optional[str] = typer.Option(
        None,
        "--focus",
        help="Comma-separated list of apps to warn about (e.g. Discord,YouTube)",
    ),
) -> None:
    """Start a study session with a live timer."""
    # check for already-running session
    active = storage.read_active()
    if active:
        console.print(
            f"[yellow]A session is already active for [bold]{active['subject']}[/bold].[/yellow]\n"
            "Run [bold]studylog stop[/bold] first."
        )
        raise typer.Exit(1)

    blocked = [a.strip() for a in focus.split(",")] if focus else []

    session = storage.new_session(subject)
    storage.write_active(session)

    console.print(f"\n[bold green]Starting session:[/bold green] {subject}")
    if blocked:
        console.print(f"[bold red]Focus mode on:[/bold red] {', '.join(blocked)}\n")

    tracker = SessionTracker(session, focus_block=blocked)
    completed = tracker.run()

    storage.clear_active()
    storage.save_session(completed)

    from studylog.display import _fmt_duration  # local import to avoid circular
    console.print(
        f"\n[bold green]Session saved![/bold green] "
        f"{subject} — {_fmt_duration(completed['duration_seconds'])}"
    )
    display.print_app_usage(completed.get("app_usage", {}))


# ---------------------------------------------------------------------------
# stop  (emergency stop if Ctrl-C didn't fire cleanly)
# ---------------------------------------------------------------------------

@app.command()
def stop() -> None:
    """Mark any lingering active session as stopped and save it."""
    active = storage.read_active()
    if not active:
        console.print("[yellow]No active session found.[/yellow]")
        raise typer.Exit(1)

    from datetime import datetime
    from studylog.display import _fmt_duration

    active["end"] = datetime.now().isoformat()
    start_dt = datetime.fromisoformat(active["start"])
    end_dt = datetime.fromisoformat(active["end"])
    active["duration_seconds"] = int((end_dt - start_dt).total_seconds())

    storage.clear_active()
    storage.save_session(active)

    console.print(
        f"[bold green]Session saved![/bold green] "
        f"{active['subject']} — {_fmt_duration(active['duration_seconds'])}"
    )


# ---------------------------------------------------------------------------
# history
# ---------------------------------------------------------------------------

@app.command()
def history() -> None:
    """List all past study sessions."""
    sessions = storage.load_sessions()
    display.print_history(sessions)


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

@app.command()
def summary(
    days: int = typer.Option(7, "--days", "-d", help="Number of past days to include"),
) -> None:
    """Show time spent per subject over the past N days."""
    sessions = storage.load_sessions()
    display.print_summary(sessions, days=days)
