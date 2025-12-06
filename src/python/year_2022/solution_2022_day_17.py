"""Pyroclastic Flow -- Advent of Code 2022 Day 17."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Set, Tuple

Point = Tuple[int, int]

SHAPES: List[List[Point]] = [
    [(0, 0), (1, 0), (2, 0), (3, 0)],  # horizontal line
    [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],  # plus
    [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],  # reverse L
    [(0, 0), (0, 1), (0, 2), (0, 3)],  # vertical line
    [(0, 0), (1, 0), (0, 1), (1, 1)],  # square
]


def parse_input(raw: str) -> str:
    """Return jet pattern."""
    return raw.strip()


def simulate(jets: str, total_rocks: int) -> int:
    """Simulate falling rocks with cycle detection."""
    occupied: Set[Point] = {(x, -1) for x in range(7)}
    jet_idx = 0
    max_y = -1
    added_height = 0
    seen = {}
    rock = 0

    while rock < total_rocks:
        shape = SHAPES[rock % len(SHAPES)]
        x = 2
        y = max_y + 4

        while True:
            # Jet push
            dx = 1 if jets[jet_idx] == ">" else -1
            jet_idx = (jet_idx + 1) % len(jets)
            if all(
                0 <= x + dx + px < 7 and (x + dx + px, y + py) not in occupied for px, py in shape
            ):
                x += dx
            # Fall
            if all((x + px, y + py - 1) not in occupied for px, py in shape):
                y -= 1
            else:
                for px, py in shape:
                    occupied.add((x + px, y + py))
                    max_y = max(max_y, y + py)
                break

        rock += 1

        # Keep only the upper portion of the tower to bound memory.
        cutoff = max_y - 50
        occupied = {pt for pt in occupied if pt[1] >= cutoff}

        # Profile of the surface
        top_profile = []
        for col in range(7):
            col_heights = [y for (cx, y) in occupied if cx == col]
            top = max(col_heights) if col_heights else -1
            top_profile.append(max_y - top)
        state = (rock % len(SHAPES), jet_idx, tuple(top_profile))
        if state in seen and rock < total_rocks:
            prev_rock, prev_height = seen[state]
            cycle_rocks = rock - prev_rock
            cycle_height = max_y - prev_height
            remaining = total_rocks - rock
            cycles = remaining // cycle_rocks
            if cycles:
                added_height += cycles * cycle_height
                rock += cycles * cycle_rocks
        else:
            seen[state] = (rock, max_y)

    return added_height + max_y + 1


def solve_part_one(jets: str) -> int:
    """Height after 2022 rocks."""
    return simulate(jets, 2022)


def solve_part_two(jets: str) -> int:
    """Height after 1 trillion rocks."""
    return simulate(jets, 1_000_000_000_000)

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
