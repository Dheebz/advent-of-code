"""Reservoir Research -- Advent of Code 2018 Day 17."""

from __future__ import annotations

import argparse
import re
from collections import deque
from pathlib import Path
from typing import Set, Tuple

Point = Tuple[int, int]


def parse_input(raw: str) -> Set[Point]:
    """Return set of clay coordinates."""
    clay: Set[Point] = set()
    for line in raw.strip().splitlines():
        nums = [int(x) for x in re.findall(r"\d+", line)]
        if line.startswith("x"):
            x = nums[0]
            y1, y2 = nums[1], nums[2]
            for y in range(y1, y2 + 1):
                clay.add((x, y))
        else:
            y = nums[0]
            x1, x2 = nums[1], nums[2]
            for x in range(x1, x2 + 1):
                clay.add((x, y))
    return clay


def flow(clay: Set[Point]) -> Tuple[Set[Point], Set[Point]]:
    """Simulate water flow; return flowing and settled tiles."""
    spring = (500, 0)
    max_y = max(y for _, y in clay)
    flowing: Set[Point] = set()
    settled: Set[Point] = set()
    stack = deque([spring])

    def below(p: Point) -> Point:
        return (p[0], p[1] + 1)

    def spread(p: Point) -> Tuple[bool, Set[Point]]:
        x, y = p
        row: Set[Point] = set()
        stable = True
        for direction in (-1, 1):
            nx = x
            while True:
                nx += direction
                pos = (nx, y)
                below_pos = (nx, y + 1)
                if pos in clay:
                    break
                row.add(pos)
                if below_pos not in clay and below_pos not in settled:
                    stable = False
                    stack.append(pos)
                    break
        return stable, row

    while stack:
        x, y = stack.pop()
        while y <= max_y and (x, y) not in clay and (x, y) not in settled:
            flowing.add((x, y))
            if (x, y + 1) not in clay and (x, y + 1) not in settled:
                y += 1
                continue
            stable, row = spread((x, y))
            if stable:
                settled.update(row | {(x, y)})
                flowing -= row | {(x, y)}
                y -= 1
            else:
                flowing.update(row)
                break
    return flowing, settled


def solve_part_one(clay: Set[Point]) -> int:
    """Tiles water can reach."""
    flowing, settled = flow(clay)
    min_y = min(y for _, y in clay)
    return sum(1 for _, y in flowing | settled if y >= min_y)


def solve_part_two(clay: Set[Point]) -> int:
    """Tiles with standing water."""
    _, settled = flow(clay)
    min_y = min(y for _, y in clay)
    return sum(1 for _, y in settled if y >= min_y)

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
