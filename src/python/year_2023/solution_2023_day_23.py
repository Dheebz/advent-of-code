"""A Long Walk -- Advent of Code 2023 Day 23."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple

Grid = List[str]
Point = Tuple[int, int]
Graph = Dict[Point, List[Tuple[Point, int]]]

DIRECTIONS = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}


def parse_input(raw: str) -> Grid:
    """Return trail map."""
    return raw.strip().splitlines()


def neighbors(grid: Grid, r: int, c: int, allow_slopes: bool) -> List[Point]:
    """Return reachable neighbors from a tile."""
    rows, cols = len(grid), len(grid[0])
    ch = grid[r][c]
    if allow_slopes:
        moves: List[Tuple[int, int]] = list(DIRECTIONS.values())
    else:
        moves = [DIRECTIONS[ch]] if ch in DIRECTIONS else list(DIRECTIONS.values())
    result = []
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        if grid[nr][nc] == "#":
            continue
        result.append((nr, nc))
    return result


def build_graph(grid: Grid, allow_slopes: bool) -> Tuple[Graph, Point, Point]:
    """Compress paths between junctions into graph edges."""
    rows, cols = len(grid), len(grid[0])
    start = (0, grid[0].index("."))
    end = (rows - 1, grid[-1].index("."))
    nodes: Set[Point] = {start, end}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                continue
            nbrs = neighbors(grid, r, c, allow_slopes)
            if len(nbrs) != 2 or (not allow_slopes and grid[r][c] in DIRECTIONS):
                nodes.add((r, c))

    graph: Graph = {node: [] for node in nodes}
    for node in nodes:
        for nr, nc in neighbors(grid, node[0], node[1], allow_slopes):
            length = 1
            cur = (nr, nc)
            prev = node
            while cur not in nodes:
                next_steps = [p for p in neighbors(grid, cur[0], cur[1], allow_slopes) if p != prev]
                if not next_steps:
                    break
                prev, cur = cur, next_steps[0]
                length += 1
            if cur in nodes:
                graph[node].append((cur, length))
    return graph, start, end


def longest_path(graph: Graph, start: Point, end: Point) -> int:
    """DFS for longest path without revisiting nodes."""
    best = 0
    stack = [(start, 0, {start})]
    while stack:
        node, dist, seen = stack.pop()
        if node == end:
            best = max(best, dist)
            continue
        for nxt, length in graph[node]:
            if nxt not in seen:
                stack.append((nxt, dist + length, seen | {nxt}))
    return best


def solve_part_one(grid: Grid) -> int:
    """Longest path obeying slopes."""
    graph, start, end = build_graph(grid, allow_slopes=False)
    return longest_path(graph, start, end)


def solve_part_two(grid: Grid) -> int:
    """Longest path treating slopes as normal trails."""
    graph, start, end = build_graph(grid, allow_slopes=True)
    return longest_path(graph, start, end)

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
