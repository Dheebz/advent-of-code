"""Advent of Code 2024 Day 21: Keypad Conundrum."""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path
from typing import Dict, Tuple

Key = str


NUMERIC_POS: Dict[Key, Tuple[int, int]] = {
    "7": (0, 0),
    "8": (0, 1),
    "9": (0, 2),
    "4": (1, 0),
    "5": (1, 1),
    "6": (1, 2),
    "1": (2, 0),
    "2": (2, 1),
    "3": (2, 2),
    "0": (3, 1),
    "A": (3, 2),
}

DIR_POS: Dict[Key, Tuple[int, int]] = {
    "^": (0, 1),
    "A": (0, 2),
    "<": (1, 0),
    "v": (1, 1),
    ">": (1, 2),
}


def parse_input(raw: str) -> list[str]:
    """
    Parse the door codes from the puzzle input.

    Args:
        raw: Input containing one code per line.

    Returns:
        List of code strings.
    """
    return raw.strip().splitlines()


def in_bounds(pos: Tuple[int, int], layout: Dict[Key, Tuple[int, int]]) -> bool:
    """
    Check whether a coordinate corresponds to a keypad button.

    Args:
        pos: Coordinate to check.
        layout: Mapping from keypad keys to coordinates.

    Returns:
        True if `pos` matches a button location.
    """
    return pos in layout.values()


def shortest_paths(src: Key, dst: Key, layout: Dict[Key, Tuple[int, int]]) -> list[str]:
    """
    Compute minimal-length paths between two keypad keys.

    Args:
        src: Source key label.
        dst: Destination key label.
        layout: Map from keys to coordinates.

    Returns:
        List of direction strings representing shortest paths.
    """
    if src == dst:
        return [""]
    target = layout[dst]
    start = layout[src]
    from collections import deque

    queue = deque([(start, "")])
    seen: Dict[Tuple[int, int], int] = {start: 0}
    paths: list[str] = []
    best_len = None
    while queue:
        (r, c), path = queue.popleft()
        if best_len is not None and len(path) > best_len:
            continue
        if (r, c) == target:
            paths.append(path)
            best_len = len(path)
            continue
        for dch, (dr, dc) in zip("^v<>", [(-1, 0), (1, 0), (0, -1), (0, 1)]):
            nr, nc = r + dr, c + dc
            if (nr, nc) not in layout.values():
                continue
            nlen = len(path) + 1
            if nlen > seen.get((nr, nc), 1 << 30):
                continue
            seen[(nr, nc)] = nlen
            queue.append(((nr, nc), path + dch))
    return paths


def canonical_paths(src: Key, dst: Key, layout: Dict[Key, Tuple[int, int]]) -> list[str]:
    """
    Return all minimal-length direction sequences between `src` and `dst`.

    Args:
        src: Starting key.
        dst: Destination key.
        layout: Map from keypad keys to coordinates.

    Returns:
        List of minimal direction strings covering the shortest distance.
    """
    from collections import deque

    start = layout[src]
    target = layout[dst]
    queue = deque([(start, "")])
    visited: Dict[Tuple[int, int], int] = {start: 0}
    paths: list[str] = []
    best = None
    while queue:
        (r, c), path = queue.popleft()
        if best is not None and len(path) > best:
            continue
        if (r, c) == target:
            paths.append(path)
            best = len(path)
            continue
        for ch, (dr, dc) in zip("^v<>", [(-1, 0), (1, 0), (0, -1), (0, 1)]):
            nr, nc = r + dr, c + dc
            if (nr, nc) not in layout.values():
                continue
            nlen = len(path) + 1
            if nlen > (visited.get((nr, nc), 1 << 30)):
                continue
            visited[(nr, nc)] = nlen
            queue.append(((nr, nc), path + ch))
    return paths


@lru_cache(maxsize=None)
def move_cost(layout_id: str, depth: int, src: Key, dst: Key) -> int:
    """
    Compute minimum cost to move the arm from `src` to `dst` through a chain of keypads.

    Args:
        layout_id: Either `"num"` or `"dir"` to select keypad layout.
        depth: Remaining depth of remote keypads ahead.
        src: Source key.
        dst: Destination key.

    Returns:
        Minimum number of button presses required.
    """
    layout = NUMERIC_POS if layout_id == "num" else DIR_POS
    paths = canonical_paths(src, dst, layout)
    if depth == 0:
        return min(len(p) + 1 for p in paths)  # press A
    best = 1 << 60
    for path in paths:
        seq = path + "A"
        cost = sequence_cost("dir", depth - 1, seq)
        if cost < best:
            best = cost
    return best


@lru_cache(maxsize=None)
def sequence_cost(layout_id: str, depth: int, seq: str) -> int:
    """
    Sum button presses required to follow a sequence of key presses.

    Args:
        layout_id: Layout identifier.
        depth: Remaining remote depth.
        seq: Sequence of keys to press.

    Returns:
        Total cost of performing the sequence.
    """
    pos = "A"
    total = 0
    for ch in seq:
        total += move_cost(layout_id, depth, pos, ch)
        pos = ch
    return total


def code_cost(code: str, depth: int) -> int:
    """
    Compute your required key presses to type `code`.

    Args:
        code: Numeric door code.
        depth: Number of remote directional keypads before the numeric keypad.

    Returns:
        Minimum number of button presses on your keypad to issue `code`.
    """
    total = 0
    pos = "A"
    for ch in code:
        total += move_cost("num", depth, pos, ch)
        pos = ch
    return total


def solve_part_one(codes: list[str]) -> int:
    """
    Sum the complexities for the original chain of robots.

    Args:
        codes: Door codes parsed from input.

    Returns:
        Sum of complexities for depth 2.
    """
    depth = 2
    total = 0
    for code in codes:
        numeric = int(code.lstrip("0") or "0")
        total += code_cost(code, depth) * numeric
    return total


def solve_part_two(codes: list[str]) -> int:
    """
    Sum the complexities for the extended robot chain.

    Args:
        codes: Door codes parsed from input.

    Returns:
        Sum of complexities for depth 25.
    """
    depth = 25
    total = 0
    for code in codes:
        numeric = int(code.lstrip("0") or "0")
        total += code_cost(code, depth) * numeric
    return total

def _infer_year_day(path: Path) -> tuple[int | None, int | None]:
    """
    Infer (year, day) from a filename like 'solution_2015_day_01.py'.

    Returns (None, None) if it can't be parsed.
    """
    name = path.name  # e.g. 'solution_2015_day_01.py'

    # Strip extension
    if name.endswith(".py"):
        base = name[:-3]
    else:
        base = name

    parts = base.split("_")
    # Expected: ["solution", "2015", "day", "01"]
    if len(parts) != 4 or parts[0] != "solution" or parts[2] != "day":
        return None, None

    try:
        year = int(parts[1])
        day = int(parts[3])
    except ValueError:
        return None, None

    return year, day

def _infer_year_day(path: Path) -> tuple[int | None, int | None]:
    """Infer (year, day) from a filename like 'solution_2015_day_01.py'.

    Returns (None, None) if it can't be parsed.
    """
    name = path.name  # e.g. 'solution_2015_day_01.py'

    # Strip extension
    if name.endswith(".py"):
        base = name[:-3]
    else:
        base = name

    parts = base.split("_")
    # Expected: ["solution", "2015", "day", "01"]
    if len(parts) != 4 or parts[0] != "solution" or parts[2] != "day":
        return None, None

    try:
        year = int(parts[1])
        day = int(parts[3])
    except ValueError:
        return None, None

    return year, day


def _find_project_root(start: Path) -> Path:
    """Find the project root directory.

    Walk upwards until we find a directory containing 'pyproject.toml',
    and treat that as the project root.

    Falls back to 'start' if nothing is found.
    """
    for parent in [start] + list(start.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return start


def _default_paths(this_file: Path) -> tuple[str, Path, Path | None, Path | None]:
    """Compute default paths for this solution file.

    Returns description, default input path, answer path, and article path
    based on the solution filename and repository layout.

    Layout:

      __inputs__/year_YYYY/input_YYYY_day_DD.txt
      __answers__/year_YYYY/answer_YYYY_day_DD.txt
      __articles__/year_YYYY/article_YYYY_day_DD.md
    """
    year, day = _infer_year_day(this_file)
    root = _find_project_root(this_file)

    if year is None or day is None:
        desc = "Solve Advent of Code puzzle."
        default_input = this_file.with_name("input.txt")
        return desc, default_input, None, None

    desc = f"Solve Advent of Code {year} Day {day:02d}."

    # __inputs__/year_YYYY/input_YYYY_day_DD.txt
    default_input = (
        root
        / "__inputs__"
        / f"year_{year}"
        / f"input_{year}_day_{day:02d}.txt"
    )

    # __answers__/year_YYYY/answer_YYYY_day_DD.txt
    answer_path = (
        root
        / "__answers__"
        / f"year_{year}"
        / f"answer_{year}_day_{day:02d}.txt"
    )

    # __articles__/year_YYYY/article_YYYY_day_DD.md
    article_path = (
        root
        / "__articles__"
        / f"year_{year}"
        / f"article_{year}_day_{day:02d}.md"
    )

    return desc, default_input, answer_path, article_path


def _cli() -> None:
    """Parse CLI arguments and run the selected parts."""
    this_file = Path(__file__).resolve()
    desc, default_input, answer_path, article_path = _default_paths(this_file)

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=(
            "Path to input file "
            f"(defaults to {default_input.relative_to(_find_project_root(this_file))!s})."
        ),
    )
    parser.add_argument(
        "--part",
        type=int,
        choices=(1, 2),
        help="Run only a single part (1 or 2). Defaults to running both.",
    )
    parser.add_argument(
        "--check-answer",
        action="store_true",
        help="If set, compare outputs against __answers__ (if available).",
    )
    args = parser.parse_args()

    raw = args.input.read_text(encoding="utf-8")
    data = parse_input(raw)

    part_one_result: int | str | None = None
    part_two_result: int | str | None = None

    if args.part in (None, 1):
        part_one_result = solve_part_one(data)
        print(f"part one: {part_one_result}")

    if args.part in (None, 2):
        part_two_result = solve_part_two(data)
        print(f"part two: {part_two_result}")

    # Optional: answer checking against __answers__
    if args.check_answer and answer_path is not None and answer_path.exists():
        answers_raw = answer_path.read_text(encoding="utf-8").splitlines()
        expected_part_one = answers_raw[0].strip() if len(answers_raw) >= 1 else None
        expected_part_two = answers_raw[1].strip() if len(answers_raw) >= 2 else None

        if part_one_result is not None and expected_part_one is not None:
            status = "OK" if str(part_one_result) == expected_part_one else "WRONG"
            print(f"[check] part one: {status} (expected {expected_part_one})")

        if part_two_result is not None and expected_part_two is not None:
            status = "OK" if str(part_two_result) == expected_part_two else "WRONG"
            print(f"[check] part two: {status} (expected {expected_part_two})")


def main() -> int:
    """Entry point for module execution."""
    _cli()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
