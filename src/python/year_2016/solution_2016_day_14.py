"""One-Time Pad -- Advent of Code 2016 Day 14."""

from __future__ import annotations

import argparse
from functools import lru_cache
from hashlib import md5
from pathlib import Path
from typing import Optional


def parse_input(raw: str) -> str:
    """Return the salt value."""
    return raw.strip()


def stretch_hash(value: str, times: int) -> str:
    """Apply repeated MD5 hashing.

    Args:
        value (str): Starting hash value.
        times (int): Number of additional hash rounds.

    Returns:
        str: Final hexadecimal digest.
    """
    result = value
    for _ in range(times):
        result = md5(result.encode()).hexdigest()
    return result


def find_triple(hash_str: str) -> Optional[str]:
    """Find the first character that appears three times consecutively.

    Args:
        hash_str (str): Hash string to scan.

    Returns:
        Optional[str]: Character if found, else None.
    """
    for idx in range(len(hash_str) - 2):
        if hash_str[idx] == hash_str[idx + 1] == hash_str[idx + 2]:
            return hash_str[idx]
    return None


def has_quint(hash_str: str, char: str) -> bool:
    """Check whether the hash contains a quintuple of the given character.

    Args:
        hash_str (str): Hash string to scan.
        char (str): Target character.

    Returns:
        bool: True if five consecutive chars found.
    """
    target = char * 5
    return target in hash_str


def find_key_index(salt: str, stretched: bool) -> int:
    """Find the index of the 64th key for the given salt.

    Args:
        salt (str): Salt value.
        stretched (bool): Whether to apply 2016 extra hash rounds.

    Returns:
        int: Index producing the 64th key.
    """
    extra = 2016 if stretched else 0

    @lru_cache(maxsize=None)
    def get_hash(index: int) -> str:
        base = md5(f"{salt}{index}".encode()).hexdigest()
        return stretch_hash(base, extra) if extra else base

    keys_found = 0
    index = 0
    while True:
        h = get_hash(index)
        char = find_triple(h)
        if char:
            for future in range(index + 1, index + 1001):
                if has_quint(get_hash(future), char):
                    keys_found += 1
                    if keys_found == 64:
                        return index
                    break
        index += 1


def solve_part_one(salt: str) -> int:
    """Index of the 64th key without hashing stretches."""
    return find_key_index(salt, False)


def solve_part_two(salt: str) -> int:
    """Index of the 64th key with stretched hashes."""
    return find_key_index(salt, True)

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
