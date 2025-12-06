"""Handy Haversacks -- Advent of Code 2020 Day 7."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

Rule = Dict[str, List[Tuple[str, int]]]


def parse_input(raw: str) -> Rule:
    """Return mapping of bag to contained bags with counts."""
    rules: Rule = {}
    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        outer, inner_part = line.split(" bags contain ")
        if inner_part == "no other bags.":
            rules[outer] = []
            continue
        contents: List[Tuple[str, int]] = []
        for item in inner_part.split(","):
            words = item.strip().split()
            count = int(words[0])
            color = " ".join(words[1:3])
            contents.append((color, count))
        rules[outer] = contents
    return rules


def can_eventually_contain(target: str, current: str, rules: Rule, memo: Dict[str, bool]) -> bool:
    """
    Determine if the current bag color can eventually contain the target color.

    Args:
        target: Color we're trying to reach.
        current: Current bag color being inspected.
        rules: Mapping of bag colors to their contents.
        memo: Cache for previously computed results.

    Returns:
        True when the target color can be reached recursively.
    """
    if current in memo:
        return memo[current]
    for color, _ in rules.get(current, []):
        if color == target or can_eventually_contain(target, color, rules, memo):
            memo[current] = True
            return True
    memo[current] = False
    return False


def solve_part_one(rules: Rule, target: str = "shiny gold") -> int:
    """
    Count how many bag colors can eventually contain the target bag.

    Args:
        rules: Bag containment rules.
        target: Target bag color to contain.

    Returns:
        Number of bag colors that can reach the target.
    """
    memo: Dict[str, bool] = {}
    return sum(
        1
        for color in rules
        if color != target and can_eventually_contain(target, color, rules, memo)
    )


def count_inside(color: str, rules: Rule, memo: Dict[str, int]) -> int:
    """
    Compute total number of bags contained inside the given color.

    Args:
        color: Bag color to evaluate.
        rules: Containment rules mapping colors to contents.
        memo: Cache for previously counted colors.

    Returns:
        Number of individual bags required inside the color.
    """
    if color in memo:
        return memo[color]
    total = 0
    for inner_color, count in rules.get(color, []):
        total += count * (1 + count_inside(inner_color, rules, memo))
    memo[color] = total
    return total


def solve_part_two(rules: Rule, target: str = "shiny gold") -> int:
    """
    Count the total bags required inside the target bag.

    Args:
        rules: Containment rules mapping colors to contents.
        target: Target bag color to measure.

    Returns:
        Total number of bags nested inside the target.
    """
    memo: Dict[str, int] = {}
    return count_inside(target, rules, memo)

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
