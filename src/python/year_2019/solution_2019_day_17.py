"""Set and Forget -- Advent of Code 2019 Day 17."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Tuple

if TYPE_CHECKING:
    from .intcode import Intcode
else:
    try:
        from .intcode import Intcode
    except ImportError:  # pragma: no cover
        from intcode import Intcode  # ty: ignore[unresolved-import]

Point = Tuple[int, int]


def parse_input(raw: str) -> List[int]:
    """Parse program values from the input text.

    Args:
        raw (str): Raw comma-separated program.

    Returns:
        List[int]: Intcode program values.
    """
    return [int(value) for value in raw.strip().split(",") if value]


def build_map(program: List[int]) -> Dict[Point, str]:
    """Run the scaffold mapping program and build a grid.

    Args:
        program (List[int]): Intcode program.

    Returns:
        Dict[Point, str]: Map of coordinates to characters.
    """
    computer = Intcode(program)
    outputs = computer.run()
    grid: Dict[Point, str] = {}
    x = y = 0
    for value in outputs:
        char = chr(value)
        if char == "\n":
            y += 1
            x = 0
            continue
        grid[(x, y)] = char
        x += 1
    return grid


def alignment_parameters(grid: Dict[Point, str]) -> int:
    """Sum alignment parameters for scaffold intersections.

    Args:
        grid (Dict[Point, str]): Map of the scaffold layout.

    Returns:
        int: Total alignment parameter.
    """
    total = 0
    for (x, y), char in grid.items():
        if char != "#":
            continue
        neighbors = [
            grid.get((x + 1, y)),
            grid.get((x - 1, y)),
            grid.get((x, y + 1)),
            grid.get((x, y - 1)),
        ]
        if all(n == "#" for n in neighbors):
            total += x * y
    return total


DIRECTIONS = {
    "^": (0, -1),
    "v": (0, 1),
    "<": (-1, 0),
    ">": (1, 0),
}
TURN_LEFT = {(0, -1): (-1, 0), (-1, 0): (0, 1), (0, 1): (1, 0), (1, 0): (0, -1)}
TURN_RIGHT = {(0, -1): (1, 0), (1, 0): (0, 1), (0, 1): (-1, 0), (-1, 0): (0, -1)}


def find_path(grid: Dict[Point, str]) -> List[str]:
    """Trace the robot's full movement path.

    Args:
        grid (Dict[Point, str]): Map of the scaffold layout.

    Returns:
        List[str]: Movement tokens alternating turns and step counts.
    """
    start = next(pos for pos, char in grid.items() if char in DIRECTIONS)
    direction = DIRECTIONS[grid[start]]
    path: List[str] = []
    position = start

    while True:
        left_dir = TURN_LEFT[direction]
        right_dir = TURN_RIGHT[direction]
        turn_made = None
        new_direction = direction
        if grid.get((position[0] + left_dir[0], position[1] + left_dir[1])) == "#":
            turn_made = "L"
            new_direction = left_dir
        elif grid.get((position[0] + right_dir[0], position[1] + right_dir[1])) == "#":
            turn_made = "R"
            new_direction = right_dir
        else:
            break

        direction = new_direction
        steps = 0
        while grid.get((position[0] + direction[0], position[1] + direction[1])) == "#":
            position = (position[0] + direction[0], position[1] + direction[1])
            steps += 1
        path.extend([turn_made, str(steps)])
    return path


def tokens_to_string(tokens: List[str]) -> str:
    """Join movement tokens into a comma-separated string.

    Args:
        tokens (List[str]): Movement tokens.

    Returns:
        str: Comma-separated representation.
    """
    return ",".join(tokens)


def replace_sequence(tokens: List[str], pattern: List[str], label: str) -> List[str]:
    """Replace occurrences of a pattern with a label.

    Args:
        tokens (List[str]): Full token list.
        pattern (List[str]): Pattern to replace.
        label (str): Replacement label.

    Returns:
        List[str]: Tokens with pattern substituted.
    """
    result: List[str] = []
    i = 0
    while i < len(tokens):
        if tokens[i : i + len(pattern)] == pattern:
            result.append(label)
            i += len(pattern)
        else:
            result.append(tokens[i])
            i += 1
    return result


def valid_pattern(pattern: List[str]) -> bool:
    """Check if a pattern fits within the input size constraint.

    Args:
        pattern (List[str]): Movement tokens.

    Returns:
        bool: True if the pattern string is <= 20 characters.
    """
    return len(tokens_to_string(pattern)) <= 20


def find_routines(path: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
    """Discover a valid decomposition into main routine and subroutines.

    Args:
        path (List[str]): Full movement path.

    Returns:
        Tuple[List[str], Dict[str, List[str]]]: Main routine tokens and mapping of labels.
    """
    for a_len in range(2, min(11, len(path)), 2):
        A = path[:a_len]
        if not valid_pattern(A):
            continue
        after_a = replace_sequence(path, A, "A")
        # find first non label
        try:
            b_start = next(i for i, t in enumerate(after_a) if t not in "ABC")
        except StopIteration:
            if len(tokens_to_string(after_a)) <= 20:
                return after_a, {"A": A, "B": [], "C": []}
            continue
        remaining_after_a = after_a[b_start:]
        for b_len in range(2, min(11, len(remaining_after_a) + 1), 2):
            B = remaining_after_a[:b_len]
            if not valid_pattern(B):
                continue
            after_b = replace_sequence(after_a, B, "B")
            try:
                c_start = next(i for i, t in enumerate(after_b) if t not in "ABC")
            except StopIteration:
                if len(tokens_to_string(after_b)) <= 20:
                    return after_b, {"A": A, "B": B, "C": []}
                continue
            remaining_after_b = after_b[c_start:]
            for c_len in range(2, min(11, len(remaining_after_b) + 1), 2):
                C = remaining_after_b[:c_len]
                if not valid_pattern(C):
                    continue
                after_c = replace_sequence(after_b, C, "C")
                if any(token not in "ABC" for token in after_c):
                    continue
                if len(tokens_to_string(after_c)) <= 20:
                    return after_c, {"A": A, "B": B, "C": C}
    raise ValueError("no routines found")


def feed_program(program: List[int], main: List[str], routines: Dict[str, List[str]]) -> int:
    """Run the vacuum robot program with the given routines.

    Args:
        program (List[int]): Intcode program.
        main (List[str]): Main routine tokens.
        routines (Dict[str, List[str]]): Subroutine token lists keyed by label.

    Returns:
        int: Final output value (dust collected).
    """
    program = program.copy()
    program[0] = 2
    computer = Intcode(program)

    inputs: List[int] = []
    for line in (
        [tokens_to_string(main)] + [tokens_to_string(routines[k]) for k in ("A", "B", "C")] + ["n"]
    ):
        inputs.extend([ord(ch) for ch in line])
        inputs.append(10)

    outputs = computer.run(inputs=inputs)
    return outputs[-1]


def solve_part_one(program: List[int]) -> int:
    """Return the sum of alignment parameters."""
    grid = build_map(program)
    return alignment_parameters(grid)


def solve_part_two(program: List[int]) -> int:
    """Return dust collected after executing routines."""
    grid = build_map(program)
    path = find_path(grid)
    main, routines = find_routines(path)
    return feed_program(program, main, routines)

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
