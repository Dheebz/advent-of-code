"""Monkey in the Middle -- Advent of Code 2022 Day 11."""

from __future__ import annotations

import argparse
from math import prod
from pathlib import Path
from typing import Callable, List


class Monkey:
    """
    Track monkey state for the circus simulation.

    Attributes:
        items: Current worry levels held by the monkey.
        operation: Function used to update worry levels.
        divisor: Divisor used to decide throwing direction.
        target_true: Index of the monkey that receives the item when the test passes.
        target_false: Index of the monkey that receives the item otherwise.
        inspected: Count of items this monkey has inspected.
    """

    def __init__(
        self,
        items: List[int],
        operation: Callable[[int], int],
        divisor: int,
        target_true: int,
        target_false: int,
    ) -> None:
        """
        Initialize a monkey with its instructions.

        Args:
            items: Initial worry levels held by the monkey.
            operation: Operation defining worry adjustments.
            divisor: Divisor used to test the worry level.
            target_true: Monkey index to receive when the test passes.
            target_false: Monkey index to receive when the test fails.
        """
        self.items = items
        self.operation = operation
        self.divisor = divisor
        self.target_true = target_true
        self.target_false = target_false
        self.inspected = 0


def parse_input(raw: str) -> List[Monkey]:
    """
    Parse the raw monkey descriptions into usable ``Monkey`` objects.

    Args:
        raw: Input text separating monkeys with a blank line.

    Returns:
        List of configured ``Monkey`` instances.
    """
    monkeys: List[Monkey] = []
    for block in raw.strip().split("\n\n"):
        lines = block.splitlines()
        items = [int(x.strip()) for x in lines[1].split(":")[1].split(",")]
        op_parts = lines[2].split("=")[1].strip().split()
        if op_parts[1] == "*":
            if op_parts[2] == "old":

                def operation(old: int) -> int:
                    return old * old
            else:
                factor = int(op_parts[2])

                def operation(old: int, f=factor) -> int:
                    return old * f
        else:
            add = int(op_parts[2])

            def operation(old: int, a=add) -> int:
                return old + a

        divisor = int(lines[3].split()[-1])
        target_true = int(lines[4].split()[-1])
        target_false = int(lines[5].split()[-1])
        monkeys.append(Monkey(items, operation, divisor, target_true, target_false))
    return monkeys


def clone_monkeys(monkeys: List[Monkey]) -> List[Monkey]:
    """
    Clone each monkey so simulations can run independently.

    Args:
        monkeys: List of monkeys to clone.

    Returns:
        Deep copy of the provided monkey list.
    """
    clones: List[Monkey] = []
    for m in monkeys:
        clone = Monkey(m.items.copy(), m.operation, m.divisor, m.target_true, m.target_false)
        clones.append(clone)
    return clones


def simulate(monkeys: List[Monkey], rounds: int, relief: bool) -> int:
    """
    Simulate the monkey inspections for the provided number of rounds.

    Args:
        monkeys: Base monkey configuration to simulate.
        rounds: Number of rounds to perform.
        relief: Whether to apply the relief division by 3.

    Returns:
        Product of the inspection counts of the two busiest monkeys.
    """
    monkeys = clone_monkeys(monkeys)
    modulus = prod(m.divisor for m in monkeys)

    for _ in range(rounds):
        for monkey in monkeys:
            while monkey.items:
                item = monkey.items.pop(0)
                item = monkey.operation(item)
                if relief:
                    item //= 3
                else:
                    item %= modulus
                target = monkey.target_true if item % monkey.divisor == 0 else monkey.target_false
                monkeys[target].items.append(item)
                monkey.inspected += 1

    counts = sorted((m.inspected for m in monkeys), reverse=True)
    return counts[0] * counts[1]


def solve_part_one(monkeys: List[Monkey]) -> int:
    """
    Run the simulation for 20 rounds with relief applied.

    Args:
        monkeys: Monkey configuration returned by `parse_input`.

    Returns:
        Monkey business metric after 20 rounds.
    """
    return simulate(monkeys, rounds=20, relief=True)


def solve_part_two(monkeys: List[Monkey]) -> int:
    """
    Run the simulation for 10000 rounds without relief, using modular reduction.

    Args:
        monkeys: Monkey configuration returned by `parse_input`.

    Returns:
        Monkey business metric after 10000 rounds.
    """
    return simulate(monkeys, rounds=10_000, relief=False)

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
