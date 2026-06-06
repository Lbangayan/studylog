"""plant.py - ASCII art plant that grows as your study session progresses."""

from __future__ import annotations

from rich.text import Text

# ---------------------------------------------------------------------------
# Stages unlock at these elapsed-minute thresholds:
#   0  -> seed
#   5  -> sprout
#   10 -> seedling
#   20 -> small plant
#   35 -> bush
#   50 -> small tree
#   70 -> full tree
# ---------------------------------------------------------------------------

STAGE_THRESHOLDS = [0, 5, 10, 20, 35, 50, 70]  # minutes

# Pure ASCII art per stage - fixed width of 13 chars.
_RAW: list[list[str]] = [
    # 0 - seed
    [
        "             ",
        "             ",
        "      .      ",
        "     (_)     ",
        "   ~~~~~~~   ",
    ],
    # 1 - sprout
    [
        "             ",
        "      '      ",
        "      |      ",
        "      |      ",
        "   ~~~~~~~   ",
    ],
    # 2 - seedling
    [
        "             ",
        "    \\ | /    ",
        "     \\|/     ",
        "      |      ",
        "   ~~~~~~~   ",
    ],
    # 3 - small plant
    [
        "      *      ",
        "    * \\|/ *  ",
        "      |      ",
        "     /|\\     ",
        "   ~~~~~~~   ",
    ],
    # 4 - bush
    [
        "    *****    ",
        "   *******   ",
        "    * | *    ",
        "      |      ",
        "   ~~~~~~~   ",
    ],
    # 5 - small tree
    [
        "     ***     ",
        "   *******   ",
        "  *********  ",
        "      |      ",
        "     /|\\     ",
        "      |      ",
        "   ~~~~~~~   ",
    ],
    # 6 - full tree
    [
        "     ***     ",
        "   *******   ",
        " *********** ",
        "  *********  ",
        "     |||     ",
        "    /|||\\    ",
        "     |||     ",
        "   ~~~~~~~   ",
    ],
]

_LABELS = [
    "Just planted!",
    "It's sprouting!",
    "Growing nicely...",
    "Looking leafy!",
    "Quite the bush!",
    "Almost a tree!",
    "Fully grown!",
]


def _color_line(line: str) -> Text:
    """Apply colors to a single ASCII art line."""
    t = Text()
    for ch in line:
        if ch == "*":
            t.append(ch, style="bold green")
        elif ch in "|/\\.,'":
            t.append(ch, style="yellow")
        elif ch == "~":
            t.append(ch, style="dim green")
        elif ch in "()_":
            t.append(ch, style="yellow")
        else:
            t.append(ch)
    return t


def get_stage(elapsed_seconds: int) -> int:
    """Return the stage index (0-6) for the given elapsed time."""
    elapsed_minutes = elapsed_seconds // 60
    stage = 0
    for i, threshold in enumerate(STAGE_THRESHOLDS):
        if elapsed_minutes >= threshold:
            stage = i
    return stage


def render_plant(elapsed_seconds: int) -> tuple[list[Text], str]:
    """Return (lines, label) for the current growth stage."""
    stage = get_stage(elapsed_seconds)
    lines = [_color_line(line) for line in _RAW[stage]]
    label = _LABELS[stage]
    return lines, label


def next_stage_in(elapsed_seconds: int) -> int | None:
    """Return seconds until the next stage, or None if already at max."""
    stage = get_stage(elapsed_seconds)
    if stage >= len(STAGE_THRESHOLDS) - 1:
        return None
    next_threshold_secs = STAGE_THRESHOLDS[stage + 1] * 60
    return max(0, next_threshold_secs - elapsed_seconds)
