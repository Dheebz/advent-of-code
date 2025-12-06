"""Many-Worlds Interpretation -- Advent of Code 2019 Day 18."""

from __future__ import annotations

import argparse
from collections import deque
from heapq import heappop, heappush
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Point = Tuple[int, int]
Edge = Tuple[str, int, int]  # target key, distance, required key mask


def parse_input(raw: str) -> List[List[str]]:
    """Parse the maze into a grid of characters.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        List[List[str]]: 2D grid of characters.
    """
    return [list(line.strip()) for line in raw.strip().splitlines()]


def neighbors(point: Point) -> Iterable[Point]:
    """Yield orthogonal neighbors for a point.

    Args:
        point (Point): Current coordinate.

    Yields:
        Iterable[Point]: Adjacent coordinates.
    """
    x, y = point
    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1


def find_nodes(grid: List[List[str]]) -> Tuple[Dict[str, Point], List[Point]]:
    """Locate keys and starting positions.

    Args:
        grid (List[List[str]]): Maze grid.

    Returns:
        Tuple[Dict[str, Point], List[Point]]: Mapping of key label to position and list of starts.
    """
    keys: Dict[str, Point] = {}
    starts: List[Point] = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "@":
                starts.append((x, y))
            elif ch.islower():
                keys[ch] = (x, y)
    return keys, starts


def bfs_edges(grid: List[List[str]], start: Point) -> List[Edge]:
    """Find reachable keys and required doors from a start.

    Args:
        grid (List[List[str]]): Maze grid.
        start (Point): Starting coordinate.

    Returns:
        List[Edge]: Reachable keys with distance and required key mask.
    """
    queue = deque([(start, 0, 0)])
    seen = {start}
    edges: List[Edge] = []
    while queue:
        (x, y), dist, req = queue.popleft()
        for nx, ny in neighbors((x, y)):
            if not (0 <= ny < len(grid) and 0 <= nx < len(grid[0])):
                continue
            if (nx, ny) in seen or grid[ny][nx] == "#":
                continue
            cell = grid[ny][nx]
            seen.add((nx, ny))
            new_req = req
            if cell.isupper():
                new_req |= 1 << (ord(cell.lower()) - ord("a"))
            if cell.islower():
                edges.append((cell, dist + 1, new_req))
            queue.append(((nx, ny), dist + 1, new_req))
    return edges


def build_graph(
    grid: List[List[str]], start_labels: List[str]
) -> Tuple[Dict[str, List[Edge]], int, List[str]]:
    """Build condensed graph between starts and keys.

    Args:
        grid (List[List[str]]): Maze grid.
        start_labels (List[str]): Labels to assign to starting positions.

    Returns:
        Tuple[Dict[str, List[Edge]], int, List[str]]: Graph adjacency,
            mask of all keys, start labels.
    """
    keys, starts = find_nodes(grid)
    nodes: Dict[str, Point] = {label: pos for label, pos in zip(start_labels, starts)}
    nodes.update(keys)
    graph: Dict[str, List[Edge]] = {}
    for label, pos in nodes.items():
        graph[label] = bfs_edges(grid, pos)
    all_keys_mask = 0
    for key in keys:
        all_keys_mask |= 1 << (ord(key) - ord("a"))
    return graph, all_keys_mask, start_labels


def shortest_collection(
    graph: Dict[str, List[Edge]], all_keys_mask: int, start_labels: List[str]
) -> int:
    """Find minimal steps to collect all keys.

    Args:
        graph (Dict[str, List[Edge]]): Condensed graph of reachable keys.
        all_keys_mask (int): Bitmask of all keys.
        start_labels (List[str]): Labels representing current positions.

    Returns:
        int: Minimal number of steps to collect every key.
    """
    start_positions = tuple(start_labels)
    heap = [(0, start_positions, 0)]
    seen = {(start_positions, 0): 0}

    while heap:
        dist, positions, collected = heappop(heap)
        if collected == all_keys_mask:
            return dist
        if seen.get((positions, collected), float("inf")) < dist:
            continue
        for i, node in enumerate(positions):
            for target, step_cost, required in graph[node]:
                key_bit = 1 << (ord(target) - ord("a"))
                if collected & key_bit:
                    continue
                if required & ~collected:
                    continue
                new_positions = list(positions)
                new_positions[i] = target
                new_mask = collected | key_bit
                new_state = (tuple(new_positions), new_mask)
                new_dist = dist + step_cost
                if new_dist < seen.get(new_state, float("inf")):
                    seen[new_state] = new_dist
                    heappush(heap, (new_dist, new_state[0], new_mask))
    raise ValueError("no path found")


def solve_part_one(grid: List[List[str]]) -> int:
    """Return minimal steps to collect all keys for a single robot."""
    graph, all_keys_mask, start_labels = build_graph(grid, ["@"])
    return shortest_collection(graph, all_keys_mask, start_labels)


def transform_for_part_two(grid: List[List[str]]) -> Tuple[List[List[str]], List[str]]:
    """Split the maze into four quadrants for part two.

    Args:
        grid (List[List[str]]): Original maze grid.

    Returns:
        Tuple[List[List[str]], List[str]]: Modified grid and start labels.
    """
    grid = [row.copy() for row in grid]
    keys, starts = find_nodes(grid)
    sx, sy = starts[0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            grid[sy + dy][sx + dx] = "#"
    new_starts = [
        (sx - 1, sy - 1),
        (sx + 1, sy - 1),
        (sx - 1, sy + 1),
        (sx + 1, sy + 1),
    ]
    labels = ["0", "1", "2", "3"]
    for label, (x, y) in zip(labels, new_starts):
        grid[y][x] = "@"
    return grid, labels


def solve_part_two(grid: List[List[str]]) -> int:
    """Return minimal steps to collect all keys with four robots."""
    transformed, labels = transform_for_part_two(grid)
    graph, all_keys_mask, start_labels = build_graph(transformed, labels)
    return shortest_collection(graph, all_keys_mask, start_labels)

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
