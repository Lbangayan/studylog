"""
test_plant.py - Visual test for all 7 bonsai growth stages.

Run with:
    uv run python tests/test_plant.py
    uv run python tests/test_plant.py --subject CSE151A
    uv run python tests/test_plant.py --fast   # skip the delay between stages
"""

import sys
import time
import argparse

from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from studylog.plant import (
    STAGE_THRESHOLDS,
    _LABELS,
    init_plant,
    render_plant,
    next_stage_in,
)

console = Console()

# Map each stage index to a fake elapsed-seconds value that triggers it
_STAGE_SECONDS = [t * 60 for t in STAGE_THRESHOLDS]


def _fmt(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _build_display(stage_idx: int, elapsed: int, subject: str) -> Panel:
    lines, label = render_plant(elapsed)
    till_next = next_stage_in(elapsed)

    # --- left: bonsai ---
    plant_text = Text()
    for line in lines:
        plant_text.append_text(line)
        plant_text.append("\n")
    plant_text.append(f"\n{label}", style="dim italic")
    if till_next is not None:
        m, s = divmod(till_next, 60)
        plant_text.append(f"\n  next stage in {m}m {s:02d}s", style="dim")

    plant_panel = Panel(plant_text, border_style="green", padding=(0, 1))

    # --- right: fake timer info ---
    info = Text()
    info.append("  Subject:  ", style="dim")
    info.append(f"{subject}\n", style="bold cyan")
    info.append("  Time:     ", style="dim")
    info.append(f"{_fmt(elapsed)}\n", style="bold green")
    info.append(f"\n  Stage {stage_idx + 1} of {len(STAGE_THRESHOLDS)}\n", style="dim")
    info.append("  Press Ctrl+C to stop", style="dim")

    info_panel = Panel(info, border_style="blue", padding=(1, 2))

    layout = Columns([plant_panel, info_panel], equal=False, expand=True)
    return Panel(layout, title="[bold]studylog — growth preview[/bold]", border_style="dim")


def run(subject: str, delay: float) -> None:
    init_plant(subject)
    console.print(f"\n[bold]Previewing all growth stages for:[/bold] [cyan]{subject}[/cyan]\n")

    for i, elapsed in enumerate(_STAGE_SECONDS):
        label = _LABELS[i]
        console.print(f"[dim]Stage {i + 1}/{len(STAGE_THRESHOLDS)} — {label} "
                      f"(~{STAGE_THRESHOLDS[i]} min)[/dim]")

        # Show a ticking countdown within this stage so it feels alive
        tick_end = elapsed + min(int(delay), 5)
        try:
            with Live(console=console, refresh_per_second=4) as live:
                t = elapsed
                end = elapsed + max(int(delay), 1)
                while t <= end:
                    live.update(_build_display(i, t, subject))
                    time.sleep(0.25)
                    t += 1
        except KeyboardInterrupt:
            console.print("\n[yellow]Preview stopped.[/yellow]")
            return

        console.print()

    console.print("[bold green]All stages complete![/bold green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Visual preview of studylog plant growth.")
    parser.add_argument("--subject", default="DSC190", help="Subject name (affects tree shape)")
    parser.add_argument("--fast", action="store_true", help="Skip delay between stages")
    args = parser.parse_args()

    delay = 0.5 if args.fast else 3.0
    run(args.subject, delay)


if __name__ == "__main__":
    main()
