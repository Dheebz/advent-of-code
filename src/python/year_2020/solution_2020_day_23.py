"""Crab Cups -- Advent of Code 2020 Day 23."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List


def parse_input(raw: str) -> List[int]:
    """Return starting cup labels."""
    return [int(ch) for ch in raw.strip()]


def play(cups: List[int], moves: int, total_cups: int | None = None) -> Dict[int, int]:
    """
    Simulate the cup game for the given number of moves.

    Args:
        cups: Initial cup ordering.
        moves: Number of moves to perform.
        total_cups: Total number of cups (if extending beyond initial list).

    Returns:
        Mapping where each cup points to the next cup.
    """
    if total_cups is None:
        total_cups = len(cups)
    next_cup: Dict[int, int] = {}
    for current, nxt in zip(cups, cups[1:]):
        next_cup[current] = nxt
    if total_cups > len(cups):
        next_cup[cups[-1]] = max(cups) + 1
        for value in range(max(cups) + 1, total_cups):
            next_cup[value] = value + 1
        next_cup[total_cups] = cups[0]
    else:
        next_cup[cups[-1]] = cups[0]

    current = cups[0]
    max_label = total_cups
    for _ in range(moves):
        pick1 = next_cup[current]
        pick2 = next_cup[pick1]
        pick3 = next_cup[pick2]
        picked = {pick1, pick2, pick3}
        next_cup[current] = next_cup[pick3]

        dest = current - 1 or max_label
        while dest in picked:
            dest = dest - 1 or max_label

        next_cup[pick3] = next_cup[dest]
        next_cup[dest] = pick1
        current = next_cup[current]
    return next_cup


def solve_part_one(cups: List[int]) -> int:
    """
    Return labels on cups after cup 1 following 100 moves.

    Args:
        cups: Initial cup ordering.

    Returns:
        Concatenated labels encountered clockwise from cup 1.
    """
    next_cup = play(cups, 100)
    result = []
    current = next_cup[1]
    while current != 1:
        result.append(str(current))
        current = next_cup[current]
    return int("".join(result))


def solve_part_two(cups: List[int]) -> int:
    """
    Return the product of the two cups immediately clockwise of cup 1.

    Args:
        cups: Initial cup ordering.

    Returns:
        Product of the two labels after cup 1 once the extended game completes.
    """
    next_cup = play(cups, 10_000_000, total_cups=1_000_000)
    first = next_cup[1]
    second = next_cup[first]
    return first * second

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
