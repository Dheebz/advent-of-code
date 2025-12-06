"""Mine Cart Madness -- Advent of Code 2018 Day 13."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Set, Tuple

Cart = Tuple[int, int, str, int]  # x, y, direction, turn_state


def parse_input(raw: str) -> Tuple[List[str], List[Cart]]:
    """Return track grid and initial carts."""
    grid = [list(line.rstrip("\n")) for line in raw.splitlines()]
    carts: List[Cart] = []
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char in "<>^v":
                carts.append((x, y, char, 0))
                grid[y][x] = "-" if char in "<>" else "|"
    return ["".join(r) for r in grid], carts


def step(grid: List[str], carts: List[Cart]) -> Tuple[List[Cart], List[Tuple[int, int]]]:
    """Advance the cart simulation one tick."""
    carts = sorted(carts, key=lambda c: (c[1], c[0]))
    positions = {(x, y): idx for idx, (x, y, _, _) in enumerate(carts)}
    crashed: Set[int] = set()
    crash_positions: List[Tuple[int, int]] = []
    for idx, (x, y, direction, turn_state) in enumerate(carts):
        if idx in crashed:
            continue
        positions.pop((x, y), None)
        if direction == "^":
            y -= 1
        elif direction == "v":
            y += 1
        elif direction == "<":
            x -= 1
        else:
            x += 1

        track = grid[y][x]
        if track == "/":
            direction = {"^": ">", "v": "<", "<": "v", ">": "^"}[direction]
        elif track == "\\":
            direction = {"^": "<", "v": ">", "<": "^", ">": "v"}[direction]
        elif track == "+":
            if turn_state % 3 == 0:
                direction = {"^": "<", "<": "v", "v": ">", ">": "^"}[direction]
            elif turn_state % 3 == 2:
                direction = {"^": ">", ">": "v", "v": "<", "<": "^"}[direction]
            turn_state = (turn_state + 1) % 3

        if (x, y) in positions:
            other = positions[(x, y)]
            crashed.update({idx, other})
            crash_positions.append((x, y))
            positions.pop((x, y), None)
        else:
            positions[(x, y)] = idx
        carts[idx] = (x, y, direction, turn_state)
    remaining = [cart for i, cart in enumerate(carts) if i not in crashed]
    return remaining, crash_positions


def solve_part_one(parsed: Tuple[List[str], List[Cart]]) -> str:
    """Location of the first crash."""
    grid, carts = parsed
    crashes: List[Tuple[int, int]] = []
    while not crashes:
        carts, crashes = step(grid, carts)
    x, y = crashes[0]
    return f"{x},{y}"


def solve_part_two(parsed: Tuple[List[str], List[Cart]]) -> str:
    """Location of the last remaining cart."""
    grid, carts = parsed
    while len(carts) > 1:
        carts, _ = step(grid, carts)
    x, y, _, _ = carts[0]
    return f"{x},{y}"

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
