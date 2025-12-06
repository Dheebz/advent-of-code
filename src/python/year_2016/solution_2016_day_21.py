"""Scrambled Letters and Hash -- Advent of Code 2016 Day 21."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List


def parse_input(raw: str) -> List[str]:
    """Return the list of scrambling instructions."""
    return [line.strip() for line in raw.strip().splitlines() if line.strip()]


def rotate_left(s: str, steps: int) -> str:
    """Rotate string left by given steps."""
    steps %= len(s)
    return s[steps:] + s[:steps]


def rotate_right(s: str, steps: int) -> str:
    """Rotate string right by given steps."""
    steps %= len(s)
    return s[-steps:] + s[:-steps]


def apply(s: str, instruction: str) -> str:
    """Apply a single scrambling instruction."""
    parts = instruction.split()
    if parts[0] == "swap" and parts[1] == "position":
        x, y = int(parts[2]), int(parts[5])
        lst = list(s)
        lst[x], lst[y] = lst[y], lst[x]
        return "".join(lst)
    if parts[0] == "swap" and parts[1] == "letter":
        a, b = parts[2], parts[5]
        return s.replace(a, "#").replace(b, a).replace("#", b)
    if parts[0] == "rotate" and parts[1] in {"left", "right"}:
        steps = int(parts[2])
        return rotate_left(s, steps) if parts[1] == "left" else rotate_right(s, steps)
    if parts[0] == "rotate" and parts[1] == "based":
        idx = s.index(parts[-1])
        steps = 1 + idx + (1 if idx >= 4 else 0)
        return rotate_right(s, steps)
    if parts[0] == "reverse":
        x, y = int(parts[2]), int(parts[4])
        return s[:x] + s[x : y + 1][::-1] + s[y + 1 :]
    if parts[0] == "move":
        x, y = int(parts[2]), int(parts[5])
        lst = list(s)
        char = lst.pop(x)
        lst.insert(y, char)
        return "".join(lst)
    return s


def invert(s: str, instruction: str) -> str:
    """Apply the inverse of a scrambling instruction."""
    parts = instruction.split()
    if parts[0] == "move":
        # invert move by swapping arguments
        y, x = int(parts[2]), int(parts[5])
        lst = list(s)
        char = lst.pop(x)
        lst.insert(y, char)
        return "".join(lst)
    if parts[0] == "rotate" and parts[1] == "based":
        # brute-force: try all rotations to find one that produces s
        for i in range(len(s)):
            candidate = rotate_left(s, i)
            if apply(candidate, instruction) == s:
                return candidate
        raise ValueError("No inverse found")
    if parts[0] == "rotate" and parts[1] == "left":
        return rotate_right(s, int(parts[2]))
    if parts[0] == "rotate" and parts[1] == "right":
        return rotate_left(s, int(parts[2]))
    if parts[0] == "swap" and parts[1] == "letter":
        return apply(s, instruction)
    if parts[0] == "swap" and parts[1] == "position":
        return apply(s, instruction)
    if parts[0] == "reverse":
        return apply(s, instruction)
    return s


def scramble(password: str, instructions: List[str]) -> str:
    """Scramble a password according to the instructions."""
    result = password
    for instruction in instructions:
        result = apply(result, instruction)
    return result


def unscramble(password: str, instructions: List[str]) -> str:
    """Unscramble a password by applying inverse instructions."""
    result = password
    for instruction in reversed(instructions):
        result = invert(result, instruction)
    return result


def solve_part_one(instructions: List[str]) -> str:
    """Scramble the starting password."""
    return scramble("abcdefgh", instructions)


def solve_part_two(instructions: List[str]) -> str:
    """Unscramble the target password."""
    return unscramble("fbgdceah", instructions)

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
