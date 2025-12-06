"""Balance Bots -- Advent of Code 2016 Day 10."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
from typing import Deque, Dict, List, Tuple

Rule = Tuple[str, int, str, int]


def parse_input(raw: str) -> Tuple[Dict[int, Rule], Dict[int, List[int]]]:
    """Return the bot rules and starting chip assignments."""
    rules: Dict[int, Rule] = {}
    bots: Dict[int, List[int]] = defaultdict(list)
    for line in raw.strip().splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        if parts[0] == "value":
            value = int(parts[1])
            bot_id = int(parts[-1])
            bots[bot_id].append(value)
        else:
            bot_id = int(parts[1])
            low_type, low_id = parts[5], int(parts[6])
            high_type, high_id = parts[-2], int(parts[-1])
            rules[bot_id] = (low_type, low_id, high_type, high_id)
    return rules, bots


def run_factory(
    rules: Dict[int, Rule], bots: Dict[int, List[int]]
) -> Tuple[int, Dict[int, List[int]]]:
    """Simulate the bots. Returns bot comparing 17/61 and outputs."""
    outputs: Dict[int, List[int]] = defaultdict(list)
    comparison_bot = -1
    queue: Deque[int] = deque(bot for bot, chips in bots.items() if len(chips) == 2)

    while queue:
        bot_id = queue.popleft()
        chips = bots[bot_id]
        if len(chips) < 2 or bot_id not in rules:
            continue
        low_val, high_val = sorted(chips)
        if low_val == 17 and high_val == 61:
            comparison_bot = bot_id
        low_type, low_id, high_type, high_id = rules[bot_id]

        if low_type == "bot":
            bots[low_id].append(low_val)
            if len(bots[low_id]) == 2:
                queue.append(low_id)
        else:
            outputs[low_id].append(low_val)

        if high_type == "bot":
            bots[high_id].append(high_val)
            if len(bots[high_id]) == 2:
                queue.append(high_id)
        else:
            outputs[high_id].append(high_val)

        bots[bot_id].clear()

    return comparison_bot, outputs


def solve_part_one(parsed: Tuple[Dict[int, Rule], Dict[int, List[int]]]) -> int:
    """Identify the bot responsible for comparing 17 and 61."""
    rules, bots = parsed
    comparison_bot, _ = run_factory(
        dict(rules), defaultdict(list, {k: v.copy() for k, v in bots.items()})
    )
    return comparison_bot


def solve_part_two(parsed: Tuple[Dict[int, Rule], Dict[int, List[int]]]) -> int:
    """Compute the product of outputs 0, 1, and 2."""
    rules, bots = parsed
    _, outputs = run_factory(dict(rules), defaultdict(list, {k: v.copy() for k, v in bots.items()}))
    return outputs[0][0] * outputs[1][0] * outputs[2][0]

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
