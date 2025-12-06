"""Crab Combat -- Advent of Code 2020 Day 22."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Deque, Tuple

Decks = Tuple[Deque[int], Deque[int]]


def parse_input(raw: str) -> Decks:
    """Return decks for both players."""
    blocks = raw.strip().split("\n\n")
    p1 = deque(int(card) for card in blocks[0].splitlines()[1:])
    p2 = deque(int(card) for card in blocks[1].splitlines()[1:])
    return p1, p2


def score(deck: Deque[int]) -> int:
    """
    Compute the combat score for a deck.

    Args:
        deck: Winner's deck.

    Returns:
        Weighted sum of card values.
    """
    return sum(multiplier * card for multiplier, card in enumerate(reversed(deck), start=1))


def play_combat(p1: Deque[int], p2: Deque[int]) -> int:
    """
    Simulate the standard crab combat game.

    Args:
        p1: Player 1 deck.
        p2: Player 2 deck.

    Returns:
        Score of the winning deck.
    """
    while p1 and p2:
        c1 = p1.popleft()
        c2 = p2.popleft()
        if c1 > c2:
            p1.extend([c1, c2])
        else:
            p2.extend([c2, c1])
    return score(p1 if p1 else p2)


def play_recursive_combat(p1: Deque[int], p2: Deque[int]) -> Tuple[int, Deque[int]]:
    """
    Simulate recursive combat, returning the winner and winning deck.

    Args:
        p1: Player 1 deck.
        p2: Player 2 deck.

    Returns:
        Tuple containing winner id and the winning deck.
    """
    seen = set()
    while p1 and p2:
        state = (tuple(p1), tuple(p2))
        if state in seen:
            return 1, p1
        seen.add(state)

        c1 = p1.popleft()
        c2 = p2.popleft()

        if len(p1) >= c1 and len(p2) >= c2:
            winner, _ = play_recursive_combat(deque(list(p1)[:c1]), deque(list(p2)[:c2]))
        else:
            winner = 1 if c1 > c2 else 2

        if winner == 1:
            p1.extend([c1, c2])
        else:
            p2.extend([c2, c1])
    return (1, p1) if p1 else (2, p2)


def solve_part_one(decks: Decks) -> int:
    """
    Return the winning score for standard combat.

    Args:
        decks: Tuple containing both players' decks.

    Returns:
        Score of the winning deck after playing combat.
    """
    p1, p2 = decks
    return play_combat(deque(p1), deque(p2))


def solve_part_two(decks: Decks) -> int:
    """
    Return the winning score for recursive combat.

    Args:
        decks: Tuple containing both players' decks.

    Returns:
        Score of the winning deck after playing recursive combat.
    """
    p1, p2 = decks
    winner, deck = play_recursive_combat(deque(p1), deque(p2))
    return score(deck)

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
