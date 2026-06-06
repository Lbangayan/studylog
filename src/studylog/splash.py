"""splash.py - Animated PyBonsai splash screen shown before each study session."""

from __future__ import annotations

import random
import shutil
import time
from math import radians

from rich.console import Console

from studylog.bonsai import draw as bonsai_draw
from studylog.bonsai import tree as bonsai_tree

console = Console()


class _Options:
    """Minimal options object matching what PyBonsai's draw/tree modules expect."""

    def __init__(self, animated: bool = True):
        self.num_layers = 8
        self.initial_len = 15
        self.angle_mean = radians(40)
        self.leaf_len = 4
        self.instant = not animated
        self.wait_time = 0.015 if animated else 0
        self.branch_chars = "~;:="
        self.leaf_chars = "&%#@"
        self.fixed_window = False


def show_splash(subject: str, animated: bool = True) -> None:
    """
    Grow a procedural PyBonsai tree seeded from the subject name, then
    transition to the live study timer.

    The same subject always produces the same tree shape.
    """
    # Deterministic seed so DSC190 always grows the same tree
    seed = hash(subject) & 0xFFFF_FFFF
    random.seed(seed)

    cols, rows = shutil.get_terminal_size(fallback=(80, 25))
    width = min(cols, 80)
    height = min(rows - 3, 25)

    # Pick tree type from subject hash (0-3)
    tree_type = hash(subject) % 4

    options = _Options(animated=animated)
    window = bonsai_draw.TerminalWindow(width, height, options)

    root_x = window.width // 2
    root_y = bonsai_tree.Tree.BOX_HEIGHT + 4
    root_y += root_y % 2  # round to even (PyBonsai requirement)
    root_pos = (root_x, root_y)

    tree_classes = [
        bonsai_tree.ClassicTree,
        bonsai_tree.FibonacciTree,
        bonsai_tree.OffsetFibTree,
        bonsai_tree.RandomOffsetFibTree,
    ]
    t = tree_classes[tree_type](window, root_pos, options)

    # Draw the tree (animated or instant)
    t.draw()

    # Final full redraw + move cursor back to bottom
    window.draw()
    window.reset_cursor()

    # Brief pause so the completed tree is visible before timer takes over
    console.print(f"\n  [bold green]Your bonsai is ready.[/bold green]  Starting session: [bold cyan]{subject}[/bold cyan]")
    time.sleep(1.2)
