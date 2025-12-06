"""Conway Cubes -- Advent of Code 2020 Day 17."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Set, Tuple

Point3 = Tuple[int, int, int]
Point4 = Tuple[int, int, int, int]


def parse_input(raw: str) -> Set[Point3]:
    """Return active cubes in 3D starting layer."""
    active: Set[Point3] = set()
    for y, line in enumerate(raw.strip().splitlines()):
        for x, char in enumerate(line.strip()):
            if char == "#":
                active.add((x, y, 0))
    return active


def neighbors_3d(point: Point3) -> List[Point3]:
    """
    Generate all 3D neighbors for a given point.

    Args:
        point: Current 3D coordinate.

    Returns:
        List of coordinates one step away from the point.
    """
    x, y, z = point
    return [
        (x + dx, y + dy, z + dz)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        for dz in (-1, 0, 1)
        if not (dx == dy == dz == 0)
    ]


def neighbors_4d(point: Point4) -> List[Point4]:
    """
    Generate all 4D neighbors for a given point.

    Args:
        point: Current 4D coordinate.

    Returns:
        List of coordinates one step away in four dimensions.
    """
    x, y, z, w = point
    return [
        (x + dx, y + dy, z + dz, w + dw)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        for dz in (-1, 0, 1)
        for dw in (-1, 0, 1)
        if not (dx == dy == dz == dw == 0)
    ]


def cycle_3d(active: Set[Point3]) -> Set[Point3]:
    """
    Perform a single boot cycle in 3D.

    Args:
        active: Currently active cubes.

    Returns:
        Updated set of active cubes after one cycle.
    """
    new_active: Set[Point3] = set()
    candidates = set(active)
    for point in active:
        candidates.update(neighbors_3d(point))
    for point in candidates:
        count = sum((neighbor in active) for neighbor in neighbors_3d(point))
        if point in active and count in (2, 3):
            new_active.add(point)
        if point not in active and count == 3:
            new_active.add(point)
    return new_active


def cycle_4d(active: Set[Point4]) -> Set[Point4]:
    """
    Perform a single boot cycle in 4D.

    Args:
        active: Currently active cubes.

    Returns:
        Updated set of active cubes after one cycle.
    """
    new_active: Set[Point4] = set()
    candidates = set(active)
    for point in active:
        candidates.update(neighbors_4d(point))
    for point in candidates:
        count = sum((neighbor in active) for neighbor in neighbors_4d(point))
        if point in active and count in (2, 3):
            new_active.add(point)
        if point not in active and count == 3:
            new_active.add(point)
    return new_active


def solve_part_one(start: Set[Point3]) -> int:
    """
    Return the number of active cubes after six 3D cycles.

    Args:
        start: Initial set of active cubes in the x-y plane.

    Returns:
        Count of active cubes after six iterations.
    """
    active = start
    for _ in range(6):
        active = cycle_3d(active)
    return len(active)


def solve_part_two(start: Set[Point3]) -> int:
    """
    Return the number of active cubes after six 4D cycles.

    Args:
        start: Initial set of active cubes in the x-y plane.

    Returns:
        Count of active cubes after extending into four dimensions and running six cycles.
    """
    active4: Set[Point4] = {(x, y, z, 0) for x, y, z in start}
    for _ in range(6):
        active4 = cycle_4d(active4)
    return len(active4)

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
