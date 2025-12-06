"""Monster Messages -- Advent of Code 2020 Day 19."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

RuleMap = Dict[int, str]


def parse_input(raw: str) -> Tuple[RuleMap, List[str]]:
    """Return rules mapping and messages."""
    rule_block, messages_block = raw.strip().split("\n\n")
    rules: RuleMap = {}
    for line in rule_block.splitlines():
        idx_str, rule_def = line.split(":")
        rules[int(idx_str)] = rule_def.strip()
    messages = [line.strip() for line in messages_block.splitlines() if line.strip()]
    return rules, messages


def build_regex(rules: RuleMap, index: int, cache: Dict[int, str]) -> str:
    """
    Recursively build a regex pattern for the given rule index.

    Args:
        rules: Mapping of rule numbers to rule definitions.
        index: Rule number to translate.
        cache: Memoization cache for already built patterns.

    Returns:
        Regex pattern string representing the rule.
    """
    if index in cache:
        return cache[index]
    rule = rules[index]
    if '"' in rule:
        value = rule.replace('"', "")
    else:
        parts = []
        for option in rule.split("|"):
            subparts = []
            for token in option.strip().split():
                subparts.append(build_regex(rules, int(token), cache))
            parts.append("".join(subparts))
        value = "|".join(parts)
        if "|" in value:
            value = f"(?:{value})"
    cache[index] = value
    return value


def solve_part_one(data: Tuple[RuleMap, List[str]]) -> int:
    """Messages that completely match rule 0."""
    rules, messages = data
    cache: Dict[int, str] = {}
    pattern = re.compile(f"^{build_regex(rules, 0, cache)}$")
    return sum(1 for message in messages if pattern.match(message))


def solve_part_two(data: Tuple[RuleMap, List[str]]) -> int:
    """Messages matching modified recursive rules for 8 and 11."""
    rules, messages = data
    cache: Dict[int, str] = {}
    rule_42 = build_regex(rules, 42, cache)
    rule_31 = build_regex(rules, 31, cache)

    # rule 8 -> 42+
    # rule 11 -> 42{n}31{n}, approximate recursion with bounded n
    parts = []
    for n in range(1, 8):
        parts.append(f"(?:{rule_42})+{rule_42 * n}{rule_31 * n}")
    pattern = re.compile(f"^(?:{'|'.join(parts)})$")
    return sum(1 for message in messages if pattern.match(message))

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
