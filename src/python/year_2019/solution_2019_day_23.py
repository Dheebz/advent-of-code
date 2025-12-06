"""Category Six -- Advent of Code 2019 Day 23."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Deque, List, Tuple

if TYPE_CHECKING:
    from .intcode import Intcode
else:
    try:
        from .intcode import Intcode
    except ImportError:  # pragma: no cover
        from intcode import Intcode  # ty: ignore[unresolved-import]


def parse_input(raw: str) -> List[int]:
    """Parse program values from the input text.

    Args:
        raw (str): Raw comma-separated program.

    Returns:
        List[int]: Intcode program values.
    """
    return [int(value) for value in raw.strip().split(",") if value]


def run_network(program: List[int]) -> Tuple[int, int]:
    """Simulate the 50-computer network.

    Args:
        program (List[int]): Intcode program.

    Returns:
        Tuple[int, int]: First Y sent to the NAT and first repeated NAT Y value.
    """
    machines = [Intcode(program) for _ in range(50)]
    queues: List[Deque[int]] = [deque([i]) for i in range(50)]
    nat_packet: Tuple[int, int] | None = None
    first_nat_y = None
    last_nat_y = None

    while True:
        idle = True
        for i, machine in enumerate(machines):
            if queues[i]:
                inputs = list(queues[i])
                queues[i].clear()
                idle = False
            else:
                inputs = [-1]
            outputs = machine.run(inputs=inputs, until_output=True)
            buffer: List[int] = []
            while outputs:
                idle = False
                buffer.extend(outputs)
                outputs = machine.run(until_output=True)
            for j in range(0, len(buffer), 3):
                dest, x, y = buffer[j : j + 3]
                if dest == 255:
                    nat_packet = (x, y)
                    if first_nat_y is None:
                        first_nat_y = y
                else:
                    queues[dest].append(x)
                    queues[dest].append(y)

        if idle and nat_packet is not None:
            x, y = nat_packet
            queues[0].append(x)
            queues[0].append(y)
            if last_nat_y == y:
                assert first_nat_y is not None
                return first_nat_y, y
            last_nat_y = y


def solve_part_one(program: List[int]) -> int:
    """Return the first Y value delivered to the NAT."""
    first_nat_y, _ = run_network(program)
    return first_nat_y


def solve_part_two(program: List[int]) -> int:
    """Return the first Y value sent twice by the NAT."""
    _, repeated_nat_y = run_network(program)
    return repeated_nat_y

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
