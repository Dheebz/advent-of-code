"""Chiton -- Advent of Code 2021 Day 15."""

from __future__ import annotations

import argparse
import heapq
from pathlib import Path
from typing import List, Tuple

Grid = List[List[int]]


def parse_input(raw: str) -> Grid:
    """
    Parse the risk level grid from the input.

    Args:
        raw: Multiline text of single-digit risk levels.

    Returns:
        Grid of integer risks.
    """
    return [[int(ch) for ch in line.strip()] for line in raw.strip().splitlines() if line.strip()]


def neighbors(r: int, c: int, height: int, width: int) -> List[Tuple[int, int]]:
    """
    List adjacent positions inside the grid.

    Args:
        r: Current row.
        c: Current column.
        height: Number of rows.
        width: Number of columns.

    Returns:
        Coordinates of neighbors (up/down/left/right).
    """
    adj = []
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < height and 0 <= nc < width:
            adj.append((nr, nc))
    return adj


def min_risk(grid: Grid) -> int:
    """
    Compute the minimum total risk path from top-left to bottom-right.

    Args:
        grid: Risk level grid.

    Returns:
        Minimum cumulative risk to reach the target.
    """
    height = len(grid)
    width = len(grid[0])
    target = (height - 1, width - 1)
    pq = [(0, 0, 0)]  # risk, row, col
    seen = {}
    while pq:
        risk, r, c = heapq.heappop(pq)
        if (r, c) == target:
            return risk
        if (r, c) in seen and seen[(r, c)] <= risk:
            continue
        seen[(r, c)] = risk
        for nr, nc in neighbors(r, c, height, width):
            next_risk = risk + grid[nr][nc]
            if seen.get((nr, nc), float("inf")) > next_risk:
                heapq.heappush(pq, (next_risk, nr, nc))
    raise ValueError("no path found")


def expand_grid(grid: Grid) -> Grid:
    """
    Expand the grid to the full five-times tiled version for Part Two.

    Args:
        grid: Original risk grid.

    Returns:
        Expanded grid where each tile increases the risk values.
    """
    height = len(grid)
    width = len(grid[0])
    full: Grid = [[0 for _ in range(width * 5)] for _ in range(height * 5)]
    for tile_r in range(5):
        for tile_c in range(5):
            increment = tile_r + tile_c
            for r in range(height):
                for c in range(width):
                    value = grid[r][c] + increment
                    while value > 9:
                        value -= 9
                    full[tile_r * height + r][tile_c * width + c] = value
    return full


def solve_part_one(grid: Grid) -> int:
    """
    Calculate minimum risk on the starting grid.

    Args:
        grid: Original risk grid.

    Returns:
        Minimum risk path total.
    """
    return min_risk(grid)


def solve_part_two(grid: Grid) -> int:
    """
    Calculate minimum risk on the expanded grid.

    Args:
        grid: Original risk grid.

    Returns:
        Minimum risk path total on the expanded grid.
    """
    expanded = expand_grid(grid)
    return min_risk(expanded)

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
