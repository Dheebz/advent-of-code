"""Forklift accessibility checks for Advent of Code 2025 Day 4."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Iterator

Coord = tuple[int, int]
Rolls = set[Coord]
DELTAS: tuple[Coord, ...] = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def parse_input(raw: str) -> Rolls:
    """
    Convert the grid diagram into a set of roll coordinates.

    Args:
        raw: Diagram containing ``@`` for rolls and ``.`` for empty spaces.

    Returns:
        Set of (row, column) coordinates containing rolls.
    """
    lines = [line.rstrip("\n") for line in raw.strip().splitlines() if line]
    rolls: Rolls = set()

    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            if char == "@":
                rolls.add((r, c))

    return rolls


def adjacent_count(rolls: Rolls, pos: Coord) -> int:
    """
    Count adjacent rolls in the eight surrounding squares.

    Args:
        rolls: Set of coordinates that currently contain rolls.
        pos: Coordinate to count neighbors around.

    Returns:
        Number of neighboring rolls touching `pos`.
    """
    r, c = pos
    return sum((r + dr, c + dc) in rolls for dr, dc in DELTAS)


def solve_part_one(rolls: Rolls) -> int:
    """
    Count rolls accessible with fewer than four neighbors.

    Args:
        rolls: Set of coordinates that currently contain rolls.

    Returns:
        Number of rolls with fewer than four adjacent rolls.
    """
    return sum(1 for pos in rolls if adjacent_count(rolls, pos) < 4)


def iter_accessible_removals(rolls: Rolls, threshold: int = 4) -> Iterator[Coord]:
    """
    Yield rolls that become accessible as neighbors are removed.

    This performs a k-core peel: any roll with fewer than ``threshold`` neighbors
    can be removed, which may in turn expose more rolls.

    Args:
        rolls: Initial set of roll coordinates.
        threshold: Minimum number of neighbors before a roll is considered removed.

    Yields:
        Coordinates that become removable during the peel.
    """
    remaining = set(rolls)
    neighbor_counts = {pos: adjacent_count(remaining, pos) for pos in remaining}
    queue = deque(pos for pos, count in neighbor_counts.items() if count < threshold)

    while queue:
        pos = queue.popleft()
        if pos not in remaining:
            continue

        remaining.remove(pos)
        yield pos

        r, c = pos
        for dr, dc in DELTAS:
            neighbor = (r + dr, c + dc)
            if neighbor in remaining:
                neighbor_counts[neighbor] -= 1
                if neighbor_counts[neighbor] < threshold:
                    queue.append(neighbor)


def solve_part_two(rolls: Rolls) -> int:
    """
    Count rolls removable through iterative accessibility peels.

    Args:
        rolls: Set of coordinates that currently contain rolls.

    Returns:
        Number of rolls that are removed during the peel process.
    """
    return sum(1 for _ in iter_accessible_removals(rolls))

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
