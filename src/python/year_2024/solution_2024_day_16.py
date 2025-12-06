"""Advent of Code 2024 Day 16: Reindeer Maze."""

from __future__ import annotations

import argparse
import heapq
from pathlib import Path
from typing import Dict, Tuple

Grid = list[str]
State = Tuple[int, int, int]  # row, col, dir

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # E, S, W, N
TURN_COST = 1000
STEP_COST = 1


def parse_input(raw: str) -> tuple[Grid, tuple[int, int], tuple[int, int]]:
    """
    Extract the grid, start, and end positions.

    Args:
        raw: Puzzle input with the maze diagram.

    Returns:
        Tuple containing the grid (list of strings), start coordinates, and end coordinates.
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


def dijkstra(grid: Grid, starts: list[State]) -> Dict[State, int]:
    """
    Run Dijkstra's algorithm over the grid with turning costs.

    Args:
        grid: Maze layout with walls marked as '#'.
        starts: Initial states to seed the search (row, col, direction).

    Returns:
        Mapping from state to minimum traveled cost.
    """
    rows, cols = len(grid), len(grid[0])
    dist: Dict[State, int] = {}
    pq: list[tuple[int, State]] = []
    for s in starts:
        dist[s] = 0
        heapq.heappush(pq, (0, s))

    while pq:
        cost, state = heapq.heappop(pq)
        if cost != dist[state]:
            continue
        r, c, d = state

        # move forward
        dr, dc = DIRECTIONS[d]
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            nstate = (nr, nc, d)
            ncost = cost + STEP_COST
            if ncost < dist.get(nstate, float("inf")):
                dist[nstate] = ncost
                heapq.heappush(pq, (ncost, nstate))

        # turn left/right
        for turn in (-1, 1):
            nd = (d + turn) % 4
            nstate = (r, c, nd)
            ncost = cost + TURN_COST
            if ncost < dist.get(nstate, float("inf")):
                dist[nstate] = ncost
                heapq.heappush(pq, (ncost, nstate))

    return dist


def solve(grid: Grid, start: tuple[int, int], end: tuple[int, int]) -> tuple[int, int]:
    """
    Find the shortest path and count tiles that lie on some optimal path.

    Args:
        grid: Maze layout with walls.
        start: Starting coordinates.
        end: Goal coordinates.

    Returns:
        Tuple of (minimum cost, number of tiles reachable with that cost).
    """
    start_state = (start[0], start[1], 0)  # facing east
    dist_from_start = dijkstra(grid, [start_state])

    best_score = min(dist for (r, c, _), dist in dist_from_start.items() if (r, c) == end)

    # distances to end (start from end with all directions)
    end_states = [(end[0], end[1], d) for d in range(4)]
    dist_to_end = dijkstra(grid, end_states)

    best_tiles: set[tuple[int, int]] = set()
    for (r, c, d), d_start in dist_from_start.items():
        total = d_start + dist_to_end.get((r, c, d), float("inf"))
        if total == best_score:
            best_tiles.add((r, c))
    return best_score, len(best_tiles)


def solve_part_one(data: tuple[Grid, tuple[int, int], tuple[int, int]]) -> int:
    """
    Compute the minimum rectangular path cost.

    Args:
        data: Parsed grid and start/end coordinates.

    Returns:
        Minimum cost from start to end respecting rotation penalties.
    """
    grid, start, end = data
    result, _ = solve(grid, start, end)
    return result


def solve_part_two(data: tuple[Grid, tuple[int, int], tuple[int, int]]) -> int:
    """
    Count how many tiles exist on some optimal path.

    Args:
        data: Parsed grid and start/end coordinates.

    Returns:
        Number of grid tiles that can lie on an optimal cost path.
    """
    grid, start, end = data
    _, tiles = solve(grid, start, end)
    return tiles

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
