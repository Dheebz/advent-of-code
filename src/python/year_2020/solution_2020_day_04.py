"""Passport Processing -- Advent of Code 2020 Day 4."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List

Passport = Dict[str, str]


def parse_input(raw: str) -> List[Passport]:
    """Return passports as dictionaries of field values."""
    passports: List[Passport] = []
    for block in raw.strip().split("\n\n"):
        fields = {}
        for item in block.split():
            key, value = item.split(":")
            fields[key] = value
        passports.append(fields)
    return passports


REQUIRED_FIELDS = {"byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"}
HCL_RE = re.compile(r"^#[0-9a-f]{6}$")
PID_RE = re.compile(r"^[0-9]{9}$")
VALID_EYE_COLORS = {"amb", "blu", "brn", "gry", "grn", "hzl", "oth"}


def has_required_fields(passport: Passport) -> bool:
    """
    Ensure the passport dictionary defines all required keys.

    Args:
        passport: Passport field map.

    Returns:
        True when every required field is present.
    """
    return REQUIRED_FIELDS.issubset(passport.keys())


def valid_height(height: str) -> bool:
    """
    Validate a height string with units ``cm`` or ``in``.

    Args:
        height: Height value with suffix (e.g. ``"160cm"``).

    Returns:
        True if the height is within the allowed range for the unit.
    """
    if height.endswith("cm"):
        try:
            value = int(height[:-2])
        except ValueError:
            return False
        return 150 <= value <= 193
    if height.endswith("in"):
        try:
            value = int(height[:-2])
        except ValueError:
            return False
        return 59 <= value <= 76
    return False


def is_valid(passport: Passport) -> bool:
    """
    Determine whether a passport passes all field validators.

    Args:
        passport: Passport field map.

    Returns:
        True when the passport contains required fields and each validator passes.
    """
    if not has_required_fields(passport):
        return False
    try:
        byr = int(passport["byr"])
        iyr = int(passport["iyr"])
        eyr = int(passport["eyr"])
    except ValueError:
        return False

    if not (1920 <= byr <= 2002):
        return False
    if not (2010 <= iyr <= 2020):
        return False
    if not (2020 <= eyr <= 2030):
        return False
    if not valid_height(passport.get("hgt", "")):
        return False
    if not HCL_RE.match(passport.get("hcl", "")):
        return False
    if passport.get("ecl") not in VALID_EYE_COLORS:
        return False
    if not PID_RE.match(passport.get("pid", "")):
        return False
    return True


def solve_part_one(passports: List[Passport]) -> int:
    """Passports containing all required fields."""
    return sum(1 for passport in passports if has_required_fields(passport))


def solve_part_two(passports: List[Passport]) -> int:
    """Passports that satisfy all validation rules."""
    return sum(1 for passport in passports if is_valid(passport))

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
