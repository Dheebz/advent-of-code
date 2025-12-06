"""Regolith Reservoir -- Advent of Code 2022 Day 14."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Set, Tuple

Point = Tuple[int, int]


def parse_input(raw: str) -> Set[Point]:
    """
    Extract rock coordinates from the wall drawing.

    Args:
        raw: Input lines describing rock segments.

    Returns:
        Set of rock coordinates that block sand.
    """
    rocks: Set[Point] = set()
    for line in raw.strip().splitlines():
        points = []
        for part in line.split(" -> "):
            x_str, y_str = part.split(",")
            points.append((int(x_str), int(y_str)))
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if x1 == x2:
                step = 1 if y2 > y1 else -1
                for y in range(y1, y2 + step, step):
                    rocks.add((x1, y))
            else:
                step = 1 if x2 > x1 else -1
                for x in range(x1, x2 + step, step):
                    rocks.add((x, y1))
    return rocks


def drop_sand(rocks: Set[Point], floor: int | None) -> int:
    """
    Simulate sand falling through the cavern until it either falls off or reaches the floor.

    Args:
        rocks: Set of coordinates already occupied by rock.
        floor: Y level of the artificial floor, or None for no floor.

    Returns:
        Number of sand grains that come to rest.
    """
    occupied = set(rocks)
    max_y = max(y for _, y in rocks)
    count = 0
    source = (500, 0)

    while True:
        if source in occupied:
            break
        x, y = source
        while True:
            if floor is None and y > max_y:
                return count
            if floor is not None and y + 1 == floor:
                occupied.add((x, y))
                count += 1
                break
            if (x, y + 1) not in occupied:
                y += 1
                continue
            if (x - 1, y + 1) not in occupied:
                x -= 1
                y += 1
                continue
            if (x + 1, y + 1) not in occupied:
                x += 1
                y += 1
                continue
            occupied.add((x, y))
            count += 1
            break
    return count


def solve_part_one(rocks: Iterable[Point]) -> int:
    """
    Count how much sand settles before anything falls into the void.

    Args:
        rocks: Iterable of initial rock positions.

    Returns:
        Number of grains that come to rest before one falls off the pit.
    """
    return drop_sand(set(rocks), floor=None)


def solve_part_two(rocks: Iterable[Point]) -> int:
    """
    Count how much sand settles once a floor is added.

    Args:
        rocks: Iterable of initial rock positions.

    Returns:
        Number of grains that come to rest until the source is blocked.
    """
    max_y = max(y for _, y in rocks)
    return drop_sand(set(rocks), floor=max_y + 2)

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
