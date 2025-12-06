"""Advent of Code 2024 Day 13: Claw Contraption."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Tuple

Machine = Tuple[int, int, int, int, int, int]  # ax, ay, bx, by, px, py


def parse_input(raw: str, offset: int = 0) -> list[Machine]:
    """
    Parse the claw machine descriptions from the raw text.

    Args:
        raw: Input containing machine blocks separated by blank lines.
        offset: Optional offset added to the piston target coordinates.

    Returns:
        List of machine tuples (ax, ay, bx, by, px, py).
    """
    text = raw.strip()
    machines: list[Machine] = []
    for chunk in text.split("\n\n"):
        lines = chunk.splitlines()
        ax, ay = [int(x.split("+")[1]) for x in lines[0].split(", ")]
        bx, by = [int(x.split("+")[1]) for x in lines[1].split(", ")]
        px, py = [int(x.split("=")[1]) + offset for x in lines[2].split(", ")]
        machines.append((ax, ay, bx, by, px, py))
    return machines


def parse_machines(path: Path, offset: int = 0) -> list[Machine]:
    """
    Parse machine definitions from a file path.

    Args:
        path: Path to the machine description file.
        offset: Optional offset added to piston coordinates.

    Returns:
        Parsed list of machines.
    """
    return parse_input(path.read_text(), offset)


def min_tokens_limited(machine: Machine) -> int | None:
    """
    Brute-force the minimum token cost respecting the 0-100 limit.

    Args:
        machine: Tuple containing thrust coefficients and target coordinates.

    Returns:
        Minimum token cost or None if no solution exists within the 0-100 bounds.
    """
    ax, ay, bx, by, px, py = machine
    best: int | None = None
    for a in range(101):
        for b in range(101):
            if ax * a + bx * b == px and ay * a + by * b == py:
                cost = 3 * a + b
                if best is None or cost < best:
                    best = cost
    return best


def min_tokens_exact(machine: Machine) -> int | None:
    """
    Solve the linear system exactly for non-negative integers.

    Args:
        machine: Tuple describing the coefficients and target piston position.

    Returns:
        Minimum token cost if a valid solution exists; otherwise None.
    """
    ax, ay, bx, by, px, py = machine
    det = ax * by - ay * bx
    if det == 0:
        return None
    a_num = px * by - py * bx
    b_num = ax * py - ay * px
    if a_num % det or b_num % det:
        return None
    a = a_num // det
    b = b_num // det
    if a < 0 or b < 0:
        return None
    return 3 * a + b


def solve_part_one(machines: Iterable[Machine]) -> int:
    """
    Sum the minimum token cost per machine under the limited search.

    Args:
        machines: Iterable of machine tuples.

    Returns:
        Total cost using the bounded brute-force solver per machine.
    """
    return sum(cost for m in machines if (cost := min_tokens_limited(m)) is not None)


def solve_part_two(machines: Iterable[Machine]) -> int:
    """
    Sum the minimum token cost per machine using the exact solver.

    Args:
        machines: Iterable of machine tuples.

    Returns:
        Total cost using the algebraic solver per machine.
    """
    return sum(cost for m in machines if (cost := min_tokens_exact(m)) is not None)

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
