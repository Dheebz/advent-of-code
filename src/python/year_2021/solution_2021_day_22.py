"""Reactor Reboot -- Advent of Code 2021 Day 22."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Tuple

Cube = Tuple[int, int, int, int, int, int]  # x1, x2, y1, y2, z1, z2 inclusive
Step = Tuple[bool, Cube]


def parse_input(raw: str) -> List[Step]:
    """
    Parse reboot steps into structured cube operations.

    Args:
        raw: Lines describing ``on/off`` steps with ranges.

    Returns:
        List of tuples containing the boolean action and cube bounds.
    """
    steps: List[Step] = []
    for line in raw.strip().splitlines():
        status, rest = line.split()
        on = status == "on"
        coords = []
        for part in rest.split(","):
            start, end = part[2:].split("..")
            coords.append((int(start), int(end)))
        cube = (coords[0][0], coords[0][1], coords[1][0], coords[1][1], coords[2][0], coords[2][1])
        steps.append((on, cube))
    return steps


def intersect(a: Cube, b: Cube) -> Optional[Cube]:
    """
    Compute the intersection of two axis-aligned cubes.

    Args:
        a: First cube.
        b: Second cube.

    Returns:
        Intersection cube if cubes overlap, otherwise None.
    """
    x1 = max(a[0], b[0])
    x2 = min(a[1], b[1])
    y1 = max(a[2], b[2])
    y2 = min(a[3], b[3])
    z1 = max(a[4], b[4])
    z2 = min(a[5], b[5])
    if x1 <= x2 and y1 <= y2 and z1 <= z2:
        return (x1, x2, y1, y2, z1, z2)
    return None


def volume(cube: Cube) -> int:
    """
    Compute the volume of an axis-aligned cube.

    Args:
        cube: Cube bounds.

    Returns:
        Integer volume of the cube.
    """
    return (cube[1] - cube[0] + 1) * (cube[3] - cube[2] + 1) * (cube[5] - cube[4] + 1)


def reboot(steps: List[Step]) -> int:
    """
    Apply a sequence of reboot steps using inclusion-exclusion.

    Args:
        steps: List of ``(on, cube)`` actions.

    Returns:
        Total number of cubes that are on after all steps.
    """
    cubes: List[Tuple[Cube, int]] = []  # cube with sign
    for on, cube in steps:
        updates: List[Tuple[Cube, int]] = []
        for existing, sign in cubes:
            inter = intersect(existing, cube)
            if inter:
                updates.append((inter, -sign))
        if on:
            updates.append((cube, 1))
        cubes.extend(updates)
    return sum(volume(c) * sign for c, sign in cubes)


def limit_steps(steps: List[Step], bound: int = 50) -> List[Step]:
    """
    Restrict steps to the initialization region.

    Args:
        steps: All reboot steps.
        bound: Distance bounds for x, y, and z.

    Returns:
        Filtered list of steps whose cubes intersect the bound.
    """
    limited = []
    for on, cube in steps:
        x1, x2, y1, y2, z1, z2 = cube
        if x1 > bound or x2 < -bound or y1 > bound or y2 < -bound or z1 > bound or z2 < -bound:
            continue
        x1 = max(x1, -bound)
        x2 = min(x2, bound)
        y1 = max(y1, -bound)
        y2 = min(y2, bound)
        z1 = max(z1, -bound)
        z2 = min(z2, bound)
        limited.append((on, (x1, x2, y1, y2, z1, z2)))
    return limited


def solve_part_one(steps: List[Step]) -> int:
    """
    Count cubes turned on within the initialization region.

    Args:
        steps: All reboot steps.

    Returns:
        Number of lit cubes after applying the initialization steps.
    """
    return reboot(limit_steps(steps))


def solve_part_two(steps: List[Step]) -> int:
    """
    Count cubes turned on after applying all reboot steps.

    Args:
        steps: All reboot steps.

    Returns:
        Number of lit cubes after executing every step.
    """
    return reboot(steps)

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
