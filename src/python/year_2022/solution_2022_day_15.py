"""Beacon Exclusion Zone -- Advent of Code 2022 Day 15."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

Sensor = Tuple[int, int, int]  # x, y, distance to beacon


def parse_input(raw: str) -> Tuple[List[Sensor], set[Tuple[int, int]]]:
    """Return sensors with their manhattan radius and set of beacon positions."""
    sensors: List[Sensor] = []
    beacons: set[Tuple[int, int]] = set()
    for line in raw.strip().splitlines():
        parts = line.replace(",", "").replace(":", "").split()
        sx = int(parts[2].split("=")[1])
        sy = int(parts[3].split("=")[1])
        bx = int(parts[8].split("=")[1])
        by = int(parts[9].split("=")[1])
        dist = abs(sx - bx) + abs(sy - by)
        sensors.append((sx, sy, dist))
        beacons.add((bx, by))
    return sensors, beacons


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping intervals."""
    if not intervals:
        return []
    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + 1:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def covered_on_row(sensors: List[Sensor], row: int) -> List[Tuple[int, int]]:
    """Intervals of x covered on given row."""
    intervals: List[Tuple[int, int]] = []
    for sx, sy, dist in sensors:
        remaining = dist - abs(sy - row)
        if remaining < 0:
            continue
        intervals.append((sx - remaining, sx + remaining))
    return merge_intervals(intervals)


def solve_part_one(parsed: Tuple[List[Sensor], set[Tuple[int, int]]]) -> int:
    """Positions that cannot contain a beacon on target row."""
    sensors, beacons = parsed
    target_row = 2_000_000
    intervals = covered_on_row(sensors, target_row)
    blocked = sum(end - start + 1 for start, end in intervals)
    blocked -= sum(
        1
        for bx, by in beacons
        if by == target_row and any(start <= bx <= end for start, end in intervals)
    )
    return blocked


def solve_part_two(parsed: Tuple[List[Sensor], set[Tuple[int, int]]]) -> int:
    """Tuning frequency of distress beacon inside search space."""
    sensors, _ = parsed
    limit = 4_000_000
    for row in range(limit + 1):
        intervals: List[Tuple[int, int]] = []
        for sx, sy, dist in sensors:
            remaining = dist - abs(sy - row)
            if remaining < 0:
                continue
            start = max(0, sx - remaining)
            end = min(limit, sx + remaining)
            intervals.append((start, end))
        merged = merge_intervals(intervals)
        if len(merged) > 1:
            x = merged[0][1] + 1
            return x * 4_000_000 + row
    raise ValueError("Beacon not found")

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
