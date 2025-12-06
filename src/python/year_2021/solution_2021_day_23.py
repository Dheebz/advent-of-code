"""Amphipod -- Advent of Code 2021 Day 23."""

from __future__ import annotations

import argparse
import heapq
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Hall = Tuple[str, ...]
Rooms = Tuple[Tuple[str, ...], ...]
State = Tuple[Hall, Rooms]

ENERGY = {"A": 1, "B": 10, "C": 100, "D": 1000}
ROOM_POSITIONS = [2, 4, 6, 8]
HALL_SPOTS = [0, 1, 3, 5, 7, 9, 10]


def parse_input(raw: str) -> List[List[str]]:
    """
    Parse the burrow layout from the input.

    Args:
        raw: Text defining the hallway and room contents.

    Returns:
        List of room rows from top to bottom.
    """
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    room_rows = [[ch for ch in line if ch in "ABCD"] for line in lines[2:-1]]
    rooms = [list(col) for col in zip(*room_rows)]
    return rooms


def build_state(room_rows: List[List[str]]) -> State:
    """
    Convert room rows into the canonical state representation.

    Args:
        room_rows: Rows of amphipod labels for each room.

    Returns:
        Tuple containing the hallway and room tuples.
    """
    hall: Hall = tuple("." for _ in range(11))
    rooms: Rooms = tuple(tuple(row) for row in room_rows)
    return hall, rooms


def path_clear(hall: Hall, start: int, end: int) -> bool:
    """
    Check whether the hallway path between two positions is empty.

    Args:
        hall: Current hallway state.
        start: Hallway position to move from.
        end: Hallway position to move toward.

    Returns:
        True if every position between `start` and `end` is empty.
    """
    step = 1 if end > start else -1
    for pos in range(start + step, end + step, step):
        if hall[pos] != ".":
            return False
    return True


def room_ready(room: Tuple[str, ...], target: str) -> bool:
    """
    Determine whether a room can accept the specified amphipod.

    Args:
        room: Current room contents top-to-bottom.
        target: Amphipod type that wants to enter.

    Returns:
        True when the room contains only empty spaces or the target type.
    """
    return all(ch in (".", target) for ch in room)


def top_occupant(room: Tuple[str, ...]) -> Tuple[int, str] | None:
    """
    Find the topmost amphipod in a room.

    Args:
        room: Room contents top-to-bottom.

    Returns:
        Tuple of depth and amphipod symbol, or None if empty.
    """
    for idx, ch in enumerate(room):
        if ch != ".":
            return idx, ch
    return None


def moves_from_hall(state: State) -> Iterable[Tuple[int, State]]:
    """
    Yield moves where amphipods enter their target room from the hallway.

    Args:
        state: Current hallway and room configuration.

    Yields:
        Tuples of (energy cost, next state) for valid hallway-to-room moves.
    """
    hall, rooms = state
    for pos, amph in enumerate(hall):
        if amph == ".":
            continue
        room_idx = ord(amph) - ord("A")
        room = list(rooms[room_idx])
        doorway = ROOM_POSITIONS[room_idx]
        if not path_clear(hall, pos, doorway):
            continue
        if not room_ready(tuple(room), amph):
            continue
        try:
            depth = max(i for i, ch in enumerate(room) if ch == ".")
        except ValueError:
            # room full
            continue
        steps = abs(pos - doorway) + depth + 1
        cost = steps * ENERGY[amph]
        room[depth] = amph
        new_hall = list(hall)
        new_hall[pos] = "."
        new_rooms = list(rooms)
        new_rooms[room_idx] = tuple(room)
        yield cost, (tuple(new_hall), tuple(new_rooms))


def moves_from_rooms(state: State) -> Iterable[Tuple[int, State]]:
    """
    Yield moves where amphipods exit rooms into the hallway.

    Args:
        state: Current hallway and room configuration.

    Yields:
        Tuples of (energy cost, next state) for valid room-to-hall moves.
    """
    hall, rooms = state
    for idx, room in enumerate(rooms):
        occupant = top_occupant(room)
        if occupant is None:
            continue
        depth, amph = occupant
        target_char = chr(ord("A") + idx)
        if amph == target_char and all(ch == target_char for ch in room[depth:]):
            continue
        doorway = ROOM_POSITIONS[idx]
        for dest in HALL_SPOTS:
            if hall[dest] != ".":
                continue
            if not path_clear(hall, doorway, dest):
                continue
            steps = abs(dest - doorway) + depth + 1
            cost = steps * ENERGY[amph]
            new_hall = list(hall)
            new_hall[dest] = amph
            new_room = list(room)
            new_room[depth] = "."
            new_rooms = list(rooms)
            new_rooms[idx] = tuple(new_room)
            yield cost, (tuple(new_hall), tuple(new_rooms))


def organize(start: State) -> int:
    """
    Find the minimum energy required to organize the amphipods.

    Args:
        start: Initial state with hallway and rooms.

    Returns:
        Minimum total energy cost to reach the organized goal state.
    """
    depth = len(start[1][0])
    goal_rooms: Rooms = tuple(tuple(chr(ord("A") + i) for _ in range(depth)) for i in range(4))
    goal: State = (tuple("." for _ in range(11)), goal_rooms)

    pq: List[Tuple[int, State]] = [(0, start)]
    best: Dict[State, int] = {start: 0}
    while pq:
        cost, state = heapq.heappop(pq)
        if state == goal:
            return cost
        if cost != best.get(state, float("inf")):
            continue
        # moves from hallway into rooms have priority
        for move_cost, next_state in moves_from_hall(state):
            new_cost = cost + move_cost
            if new_cost < best.get(next_state, float("inf")):
                best[next_state] = new_cost
                heapq.heappush(pq, (new_cost, next_state))
        for move_cost, next_state in moves_from_rooms(state):
            new_cost = cost + move_cost
            if new_cost < best.get(next_state, float("inf")):
                best[next_state] = new_cost
                heapq.heappush(pq, (new_cost, next_state))
    raise ValueError("no solution found")


def solve_part_one(initial_rooms: List[List[str]]) -> int:
    """
    Calculate least energy to organize the amphipods for part one.

    Args:
        initial_rooms: Parsed room rows (2 deep).

    Returns:
        Minimum energy required to organize when rooms are two rows deep.
    """
    start = build_state([list(room) for room in initial_rooms])
    return organize(start)


def solve_part_two(initial_rooms: List[List[str]]) -> int:
    """
    Calculate least energy for the unfolded burrow in part two.

    Args:
        initial_rooms: Parsed room rows (2 deep) before unfolding.

    Returns:
        Minimum energy to organize using the expanded room depth.
    """
    insert = [["D", "C", "B", "A"], ["D", "B", "A", "C"]]
    expanded_rows = []
    expanded_rows.append([room[0] for room in initial_rooms])
    expanded_rows.extend(insert)
    expanded_rows.append([room[1] for room in initial_rooms])
    rooms = [list(col) for col in zip(*expanded_rows)]
    start = build_state(rooms)
    return organize(start)

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
