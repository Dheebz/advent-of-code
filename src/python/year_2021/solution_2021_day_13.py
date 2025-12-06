"""Transparent Origami -- Advent of Code 2021 Day 13."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Set, Tuple

Point = Tuple[int, int]
Fold = Tuple[str, int]


def parse_input(raw: str) -> Tuple[Set[Point], List[Fold]]:
    """
    Parse the grid points and fold instructions from the input.

    Args:
        raw: Puzzle text with dots and fold lines separated by a blank line.

    Returns:
        Tuple of dot coordinates and fold instructions.
    """
    dots_part, folds_part = raw.strip().split("\n\n")
    dots: Set[Point] = set()
    for line in dots_part.splitlines():
        x_str, y_str = line.split(",")
        dots.add((int(x_str), int(y_str)))
    folds: List[Fold] = []
    for line in folds_part.splitlines():
        axis, value = line.split("=")
        folds.append((axis[-1], int(value)))
    return dots, folds


def apply_fold(dots: Set[Point], fold: Fold) -> Set[Point]:
    """
    Apply a single fold instruction to the set of dots.

    Args:
        dots: Current set of dot coordinates.
        fold: Fold instruction as (axis, value).

    Returns:
        Updated set of dot coordinates after applying the fold.
    """
    axis, value = fold
    new_dots: Set[Point] = set()
    for x, y in dots:
        if axis == "x" and x > value:
            x = value - (x - value)
        elif axis == "y" and y > value:
            y = value - (y - value)
        new_dots.add((x, y))
    return new_dots


def solve_part_one(data: Tuple[Set[Point], List[Fold]]) -> int:
    """
    Count visible dots after the first fold.

    Args:
        data: Parsed dots and fold instructions.

    Returns:
        Number of dots visible after the first fold.
    """
    dots, folds = data
    folded = apply_fold(dots, folds[0])
    return len(folded)


def render(dots: Set[Point]) -> str:
    """
    Render the dots as lines of text.

    Args:
        dots: Set of coordinates to draw.

    Returns:
        Multiline string representing the grid.
    """
    max_x = max(x for x, _ in dots)
    max_y = max(y for _, y in dots)
    rows = []
    for y in range(max_y + 1):
        row = []
        for x in range(max_x + 1):
            row.append("#" if (x, y) in dots else ".")
        rows.append("".join(row))
    return "\n".join(rows)


def solve_part_two(data: Tuple[Set[Point], List[Fold]]) -> str:
    """
    Return the registration code rendered after completing all folds.

    Args:
        data: Parsed dots and fold instructions.

    Returns:
        Decoded registration message.
    """
    dots, folds = data
    for fold in folds:
        dots = apply_fold(dots, fold)
    return decode_message(render(dots))


# OCR for the common 5x6 block font used in AoC (upper-case letters)
CHAR_MAP = {
    (".##..", "#..#.", "#..#.", "####.", "#..#.", "#..#."): "A",
    ("###..", "#..#.", "###..", "#..#.", "#..#.", "###.."): "B",
    (".##..", "#..#.", "#....", "#....", "#..#.", ".##.."): "C",
    ("###..", "#..#.", "#..#.", "#..#.", "#..#.", "###.."): "D",
    ("####.", "#....", "###..", "#....", "#....", "####."): "E",
    ("####.", "#....", "###..", "#....", "#....", "#...."): "F",
    (".##..", "#..#.", "#....", "#.##.", "#..#.", ".###."): "G",
    ("#..#.", "#..#.", "####.", "#..#.", "#..#.", "#..#."): "H",
    ("###..", ".#...", ".#...", ".#...", ".#...", "###.."): "I",
    ("..##.", "...#.", "...#.", "...#.", "#..#.", ".##.."): "J",
    ("#..#.", "#.#..", "##...", "#.#..", "#.#..", "#..#."): "K",
    ("#....", "#....", "#....", "#....", "#....", "####."): "L",
    ("#..#.", "##.##", "#.#.#", "#..#.", "#..#.", "#..#."): "M",
    ("#..#.", "##.#.", "#.#.#", "#..##", "#..#.", "#..#."): "N",
    (".##..", "#..#.", "#..#.", "#..#.", "#..#.", ".##.."): "O",
    ("###..", "#..#.", "#..#.", "###..", "#....", "#...."): "P",
    (".##..", "#..#.", "#..#.", "#..#.", "#.##.", ".###."): "Q",
    ("###..", "#..#.", "#..#.", "###..", "#.#..", "#..#."): "R",
    (".###.", "#....", "#....", ".##..", "...#.", "###.."): "S",
    ("####.", "..#..", "..#..", "..#..", "..#..", "..#.."): "T",
    ("#..#.", "#..#.", "#..#.", "#..#.", "#..#.", ".##.."): "U",
    ("#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."): "V",
    ("#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"): "W",
    ("#..#.", "#..#.", ".##..", ".##..", "#..#.", "#..#."): "X",
    ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."): "Y",
    ("####.", "...#.", "..#..", ".#...", "#....", "####."): "Z",
}


def decode_message(grid: str, width: int = 5) -> str:
    """
    Decode a rendered grid using the AoC block font.

    Args:
        grid: Rendered grid string.
        width: Width in characters of each letter block.

    Returns:
        Decoded uppercase text or ``?`` for unknown blocks.
    """
    lines = grid.splitlines()
    if not lines:
        return ""
    text = []
    for start in range(0, len(lines[0]), width):
        block = tuple(line[start : start + width].ljust(width, ".") for line in lines)
        letter = CHAR_MAP.get(block, "?")
        text.append(letter)
    return "".join(text)

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
