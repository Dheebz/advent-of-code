"""Two-Factor Authentication -- Advent of Code 2016 Day 8."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Command = Tuple[str, Tuple[int, int]]


def parse_input(raw: str) -> List[Command]:
    """Parse the screen manipulation commands."""
    commands: List[Command] = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("rect"):
            a, b = line.split()[1].split("x")
            commands.append(("rect", (int(a), int(b))))
        elif line.startswith("rotate row"):
            parts = line.split()
            y = int(parts[2].split("=")[1])
            amount = int(parts[-1])
            commands.append(("row", (y, amount)))
        elif line.startswith("rotate column"):
            parts = line.split()
            x = int(parts[2].split("=")[1])
            amount = int(parts[-1])
            commands.append(("col", (x, amount)))
    return commands


def apply(commands: Iterable[Command], width: int = 50, height: int = 6) -> List[List[bool]]:
    """Execute commands and return the resulting screen."""
    screen = [[False for _ in range(width)] for _ in range(height)]
    for kind, (a, b) in commands:
        if kind == "rect":
            w, h = a, b
            for y in range(h):
                for x in range(w):
                    screen[y][x] = True
        elif kind == "row":
            y, shift = a, b
            shift %= width
            screen[y] = screen[y][-shift:] + screen[y][:-shift]
        elif kind == "col":
            x, shift = a, b
            shift %= height
            column = [screen[y][x] for y in range(height)]
            column = column[-shift:] + column[:-shift]
            for y in range(height):
                screen[y][x] = column[y]
    return screen


FONT: Dict[str, str] = {
    ".##..#..#.#..#.####.#..#.#..#.": "A",
    "###..#..#.###..#..#.#..#.###..": "B",
    ".##..#..#.#....#....#..#..##..": "C",
    "####.#....###..#....#....####.": "E",
    "####.#....###..#....#....#....": "F",
    ".###.#....#....#.##.#..#..###.": "G",
    "#..#.#..#.####.#..#.#..#.#..#.": "H",
    "..##....#....#....#.#..#..##..": "J",
    "#..#.#.#..##...#.#..#.#..#..#.": "K",
    "#....#....#....#....#....####.": "L",
    ".##..#..#.#..#.#..#.#..#..##..": "O",
    "###..#..#.#..#.###..#....#....": "P",
    "###..#..#.#..#.###..#.#..#..#.": "R",
    ".###.#.....##.....#....#.###..": "S",
    "#..#.#..#.#..#.#..#.#..#..##..": "U",
    "####....#...#...#...#....####.": "Z",
}


def render_code(screen: List[List[bool]]) -> str:
    """Translate the lit pixels into letters using a fixed 5-wide font."""
    height = len(screen)
    width = len(screen[0])
    letters = []
    for start in range(0, width, 5):
        block = [
            "".join("#" if screen[y][x] else "." for x in range(start, start + 5))
            for y in range(height)
        ]
        key = "".join(block)
        letters.append(FONT.get(key, ""))  # TODO: Remove This section
    return "".join(letters)


def solve_part_one(commands: List[Command]) -> int:
    """Count lit pixels after executing all commands."""
    screen = apply(commands)
    return sum(row.count(True) for row in screen)


def solve_part_two(commands: List[Command]) -> str:
    """Render the message on the screen."""
    screen = apply(commands)
    return render_code(screen)

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
