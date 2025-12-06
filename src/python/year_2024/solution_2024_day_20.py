"""Advent of Code 2024 Day 20: Race Condition."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Dict

Point = tuple[int, int]


def parse_input(raw: str) -> tuple[list[str], Point, Point]:
    """
    Parse the racetrack map with start and end coordinates.

    Args:
        raw: Input maze string.

    Returns:
        Tuple of grid rows, start position, and end position.
    """
    grid = raw.strip().splitlines()
    start = end = (0, 0)
    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            if ch == "S":
                start = (r, c)
            elif ch == "E":
                end = (r, c)
    return grid, start, end


def bfs(grid: list[str], start: Point) -> Dict[Point, int]:
    """
    Perform BFS from `start` over the track cells.

    Args:
        grid: Maze grid with walls as '#'.
        start: Starting coordinate.

    Returns:
        Mapping from reachable track cells to their shortest distance from `start`.
    """
    rows, cols = len(grid), len(grid[0])
    dist: Dict[Point, int] = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                queue.append((nr, nc))
    return dist


def count_cheats(grid: list[str], start: Point, end: Point, max_cheat: int, threshold: int) -> int:
    """
    Count cheats that save at least `threshold` picoseconds using up to `max_cheat` cheating steps.

    Args:
        grid: Maze grid.
        start: Start coordinate.
        end: End coordinate.
        max_cheat: Maximum number of cheating moves allowed.
        threshold: Minimum picoseconds saved to count.

    Returns:
        Number of cheats meeting the threshold.
    """
    dist_start = bfs(grid, start)
    dist_end = bfs(grid, end)
    base = dist_start[end]
    rows, cols = len(grid), len(grid[0])
    result = 0
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in dist_start:
                continue
            for dr in range(-max_cheat, max_cheat + 1):
                rem = max_cheat - abs(dr)
                for dc in range(-rem, rem + 1):
                    if dr == 0 and dc == 0:
                        continue
                    cheat_len = abs(dr) + abs(dc)
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                    if (nr, nc) not in dist_end:
                        continue
                    total = dist_start[(r, c)] + cheat_len + dist_end[(nr, nc)]
                    saved = base - total
                    if saved >= threshold:
                        result += 1
    return result


def solve_part_one(data: tuple[list[str], Point, Point]) -> int:
    """
    Count cheats that save at least 100 picoseconds when cheating for 2 moves.

    Args:
        data: Parsed grid, start, end.

    Returns:
        Number of qualifying cheats.
    """
    grid, start, end = data
    return count_cheats(grid, start, end, max_cheat=2, threshold=100)


def solve_part_two(data: tuple[list[str], Point, Point]) -> int:
    """
    Count cheats that save at least 50 picoseconds with up to 20 cheating moves.

    Args:
        data: Parsed grid, start, end.

    Returns:
        Number of qualifying cheats.
    """
    grid, start, end = data
    return count_cheats(grid, start, end, max_cheat=20, threshold=50)

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
