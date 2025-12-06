"""Go With The Flow -- Advent of Code 2018 Day 19."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

Instruction = Tuple[str, int, int, int]


def parse_input(raw: str) -> Tuple[int, List[Instruction]]:
    """Parse the instruction pointer register and program."""
    lines = raw.strip().splitlines()
    ip_reg = int(lines[0].split()[1])
    program: List[Instruction] = []
    for line in lines[1:]:
        parts = line.split()
        program.append((parts[0], int(parts[1]), int(parts[2]), int(parts[3])))
    return ip_reg, program


def apply(op: str, regs: List[int], a: int, b: int, c: int) -> None:
    """Apply an operation in place to the registers."""
    if op == "addr":
        regs[c] = regs[a] + regs[b]
    elif op == "addi":
        regs[c] = regs[a] + b
    elif op == "mulr":
        regs[c] = regs[a] * regs[b]
    elif op == "muli":
        regs[c] = regs[a] * b
    elif op == "banr":
        regs[c] = regs[a] & regs[b]
    elif op == "bani":
        regs[c] = regs[a] & b
    elif op == "borr":
        regs[c] = regs[a] | regs[b]
    elif op == "bori":
        regs[c] = regs[a] | b
    elif op == "setr":
        regs[c] = regs[a]
    elif op == "seti":
        regs[c] = a
    elif op == "gtir":
        regs[c] = 1 if a > regs[b] else 0
    elif op == "gtri":
        regs[c] = 1 if regs[a] > b else 0
    elif op == "gtrr":
        regs[c] = 1 if regs[a] > regs[b] else 0
    elif op == "eqir":
        regs[c] = 1 if a == regs[b] else 0
    elif op == "eqri":
        regs[c] = 1 if regs[a] == b else 0
    elif op == "eqrr":
        regs[c] = 1 if regs[a] == regs[b] else 0


def execute(
    ip_reg: int, program: List[Instruction], initial: List[int], stop_ip: int | None = None
) -> List[int]:
    """Execute the program and return final registers."""
    regs = initial[:]
    ip = 0
    while 0 <= ip < len(program):
        if stop_ip is not None and ip == stop_ip:
            break
        regs[ip_reg] = ip
        op, a, b, c = program[ip]
        apply(op, regs, a, b, c)
        ip = regs[ip_reg] + 1
    return regs


def sum_of_divisors(n: int) -> int:
    """Sum all divisors of n."""
    total = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
    return total


def solve_part_one(parsed: Tuple[int, List[Instruction]]) -> int:
    """Register 0 value after running the program."""
    ip_reg, program = parsed
    regs = execute(ip_reg, program, [0, 0, 0, 0, 0, 0])
    return regs[0]


def solve_part_two(parsed: Tuple[int, List[Instruction]]) -> int:
    """Optimized: sum of divisors of the target value built during setup."""
    ip_reg, program = parsed
    regs = execute(ip_reg, program, [1, 0, 0, 0, 0, 0], stop_ip=1)
    target = regs[1]
    return sum_of_divisors(target)

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
