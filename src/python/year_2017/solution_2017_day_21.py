"""Fractal Art -- Advent of Code 2017 Day 21."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

Grid = List[str]


def rotate(grid: Grid) -> Grid:
    """Rotate a square grid 90 degrees clockwise."""
    size = len(grid)
    return ["".join(grid[size - j - 1][i] for j in range(size)) for i in range(size)]


def flip(grid: Grid) -> Grid:
    """Flip a grid horizontally."""
    return [row[::-1] for row in grid]


def all_variants(grid: Grid) -> List[Grid]:
    """Generate all unique rotations and flips of a grid."""
    variants = []
    current = grid
    for _ in range(4):
        variants.append(current)
        variants.append(flip(current))
        current = rotate(current)
    # remove duplicates
    unique = []
    seen = set()
    for var in variants:
        key = tuple(var)
        if key not in seen:
            seen.add(key)
            unique.append(var)
    return unique


def parse_input(raw: str) -> Dict[tuple[str, ...], Grid]:
    """Return mapping from input pattern variants to output grid."""
    rules: Dict[tuple[str, ...], Grid] = {}
    for line in raw.strip().splitlines():
        left, right = line.split(" => ")
        input_grid = left.split("/")
        output_grid = right.split("/")
        for variant in all_variants(input_grid):
            rules[tuple(variant)] = output_grid
    return rules


def split_grid(grid: Grid) -> List[Grid]:
    """Split a grid into 2x2 or 3x3 blocks depending on size."""
    size = len(grid)
    block_size = 2 if size % 2 == 0 else 3
    blocks = []
    for y in range(0, size, block_size):
        for x in range(0, size, block_size):
            block = [grid[y + dy][x : x + block_size] for dy in range(block_size)]
            blocks.append(block)
    return blocks


def join_blocks(blocks: List[Grid]) -> Grid:
    """Reassemble blocks back into a single grid."""
    block_size = len(blocks[0])
    blocks_per_row = int(len(blocks) ** 0.5)
    rows: List[str] = []
    for row_block in range(blocks_per_row):
        for line_idx in range(block_size):
            row = ""
            for col_block in range(blocks_per_row):
                row += blocks[row_block * blocks_per_row + col_block][line_idx]
            rows.append(row)
    return rows


def enhance(grid: Grid, rules: Dict[tuple[str, ...], Grid]) -> Grid:
    """Enhance a grid by applying the transformation rules to each block."""
    blocks = split_grid(grid)
    enhanced = []
    for block in blocks:
        enhanced.append(rules[tuple(block)])
    return join_blocks(enhanced)


def run_iterations(rules: Dict[tuple[str, ...], Grid], iterations: int) -> Grid:
    """Run enhancement for a number of iterations starting from the seed grid."""
    grid = [".#.", "..#", "###"]
    for _ in range(iterations):
        grid = enhance(grid, rules)
    return grid


def solve_part_one(rules: Dict[tuple[str, ...], Grid]) -> int:
    """Pixels on after 5 iterations."""
    grid = run_iterations(rules, 5)
    return sum(row.count("#") for row in grid)


def solve_part_two(rules: Dict[tuple[str, ...], Grid]) -> int:
    """Pixels on after 18 iterations."""
    grid = run_iterations(rules, 18)
    return sum(row.count("#") for row in grid)

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
