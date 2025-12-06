"""Mode Maze -- Advent of Code 2018 Day 22."""

from __future__ import annotations

import argparse
import heapq
from functools import lru_cache
from pathlib import Path
from typing import Tuple

Point = Tuple[int, int]


def parse_input(raw: str) -> Tuple[int, Point]:
    """Return cave depth and target coordinate."""
    lines = raw.strip().splitlines()
    depth = int(lines[0].split()[1])
    target_parts = lines[1].split()[1].split(",")
    target = (int(target_parts[0]), int(target_parts[1]))
    return depth, target


@lru_cache(maxsize=None)
def geologic_index(depth: int, target: Point, x: int, y: int) -> int:
    """Compute geologic index for a coordinate."""
    if (x, y) == (0, 0) or (x, y) == target:
        return 0
    if y == 0:
        return x * 16807
    if x == 0:
        return y * 48271
    return erosion_level(depth, target, x - 1, y) * erosion_level(depth, target, x, y - 1)


@lru_cache(maxsize=None)
def erosion_level(depth: int, target: Point, x: int, y: int) -> int:
    """Compute erosion level."""
    return (geologic_index(depth, target, x, y) + depth) % 20183


def region_type(depth: int, target: Point, x: int, y: int) -> int:
    """Return region type (0 rocky, 1 wet, 2 narrow)."""
    return erosion_level(depth, target, x, y) % 3


def solve_part_one(parsed: Tuple[int, Point]) -> int:
    """Risk level for rectangle from 0,0 to target."""
    depth, target = parsed
    tx, ty = target
    return sum(region_type(depth, target, x, y) for x in range(tx + 1) for y in range(ty + 1))


TOOLS = {
    0: {"torch", "climbing"},
    1: {"climbing", "neither"},
    2: {"torch", "neither"},
}


def solve_part_two(parsed: Tuple[int, Point]) -> int:
    """Shortest time to reach target with torch using A* / Dijkstra."""
    depth, target = parsed
    start = (0, 0, "torch")
    heap = [(0, start)]
    dist = {start: 0}
    tx, ty = target
    limit_x, limit_y = tx + 50, ty + 50

    while heap:
        time, (x, y, tool) = heapq.heappop(heap)
        if (x, y) == target and tool == "torch":
            return time
        if time != dist[(x, y, tool)]:
            continue
        # switch tools
        for new_tool in TOOLS[region_type(depth, target, x, y)]:
            if new_tool != tool:
                state = (x, y, new_tool)
                new_time = time + 7
                if new_time < dist.get(state, 1e18):
                    dist[state] = new_time
                    heapq.heappush(heap, (new_time, state))
        # move
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx > limit_x or ny > limit_y:
                continue
            if tool in TOOLS[region_type(depth, target, nx, ny)]:
                state = (nx, ny, tool)
                new_time = time + 1
                if new_time < dist.get(state, 1e18):
                    dist[state] = new_time
                    heapq.heappush(heap, (new_time, state))
    raise ValueError("Path not found")

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
