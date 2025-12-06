"""Beacon Scanner -- Advent of Code 2021 Day 19."""

from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple

Point = Tuple[int, int, int]
Scanner = List[Point]


def parse_input(raw: str) -> List[Scanner]:
    """
    Parse the beacon scanner inputs.

    Args:
        raw: Scanner blocks separated by blank lines.

    Returns:
        List of scanners, each with beacon coordinates.
    """
    scanners: List[Scanner] = []
    for block in raw.strip().split("\n\n"):
        lines = block.splitlines()[1:]  # skip header
        beacons: Scanner = []
        for line in lines:
            x, y, z = (int(value) for value in line.split(","))
            beacons.append((x, y, z))
        scanners.append(beacons)
    return scanners


def all_rotations(point: Point) -> List[Point]:
    """
    Generate all 24 rotations of a 3D point.

    Args:
        point: Original 3D point.

    Returns:
        List of rotated versions of the point.
    """
    x, y, z = point
    return [
        (x, y, z),
        (x, -y, -z),
        (x, z, -y),
        (x, -z, y),
        (-x, y, -z),
        (-x, -y, z),
        (-x, z, y),
        (-x, -z, -y),
        (y, x, -z),
        (y, -x, z),
        (y, z, x),
        (y, -z, -x),
        (-y, x, z),
        (-y, -x, -z),
        (-y, z, -x),
        (-y, -z, x),
        (z, x, y),
        (z, -x, -y),
        (z, y, -x),
        (z, -y, x),
        (-z, x, -y),
        (-z, -x, y),
        (-z, y, x),
        (-z, -y, -x),
    ]


ROTATION_CACHE: Dict[Point, List[Point]] = {}


def rotated(point: Point) -> List[Point]:
    """
    Return cached rotations for a point.

    Args:
        point: Coordinates to rotate.

    Returns:
        List of precomputed rotations.
    """
    if point not in ROTATION_CACHE:
        ROTATION_CACHE[point] = all_rotations(point)
    return ROTATION_CACHE[point]


def match_scanner(known: Set[Point], scanner: Scanner) -> Tuple[Point, Scanner] | None:
    """
    Try to align a scanner with an already placed set of beacons.

    Args:
        known: Beacons already placed in the master map.
        scanner: Scanner to align.

    Returns:
        Tuple of offset and aligned beacon list when a match is found, otherwise None.
    """
    rotated_scanners = list(zip(*[rotated(p) for p in scanner]))
    for variant in rotated_scanners:
        deltas: Dict[Point, int] = {}
        for beacon in variant:
            for ref in known:
                delta = (ref[0] - beacon[0], ref[1] - beacon[1], ref[2] - beacon[2])
                deltas[delta] = deltas.get(delta, 0) + 1
                if deltas[delta] >= 12:
                    aligned = [(b[0] + delta[0], b[1] + delta[1], b[2] + delta[2]) for b in variant]
                    return delta, aligned
    return None


def align_scanners(scanners: List[Scanner]) -> Tuple[Set[Point], List[Point]]:
    """
    Align all scanners and accumulate beacons/positions.

    Args:
        scanners: Input scanners to align.

    Returns:
        Tuple of all beacons and scanner positions.
    """
    placed = {tuple(b) for b in scanners[0]}
    scanner_positions: List[Point] = [(0, 0, 0)]
    remaining = scanners[1:]

    while remaining:
        next_remaining = []
        for scanner in remaining:
            match = match_scanner(placed, scanner)
            if match:
                offset, aligned = match
                scanner_positions.append(offset)
                placed.update(aligned)
            else:
                next_remaining.append(scanner)
        if len(next_remaining) == len(remaining):
            raise ValueError("could not align all scanners")
        remaining = next_remaining
    return placed, scanner_positions


def manhattan(a: Point, b: Point) -> int:
    """
    Compute the Manhattan distance between two points.

    Args:
        a: First point.
        b: Second point.

    Returns:
        Manhattan distance between the points.
    """
    return sum(abs(x - y) for x, y in zip(a, b))


def solve_part_one(scanners: List[Scanner]) -> int:
    """
    Count unique beacons after aligning all scanners.

    Args:
        scanners: Parsed scanner inputs.

    Returns:
        Total number of distinct beacons.
    """
    beacons, _ = align_scanners(scanners)
    return len(beacons)


def solve_part_two(scanners: List[Scanner]) -> int:
    """
    Find the largest Manhattan distance between any two scanners.

    Args:
        scanners: Parsed scanner inputs.

    Returns:
        Maximum Manhattan distance between scanner positions.
    """
    _, positions = align_scanners(scanners)
    return max(manhattan(a, b) for a, b in combinations(positions, 2))

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
