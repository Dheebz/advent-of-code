"""Planet of Discord -- Advent of Code 2019 Day 24."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Set, Tuple

Point = Tuple[int, int]


def parse_input(raw: str) -> Set[Point]:
    """Parse bug positions from the input grid.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        Set[Point]: Set of bug coordinates.
    """
    bugs = set()
    for y, line in enumerate(raw.strip().splitlines()):
        for x, ch in enumerate(line.strip()):
            if ch == "#":
                bugs.add((x, y))
    return bugs


def biodiversity(bugs: Set[Point]) -> int:
    """Compute biodiversity rating for a grid state.

    Args:
        bugs (Set[Point]): Coordinates with bugs.

    Returns:
        int: Biodiversity rating.
    """
    rating = 0
    for y in range(5):
        for x in range(5):
            idx = y * 5 + x
            if (x, y) in bugs:
                rating += 1 << idx
    return rating


def neighbors(point: Point) -> Set[Point]:
    """Return orthogonal neighbors of a point."""
    x, y = point
    return {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}


def step(bugs: Set[Point]) -> Set[Point]:
    """Advance one minute in the single-layer automaton.

    Args:
        bugs (Set[Point]): Current bug positions.

    Returns:
        Set[Point]: Updated bug positions.
    """
    new_bugs: Set[Point] = set()
    for y in range(5):
        for x in range(5):
            point = (x, y)
            adj = sum((n in bugs) for n in neighbors(point) if 0 <= n[0] < 5 and 0 <= n[1] < 5)
            if point in bugs:
                if adj == 1:
                    new_bugs.add(point)
            else:
                if adj in (1, 2):
                    new_bugs.add(point)
    return new_bugs


def solve_part_one(initial: Set[Point]) -> int:
    """Find the first repeated biodiversity rating."""
    seen = set()
    bugs = initial
    while True:
        rating = biodiversity(bugs)
        if rating in seen:
            return rating
        seen.add(rating)
        bugs = step(bugs)


def recursive_neighbors(x: int, y: int, level: int) -> Set[Tuple[int, int, int]]:
    """Return neighbors across recursive grid levels."""
    results = set()
    if x == 2 and y == 2:
        return results
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if nx == 2 and ny == 2:
            # into inner level
            if x == 1:
                results.update({(0, iy, level + 1) for iy in range(5)})
            elif x == 3:
                results.update({(4, iy, level + 1) for iy in range(5)})
            elif y == 1:
                results.update({(ix, 0, level + 1) for ix in range(5)})
            elif y == 3:
                results.update({(ix, 4, level + 1) for ix in range(5)})
        elif nx < 0:
            results.add((1, 2, level - 1))
        elif nx > 4:
            results.add((3, 2, level - 1))
        elif ny < 0:
            results.add((2, 1, level - 1))
        elif ny > 4:
            results.add((2, 3, level - 1))
        else:
            results.add((nx, ny, level))
    return results


def step_recursive(bugs: Dict[int, Set[Point]]) -> Dict[int, Set[Point]]:
    """Advance one minute in the recursive automaton."""
    new_bugs: Dict[int, Set[Point]] = {}
    levels = range(min(bugs.keys()) - 1, max(bugs.keys()) + 2)
    for level in levels:
        current: Set[Point] = set()
        for y in range(5):
            for x in range(5):
                if (x, y) == (2, 2):
                    continue
                adj = 0
                for nx, ny, nl in recursive_neighbors(x, y, level):
                    if nl in bugs and (nx, ny) in bugs[nl]:
                        adj += 1
                occupied = level in bugs and (x, y) in bugs[level]
                if occupied and adj == 1:
                    current.add((x, y))
                if not occupied and adj in (1, 2):
                    current.add((x, y))
        if current:
            new_bugs[level] = current
    return new_bugs


def solve_part_two(initial: Set[Point], minutes: int = 200) -> int:
    """Simulate recursive grids and count bugs after the given time."""
    bugs: Dict[int, Set[Point]] = {0: {p for p in initial if p != (2, 2)}}
    for _ in range(minutes):
        bugs = step_recursive(bugs)
    return sum(len(level_bugs) for level_bugs in bugs.values())

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
