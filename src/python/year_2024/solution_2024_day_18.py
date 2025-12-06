"""Advent of Code 2024 Day 18: RAM Run."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Iterable

Point = tuple[int, int]

GRID_SIZE = 71  # coordinates 0..70


def parse_input(raw: str) -> list[Point]:
    """
    Parse the falling bytes into coordinate pairs.

    Args:
        raw: Input containing lines of ``X,Y`` coordinates.

    Returns:
        List of points in the order the bytes fall.
    """
    coords: list[Point] = []
    for line in raw.strip().splitlines():
        x_str, y_str = line.split(",")
        coords.append((int(x_str), int(y_str)))
    return coords


def neighbors(x: int, y: int) -> Iterable[Point]:
    """
    Yield in-bounds adjacent cells.

    Args:
        x: Current x coordinate.
        y: Current y coordinate.

    Yields:
        Neighboring coordinates within the grid.
    """
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            yield nx, ny


def shortest_path(blocked: set[Point]) -> int | None:
    """
    Find the shortest path from start to exit avoiding blocked cells.

    Args:
        blocked: Set of coordinates that are corrupted.

    Returns:
        Number of steps in the shortest path or `None` if blocked.
    """
    start = (0, 0)
    end = (GRID_SIZE - 1, GRID_SIZE - 1)
    if start in blocked or end in blocked:
        return None
    queue = deque([(start[0], start[1], 0)])
    seen = {start}
    while queue:
        x, y, dist = queue.popleft()
        if (x, y) == end:
            return dist
        for nx, ny in neighbors(x, y):
            if (nx, ny) not in blocked and (nx, ny) not in seen:
                seen.add((nx, ny))
                queue.append((nx, ny, dist + 1))
    return None


def solve_part_one(coords: list[Point]) -> int:
    """
    Determine the shortest path length after the first kilobyte lands.

    Args:
        coords: Falling byte coordinates in arrival order.

    Returns:
        Length of the shortest path or raises if none exists.
    """
    blocked = set(coords[:1024])
    path_len = shortest_path(blocked)
    if path_len is None:
        raise ValueError("No path after 1024 bytes")
    return path_len


def first_blocking_byte(coords: list[Point]) -> Point:
    """
    Binary search for the first byte that cuts off the path.

    Args:
        coords: Ordered byte arrivals.

    Returns:
        Coordinate of the byte that first prevents reaching the exit.
    """
    low, high = 0, len(coords)
    while low < high:
        mid = (low + high) // 2
        blocked = set(coords[: mid + 1])
        if shortest_path(blocked) is None:
            high = mid
        else:
            low = mid + 1
    return coords[low]


def solve_part_two(coords: list[Point]) -> str:
    """
    Determine when the exit becomes unreachable.

    Args:
        coords: Falling byte coordinates in order.

    Returns:
        Coordinates of the blocking byte formatted as ``x,y``.
    """
    x, y = first_blocking_byte(coords)
    return f"{x},{y}"

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
