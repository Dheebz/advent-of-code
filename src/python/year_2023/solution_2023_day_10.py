"""Pipe Maze -- Advent of Code 2023 Day 10."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

Grid = List[str]
Point = Tuple[int, int]

CONNECTIONS: Dict[str, List[Point]] = {
    "|": [(-1, 0), (1, 0)],
    "-": [(0, -1), (0, 1)],
    "L": [(-1, 0), (0, 1)],
    "J": [(-1, 0), (0, -1)],
    "7": [(1, 0), (0, -1)],
    "F": [(1, 0), (0, 1)],
}


def parse_input(raw: str) -> Grid:
    """Return map grid."""
    return raw.strip().splitlines()


def find_start(grid: Grid) -> Point:
    """Locate S."""
    for r, row in enumerate(grid):
        c = row.find("S")
        if c != -1:
            return (r, c)
    raise ValueError("Start not found")


def valid_neighbors(point: Point, grid: Grid) -> List[Point]:
    """Neighbors connected to start."""
    r, c = point
    rows, cols = len(grid), len(grid[0])
    neighbors: List[Point] = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        ch = grid[nr][nc]
        if ch in CONNECTIONS and (-dr, -dc) in CONNECTIONS[ch]:
            neighbors.append((nr, nc))
    return neighbors


def determine_start_char(neighbors: List[Point], start: Point) -> str:
    """Infer the pipe shape for the start tile."""
    dirs = []
    for nr, nc in neighbors:
        dr = nr - start[0]
        dc = nc - start[1]
        dirs.append((dr, dc))
    dirs_set = set(dirs)
    for ch, conns in CONNECTIONS.items():
        if set(conns) == dirs_set:
            return ch
    raise ValueError("No matching start shape")


def trace_loop(grid: Grid) -> Tuple[Set[Point], str]:
    """Return set of loop points and the inferred start char."""
    start = find_start(grid)
    neighbors = valid_neighbors(start, grid)
    start_char = determine_start_char(neighbors, start)

    loop: Set[Point] = {start}
    prev = start
    current = neighbors[0]
    while current != start:
        loop.add(current)
        r, c = current
        ch = grid[r][c]
        if ch == "S":
            ch = start_char
        for dr, dc in CONNECTIONS[ch]:
            nr, nc = r + dr, c + dc
            if (nr, nc) != prev and (grid[nr][nc] in CONNECTIONS or grid[nr][nc] == "S"):
                prev, current = current, (nr, nc)
                break
    return loop, start_char


def solve_part_one(grid: Grid) -> int:
    """Farthest point distance along loop."""
    loop, _ = trace_loop(grid)
    return len(loop) // 2


def solve_part_two(grid: Grid) -> int:
    """Count enclosed tiles inside the loop."""
    loop, start_char = trace_loop(grid)
    rows, cols = len(grid), len(grid[0])

    # Build scaled grid marking pipes as walls.
    height = rows * 2 + 1
    width = cols * 2 + 1
    walls = [[False] * width for _ in range(height)]
    for r, c in loop:
        ch = grid[r][c]
        if ch == "S":
            ch = start_char
        cy, cx = 2 * r + 1, 2 * c + 1
        walls[cy][cx] = True
        for dr, dc in CONNECTIONS[ch]:
            walls[cy + dr][cx + dc] = True

    # Flood fill outside space.
    visited = [[False] * width for _ in range(height)]
    queue = deque([(0, 0)])
    visited[0][0] = True
    while queue:
        y, x = queue.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and not walls[ny][nx] and not visited[ny][nx]:
                visited[ny][nx] = True
                queue.append((ny, nx))

    inside = 0
    for r in range(rows):
        for c in range(cols):
            cy, cx = 2 * r + 1, 2 * c + 1
            if (r, c) not in loop and not visited[cy][cx]:
                inside += 1
    return inside

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
