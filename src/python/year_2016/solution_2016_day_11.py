"""Radioisotope Thermoelectric Generators -- Advent of Code 2016 Day 11."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Tuple

Pair = Tuple[int, int]  # (generator_floor, microchip_floor)
State = Tuple[int, Tuple[Pair, ...]]


def parse_input(raw: str) -> Tuple[List[Pair], int]:
    """Parse the starting positions for all microchips and generators."""
    floors = raw.strip().splitlines()
    items: Dict[str, List[int]] = {}
    for floor_idx, line in enumerate(floors):
        words = line.replace(",", "").replace(".", "").split()
        for idx, word in enumerate(words):
            if word.endswith("generator"):
                element = words[idx - 1]
                items.setdefault(element, [-1, -1])[0] = floor_idx
            elif word.endswith("microchip"):
                element = words[idx - 1].split("-")[0]
                items.setdefault(element, [-1, -1])[1] = floor_idx
    pairs: List[Pair] = [(value[0], value[1]) for value in items.values()]
    return pairs, len(floors)


def canonical_state(elevator: int, pairs: Iterable[Pair]) -> State:
    """Normalize state ordering for deduplication.

    Args:
        elevator (int): Current elevator floor.
        pairs (Iterable[Pair]): Generator/microchip floor pairs.

    Returns:
        State: Canonicalized state tuple.
    """
    return elevator, tuple(sorted(tuple(pair) for pair in pairs))  # type: ignore[return-value]


def is_valid(state: State) -> bool:
    """Check whether a state is safe (no fried chips).

    Args:
        state (State): Candidate state.

    Returns:
        bool: True if all chips are protected or with their generator.
    """
    elevator, pairs = state
    floors = max(max(gen, chip) for gen, chip in pairs) + 1
    for floor in range(floors):
        gens = {idx for idx, (g, _) in enumerate(pairs) if g == floor}
        if not gens:
            continue
        for idx, (_, chip_floor) in enumerate(pairs):
            if chip_floor == floor and idx not in gens:
                return False
    return True


def generate_moves(state: State, floor_count: int) -> Iterable[State]:
    """Yield valid next states reachable in one elevator move.

    Args:
        state (State): Current state.
        floor_count (int): Total number of floors.

    Returns:
        Iterable[State]: Valid successor states.
    """
    elevator, pairs = state
    items_on_floor: List[Tuple[int, bool]] = []
    for idx, (gen_floor, chip_floor) in enumerate(pairs):
        if gen_floor == elevator:
            items_on_floor.append((idx, True))
        if chip_floor == elevator:
            items_on_floor.append((idx, False))

    for direction in (-1, 1):
        next_floor = elevator + direction
        if not 0 <= next_floor < floor_count:
            continue
        for i, first in enumerate(items_on_floor):
            combos = [first]
            yield_state = move_items(elevator, next_floor, pairs, combos)
            if yield_state and is_valid(yield_state):
                yield yield_state
            for second in items_on_floor[i + 1 :]:
                combos = [first, second]
                yield_state = move_items(elevator, next_floor, pairs, combos)
                if yield_state and is_valid(yield_state):
                    yield yield_state


def move_items(
    elevator: int, next_floor: int, pairs: Tuple[Pair, ...], items: List[Tuple[int, bool]]
) -> State | None:
    """Move selected items to another floor if resulting state is valid.

    Args:
        elevator (int): Current elevator floor.
        next_floor (int): Destination floor.
        pairs (Tuple[Pair, ...]): Current generator/microchip positions.
        items (List[Tuple[int, bool]]): Items to move as (index, is_generator).

    Returns:
        State | None: New state or None if invalid.
    """
    new_pairs = [list(pair) for pair in pairs]
    for idx, is_gen in items:
        new_pairs[idx][0 if is_gen else 1] = next_floor
    state = canonical_state(next_floor, [tuple(pair) for pair in new_pairs])  # type: ignore[list-item]
    return state


def bfs(start: State, floor_count: int) -> int:
    """Find minimal moves to bring all items to the top floor.

    Args:
        start (State): Starting state.
        floor_count (int): Total number of floors.

    Returns:
        int: Minimal number of moves.
    """
    goal_floor = floor_count - 1
    goal_pairs = tuple((goal_floor, goal_floor) for _ in start[1])
    goal = (goal_floor, goal_pairs)

    queue: Deque[Tuple[State, int]] = deque([(start, 0)])
    seen = {start}

    while queue:
        state, steps = queue.popleft()
        if state == goal:
            return steps
        elevator, pairs = state
        # Skip moving down if everything below is already clear.
        min_item_floor = min(min(gen, chip) for gen, chip in pairs)
        for next_state in generate_moves(state, floor_count):
            if next_state in seen:
                continue
            if next_state[0] < elevator and min_item_floor >= elevator:
                continue
            seen.add(next_state)
            queue.append((next_state, steps + 1))
    raise ValueError("No solution found")


def solve_part_one(parsed: Tuple[List[Pair], int]) -> int:
    """Minimum steps to move all items to the top floor."""
    pairs, floor_count = parsed
    start = canonical_state(0, pairs)
    return bfs(start, floor_count)


def solve_part_two(parsed: Tuple[List[Pair], int]) -> int:
    """Minimum steps with additional devices on the first floor."""
    pairs, floor_count = parsed
    extended = pairs + [(0, 0), (0, 0)]  # elerium and dilithium
    start = canonical_state(0, extended)
    return bfs(start, floor_count)

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
