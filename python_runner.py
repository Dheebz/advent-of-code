"""CLI runner for Advent of Code solution modules."""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Iterable, Optional

# Root folder of the repo (this file lives at the top level)
REPO_ROOT = Path(__file__).resolve().parent

# Where your Python source lives
SRC_ROOT = REPO_ROOT / "src" / "python"

# Where canonical inputs live now
INPUT_ROOT = REPO_ROOT / "__inputs__"

# Max days per year (default 25, but 2025 only has 12)
DEFAULT_MAX_DAYS = 25
MAX_DAYS_PER_YEAR: dict[int, int] = {
    2025: 12,
    # everything else falls back to DEFAULT_MAX_DAYS
}


def max_days_for_year(year: int) -> int:
    """Return the number of days available for a given year."""
    return MAX_DAYS_PER_YEAR.get(year, DEFAULT_MAX_DAYS)


def iter_days_to_run(year: int, day: Optional[int]) -> Iterable[int]:
    """Yield days to run for the given year.

    If `day` is provided, just that day. Otherwise, all days from 1 to the year's max.
    """
    if day is not None:
        yield day
    else:
        for d in range(1, max_days_for_year(year) + 1):
            yield d


def main(argv: Optional[list[str]] = None) -> int:
    """Parse CLI arguments and run the requested parts.

    Mandatory arguments:
        --year: Year of the Advent of Code event.

    Optional arguments:
        --day: Day of the Advent of Code event. When omitted, runs all days in the year.
        --part: Run only a single part (1 or 2). When omitted, both parts run.
        --input: Path to the puzzle input file. Defaults to the day's input under
            __inputs__/year_YYYY/input_YYYY_day_DD.txt.
    """
    parser = argparse.ArgumentParser(description="Run Advent of Code solutions.")
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year of the Advent of Code event (e.g. 2015, 2025).",
    )
    parser.add_argument(
        "--day",
        type=int,
        help=(
            "Day of the Advent of Code event. When omitted, runs all days in the year. "
            "Range depends on the year (most years 1–25, 2025 is 1–12)."
        ),
    )
    parser.add_argument(
        "--part",
        type=int,
        choices=[1, 2],
        help="Run only a single part (1 or 2). When omitted, both parts run.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help=(
            "Path to the puzzle input file. Defaults to the day's input in "
            "__inputs__/year_YYYY/input_YYYY_day_DD.txt"
        ),
    )

    args = parser.parse_args(argv)

    year: int = args.year
    day: Optional[int] = args.day
    part: Optional[int] = args.part
    input_path_override: Optional[Path] = args.input

    # Validate day against max days for the year if provided
    max_days = max_days_for_year(year)
    if day is not None and not (1 <= day <= max_days):
        parser.error(f"Year {year} only has days 1–{max_days}, but you requested day {day}.")

    # Ensure src/python is on sys.path (for running directly from repo)
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    results = []

    for d in iter_days_to_run(year, day):
        # Module path: year_YYYY.solution_YYYY_day_DD
        package_name = f"year_{year}"
        module_name = f"solution_{year}_day_{d:02d}"
        full_module_name = f"{package_name}.{module_name}"

        try:
            module = importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            print(
                f"[WARN] Solution module for Year {year} Day {d:02d} "
                f"({full_module_name}) not found.",
                file=sys.stderr,
            )
            continue

        # Decide which input path to use for THIS day
        if input_path_override is not None:
            input_path = input_path_override
        else:
            # __inputs__/year_YYYY/input_YYYY_day_DD.txt
            input_path = INPUT_ROOT / f"year_{year}" / f"input_{year}_day_{d:02d}.txt"

        try:
            raw_input = input_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"[WARN] Input file for Year {year} Day {d:02d} not found: {input_path}",
                file=sys.stderr,
            )
            continue

        # Parse once, then materialise so both parts can reuse it
        try:
            parsed = module.parse_input(raw_input)
        except AttributeError as exc:
            print(
                f"[ERROR] Module {full_module_name} is missing parse_input(): {exc}",
                file=sys.stderr,
            )
            continue

        # Materialise into a list so it can be iterated multiple times if needed
        if isinstance(parsed, Mapping):
            instructions = parsed
        elif isinstance(parsed, Iterator):
            instructions = list(parsed)
        else:
            instructions = parsed

        if part in (None, 1):
            try:
                part_one_result = module.solve_part_one(instructions)
            except AttributeError as exc:
                print(
                    f"[ERROR] Module {full_module_name} is missing solve_part_one(): {exc}",
                    file=sys.stderr,
                )
            else:
                results.append((year, d, 1, part_one_result))
                print(f"Year {year} Day {d:02d} Part 1: {part_one_result}")

        if part in (None, 2):
            try:
                part_two_result = module.solve_part_two(instructions)
            except AttributeError as exc:
                print(
                    f"[ERROR] Module {full_module_name} is missing solve_part_two(): {exc}",
                    file=sys.stderr,
                )
            else:
                results.append((year, d, 2, part_two_result))
                print(f"Year {year} Day {d:02d} Part 2: {part_two_result}")

    # Non-zero exit if we never ran anything successfully
    if not results:
        print(
            "[INFO] No solutions were run. Check year/day, modules, and input files.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
