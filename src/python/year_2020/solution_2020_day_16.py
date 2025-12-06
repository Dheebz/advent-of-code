"""Ticket Translation -- Advent of Code 2020 Day 16."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

Rule = Dict[str, List[Tuple[int, int]]]
Ticket = List[int]


def parse_input(raw: str) -> Tuple[Rule, Ticket, List[Ticket]]:
    """Return rules, your ticket, and nearby tickets."""
    sections = raw.strip().split("\n\n")
    rules: Rule = {}
    for line in sections[0].splitlines():
        name, ranges_part = line.split(":")
        ranges: List[Tuple[int, int]] = []
        for r in ranges_part.strip().split(" or "):
            low, high = r.split("-")
            ranges.append((int(low), int(high)))
        rules[name.strip()] = ranges

    your_ticket = [int(x) for x in sections[1].splitlines()[1].split(",")]
    nearby = [[int(x) for x in line.split(",")] for line in sections[2].splitlines()[1:]]
    return rules, your_ticket, nearby


def valid_for_any_rule(value: int, rules: Rule) -> bool:
    """
    Check if a value fits any of the provided rules.

    Args:
        value: Number to validate.
        rules: Mapping of field names to their valid ranges.

    Returns:
        True when the value lies within any of the ranges.
    """
    for ranges in rules.values():
        for low, high in ranges:
            if low <= value <= high:
                return True
    return False


def valid_for_rule(value: int, ranges: List[Tuple[int, int]]) -> bool:
    """
    Check if a value falls inside a specific field's ranges.

    Args:
        value: Number to validate.
        ranges: List of inclusive ranges for the field.

    Returns:
        True when the value satisfies at least one of the ranges.
    """
    return any(low <= value <= high for low, high in ranges)


def solve_part_one(data: Tuple[Rule, Ticket, List[Ticket]]) -> int:
    """
    Compute the ticket scanning error rate.

    Args:
        data: Tuple containing rules, your ticket, and nearby tickets.

    Returns:
        Sum of invalid values from nearby tickets.
    """
    rules, _, nearby = data
    error = 0
    for ticket in nearby:
        for value in ticket:
            if not valid_for_any_rule(value, rules):
                error += value
    return error


def determine_fields(rules: Rule, tickets: List[Ticket]) -> Dict[str, int]:
    """
    Determine the field ordering by elimination.

    Args:
        rules: Field rules mapping to ranges.
        tickets: List of valid tickets to consider.

    Returns:
        Mapping from field name to its column index.
    """
    field_possibilities: Dict[str, set[int]] = {}
    field_count = len(tickets[0])
    for name, ranges in rules.items():
        possible = set()
        for idx in range(field_count):
            if all(valid_for_rule(ticket[idx], ranges) for ticket in tickets):
                possible.add(idx)
        field_possibilities[name] = possible

    assignments: Dict[str, int] = {}
    while field_possibilities:
        determined = [
            (name, next(iter(indices)))
            for name, indices in field_possibilities.items()
            if len(indices) == 1
        ]
        if not determined:
            raise ValueError("could not resolve fields")
        for name, index in determined:
            assignments[name] = index
            del field_possibilities[name]
            for other_indices in field_possibilities.values():
                other_indices.discard(index)
    return assignments


def solve_part_two(data: Tuple[Rule, Ticket, List[Ticket]]) -> int:
    """
    Multiply the values of departure fields on your ticket.

    Args:
        data: Tuple containing rules, your ticket, and nearby tickets.

    Returns:
        Product of values whose field names start with "departure".
    """
    rules, your_ticket, nearby = data
    valid_tickets = [
        ticket for ticket in nearby if all(valid_for_any_rule(value, rules) for value in ticket)
    ]
    valid_tickets.append(your_ticket)

    fields = determine_fields(rules, valid_tickets)
    product = 1
    for name, index in fields.items():
        if name.startswith("departure"):
            product *= your_ticket[index]
    return product

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
