"""display.py – rich tables and summary charts."""

from __future__ import annotations

from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

BAR_WIDTH = 20


def _bar(fraction: float) -> str:
    filled = round(fraction * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def _fmt_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


# ---------------------------------------------------------------------------
# App usage breakdown
# ---------------------------------------------------------------------------

def print_app_usage(app_usage: dict[str, int]) -> None:
    if not app_usage:
        console.print("[dim]No app usage data recorded.[/dim]")
        return

    total = sum(app_usage.values()) or 1
    sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)

    table = Table(
        title="App Usage This Session",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("App", style="cyan", no_wrap=True)
    table.add_column("Time", justify="right")
    table.add_column("Bar", no_wrap=True)

    for app, secs in sorted_apps:
        frac = secs / total
        table.add_row(app, _fmt_duration(secs), f"[green]{_bar(frac)}[/green]")

    console.print(table)


# ---------------------------------------------------------------------------
# History table
# ---------------------------------------------------------------------------

def print_history(sessions: list[dict]) -> None:
    if not sessions:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        return

    table = Table(
        title="Study History",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Subject", style="cyan")
    table.add_column("Date")
    table.add_column("Duration", justify="right")
    table.add_column("Top App", style="dim")

    for i, s in enumerate(reversed(sessions), 1):
        start = datetime.fromisoformat(s["start"])
        date_str = start.strftime("%Y-%m-%d %H:%M")
        duration = _fmt_duration(s.get("duration_seconds", 0))
        app_usage = s.get("app_usage", {})
        top_app = max(app_usage, key=app_usage.get, default="—")  # type: ignore[arg-type]
        table.add_row(str(i), s["subject"], date_str, duration, top_app)

    console.print(table)


# ---------------------------------------------------------------------------
# Summary (per-subject breakdown over N days)
# ---------------------------------------------------------------------------

def print_summary(sessions: list[dict], days: int = 7) -> None:
    cutoff = datetime.now() - timedelta(days=days)
    recent = [
        s for s in sessions
        if datetime.fromisoformat(s["start"]) >= cutoff
    ]

    if not recent:
        console.print(f"[yellow]No sessions in the past {days} days.[/yellow]")
        return

    # aggregate by subject
    totals: dict[str, int] = {}
    for s in recent:
        totals[s["subject"]] = totals.get(s["subject"], 0) + s.get("duration_seconds", 0)

    grand_total = sum(totals.values()) or 1
    sorted_subjects = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    table = Table(
        title=f"Study Summary — Past {days} Days",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Subject", style="cyan")
    table.add_column("Total Time", justify="right")
    table.add_column("Bar", no_wrap=True)
    table.add_column("%", justify="right")

    for subject, secs in sorted_subjects:
        frac = secs / grand_total
        pct = f"{frac * 100:.1f}%"
        table.add_row(subject, _fmt_duration(secs), f"[blue]{_bar(frac)}[/blue]", pct)

    total_text = Text(f"Total: {_fmt_duration(grand_total)}", style="bold")
    console.print(table)
    console.print(total_text)
