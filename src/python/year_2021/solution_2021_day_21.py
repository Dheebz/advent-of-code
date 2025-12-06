"""Dirac Dice -- Advent of Code 2021 Day 21."""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path
from typing import Tuple


def parse_input(raw: str) -> Tuple[int, int]:
    """
    Parse the starting positions for both players.

    Args:
        raw: Two-line input specifying each player's starting location.

    Returns:
        Tuple of 1-based starting positions for player 1 and player 2.
    """
    lines = raw.strip().splitlines()
    p1 = int(lines[0].split(":")[1])
    p2 = int(lines[1].split(":")[1])
    return p1, p2


def solve_part_one(data: Tuple[int, int]) -> int:
    """
    Simulate the deterministic dice game.

    Args:
        data: Tuple containing the two players' starting positions.

    Returns:
        Product of the losing player's score and the number of dice rolls.
    """
    p1, p2 = data
    scores = [0, 0]
    positions = [p1 - 1, p2 - 1]  # zero-based
    die = 1
    rolls = 0
    player = 0
    while True:
        move = 0
        for _ in range(3):
            move += die
            die = die % 100 + 1
            rolls += 1
        positions[player] = (positions[player] + move) % 10
        scores[player] += positions[player] + 1
        if scores[player] >= 1000:
            return scores[1 - player] * rolls
        player = 1 - player


@lru_cache(maxsize=None)
def quantum_round(p1: int, p2: int, s1: int, s2: int, turn: int) -> Tuple[int, int]:
    """
    Compute win counts for each player from the current quantum state.

    Args:
        p1: Position of player 1 (zero-based).
        p2: Position of player 2 (zero-based).
        s1: Score of player 1.
        s2: Score of player 2.
        turn: Player whose turn it is (0 or 1).

    Returns:
        Tuple (wins1, wins2) for all universes from this state.
    """
    if s1 >= 21:
        return (1, 0)
    if s2 >= 21:
        return (0, 1)

    wins1 = wins2 = 0
    for roll_sum, count in ROLL_COUNTS.items():
        if turn == 0:
            new_p1 = (p1 + roll_sum) % 10
            new_s1 = s1 + new_p1 + 1
            w1, w2 = quantum_round(new_p1, p2, new_s1, s2, 1)
        else:
            new_p2 = (p2 + roll_sum) % 10
            new_s2 = s2 + new_p2 + 1
            w1, w2 = quantum_round(p1, new_p2, s1, new_s2, 0)
        wins1 += w1 * count
        wins2 += w2 * count
    return wins1, wins2


ROLL_COUNTS = {
    3: 1,
    4: 3,
    5: 6,
    6: 7,
    7: 6,
    8: 3,
    9: 1,
}


def solve_part_two(data: Tuple[int, int]) -> int:
    """
    Count the winning universes for both players.

    Args:
        data: Tuple containing the two players' starting positions.

    Returns:
        Larger of the two win counts.
    """
    p1, p2 = data
    wins = quantum_round(p1 - 1, p2 - 1, 0, 0, 0)
    return max(wins)

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
