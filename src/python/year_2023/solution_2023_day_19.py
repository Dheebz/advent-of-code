"""Aplenty -- Advent of Code 2023 Day 19."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

Rule = Tuple[str, str, int, str]  # variable, op, value, target
Workflow = List[Rule]
Part = Dict[str, int]
Range = Dict[str, Tuple[int, int]]


def parse_input(raw: str) -> Tuple[Dict[str, Workflow], List[Part]]:
    """Parse workflows and parts."""
    workflows_raw, parts_raw = raw.strip().split("\n\n")
    workflows: Dict[str, Workflow] = {}
    for line in workflows_raw.splitlines():
        name, rest = line.split("{")
        rules_str = rest.rstrip("}")
        rules: Workflow = []
        for chunk in rules_str.split(","):
            if ":" in chunk:
                cond, target = chunk.split(":")
                if "<" in cond:
                    var, val = cond.split("<")
                    rules.append((var, "<", int(val), target))
                else:
                    var, val = cond.split(">")
                    rules.append((var, ">", int(val), target))
            else:
                rules.append(("default", "", 0, chunk))
        workflows[name] = rules

    parts: List[Part] = []
    for line in parts_raw.splitlines():
        attrs = {}
        for segment in line.strip("{}").split(","):
            key, val = segment.split("=")
            attrs[key] = int(val)
        parts.append(attrs)
    return workflows, parts


def run_part(part: Part, workflows: Dict[str, Workflow]) -> str:
    """Return final destination for a part."""
    current = "in"
    while True:
        for var, op, val, target in workflows[current]:
            if var == "default":
                current = target
                break
            if op == "<" and part[var] < val or op == ">" and part[var] > val:
                current = target
                break
        if current in {"A", "R"}:
            return current


def solve_part_one(parsed: Tuple[Dict[str, Workflow], List[Part]]) -> int:
    """Sum of ratings for accepted parts."""
    workflows, parts = parsed
    return sum(sum(part.values()) for part in parts if run_part(part, workflows) == "A")


def count_accept(workflows: Dict[str, Workflow], name: str, ranges: Range) -> int:
    """Count accepted combinations for given workflow."""
    if name == "A":
        total = 1
        for lo, hi in ranges.values():
            total *= hi - lo + 1
        return total
    if name == "R":
        return 0

    total = 0
    current_ranges = dict(ranges)
    for var, op, val, target in workflows[name]:
        if var == "default":
            total += count_accept(workflows, target, current_ranges)
            break
        lo, hi = current_ranges[var]
        if op == "<":
            true_range = (lo, min(hi, val - 1))
            false_range = (max(lo, val), hi)
        else:
            true_range = (max(lo, val + 1), hi)
            false_range = (lo, min(hi, val))
        if true_range[0] <= true_range[1]:
            new_ranges = dict(current_ranges)
            new_ranges[var] = true_range
            total += count_accept(workflows, target, new_ranges)
        if false_range[0] <= false_range[1]:
            current_ranges[var] = false_range
        else:
            break
    return total


def solve_part_two(parsed: Tuple[Dict[str, Workflow], List[Part]]) -> int:
    """Count accepted combinations across full range."""
    workflows, _ = parsed
    initial: Range = {key: (1, 4000) for key in ["x", "m", "a", "s"]}
    return count_accept(workflows, "in", initial)

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
