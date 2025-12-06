"""Monkey Math -- Advent of Code 2022 Day 21."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple, Union

Expr = Union[int, Tuple[str, str, str]]


def parse_input(raw: str) -> Dict[str, Expr]:
    """Return mapping from monkey name to expression/value."""
    monkeys: Dict[str, Expr] = {}
    for line in raw.strip().splitlines():
        name, expr = line.split(": ")
        parts = expr.split()
        if len(parts) == 1:
            monkeys[name] = int(parts[0])
        else:
            monkeys[name] = (parts[0], parts[1], parts[2])
    return monkeys


def evaluate(name: str, monkeys: Dict[str, Expr], ignore: str | None = None) -> int | None:
    """Evaluate expression; return None if depends on ignore."""
    if name == ignore:
        return None
    expr = monkeys[name]
    if isinstance(expr, int):
        return expr
    left, op, right = expr
    l_val = evaluate(left, monkeys, ignore)
    r_val = evaluate(right, monkeys, ignore)
    if l_val is None or r_val is None:
        return None
    if op == "+":
        return l_val + r_val
    if op == "-":
        return l_val - r_val
    if op == "*":
        return l_val * r_val
    return l_val // r_val


def solve_for(name: str, target: int, monkeys: Dict[str, Expr]) -> int:
    """Back-solve for the value of the given name to reach target."""
    if name == "humn":
        return target
    left, op, right = monkeys[name]  # type: ignore[index]
    l_val = evaluate(left, monkeys, ignore="humn")
    r_val = evaluate(right, monkeys, ignore="humn")
    if l_val is None:
        unknown, known, is_left = left, r_val, True
    else:
        unknown, known, is_left = right, l_val, False

    assert known is not None
    if op == "+":
        new_target = target - known
    elif op == "-":
        new_target = target + known if is_left else known - target
    elif op == "*":
        new_target = target // known
    else:  # "/"
        new_target = target * known if is_left else known // target
    return solve_for(unknown, new_target, monkeys)


def solve_part_one(monkeys: Dict[str, Expr]) -> int:
    """Value shouted by root."""
    return evaluate("root", monkeys)  # type: ignore[return-value]


def solve_part_two(monkeys: Dict[str, Expr]) -> int:
    """Human value needed so both sides of root match."""
    left, _, right = monkeys["root"]  # type: ignore[index]
    l_val = evaluate(left, monkeys, ignore="humn")
    r_val = evaluate(right, monkeys, ignore="humn")
    if l_val is None:
        return solve_for(left, r_val, monkeys)  # type: ignore[arg-type]
    return solve_for(right, l_val, monkeys)  # type: ignore[arg-type]

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
