"""Trash Compactor - Advent of Code 2025 Day 6."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

Record = Tuple[int, int, int, int, str]
Records = List[Record]


def parse_input(raw: str) -> Dict[str, object]:
    """
    Parse the input data.

    Returns a dict with:
      - "records": part-one-friendly list of (ints..., op) tuples
      - "grid_lines": original non-empty lines (with spaces preserved)
    """
    # Keep raw lines WITH spaces for the grid
    raw_lines = raw.splitlines()
    grid_lines = [line for line in raw_lines if line.strip()]

    if len(grid_lines) < 2:
        raise ValueError("Expected at least one row of numbers and one row of operators")

    # For part one we can safely collapse whitespace
    token_lines = [line.split() for line in grid_lines]

    # Last line = operators, everything above = numbers
    *number_rows, op_row = token_lines
    num_cols = len(op_row)

    if num_cols == 0:
        raise ValueError("No problems found in operator row")

    # All numeric rows must have the same number of entries
    if any(len(row) != num_cols for row in number_rows):
        raise ValueError("All rows must have the same number of values")

    records: Records = []
    for c in range(num_cols):
        nums = [int(row[c]) for row in number_rows]
        op = op_row[c]
        # Record is (int, int, int, int, str) in your puzzle; this generalizes
        record: Record = (nums[0], nums[1], nums[2], nums[3], op)
        records.append(record)

    return {
        "records": records,
        "grid_lines": grid_lines,
    }


def aggregate_record(record: Record) -> int:
    """
    Aggregate a single record by performing the indicated operation.

    Args:
        record: A tuple of four integers and an operator string.

    Returns:
        The result of applying the operation to the four integers.
    """
    op = record[4]
    if op == "+":
        return record[0] + record[1] + record[2] + record[3]
    elif op == "-":
        return record[0] - record[1] - record[2] - record[3]
    elif op == "*":
        return record[0] * record[1] * record[2] * record[3]
    elif op == "/":
        if record[1] == 0 or record[2] == 0 or record[3] == 0:
            raise ValueError("Division by zero in record")
        return record[0] // record[1] // record[2] // record[3]
    else:
        raise ValueError(f"Unknown operation: {op}")


def solve_part_one(data: Dict[str, object]) -> str | int:
    """
    Solve part one of the problem.

    For each record, perform the indicated operation on the four integers,
    then sum all the results.

    Args:
        data: Parsed input data.

    Returns:
        The sum of all aggregated record results.
    """
    records: Records = data["records"]  # type: ignore[assignment]
    total = 0
    for record in records:
        total += aggregate_record(record)
    return total


def solve_part_two(data: Dict[str, object]) -> str | int:
    """
    Solve part two of the problem.

    Cephalopod math is written in columns:

      - Treat the worksheet as a character grid.
      - Columns that are all spaces are separators between problems.
      - Within each contiguous block of columns (a problem):
          * Each column that has digits in the top rows is ONE number.
          * Digits are read top-to-bottom, skipping spaces.
          * The bottom row in that block has exactly one operator (+ or *).

    Args:
        data: Parsed input data.

    Returns:
        The sum of all evaluated problems.
    """
    grid_lines: List[str] = data["grid_lines"]  # type: ignore[assignment]

    # Normalize all lines to the same width by padding with spaces on the right
    height = len(grid_lines)
    width = max(len(line) for line in grid_lines)
    lines = [line.ljust(width) for line in grid_lines]

    # A separator column is one where *every* row has a space
    is_sep = [all(lines[r][c] == " " for r in range(height)) for c in range(width)]

    # Group columns into contiguous non-separator segments (each is one problem)
    segments: List[List[int]] = []
    current: List[int] = []
    for c in range(width):
        if is_sep[c]:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(c)
    if current:
        segments.append(current)

    total = 0

    # All rows except the last contain digits; last row has operators
    digit_row_count = height - 1

    for seg in segments:
        numbers: List[int] = []
        op: str | None = None

        for c in seg:
            column_chars = [lines[r][c] for r in range(height)]

            # Operator lives in the bottom row (last line)
            bottom = column_chars[-1]
            if bottom in {"+", "*"}:
                if op is None:
                    op = bottom
                elif op != bottom:
                    raise ValueError(f"Multiple different operators in one segment at column {c}")

            # Build the number from the digit rows (top to just above bottom)
            digits = [ch for ch in column_chars[:digit_row_count] if ch != " "]
            if digits:
                numbers.append(int("".join(digits)))

        # If no operator or no numbers, skip (shouldn't happen with valid input)
        if op is None or not numbers:
            continue

        # '+' and '*' are commutative, so column order (left/right) doesn't matter
        if op == "+":
            value = sum(numbers)
        elif op == "*":
            value = 1
            for n in numbers:
                value *= n
        else:
            raise ValueError(f"Unsupported operator in part two: {op!r}")

        total += value

    return total

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
