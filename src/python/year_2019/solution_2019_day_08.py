"""Space Image Format -- Advent of Code 2019 Day 8."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

# 6x5 font used across AoC puzzles.
FONT_ROWS: Dict[str, List[str]] = {
    "A": [".##..", "#..#.", "#..#.", "####.", "#..#.", "#..#."],
    "B": ["###..", "#..#.", "###..", "#..#.", "#..#.", "###.."],
    "C": [".##..", "#..#.", "#....", "#....", "#..#.", ".##.."],
    "D": ["###..", "#..#.", "#..#.", "#..#.", "#..#.", "###.."],
    "E": ["####.", "#....", "###..", "#....", "#....", "####."],
    "F": ["####.", "#....", "###..", "#....", "#....", "#...."],
    "G": [".##..", "#..#.", "#....", "#.##.", "#..#.", ".###."],
    "H": ["#..#.", "#..#.", "####.", "#..#.", "#..#.", "#..#."],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..##.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#..#.", "#.#..", "##...", "#.#..", "#.#..", "#..#."],
    "L": ["#....", "#....", "#....", "#....", "#....", "####."],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".##..", "#..#.", "#..#.", "#..#.", "#..#.", ".##.."],
    "P": ["###..", "#..#.", "#..#.", "###..", "#....", "#...."],
    "Q": [".##..", "#..#.", "#..#.", "#..#.", "#.##.", ".###."],
    "R": ["###..", "#..#.", "#..#.", "###..", "#.#..", "#..#."],
    "S": [".###.", "#....", "#....", ".##..", "...#.", "###.."],
    "T": ["####.", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#..#.", "#..#.", "#..#.", "#..#.", "#..#.", ".##.."],
    "V": ["#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#.."],
    "Z": ["####.", "...#.", "..#..", ".#...", "#....", "####."],
}

OCR_FONT: Dict[str, str] = {"".join(rows): letter for letter, rows in FONT_ROWS.items()}


def parse_input(raw: str) -> List[int]:
    """Convert raw pixels into a flat list of integers.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        List[int]: Pixel values.
    """
    return [int(ch) for ch in raw.strip()]


def split_layers(pixels: List[int], width: int, height: int) -> List[List[int]]:
    """Split the flat pixel list into layers.

    Args:
        pixels (List[int]): Flat pixel data.
        width (int): Image width.
        height (int): Image height.

    Returns:
        List[List[int]]: Layers of size ``width * height``.
    """
    size = width * height
    return [pixels[i : i + size] for i in range(0, len(pixels), size)]


def solve_part_one(pixels: List[int], width: int = 25, height: int = 6) -> int:
    """Compute checksum for the layer with fewest zeros.

    Args:
        pixels (List[int]): Flat pixel data.
        width (int, optional): Image width. Defaults to 25.
        height (int, optional): Image height. Defaults to 6.

    Returns:
        int: Count of 1 digits multiplied by count of 2 digits.
    """
    layers = split_layers(pixels, width, height)
    layer = min(layers, key=lambda layer_pixels: layer_pixels.count(0))
    return layer.count(1) * layer.count(2)


def render_image(pixels: List[int], width: int, height: int) -> List[str]:
    """Render the final image after stacking layers.

    Args:
        pixels (List[int]): Flat pixel data.
        width (int): Image width.
        height (int): Image height.

    Returns:
        List[str]: Rendered rows using ``#`` for white and ``.`` for black.
    """
    layers = split_layers(pixels, width, height)
    final = [2] * (width * height)
    for layer in layers:
        for idx, value in enumerate(layer):
            if final[idx] == 2 and value != 2:
                final[idx] = value
    rows = []
    for row in range(height):
        line = ""
        for col in range(width):
            line += "#" if final[row * width + col] == 1 else "."
        rows.append(line)
    return rows


def decode_rows(rows: List[str], letter_width: int = 5) -> str:
    """Decode rendered rows into OCR text.

    Args:
        rows (List[str]): Rendered image rows.
        letter_width (int, optional): Width of each letter. Defaults to 5.

    Returns:
        str: Decoded text string.
    """
    text = ""
    width = len(rows[0])
    for offset in range(0, width, letter_width):
        pattern = "".join(row[offset : offset + letter_width] for row in rows)
        text += OCR_FONT.get(pattern, "?")
    return text


def solve_part_two(pixels: List[int], width: int = 25, height: int = 6) -> str:
    """Decode the registration code from the image.

    Args:
        pixels (List[int]): Flat pixel data.
        width (int, optional): Image width. Defaults to 25.
        height (int, optional): Image height. Defaults to 6.

    Returns:
        str: OCR-decoded text.
    """
    rows = render_image(pixels, width, height)
    return decode_rows(rows)

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
