"""Advent of Code 2024 Day 12: Garden Groups."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

Grid = list[str]
Point = tuple[int, int]


def parse_input(raw: str) -> Grid:
    """
    Parse the garden grid into rows.

    Args:
        raw: Multi-line input describing the garden layout.

    Returns:
        List of row strings.
    """
    return raw.strip().splitlines()


def neighbors(r: int, c: int, rows: int, cols: int) -> Iterable[Point]:
    """
    Yield orthogonal neighbors within the grid bounds.

    Args:
        r: Current row index.
        c: Current column index.
        rows: Total number of rows.
        cols: Total number of columns.

    Yields:
        Neighbor coordinates (row, col) inside the grid.
    """
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


def flood_region(grid: Grid, start: Point, visited: set[Point]) -> set[Point]:
    """
    Flood-fill a region of matching characters starting at `start`.

    Args:
        grid: List of row strings.
        start: Starting coordinate for the flood.
        visited: Set tracking already visited coordinates.

    Returns:
        Set of coordinates belonging to the flood-filled region.
    """
    rows, cols = len(grid), len(grid[0])
    target = grid[start[0]][start[1]]
    region: set[Point] = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        r, c = queue.popleft()
        region.add((r, c))
        for nr, nc in neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] == target:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return region


def region_perimeter(region: set[Point], rows: int, cols: int) -> int:
    """
    Compute the perimeter of a region based on exposed edges.

    Args:
        region: Coordinates forming the region.
        rows: Number of rows in the grid.
        cols: Number of columns in the grid.

    Returns:
        Integer perimeter of the region.
    """
    perim = 0
    for r, c in region:
        for nr, nc in neighbors(r, c, rows, cols):
            if (nr, nc) not in region:
                perim += 1
        # edges at boundary of grid
        if r == 0:
            perim += 1
        if r == rows - 1:
            perim += 1
        if c == 0:
            perim += 1
        if c == cols - 1:
            perim += 1
    return perim


def region_sides(region: set[Point]) -> int:
    """
    Count the number of side segments along a region boundary.

    Args:
        region: Coordinates belonging to a single region.

    Returns:
        Number of distinct horizontal and vertical segments around the region.
    """
    horiz: defaultdict[int, list[int]] = defaultdict(list)
    vert: defaultdict[int, list[int]] = defaultdict(list)

    for r, c in region:
        # top edge
        if (r - 1, c) not in region:
            horiz[r].append(c)
        # bottom edge
        if (r + 1, c) not in region:
            horiz[r + 1].append(c)
        # left edge
        if (r, c - 1) not in region:
            vert[c].append(r)
        # right edge
        if (r, c + 1) not in region:
            vert[c + 1].append(r)

    def count_segments(lines: dict[int, list[int]]) -> int:
        """
        Count contiguous horizontal or vertical segments.

        Args:
            lines: Map from coordinate to list of line positions.

        Returns:
            Number of continuous segments in `lines`.
        """
        total = 0
        for positions in lines.values():
            positions.sort()
            if not positions:
                continue
            segments = 1
            for a, b in zip(positions, positions[1:]):
                if b != a + 1:
                    segments += 1
            total += segments
        return total

    return count_segments(horiz) + count_segments(vert)


def solve(grid: Grid) -> tuple[int, int]:
    """
    Compute both puzzle parts from the grid.

    Args:
        grid: Parsed garden grid.

    Returns:
        Tuple containing part1 and part2 results.
    """
    rows, cols = len(grid), len(grid[0])
    visited: set[Point] = set()
    part1 = 0
    part2 = 0
    for r in range(rows):
        for c in range(cols):
            if (r, c) in visited:
                continue
            region = flood_region(grid, (r, c), visited)
            area = len(region)
            perim = region_perimeter(region, rows, cols)
            sides = region_sides(region)
            part1 += area * perim
            part2 += area * sides
    return part1, part2


def solve_part_one(grid: Grid) -> int:
    """
    Compute part one result (total area times perimeter).

    Args:
        grid: Parsed garden grid.

    Returns:
        Summed area-perimeter product of each region.
    """
    part1, _ = solve(grid)
    return part1


def solve_part_two(grid: Grid) -> int:
    """
    Compute part two result (total area times region sides).

    Args:
        grid: Parsed garden grid.

    Returns:
        Summed area-side product of each region.
    """
    _, part2 = solve(grid)
    return part2

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
