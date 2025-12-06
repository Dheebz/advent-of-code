"""Monitoring Station -- Advent of Code 2019 Day 10."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple

Point = Tuple[int, int]


def parse_input(raw: str) -> Set[Point]:
    """Parse asteroid coordinates from the input.

    Args:
        raw (str): Raw puzzle input map.

    Returns:
        Set[Point]: Set of asteroid coordinates.
    """
    asteroids: Set[Point] = set()
    for y, line in enumerate(raw.strip().splitlines()):
        for x, char in enumerate(line.strip()):
            if char == "#":
                asteroids.add((x, y))
    return asteroids


def visible_from(origin: Point, asteroids: Set[Point]) -> int:
    """Count unique directions visible from the origin.

    Args:
        origin (Point): Monitoring station coordinate.
        asteroids (Set[Point]): All asteroid coordinates.

    Returns:
        int: Number of asteroids visible from origin.
    """
    ox, oy = origin
    seen = set()
    for ax, ay in asteroids:
        if (ax, ay) == origin:
            continue
        dx, dy = ax - ox, ay - oy
        g = math.gcd(dx, dy)
        seen.add((dx // g, dy // g))
    return len(seen)


def find_best_station(asteroids: Set[Point]) -> Tuple[Point, int]:
    """Find the asteroid with maximal visibility.

    Args:
        asteroids (Set[Point]): All asteroid coordinates.

    Returns:
        Tuple[Point, int]: Best coordinate and visible count.
    """
    best_point = (0, 0)
    best_count = 0
    for asteroid in asteroids:
        count = visible_from(asteroid, asteroids)
        if count > best_count:
            best_count = count
            best_point = asteroid
    return best_point, best_count


def solve_part_one(asteroids: Set[Point]) -> int:
    """Return visibility count for the optimal station."""
    _, count = find_best_station(asteroids)
    return count


def angle_from_up(dx: int, dy: int) -> float:
    """Compute clockwise angle from the upward direction.

    Args:
        dx (int): Delta x from station to asteroid.
        dy (int): Delta y from station to asteroid.

    Returns:
        float: Angle in radians, clockwise from up.
    """
    angle = math.atan2(dx, -dy)  # rotate so 0 is up, clockwise positive
    if angle < 0:
        angle += 2 * math.pi
    return angle


def solve_part_two(asteroids: Set[Point], target_vaporized: int = 200) -> int:
    """Simulate vaporization order and return the target asteroid code.

    Args:
        asteroids (Set[Point]): All asteroid coordinates.
        target_vaporized (int, optional): Target index (1-based). Defaults to 200.

    Returns:
        int: Encoded x * 100 + y of the target asteroid.
    """
    station, _ = find_best_station(asteroids)
    ox, oy = station
    remaining = asteroids - {station}

    # Map angle to list of asteroids sorted by distance.
    grouped: Dict[float, List[Tuple[float, Point]]] = {}
    for ax, ay in remaining:
        dx, dy = ax - ox, ay - oy
        angle = angle_from_up(dx, dy)
        distance = math.hypot(dx, dy)
        grouped.setdefault(angle, []).append((distance, (ax, ay)))

    for asteroids_at_angle in grouped.values():
        asteroids_at_angle.sort()

    angles = sorted(grouped.keys())
    vaporized_count = 0
    while True:
        for angle in angles:
            if not grouped[angle]:
                continue
            _, asteroid = grouped[angle].pop(0)
            vaporized_count += 1
            if vaporized_count == target_vaporized:
                x, y = asteroid
                return x * 100 + y
        if all(not group for group in grouped.values()):
            break
    raise ValueError("target vaporized asteroid not found")

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
