"""Duet -- Advent of Code 2017 Day 18."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Dict, List, Tuple

Instruction = Tuple[str, List[str]]


def parse_input(raw: str) -> List[Instruction]:
    """Parse program instructions."""
    program: List[Instruction] = []
    for line in raw.strip().splitlines():
        parts = line.strip().split()
        if parts:
            program.append((parts[0], parts[1:]))
    return program


def get_value(regs: Dict[str, int], operand: str) -> int:
    """Resolve a register or integer operand to an int."""
    return regs[operand] if operand.isalpha() else int(operand)


def solve_part_one(program: List[Instruction]) -> int:
    """First recovered frequency."""
    regs: Dict[str, int] = {}
    last_sound = 0
    ip = 0
    while 0 <= ip < len(program):
        op, args = program[ip]
        if op == "snd":
            last_sound = get_value(regs, args[0])
            ip += 1
        elif op == "set":
            regs[args[0]] = get_value(regs, args[1])
            ip += 1
        elif op == "add":
            regs[args[0]] = regs.get(args[0], 0) + get_value(regs, args[1])
            ip += 1
        elif op == "mul":
            regs[args[0]] = regs.get(args[0], 0) * get_value(regs, args[1])
            ip += 1
        elif op == "mod":
            regs[args[0]] = regs.get(args[0], 0) % get_value(regs, args[1])
            ip += 1
        elif op == "rcv":
            if get_value(regs, args[0]) != 0:
                return last_sound
            ip += 1
        elif op == "jgz":
            if get_value(regs, args[0]) > 0:
                ip += get_value(regs, args[1])
            else:
                ip += 1
    raise ValueError("No recovery")


def solve_part_two(program: List[Instruction]) -> int:
    """Count how many times program 1 sends a value before deadlock."""
    queues = {0: deque(), 1: deque()}
    regs: Dict[int, Dict[str, int]] = {0: {"p": 0}, 1: {"p": 1}}
    ip = {0: 0, 1: 0}
    sent_counts = {0: 0, 1: 0}

    def step(pid: int) -> bool:
        """Execute until waiting or program ends. Return True if progressed."""
        while 0 <= ip[pid] < len(program):
            op, args = program[ip[pid]]
            if op == "snd":
                queues[1 - pid].append(get_value(regs[pid], args[0]))
                sent_counts[pid] += 1
                ip[pid] += 1
            elif op == "set":
                regs[pid][args[0]] = get_value(regs[pid], args[1])
                ip[pid] += 1
            elif op == "add":
                regs[pid][args[0]] = regs[pid].get(args[0], 0) + get_value(regs[pid], args[1])
                ip[pid] += 1
            elif op == "mul":
                regs[pid][args[0]] = regs[pid].get(args[0], 0) * get_value(regs[pid], args[1])
                ip[pid] += 1
            elif op == "mod":
                regs[pid][args[0]] = regs[pid].get(args[0], 0) % get_value(regs[pid], args[1])
                ip[pid] += 1
            elif op == "rcv":
                if queues[pid]:
                    regs[pid][args[0]] = queues[pid].popleft()
                    ip[pid] += 1
                else:
                    return False
            elif op == "jgz":
                if get_value(regs[pid], args[0]) > 0:
                    ip[pid] += get_value(regs[pid], args[1])
                else:
                    ip[pid] += 1
        return False

    while True:
        progressed0 = step(0)
        progressed1 = step(1)
        if not progressed0 and not progressed1:
            break
    return sent_counts[1]

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
