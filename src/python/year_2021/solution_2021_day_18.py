"""Snailfish -- Advent of Code 2021 Day 18."""

from __future__ import annotations

import argparse
import ast
import copy
from pathlib import Path
from typing import List, Tuple, Union

Snail = Union[int, List["Snail"]]


def parse_input(raw: str) -> List[Snail]:
    """
    Parse snailfish numbers from the input.

    Args:
        raw: Multiline text where each line is a snailfish number.

    Returns:
        List of parsed snailfish numbers.
    """
    return [ast.literal_eval(line) for line in raw.strip().splitlines() if line.strip()]


def add_to_leftmost(snail: Snail, value: int) -> Snail:
    """
    Add a value to the leftmost regular number in a snailfish number.

    Args:
        snail: Snailfish number to modify.
        value: Value to propagate to the leftmost element.

    Returns:
        Updated snailfish number.
    """
    if isinstance(snail, int):
        return snail + value
    return [add_to_leftmost(snail[0], value), snail[1]]


def add_to_rightmost(snail: Snail, value: int) -> Snail:
    """
    Add a value to the rightmost regular number in a snailfish number.

    Args:
        snail: Snailfish number to modify.
        value: Value to propagate to the rightmost element.

    Returns:
        Updated snailfish number.
    """
    if isinstance(snail, int):
        return snail + value
    return [snail[0], add_to_rightmost(snail[1], value)]


def explode(snail: Snail, depth: int = 0) -> Tuple[bool, Snail, int, int]:
    """
    Perform a single explode operation if possible.

    Args:
        snail: Snailfish number to inspect.
        depth: Current depth in the nesting.

    Returns:
        Tuple indicating (changed, new_snail, add_left, add_right).
    """
    if isinstance(snail, int):
        return False, snail, 0, 0
    left, right = snail
    if depth >= 4 and isinstance(left, int) and isinstance(right, int):
        return True, 0, left, right

    changed, new_left, add_left, add_right = explode(left, depth + 1)
    if changed:
        new_right = add_to_leftmost(right, add_right)
        return True, [new_left, new_right], add_left, 0

    changed, new_right, add_left, add_right = explode(right, depth + 1)
    if changed:
        new_left = add_to_rightmost(left, add_left)
        return True, [new_left, new_right], 0, add_right

    return False, snail, 0, 0


def split(snail: Snail) -> Tuple[bool, Snail]:
    """
    Split the snailfish number if any regular number is >= 10.

    Args:
        snail: Snailfish number to process.

    Returns:
        Tuple indicating (changed, new_snail).
    """
    if isinstance(snail, int):
        if snail >= 10:
            left = snail // 2
            right = snail - left
            return True, [left, right]
        return False, snail
    left, right = snail
    changed, new_left = split(left)
    if changed:
        return True, [new_left, right]
    changed, new_right = split(right)
    if changed:
        return True, [left, new_right]
    return False, snail


def reduce_snail(snail: Snail) -> Snail:
    """
    Reduce a snailfish number by repeatedly exploding then splitting.

    Args:
        snail: Snailfish number to reduce.

    Returns:
        Fully reduced snailfish number.
    """
    while True:
        changed, snail, _, _ = explode(snail)
        if changed:
            continue
        changed, snail = split(snail)
        if not changed:
            break
    return snail


def add_snails(a: Snail, b: Snail) -> Snail:
    """
    Add two snailfish numbers and reduce the result.

    Args:
        a: Left operand.
        b: Right operand.

    Returns:
        Reduced sum.
    """
    return reduce_snail([a, b])


def magnitude(snail: Snail) -> int:
    """
    Compute the magnitude of a snailfish number.

    Args:
        snail: Snailfish number.

    Returns:
        Magnitude value computed recursively.
    """
    if isinstance(snail, int):
        return snail
    left, right = snail
    return 3 * magnitude(left) + 2 * magnitude(right)


def solve_part_one(numbers: List[Snail]) -> int:
    """
    Compute the magnitude of the final snailfish sum.

    Args:
        numbers: Parsed snailfish numbers.

    Returns:
        Magnitude of the reduced sum.
    """
    total = copy.deepcopy(numbers[0])
    for number in numbers[1:]:
        total = add_snails(total, copy.deepcopy(number))
    return magnitude(total)


def solve_part_two(numbers: List[Snail]) -> int:
    """
    Find the largest magnitude of any ordered pair sum.

    Args:
        numbers: Parsed snailfish numbers.

    Returns:
        Maximum magnitude from adding two distinct numbers.
    """
    max_mag = 0
    for i, first in enumerate(numbers):
        for j, second in enumerate(numbers):
            if i == j:
                continue
            result = add_snails(copy.deepcopy(first), copy.deepcopy(second))
            max_mag = max(max_mag, magnitude(result))
    return max_mag

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
