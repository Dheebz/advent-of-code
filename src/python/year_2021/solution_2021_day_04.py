"""Giant Squid -- Advent of Code 2021 Day 4."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

Board = List[List[int]]
DrawsAndBoards = Tuple[List[int], List[Board]]


def parse_input(raw: str) -> DrawsAndBoards:
    """
    Parse the drawn numbers and bingo boards from the input.

    Args:
        raw: Input text containing the draw order followed by board grids.

    Returns:
        Tuple of draw list and list of bingo boards.
    """
    sections = raw.strip().split("\n\n")
    draws = [int(x) for x in sections[0].split(",")]
    boards: List[Board] = []
    for block in sections[1:]:
        board = [[int(x) for x in line.split()] for line in block.splitlines()]
        boards.append(board)
    return draws, boards


def mark_board(board: Board, called: int) -> None:
    """
    Mark the called number on the board by replacing it with ``-1``.

    Args:
        board: Board to mutate.
        called: Number that has been drawn.
    """
    for row in board:
        for i, value in enumerate(row):
            if value == called:
                row[i] = -1


def is_winner(board: Board) -> bool:
    """
    Check whether the board has a completed row or column.

    Args:
        board: Board to evaluate.

    Returns:
        True if any row or column is fully marked, False otherwise.
    """
    size = len(board)
    for row in board:
        if all(value == -1 for value in row):
            return True
    for col in range(size):
        if all(board[row][col] == -1 for row in range(size)):
            return True
    return False


def board_score(board: Board, called: int) -> int:
    """
    Calculate the score of a winning bingo board.

    Args:
        board: Winning board.
        called: Last number that was called.

    Returns:
        Sum of unmarked values multiplied by the last called number.
    """
    return sum(value for row in board for value in row if value != -1) * called


def solve_part_one(data: DrawsAndBoards) -> int:
    """
    Determine the score of the first board that wins.

    Args:
        data: Parsed draw order and boards.

    Returns:
        Score of the first winning board.
    """
    draws, boards = data
    boards = [[row[:] for row in board] for board in boards]
    for number in draws:
        for board in boards:
            mark_board(board, number)
        for board in boards:
            if is_winner(board):
                return board_score(board, number)
    raise ValueError("no winner")


def solve_part_two(data: DrawsAndBoards) -> int:
    """
    Determine the score of the last board that wins.

    Args:
        data: Parsed draw order and boards.

    Returns:
        Score of the final winning board.
    """
    draws, boards = data
    boards = [[row[:] for row in board] for board in boards]
    won = set()
    last_score = None
    for number in draws:
        for idx, board in enumerate(boards):
            if idx in won:
                continue
            mark_board(board, number)
            if is_winner(board):
                won.add(idx)
                last_score = board_score(board, number)
    if last_score is None:
        raise ValueError("no winning board")
    return last_score

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
