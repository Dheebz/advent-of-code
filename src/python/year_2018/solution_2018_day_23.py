"""Experimental Emergency Teleportation -- Advent of Code 2018 Day 23."""

from __future__ import annotations

import argparse
import heapq
import re
from pathlib import Path
from typing import List, Tuple

Bot = Tuple[int, int, int, int]  # x, y, z, r


def parse_input(raw: str) -> List[Bot]:
    """Return list of bots (x, y, z, radius)."""
    bots: List[Bot] = []
    for line in raw.strip().splitlines():
        nums = [int(x) for x in re.findall(r"-?\d+", line)]
        bots.append((nums[0], nums[1], nums[2], nums[3]))
    return bots


def manhattan(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    """Compute Manhattan distance in 3D."""
    return sum(abs(a[i] - b[i]) for i in range(3))


def solve_part_one(bots: List[Bot]) -> int:
    """Bots in range of the strongest bot (largest radius)."""
    strongest = max(bots, key=lambda b: b[3])
    sx, sy, sz, sr = strongest
    return sum(1 for x, y, z, _ in bots if manhattan((sx, sy, sz), (x, y, z)) <= sr)


def solve_part_two(bots: List[Bot]) -> int:
    """
    Distance from origin to the point in range of the most bots (closest if tie).

    Uses a best-first search over cubes; prunes cubes that no bots can reach,
    and stops when no remaining cube can beat the current best.
    """
    # Bounding box around all bots
    min_x = min(x for x, _, _, _ in bots)
    max_x = max(x for x, _, _, _ in bots)
    min_y = min(y for _, y, _, _ in bots)
    max_y = max(y for _, y, _, _ in bots)
    min_z = min(z for _, _, z, _ in bots)
    max_z = max(z for _, _, z, _ in bots)

    # Side length of starting cube: power of two covering the entire bounding box
    span_x = max_x - min_x
    span_y = max_y - min_y
    span_z = max_z - min_z
    size = 1
    max_span = max(span_x, span_y, span_z)
    while size <= max_span:
        size *= 2

    Cube = Tuple[int, int, int, int]  # minx, miny, minz, size

    def bots_in_cube(cube: Cube) -> int:
        """How many bots intersect this axis-aligned cube (Manhattan distance)."""
        minx, miny, minz, sz = cube
        maxx = minx + sz - 1
        maxy = miny + sz - 1
        maxz = minz + sz - 1

        count = 0
        for bx, by, bz, r in bots:
            dx = 0
            if bx < minx:
                dx = minx - bx
            elif bx > maxx:
                dx = bx - maxx

            dy = 0
            if by < miny:
                dy = miny - by
            elif by > maxy:
                dy = by - maxy

            dz = 0
            if bz < minz:
                dz = minz - bz
            elif bz > maxz:
                dz = bz - maxz

            if dx + dy + dz <= r:
                count += 1
        return count

    def dist_from_origin_to_cube(cube: Cube) -> int:
        """Minimum Manhattan distance from (0, 0, 0) to any point in the cube."""
        minx, miny, minz, sz = cube
        maxx = minx + sz - 1
        maxy = miny + sz - 1
        maxz = minz + sz - 1

        def axis_dist(lo: int, hi: int) -> int:
            if lo <= 0 <= hi:
                return 0
            if hi < 0:
                return -hi
            return lo  # lo > 0

        return axis_dist(minx, maxx) + axis_dist(miny, maxy) + axis_dist(minz, maxz)

    # Initial cube covering all bots
    initial_cube: Cube = (min_x, min_y, min_z, size)
    initial_count = bots_in_cube(initial_cube)
    initial_dist = dist_from_origin_to_cube(initial_cube)

    # Heap entries: (-bot_count, distance_from_origin, size, cube)
    heap: List[Tuple[int, int, int, Cube]] = []
    heapq.heappush(heap, (-initial_count, initial_dist, size, initial_cube))

    best_count = 0
    best_distance = 0

    while heap:
        neg_count, cube_dist, sz, cube = heapq.heappop(heap)
        count = -neg_count

        # If this cube can't beat the current best, no later cube can either
        if count < best_count:
            break

        minx, miny, minz, sz = cube

        if sz == 1:
            # Single point: candidate solution
            distance = manhattan((minx, miny, minz), (0, 0, 0))
            if count > best_count or (count == best_count and distance < best_distance):
                best_count = count
                best_distance = distance
            continue

        # Subdivide into 8 subcubes
        half = sz // 2
        for dx in (0, half):
            for dy in (0, half):
                for dz in (0, half):
                    sub_cube: Cube = (minx + dx, miny + dy, minz + dz, half)
                    c = bots_in_cube(sub_cube)
                    if c == 0:
                        # No bots can reach this cube, ignore it.
                        continue
                    d = dist_from_origin_to_cube(sub_cube)
                    heapq.heappush(heap, (-c, d, half, sub_cube))

    return best_distance

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
