"""Advent of Code 2024 Day 14: Restroom Redoubt."""

from __future__ import annotations

import argparse
from pathlib import Path

Robot = tuple[int, int, int, int]

WIDTH = 101
HEIGHT = 103


def parse_input(raw: str) -> list[Robot]:
    """
    Parse the robot initial positions and velocities.

    Args:
        raw: Lines like ``position=<x,y> velocity=<dx,dy>``.

    Returns:
        List of tuples (x, y, dx, dy).
    """
    robots: list[Robot] = []
    for line in raw.strip().splitlines():
        pos_part, vel_part = line.split()
        x, y = [int(v) for v in pos_part.split("=")[1].split(",")]
        dx, dy = [int(v) for v in vel_part.split("=")[1].split(",")]
        robots.append((x, y, dx, dy))
    return robots


def simulate(robots: list[Robot], seconds: int) -> list[tuple[int, int]]:
    """
    Compute positions after a number of seconds with wraparound.

    Args:
        robots: List of (x, y, dx, dy) tuples.
        seconds: Number of seconds to simulate.

    Returns:
        List of (x, y) coordinates after time `seconds`.
    """
    positions: list[tuple[int, int]] = []
    for x, y, dx, dy in robots:
        nx = (x + dx * seconds) % WIDTH
        ny = (y + dy * seconds) % HEIGHT
        positions.append((nx, ny))
    return positions


def solve_part_one(robots: list[Robot]) -> int:
    """
    Compute the product of quadrant counts after 100 seconds.

    Args:
        robots: Parsed robot data.

    Returns:
        Product of counts of robots in each quadrant relative to center.
    """
    positions = simulate(robots, 100)
    mid_x = WIDTH // 2
    mid_y = HEIGHT // 2
    q = [0, 0, 0, 0]
    for x, y in positions:
        if x == mid_x or y == mid_y:
            continue
        idx = (y > mid_y) * 2 + (x > mid_x)
        q[idx] += 1
    return q[0] * q[1] * q[2] * q[3]


def bounding_area(positions: list[tuple[int, int]]) -> int:
    """
    Compute the bounding box area for the given positions.

    Args:
        positions: List of (x, y) coordinates.

    Returns:
        Area of the smallest axis-aligned rectangle enclosing all points.
    """
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    return (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)


def solve_part_two(robots: list[Robot]) -> int:
    """
    Find the time that minimizes the bounding box area.

    Args:
        robots: Parsed robot data.

    Returns:
        Number of seconds needed to achieve the smallest bounding area.
    """
    best_time = 0
    best_area = float("inf")
    period = WIDTH * HEIGHT  # positions repeat after this many seconds
    for t in range(period):
        positions = simulate(robots, t)
        area = bounding_area(positions)
        if area < best_area:
            best_area = area
            best_time = t
    return best_time

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
