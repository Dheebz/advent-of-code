"""Blizzard Basin -- Advent of Code 2022 Day 24."""

from __future__ import annotations

import argparse
from collections import deque
from math import lcm
from pathlib import Path
from typing import Deque, List, Set, Tuple

Point = Tuple[int, int]
Blizzard = Tuple[int, int, str]


def parse_input(raw: str) -> Tuple[List[str], List[Blizzard], Point, Point]:
    """
    Extract the map and blizzard start positions.

    Args:
        raw: Puzzle text containing the valley map and blizzard markers.

    Returns:
        Tuple containing the grid lines, list of blizzard tuples, start, and end points.
    """
    lines = raw.strip().splitlines()
    height = len(lines)
    blizzards: List[Blizzard] = []
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch in "<>^v":
                blizzards.append((x, y, ch))
    start = (lines[0].index("."), 0)
    end = (lines[-1].index("."), height - 1)
    return lines, blizzards, start, end


def blizzard_positions(blizzards: List[Blizzard], width: int, height: int, time: int) -> Set[Point]:
    """
    Compute which positions are blocked by blizzards at the given minute.

    Args:
        blizzards: List of initial blizzard states.
        width: Width of the map grid.
        height: Height of the map grid.
        time: Minute offset to evaluate.

    Returns:
        Set of coordinates currently occupied by blizzards.
    """
    positions = set()
    for x, y, d in blizzards:
        if d == ">":
            nx = 1 + ((x - 1 + time) % (width - 2))
            ny = y
        elif d == "<":
            nx = 1 + ((x - 1 - time) % (width - 2))
            ny = y
        elif d == "^":
            nx = x
            ny = 1 + ((y - 1 - time) % (height - 2))
        else:  # "v"
            nx = x
            ny = 1 + ((y - 1 + time) % (height - 2))
        positions.add((nx, ny))
    return positions


def traverse(
    blizzards: List[Blizzard],
    width: int,
    height: int,
    start: Point,
    goal: Point,
    start_time: int,
) -> int:
    """
    Find the earliest minute to reach the goal while avoiding blizzards.

    Args:
        blizzards: List of initial blizzard definitions.
        width: Width of the map grid.
        height: Height of the map grid.
        start: Starting coordinate to begin traversal.
        goal: Coordinate that needs to be reached.
        start_time: Minute offset from which traversal begins.

    Returns:
        Earliest minute at which the goal can be reached.
    """
    period = lcm(width - 2, height - 2)
    queue: Deque[Tuple[int, Point]] = deque([(start_time, start)])
    seen = {(start_time % period, start)}

    while queue:
        time, (x, y) = queue.popleft()
        next_time = time + 1
        blocked = blizzard_positions(blizzards, width, height, next_time)
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) == goal:
                return next_time
            if (nx, ny) == start or (1 <= nx < width - 1 and 1 <= ny < height - 1):
                if (nx, ny) not in blocked:
                    key = (next_time % period, (nx, ny))
                    if key not in seen:
                        seen.add(key)
                        queue.append((next_time, (nx, ny)))
    raise ValueError("Path not found")


def solve_part_one(parsed: Tuple[List[str], List[Blizzard], Point, Point]) -> int:
    """
    Determine how long it takes to reach the goal once.

    Args:
        parsed: Tuple returned by `parse_input`.

    Returns:
        Fewest minutes required to reach the goal from the start.
    """
    grid, blizzards, start, end = parsed
    return traverse(blizzards, len(grid[0]), len(grid), start, end, 0)


def solve_part_two(parsed: Tuple[List[str], List[Blizzard], Point, Point]) -> int:
    """
    Compute the total time for the complete round trip start->end->start->end.

    Args:
        parsed: Tuple returned by `parse_input`.

    Returns:
        Minutes needed to traverse there, back, and there again.
    """
    grid, blizzards, start, end = parsed
    first = traverse(blizzards, len(grid[0]), len(grid), start, end, 0)
    back = traverse(blizzards, len(grid[0]), len(grid), end, start, first)
    final = traverse(blizzards, len(grid[0]), len(grid), start, end, back)
    return final

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
