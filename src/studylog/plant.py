"""plant.py - PyBonsai-backed plant that grows larger at each time milestone."""

from __future__ import annotations

import random
from math import radians

from rich.text import Text

from studylog.bonsai import draw as bonsai_draw
from studylog.bonsai import tree as bonsai_tree

# ---------------------------------------------------------------------------
# Stage thresholds and labels
# ---------------------------------------------------------------------------

STAGE_THRESHOLDS = [0, 5, 10, 20, 35, 50, 70]  # minutes

_LABELS = [
    "Just planted!",
    "It's sprouting!",
    "Growing nicely...",
    "Looking leafy!",
    "Quite the bush!",
    "Almost a tree!",
    "Fully grown!",
]

# (num_layers, initial_len) per stage — tree grows more complex over time
_STAGE_PARAMS = [
    (1,  3),   # 0 — tiny stub
    (2,  5),   # 1
    (3,  7),   # 2
    (4,  9),   # 3
    (5, 11),   # 4
    (6, 13),   # 5
    (8, 15),   # 6 — full tree
]

PANEL_WIDTH  = 36   # chars — matches the left panel width
PANEL_HEIGHT = 20   # fixed so the panel doesn't jump when the tree grows

# ---------------------------------------------------------------------------
# Module-level state (set once per session via init_plant)
# ---------------------------------------------------------------------------

_seed: int = 0
_cache: dict[int, list[Text]] = {}


def init_plant(subject: str) -> None:
    """Call this before starting a session to seed the RNG from the subject."""
    global _seed, _cache
    _seed = hash(subject) & 0xFFFF_FFFF
    _cache = {}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class _Opts:
    """Minimal options shim for PyBonsai's draw/tree modules."""

    def __init__(self, num_layers: int, initial_len: int) -> None:
        self.num_layers   = num_layers
        self.initial_len  = initial_len
        self.angle_mean   = radians(40)
        self.leaf_len     = 3
        self.instant      = True
        self.wait_time    = 0
        self.branch_chars = "~;:="
        self.leaf_chars   = "&%#@"
        self.fixed_window = True   # never expand beyond PANEL_HEIGHT


def _generate_bonsai(stage: int) -> list[Text]:
    """Generate a PyBonsai tree for this stage, return as rich Text lines."""
    num_layers, initial_len = _STAGE_PARAMS[stage]

    # Each stage has a deterministic but unique seed so it always looks the same
    random.seed(_seed + stage * 31337)

    opts   = _Opts(num_layers, initial_len)
    window = bonsai_draw.TerminalWindow(PANEL_WIDTH, PANEL_HEIGHT, opts)

    root_x = window.width // 2
    root_y = bonsai_tree.Tree.BOX_HEIGHT + 4
    root_y += root_y % 2
    root_pos = (root_x, root_y)

    tree_type = _seed % 4
    tree_classes = [
        bonsai_tree.ClassicTree,
        bonsai_tree.FibonacciTree,
        bonsai_tree.OffsetFibTree,
        bonsai_tree.RandomOffsetFibTree,
    ]
    t = tree_classes[tree_type](window, root_pos, opts)
    t.draw()

    # Convert the ANSI-colored char grid to rich Text lines
    lines: list[Text] = []
    for row in window.chars:
        row_str = "".join(row)
        lines.append(Text.from_ansi(row_str))

    return lines


# ---------------------------------------------------------------------------
# Public API (same interface as before so tracker.py needs no changes)
# ---------------------------------------------------------------------------

def get_stage(elapsed_seconds: int) -> int:
    elapsed_minutes = elapsed_seconds // 60
    stage = 0
    for i, threshold in enumerate(STAGE_THRESHOLDS):
        if elapsed_minutes >= threshold:
            stage = i
    return stage


def render_plant(elapsed_seconds: int) -> tuple[list[Text], str]:
    """Return (rich Text lines, label) for the current stage. Cached per stage."""
    stage = get_stage(elapsed_seconds)
    if stage not in _cache:
        _cache[stage] = _generate_bonsai(stage)
    return _cache[stage], _LABELS[stage]


def next_stage_in(elapsed_seconds: int) -> int | None:
    """Seconds until the next stage, or None if already at max."""
    stage = get_stage(elapsed_seconds)
    if stage >= len(STAGE_THRESHOLDS) - 1:
        return None
    return max(0, STAGE_THRESHOLDS[stage + 1] * 60 - elapsed_seconds)
