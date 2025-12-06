"""Docking Data -- Advent of Code 2020 Day 14."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

Instruction = Tuple[str, int, int | str]


def parse_input(raw: str) -> List[Instruction]:
    """Return list of instructions."""
    instructions: List[Instruction] = []
    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        if line.startswith("mask"):
            instructions.append(("mask", 0, line.split("=")[1].strip()))
        else:
            left, value_str = line.split("=")
            addr = int(left[left.index("[") + 1 : left.index("]")])
            instructions.append(("mem", addr, int(value_str.strip())))
    return instructions


def apply_mask_value(mask: str, value: int) -> int:
    """
    Apply the mask to a value according to part one rules.

    Args:
        mask: Mask string containing ``0``, ``1``, and ``X``.
        value: Integer value to mask.

    Returns:
        Masked integer value.
    """
    bits = list(f"{value:036b}")
    for i, char in enumerate(mask):
        if char == "X":
            continue
        bits[i] = char
    return int("".join(bits), 2)


def apply_mask_address(mask: str, address: int) -> List[int]:
    """
    Apply the mask to generate all floating memory addresses.

    Args:
        mask: Mask string with floating bits.
        address: Original memory address.

    Returns:
        List of all concrete addresses after applying floating bits.
    """
    base = []
    floating_positions: List[int] = []
    for i, char in enumerate(mask):
        if char == "0":
            base.append((address >> (35 - i)) & 1)
        elif char == "1":
            base.append(1)
        else:  # X
            base.append("X")
            floating_positions.append(i)

    addresses: List[int] = []
    combinations = 1 << len(floating_positions)
    for combo in range(combinations):
        bits = base.copy()
        for bit_index, pos in enumerate(floating_positions):
            bit_value = (combo >> bit_index) & 1
            bits[pos] = bit_value
        addr_value = 0
        for bit in bits:
            addr_value = (addr_value << 1) | int(bit)
        addresses.append(addr_value)
    return addresses


def solve_part_one(instructions: List[Instruction]) -> int:
    """
    Sum all values left in memory after applying the value mask.

    Args:
        instructions: Program instructions alternating between mask and memory writes.

    Returns:
        Sum of values in memory after executing the program.
    """
    mask = "X" * 36
    memory: Dict[int, int] = {}
    for kind, addr, value in instructions:
        if kind == "mask":
            mask = value  # type: ignore[assignment]
        else:
            memory[addr] = apply_mask_value(mask, int(value))
    return sum(memory.values())


def solve_part_two(instructions: List[Instruction]) -> int:
    """
    Sum all values after decoding memory addresses using the floating mask.

    Args:
        instructions: Program instructions alternating between mask and memory writes.

    Returns:
        Sum of values in memory after executing the program with address decoding.
    """
    mask = "X" * 36
    memory: Dict[int, int] = {}
    for kind, addr, value in instructions:
        if kind == "mask":
            mask = value  # type: ignore[assignment]
        else:
            for target in apply_mask_address(mask, addr):
                memory[target] = int(value)
    return sum(memory.values())

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
