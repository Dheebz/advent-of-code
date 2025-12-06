"""Advent of Code 2024 Day 17: Chronospatial Computer."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_input(raw: str) -> tuple[int, int, int, list[int]]:
    """
    Parse the registers and program from the debugger dump.

    Args:
        raw: Input text with register initializations followed by the program.

    Returns:
        Tuple of initial A, B, C values and the list of program opcodes.
    """
    parts = raw.strip().splitlines()
    a = int(parts[0].split(":")[1].strip())
    b = int(parts[1].split(":")[1].strip())
    c = int(parts[2].split(":")[1].strip())
    program = [int(x) for x in parts[4].split(":")[1].strip().split(",")]
    return a, b, c, program


def run_program(a: int, b: int, c: int, program: list[int]) -> list[int]:
    """
    Execute the chronospatial computer program with the given registers.

    Args:
        a: Initial value for register A.
        b: Initial value for register B.
        c: Initial value for register C.
        program: List of opcode-instruction pairs.

    Returns:
        List of output values emitted by the `out` instruction.
    """
    ip = 0
    output: list[int] = []

    def combo(value: int) -> int:
        if value <= 3:
            return value
        if value == 4:
            return a
        if value == 5:
            return b
        if value == 6:
            return c
        raise ValueError("Invalid combo operand")

    while 0 <= ip < len(program):
        opcode = program[ip]
        operand = program[ip + 1]
        if opcode == 0:  # adv
            a //= 2 ** combo(operand)
        elif opcode == 1:  # bxl
            b ^= operand
        elif opcode == 2:  # bst
            b = combo(operand) % 8
        elif opcode == 3:  # jnz
            if a != 0:
                ip = operand
                continue
        elif opcode == 4:  # bxc
            b ^= c
        elif opcode == 5:  # out
            output.append(combo(operand) % 8)
        elif opcode == 6:  # bdv
            b = a // (2 ** combo(operand))
        elif opcode == 7:  # cdv
            c = a // (2 ** combo(operand))
        else:
            raise ValueError(f"Unknown opcode {opcode}")
        ip += 2
    return output


def solve_part_one(data: tuple[int, int, int, list[int]]) -> str:
    """
    Determine the output string produced by the debugger program.

    Args:
        data: Initial values for registers A, B, C and the program.

    Returns:
        Comma-separated string of all outputs.
    """
    a, b, c, program = data
    output = run_program(a, b, c, program)
    return ",".join(str(value) for value in output)


def solve_part_two(data: tuple[int, int, int, list[int]]) -> int:
    """
    Find the lowest positive initial `A` that causes the program to output itself.

    Args:
        data: Initial registers (A ignored) and the program list.

    Returns:
        Minimum positive `A` that makes the output equal the program.
    """
    _, b, c, program = data
    target = program
    candidates = [0]
    for idx in range(len(target) - 1, -1, -1):
        new_candidates: list[int] = []
        suffix_len = len(target) - idx
        for cand in candidates:
            for digit in range(8):
                a_val = (cand << 3) | digit
                out = run_program(a_val, b, c, program)
                if out[-suffix_len:] == target[idx:]:
                    new_candidates.append(a_val)
        candidates = new_candidates
    return min(candidates)

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
