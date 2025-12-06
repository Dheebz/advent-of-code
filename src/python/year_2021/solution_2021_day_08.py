"""Seven Segment Search -- Advent of Code 2021 Day 8."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

Entry = Tuple[List[str], List[str]]


def parse_input(raw: str) -> List[Entry]:
    """
    Parse the signal patterns and output digits from the input.

    Args:
        raw: Input lines of signal patterns followed by output values.

    Returns:
        List of tuples containing pattern list and output list.
    """
    entries: List[Entry] = []
    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        patterns_str, output_str = line.split(" | ")
        entries.append((patterns_str.split(), output_str.split()))
    return entries


def decode_entry(patterns: List[str], outputs: List[str]) -> int:
    """
    Decode a single entry by deducing the wiring mapping.

    Args:
        patterns: Ten unique signal patterns.
        outputs: Four output values to decode.

    Returns:
        Integer represented by the decoded output values.
    """
    patterns_sets = [set(p) for p in patterns]
    digits: dict[int, set[str]] = {}
    digits[1] = next(p for p in patterns_sets if len(p) == 2)
    digits[4] = next(p for p in patterns_sets if len(p) == 4)
    digits[7] = next(p for p in patterns_sets if len(p) == 3)
    digits[8] = next(p for p in patterns_sets if len(p) == 7)

    six_segments = [p for p in patterns_sets if len(p) == 6]
    five_segments = [p for p in patterns_sets if len(p) == 5]

    digits[9] = next(p for p in six_segments if digits[4] <= p)
    six_segments.remove(digits[9])
    digits[0] = next(p for p in six_segments if digits[1] <= p)
    six_segments.remove(digits[0])
    digits[6] = six_segments[0]

    digits[3] = next(p for p in five_segments if digits[1] <= p)
    five_segments.remove(digits[3])
    digits[5] = next(p for p in five_segments if p <= digits[6])
    five_segments.remove(digits[5])
    digits[2] = five_segments[0]

    mapping = {"".join(sorted(value)): digit for digit, value in digits.items()}
    decoded = int("".join(str(mapping["".join(sorted(o))]) for o in outputs))
    return decoded


def solve_part_one(entries: List[Entry]) -> int:
    """
    Count how many output digits have an unambiguous length.

    Args:
        entries: Parsed signal patterns and outputs.

    Returns:
        Total number of output digits with unique segment counts.
    """
    unique_lengths = {2, 3, 4, 7}
    return sum(1 for _, outputs in entries for value in outputs if len(value) in unique_lengths)


def solve_part_two(entries: List[Entry]) -> int:
    """
    Sum all decoded output values across entries.

    Args:
        entries: Parsed signal patterns and outputs.

    Returns:
        Sum of all decoded numbers.
    """
    return sum(decode_entry(patterns, outputs) for patterns, outputs in entries)

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
