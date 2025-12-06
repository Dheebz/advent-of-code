"""Space Police -- Advent of Code 2019 Day 11."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Tuple

if TYPE_CHECKING:
    from .intcode import Intcode
else:
    try:
        from .intcode import Intcode
    except ImportError:  # pragma: no cover
        from intcode import Intcode  # ty: ignore[unresolved-import]

Point = Tuple[int, int]

# 6x5 font for OCR.
FONT_ROWS = {
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
# build a compact 4x6 font by trimming the rightmost column
FONT_ROWS_4 = {letter: [row[:-1] for row in rows] for letter, rows in FONT_ROWS.items()}
OCR_FONT = {"".join(rows): letter for letter, rows in FONT_ROWS_4.items()}


def parse_input(raw: str) -> List[int]:
    """Parse program values from the input text.

    Args:
        raw (str): Raw comma-separated program.

    Returns:
        List[int]: Intcode program values.
    """
    return [int(value) for value in raw.strip().split(",") if value]


def run_robot(program: List[int], start_color: int = 0) -> Dict[Point, int]:
    """Simulate the painting robot.

    Args:
        program (List[int]): Intcode program.
        start_color (int, optional): Initial panel color. Defaults to 0.

    Returns:
        Dict[Point, int]: Map of painted panels and their final colors.
    """
    computer = Intcode(program)
    grid: Dict[Point, int] = {}
    position = (0, 0)
    direction = 0  # 0=up,1=right,2=down,3=left
    grid[position] = start_color
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while not computer.halted:
        current_color = grid.get(position, 0)
        outputs = computer.run(inputs=[current_color], until_output=True)
        if computer.halted or not outputs:
            break
        paint_color = outputs[-1]
        turn_output = computer.run(until_output=True)
        if computer.halted or not turn_output:
            break
        turn = turn_output[-1]

        grid[position] = paint_color
        direction = (direction + (1 if turn == 1 else -1)) % 4
        dx, dy = deltas[direction]
        position = (position[0] + dx, position[1] + dy)

    return grid


def solve_part_one(program: List[int]) -> int:
    """Count panels painted at least once."""
    painted = run_robot(program, start_color=0)
    return len(painted)


def render_grid(grid: Dict[Point, int]) -> str:
    """Render the painted registration identifier.

    Args:
        grid (Dict[Point, int]): Painted panel colors.

    Returns:
        str: Rendered image using ``#`` for white and ``.`` for black.
    """
    white_points = [point for point, color in grid.items() if color == 1]
    min_x = min(x for x, _ in white_points)
    max_x = max(x for x, _ in white_points)
    min_y = min(y for _, y in white_points)
    max_y = max(y for _, y in white_points)

    rows = []
    for y in range(max_y, min_y - 1, -1):
        row = ""
        for x in range(min_x, max_x + 1):
            row += "#" if grid.get((x, y), 0) == 1 else "."
        rows.append(row)
    return "\n".join(rows)


def decode_text(image: str, letter_width: int = 4) -> str:
    """Decode the rendered image using the OCR font.

    Args:
        image (str): Rendered image as newline-separated rows.
        letter_width (int, optional): Width of each letter. Defaults to 4.

    Returns:
        str: Decoded registration text.
    """
    rows = image.splitlines()
    width = max(len(r) for r in rows)
    rows = [r.ljust(width, ".") for r in rows]
    text = ""
    offset = 0
    while offset + letter_width <= width:
        # skip empty spacer columns
        if all(row[offset] == "." for row in rows):
            offset += 1
            continue
        pattern = "".join(row[offset : offset + letter_width] for row in rows)
        text += OCR_FONT.get(pattern, "?")
        offset += letter_width
    return text


def solve_part_two(program: List[int]) -> str:
    """Render and decode the registration identifier."""
    painted = run_robot(program, start_color=1)
    image = render_grid(painted)
    return decode_text(image)

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
