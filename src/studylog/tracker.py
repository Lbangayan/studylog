"""tracker.py – live timer display + background app-usage polling (Windows)."""

from __future__ import annotations

import time
import threading
from datetime import datetime

from rich.console import Console
from rich.columns import Columns
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from studylog import storage
from studylog.plant import init_plant, render_plant, next_stage_in, get_stage

console = Console()

# ---------------------------------------------------------------------------
# App tracking (Windows only via pywin32)
# ---------------------------------------------------------------------------

def _get_active_exe() -> str | None:
    """Return the exe name of the current foreground window, or None."""
    try:
        import win32gui
        import win32process
        import psutil  # not required; fall back gracefully

        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            import psutil
            return psutil.Process(pid).name()
        except Exception:
            pass
        # fallback: just return window title
        return win32gui.GetWindowText(hwnd) or None
    except Exception:
        return None


def _get_active_exe_simple() -> str | None:
    """Simpler fallback using only pywin32 (no psutil)."""
    try:
        import win32gui
        import win32process
        import win32api

        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        handle = win32api.OpenProcess(0x0400 | 0x0010, False, pid)
        exe_path: str = win32process.GetModuleFileNameEx(handle, 0)
        win32api.CloseHandle(handle)
        return exe_path.split("\\")[-1]
    except Exception:
        return None


def get_foreground_app() -> str | None:
    """Best-effort: try psutil first, then pywin32 fallback, then None."""
    try:
        import psutil  # noqa: F401 – just testing availability
        return _get_active_exe()
    except ImportError:
        return _get_active_exe_simple()


# ---------------------------------------------------------------------------
# Live timer + app poller
# ---------------------------------------------------------------------------

def _format_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class SessionTracker:
    """Runs the live UI and polls the active app in a background thread."""

    POLL_INTERVAL = 2  # seconds between app checks

    def __init__(self, session: dict, focus_block: list[str] | None = None):
        self.session = session
        self.focus_block = [a.lower() for a in (focus_block or [])]
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._last_app: str | None = None
        self._app_start: float = time.monotonic()
        # plant panel is expensive to build (re-parses bonsai ANSI), so cache
        # it and only rebuild when the growth stage actually changes
        self._cached_stage: int | None = None
        self._cached_plant_panel: Panel | None = None

    # ------------------------------------------------------------------
    # Background polling thread
    # ------------------------------------------------------------------

    def _poll_apps(self) -> None:
        while not self._stop_event.is_set():
            app = get_foreground_app()
            now = time.monotonic()

            with self._lock:
                if app and app != self._last_app:
                    # credit elapsed time to previous app
                    if self._last_app:
                        elapsed = int(now - self._app_start)
                        self.session["app_usage"][self._last_app] = (
                            self.session["app_usage"].get(self._last_app, 0) + elapsed
                        )
                    self._last_app = app
                    self._app_start = now

            # focus-mode warning
            if app and self.focus_block:
                for blocked in self.focus_block:
                    if blocked in app.lower():
                        console.print(
                            f"\n[bold red]⚠ Focus mode:[/bold red] {app} is blocked!",
                            highlight=False,
                        )
                        break

            time.sleep(self.POLL_INTERVAL)

    def _flush_current_app(self) -> None:
        """Credit remaining time to the last seen app on stop."""
        now = time.monotonic()
        with self._lock:
            if self._last_app:
                elapsed = int(now - self._app_start)
                self.session["app_usage"][self._last_app] = (
                    self.session["app_usage"].get(self._last_app, 0) + elapsed
                )

    # ------------------------------------------------------------------
    # Live timer UI
    # ------------------------------------------------------------------

    def _build_plant_panel(self, elapsed: int) -> Panel:
        """Build the bonsai panel. Cached and only rebuilt when the stage changes.

        Only the static tree + stage label live here; the per-second countdown
        lives in the info panel so this panel stays identical between stages.
        """
        stage = get_stage(elapsed)
        if stage == self._cached_stage and self._cached_plant_panel is not None:
            return self._cached_plant_panel

        plant_lines, plant_label = render_plant(elapsed)

        plant_text = Text()
        for line in plant_lines:
            plant_text.append_text(line)
            plant_text.append("\n")
        plant_text.append(f"\n{plant_label}", style="dim italic")

        panel = Panel(plant_text, border_style="green", padding=(0, 1))
        self._cached_stage = stage
        self._cached_plant_panel = panel
        return panel

    def _build_panel(self, elapsed: int) -> Panel:
        subject = self.session["subject"]
        duration_str = _format_duration(elapsed)

        # --- left side: plant (cached between stage changes) ---
        plant_panel = self._build_plant_panel(elapsed)

        # --- right side: timer info ---
        info = Text()
        info.append("  Subject:  ", style="dim")
        info.append(f"{subject}\n", style="bold cyan")
        info.append("  Time:     ", style="dim")
        info.append(f"{duration_str}\n", style="bold green")

        till_next = next_stage_in(elapsed)
        if till_next is not None:
            m, s = divmod(till_next, 60)
            info.append("  Next:     ", style="dim")
            info.append(f"stage in {m}m {s:02d}s\n", style="green")

        if self.focus_block:
            blocked = ", ".join(self.focus_block)
            info.append("  Blocking: ", style="dim")
            info.append(f"{blocked}\n", style="bold red")

        info.append("\n  Press Ctrl+C to stop", style="dim")
        info_panel = Panel(info, border_style="blue", padding=(1, 2))

        # --- combine side by side ---
        layout = Columns([plant_panel, info_panel], equal=False, expand=True)
        return Panel(layout, title="[bold]studylog[/bold]", border_style="dim")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """Block until Ctrl-C, then return the completed session dict."""
        init_plant(self.session["subject"])

        start_mono = time.monotonic()
        start_dt = datetime.now()

        # kick off app-polling thread
        poll_thread = threading.Thread(target=self._poll_apps, daemon=True)
        poll_thread.start()

        try:
            # auto_refresh=False so there is exactly one controlled redraw per
            # tick (avoids a background refresh thread racing our updates);
            # vertical_overflow="crop" keeps the rendered height constant.
            with Live(
                console=console,
                auto_refresh=False,
                vertical_overflow="crop",
            ) as live:
                while True:
                    elapsed = int(time.monotonic() - start_mono)
                    live.update(self._build_panel(elapsed), refresh=True)
                    time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._stop_event.set()
            poll_thread.join(timeout=3)
            self._flush_current_app()

        end_dt = datetime.now()
        elapsed_total = int((end_dt - start_dt).total_seconds())

        self.session["start"] = start_dt.isoformat()
        self.session["end"] = end_dt.isoformat()
        self.session["duration_seconds"] = elapsed_total

        return self.session
