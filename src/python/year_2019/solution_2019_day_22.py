"""Slam Shuffle -- Advent of Code 2019 Day 22."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple


def parse_input(raw: str) -> List[str]:
    """Parse shuffle instructions.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        List[str]: List of instructions.
    """
    return [line.strip() for line in raw.strip().splitlines() if line.strip()]


def modinv(value: int, modulus: int) -> int:
    """Compute modular inverse."""
    return pow(value, -1, modulus)


def build_transform(instructions: List[str], deck_size: int) -> Tuple[int, int]:
    """Convert shuffles into a linear transformation.

    Args:
        instructions (List[str]): Shuffle operations.
        deck_size (int): Deck size.

    Returns:
        Tuple[int, int]: Coefficients (a, b) for new_position = a*x + b (mod deck_size).
    """
    a, b = 1, 0  # new_position = a*x + b
    for line in instructions:
        if line == "deal into new stack":
            a = (-a) % deck_size
            b = (-b - 1) % deck_size
        elif line.startswith("cut"):
            n = int(line.split()[-1])
            b = (b - n) % deck_size
        elif line.startswith("deal with increment"):
            n = int(line.split()[-1])
            a = (a * n) % deck_size
            b = (b * n) % deck_size
        else:
            raise ValueError(f"unknown instruction {line}")
    return a, b


def apply_transform(a: int, b: int, x: int, deck_size: int) -> int:
    """Apply the linear transform to position x."""
    return (a * x + b) % deck_size


def repeat_transform(a: int, b: int, times: int, deck_size: int) -> Tuple[int, int]:
    """Repeat the transform efficiently.

    Args:
        a (int): Linear coefficient.
        b (int): Offset.
        times (int): Number of repetitions.
        deck_size (int): Deck size.

    Returns:
        Tuple[int, int]: Combined coefficients after repetition.
    """
    an = pow(a, times, deck_size)
    if a == 1:
        bn = (b * times) % deck_size
    else:
        bn = (b * (an - 1) * modinv((a - 1) % deck_size, deck_size)) % deck_size
    return an, bn


def solve_part_one(instructions: List[str]) -> int:
    """Return the position of card 2019 after shuffling."""
    deck_size = 10007
    a, b = build_transform(instructions, deck_size)
    return apply_transform(a, b, 2019, deck_size)


def solve_part_two(instructions: List[str]) -> int:
    """Return the card at position 2020 after large repeated shuffles."""
    deck_size = 119_315_717_514_047
    times = 101_741_582_076_661
    a, b = build_transform(instructions, deck_size)
    a_n, b_n = repeat_transform(a, b, times, deck_size)
    # Find original card at position 2020 after shuffles.
    return ((2020 - b_n) * modinv(a_n, deck_size)) % deck_size

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
