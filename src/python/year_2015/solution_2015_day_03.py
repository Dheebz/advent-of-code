"""Perfectly Spherical Houses in a Vacuum -- Advent of Code 2015 Day 3."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Set, Tuple

Coord = Tuple[int, int]


def parse_input(raw: str) -> str:
    """Return the trimmed direction string.

    Args:
        raw (str): Full puzzle input.

    Returns:
        str: Sequence of movement characters.
    """
    return raw.strip()


def deliver(instructions: Iterable[str], workers: int = 1) -> int:
    """Count unique houses visited by one or more workers following directions.

    Args:
        instructions (Iterable[str]): Movement characters ``^``, ``v``, ``<``, ``>``.
        workers (int): Number of delivery workers sharing the instruction stream.

    Returns:
        int: Count of distinct houses visited.
    """
    positions: list[Coord] = [(0, 0) for _ in range(workers)]
    visited: Set[Coord] = {(0, 0)}

    moves = {"^": (0, 1), "v": (0, -1), ">": (1, 0), "<": (-1, 0)}

    for step, char in enumerate(instructions):
        idx = step % workers
        dx, dy = moves[char]
        x, y = positions[idx]
        positions[idx] = (x + dx, y + dy)
        visited.add(positions[idx])

    return len(visited)


def solve_part_one(instructions: str) -> int:
    """Return houses visited by Santa alone."""
    return deliver(instructions, workers=1)


def solve_part_two(instructions: str) -> int:
    """Return houses visited with Robo-Santa assisting."""
    return deliver(instructions, workers=2)


def main() -> None:
    """
    Entry point for module execution.

    Args:
        None.

    Returns:
        Exit status code (``0`` for success).
    """
    parser = argparse.ArgumentParser(description="Solve Advent of Code 2015 Day 3.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).with_name("input_2015_day_03.txt"),
        help="Path to input file (defaults to the bundled input).",
    )
    parser.add_argument(
        "--part",
        type=int,
        choices=(1, 2),
        help="Run only the selected part (1 or 2). Defaults to running both.",
    )
    args = parser.parse_args()

    part_one, part_two = run(args.input, args.part)

    if part_one is not None:
        print(f"part one: {part_one}")

    if part_two is not None:
        print(f"part two: {part_two}")


def run(input_path: Path, part: int | None = None) -> tuple[int | None, int | None]:
    """Execute the selected puzzle parts and return their answers.

    Args:
        input_path (Path): Path to the puzzle input file.
        part (int | None, optional): Which part to run (1, 2, or both when None).

    Returns:
        tuple[int | None, int | None]: Answers for part one and part two (None if skipped).
    """
    directions = parse_input(input_path.read_text())

    part_one = solve_part_one(directions) if part in (None, 1) else None
    part_two = solve_part_two(directions) if part in (None, 2) else None

    return part_one, part_two


if __name__ == "__main__":
    main()

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
