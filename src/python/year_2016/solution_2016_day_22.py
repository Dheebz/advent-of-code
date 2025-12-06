"""Grid Computing -- Advent of Code 2016 Day 22."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Tuple

Node = Dict[str, int]
Point = Tuple[int, int]


def parse_input(raw: str) -> List[Node]:
    """Parse node information from the input."""
    nodes: List[Node] = []
    for line in raw.strip().splitlines():
        if not line.startswith("/dev"):
            continue
        parts = line.split()
        name = parts[0]
        size, used, avail = (int(part[:-1]) for part in parts[1:4])
        x_str, y_str = name.split("/")[-1].split("-")[1:]
        x, y = int(x_str[1:]), int(y_str[1:])
        nodes.append({"x": x, "y": y, "size": size, "used": used, "avail": avail})
    return nodes


def solve_part_one(nodes: List[Node]) -> int:
    """Count viable pairs of nodes."""
    count = 0
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i == j or a["used"] == 0:
                continue
            if a["used"] <= b["avail"]:
                count += 1
    return count


def bfs(start: Point, target: Point, blocked: set[Point], max_x: int, max_y: int) -> int:
    """Breadth-first search distance avoiding blocked cells.

    Args:
        start (Point): Starting coordinate.
        target (Point): Target coordinate.
        blocked (set[Point]): Impassable positions.
        max_x (int): Maximum x bound (inclusive).
        max_y (int): Maximum y bound (inclusive).

    Returns:
        int: Shortest distance in steps.
    """
    queue: Deque[Tuple[Point, int]] = deque([(start, 0)])
    seen = {start}
    while queue:
        (x, y), dist = queue.popleft()
        if (x, y) == target:
            return dist
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx <= max_x and 0 <= ny <= max_y):
                continue
            if (nx, ny) in blocked or (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            queue.append(((nx, ny), dist + 1))
    raise ValueError("No path found")


def solve_part_two(nodes: List[Node]) -> int:
    """Fewest steps to move the goal data to (0, 0)."""
    grid: Dict[Point, Node] = {(n["x"], n["y"]): n for n in nodes}
    max_x = max(n["x"] for n in nodes)
    max_y = max(n["y"] for n in nodes)
    goal = (max_x, 0)
    empty = next(pos for pos, node in grid.items() if node["used"] == 0)
    empty_size = grid[empty]["size"]

    blocked = {pos for pos, node in grid.items() if node["used"] > empty_size}
    blocked.add(goal)  # do not step on the goal data while positioning the hole

    target_adjacent = (goal[0] - 1, goal[1])
    distance = bfs(empty, target_adjacent, blocked, max_x, max_y)

    # One step to swap with the goal, then each left shift takes 5 moves.
    return distance + 1 + 5 * (goal[0] - 0 - 1)

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
