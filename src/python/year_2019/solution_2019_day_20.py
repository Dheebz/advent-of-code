"""Donut Maze -- Advent of Code 2019 Day 20."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Dict, List, Tuple

Point = Tuple[int, int]


def parse_input(raw: str) -> List[List[str]]:
    """Parse the donut maze into a grid.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        List[List[str]]: Grid of characters.
    """
    return [list(line.rstrip("\n")) for line in raw.splitlines() if line]


def find_portals(
    grid: List[List[str]],
) -> Tuple[Dict[str, List[Point]], Dict[Point, str]]:
    """Locate portal labels and classify them as inner or outer.

    Args:
        grid (List[List[str]]): Maze grid.

    Returns:
        Tuple[Dict[str, List[Point]], Dict[Point, str]]: Portal positions by label and side map.
    """
    height = len(grid)
    width = len(grid[0])
    portals: Dict[str, List[Point]] = {}
    portal_side: Dict[Point, str] = {}
    visited = set()

    for y in range(height):
        for x in range(width):
            if not grid[y][x].isupper() or (x, y) in visited:
                continue
            for dx, dy in [(1, 0), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and grid[ny][nx].isupper():
                    label = grid[y][x] + grid[ny][nx]
                    visited.add((x, y))
                    visited.add((nx, ny))
                    # find portal entrance
                    bx, by = x - dx, y - dy
                    fx, fy = nx + dx, ny + dy
                    if 0 <= bx < width and 0 <= by < height and grid[by][bx] == ".":
                        pos = (bx, by)
                    else:
                        pos = (fx, fy)
                    portals.setdefault(label, []).append(pos)
                    # determine inner vs outer
                    if pos[0] <= 2 or pos[1] <= 2 or pos[0] >= width - 3 or pos[1] >= height - 3:
                        portal_side[pos] = "outer"
                    else:
                        portal_side[pos] = "inner"
    return portals, portal_side


def build_links(portals: Dict[str, List[Point]]) -> Dict[Point, Point]:
    """Create bidirectional links between paired portals.

    Args:
        portals (Dict[str, List[Point]]): Portal positions grouped by label.

    Returns:
        Dict[Point, Point]: Mapping from entrance to destination.
    """
    links: Dict[Point, Point] = {}
    for label, positions in portals.items():
        if len(positions) == 2:
            a, b = positions
            links[a] = b
            links[b] = a
    return links


def solve_part_one(grid: List[List[str]]) -> int:
    """Find shortest path from AA to ZZ without recursion."""
    portals, _ = find_portals(grid)
    links = build_links(portals)
    start = portals["AA"][0]
    end = portals["ZZ"][0]

    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        position, dist = queue.popleft()
        if position == end:
            return dist
        x, y = position
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if grid[ny][nx] == "." and (nx, ny) not in seen:
                seen.add((nx, ny))
                queue.append(((nx, ny), dist + 1))
        if position in links:
            dest = links[position]
            if dest not in seen:
                seen.add(dest)
                queue.append((dest, dist + 1))
    raise ValueError("no path found")


def solve_part_two(grid: List[List[str]]) -> int:
    """Find shortest path through recursive maze levels."""
    portals, portal_side = find_portals(grid)
    links = build_links(portals)
    start = portals["AA"][0]
    end = portals["ZZ"][0]

    queue = deque([(start, 0, 0)])  # position, depth, distance
    seen = {(start, 0)}
    while queue:
        position, level, dist = queue.popleft()
        if position == end and level == 0:
            return dist
        x, y = position
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if grid[ny][nx] == "." and ((nx, ny), level) not in seen:
                seen.add(((nx, ny), level))
                queue.append(((nx, ny), level, dist + 1))
        if position in links and position not in (start, end):
            side = portal_side[position]
            new_level = level + (1 if side == "inner" else -1)
            if new_level >= 0:
                dest = links[position]
                if (dest, new_level) not in seen:
                    seen.add((dest, new_level))
                    queue.append((dest, new_level, dist + 1))
    raise ValueError("no path found")

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
