"""Packet Decoder -- Advent of Code 2021 Day 16."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple


def parse_input(raw: str) -> str:
    """Return the hexadecimal transmission."""
    return raw.strip()


def hex_to_bits(hex_string: str) -> str:
    """Convert each hex digit to four bits of binary."""
    return "".join(f"{int(ch, 16):04b}" for ch in hex_string)


def parse_literal(bits: str, index: int) -> Tuple[int, int]:
    """Read a literal value starting at `index` and return (value, next_index)."""
    literal_bits = []
    while True:
        group = bits[index : index + 5]
        literal_bits.append(group[1:])
        index += 5
        if group[0] == "0":
            break
    return int("".join(literal_bits), 2), index


def parse_packet(bits: str, index: int = 0) -> Tuple[int, int, int]:
    """Return (version_sum, value, next_index) for the packet starting at `index`."""
    version = int(bits[index : index + 3], 2)
    type_id = int(bits[index + 3 : index + 6], 2)
    index += 6
    version_sum = version

    if type_id == 4:
        value, index = parse_literal(bits, index)
        return version_sum, value, index

    length_type_id = bits[index]
    index += 1
    values: list[int] = []

    if length_type_id == "0":
        total_length = int(bits[index : index + 15], 2)
        index += 15
        end_index = index + total_length
        while index < end_index:
            sub_version, sub_value, index = parse_packet(bits, index)
            version_sum += sub_version
            values.append(sub_value)
    else:
        count = int(bits[index : index + 11], 2)
        index += 11
        for _ in range(count):
            sub_version, sub_value, index = parse_packet(bits, index)
            version_sum += sub_version
            values.append(sub_value)

    if type_id == 0:
        value = sum(values)
    elif type_id == 1:
        value = 1
        for v in values:
            value *= v
    elif type_id == 2:
        value = min(values)
    elif type_id == 3:
        value = max(values)
    elif type_id == 5:
        value = 1 if values[0] > values[1] else 0
    elif type_id == 6:
        value = 1 if values[0] < values[1] else 0
    elif type_id == 7:
        value = 1 if values[0] == values[1] else 0
    else:
        raise ValueError(f"unknown type id {type_id}")

    return version_sum, value, index


def solve_part_one(hex_payload: str) -> int:
    """Sum every packet version in the transmission."""
    bits = hex_to_bits(parse_input(hex_payload))
    version_sum, _, _ = parse_packet(bits)
    return version_sum


def solve_part_two(hex_payload: str) -> int:
    """Return the value of the outermost packet."""
    bits = hex_to_bits(parse_input(hex_payload))
    _, value, _ = parse_packet(bits)
    return value

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
