"""Cryostasis -- Advent of Code 2019 Day 25."""

from __future__ import annotations

import argparse
import re
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Set, Tuple

if TYPE_CHECKING:
    from .intcode import Intcode
else:
    try:
        from .intcode import Intcode
    except ImportError:  # pragma: no cover
        from intcode import Intcode  # ty: ignore[unresolved-import]

Output = str


DANGEROUS_ITEMS = {
    "giant electromagnet",
    "infinite loop",
    "escape pod",
    "photons",
    "molten lava",
}

OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}


def parse_input(raw: str) -> List[int]:
    """Parse program values from the input text.

    Args:
        raw (str): Raw comma-separated program.

    Returns:
        List[int]: Intcode program values.
    """
    return [int(value) for value in raw.strip().split(",") if value]


def send_command(machine: Intcode, command: str) -> Output:
    """Send a textual command to the Intcode machine.

    Args:
        machine (Intcode): Running Intcode computer.
        command (str): Command string to send.

    Returns:
        Output: Machine output decoded to text.
    """
    ascii_input = [ord(ch) for ch in command]
    ascii_input.append(10)
    output = machine.run(inputs=ascii_input)
    return "".join(chr(c) for c in output)


def parse_room(output: str) -> Tuple[str, List[str], List[str]]:
    """Parse room description into name, doors, and items.

    Args:
        output (str): Text output from the machine.

    Returns:
        Tuple[str, List[str], List[str]]: Room name, available doors, and items present.
    """
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    name = ""
    doors: List[str] = []
    items: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("=="):
            name = line.strip("= ").strip()
        elif line.startswith("Doors here lead:"):
            i += 1
            while i < len(lines) and lines[i].startswith("-"):
                doors.append(lines[i][2:])
                i += 1
            continue
        elif line.startswith("Items here:"):
            i += 1
            while i < len(lines) and lines[i].startswith("-"):
                items.append(lines[i][2:])
                i += 1
            continue
        i += 1
    return name, doors, items


def explore_map(
    machine: Intcode,
) -> Tuple[Dict[str, Dict[str, str]], Set[str], str | None, str | None, str]:
    """DFS the map, collecting safe items and building graph metadata.

    Args:
        machine (Intcode): Intcode computer controlling the droid.

    Returns:
        Tuple[Dict[str, Dict[str, str]], Set[str], str | None, str | None, str]:
            Room graph, collected items, checkpoint name, pressure direction, and start room.
    """
    graph: Dict[str, Dict[str, str]] = {}
    collected: Set[str] = set()
    checkpoint = None
    pressure_direction = None

    def dfs(current_room: str, came_from: str | None, output: str) -> None:
        nonlocal checkpoint, pressure_direction
        name, doors, items = parse_room(output)
        graph.setdefault(name, {})
        # pick up safe items
        for item in items:
            if item in DANGEROUS_ITEMS or item in collected:
                continue
            send_command(machine, f"take {item}")
            collected.add(item)

        if name == "Security Checkpoint":
            checkpoint = name
            # assume the door not equal to came_from is the pressure floor
            for door in doors:
                if door != came_from:
                    pressure_direction = door
            # do not step onto the pressure plate during exploration
        for door in doors:
            if name == "Security Checkpoint" and door == pressure_direction:
                continue  # skip the pressure floor until testing
            if door in graph[name]:
                continue
            response = send_command(machine, door)
            next_name, _, _ = parse_room(response)
            graph[name][door] = next_name
            graph.setdefault(next_name, {})[OPPOSITE[door]] = name
            dfs(next_name, OPPOSITE[door], response)
            back_output = send_command(machine, OPPOSITE[door])
            back_name, _, _ = parse_room(back_output)
            if back_name != name:
                raise ValueError("failed to backtrack to expected room")

    initial_output = "".join(chr(c) for c in machine.run())
    start_name, _, _ = parse_room(initial_output)
    dfs(start_name, None, initial_output)
    return graph, collected, checkpoint, pressure_direction, start_name


def path_between(graph: Dict[str, Dict[str, str]], start: str, target: str) -> List[str]:
    """Find a path of directions between two rooms.

    Args:
        graph (Dict[str, Dict[str, str]]): Room adjacency graph.
        start (str): Starting room name.
        target (str): Target room name.

    Returns:
        List[str]: Directions to move from start to target.
    """
    queue = deque([(start, [])])
    seen = {start}
    while queue:
        room, path = queue.popleft()
        if room == target:
            return path
        for direction, neighbor in graph.get(room, {}).items():
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, path + [direction]))
    raise ValueError("no path")


def move_along(machine: Intcode, directions: List[str]) -> str:
    """Follow the provided directions using the machine.

    Args:
        machine (Intcode): Intcode computer.
        directions (List[str]): Directions to send in order.

    Returns:
        str: Output from the final move.
    """
    output = ""
    for direction in directions:
        output = send_command(machine, direction)
    return output


def solve_part_one(program: List[int]) -> int:
    """Find the correct item combination to pass the pressure floor."""
    machine = Intcode(program)
    graph, collected, checkpoint, pressure_direction, start = explore_map(machine)
    if checkpoint is None or pressure_direction is None:
        raise ValueError("failed to locate checkpoint")

    # Move to checkpoint with all collected items.
    path_to_checkpoint = path_between(graph, start, checkpoint)
    move_along(machine, path_to_checkpoint)

    # Prepare clones for testing combinations.
    checkpoint_state = machine.clone()
    items = list(collected)
    direction_to_exit = pressure_direction

    for mask in range(1, 1 << len(items)):
        test_machine = checkpoint_state.clone()
        # Drop all items first.
        for item in items:
            send_command(test_machine, f"drop {item}")
        # Take selected subset.
        for idx, item in enumerate(items):
            if mask & (1 << idx):
                send_command(test_machine, f"take {item}")
        output = send_command(test_machine, direction_to_exit)
        if "Alert" not in output:
            # success; parse code
            match = re.search(r"([0-9]+)", output)
            if match:
                return int(match.group(1))
    raise ValueError("no valid combination found")


def solve_part_two(input_data: object) -> str:
    """Return the celebratory message."""
    return "Merry Christmas!"

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
