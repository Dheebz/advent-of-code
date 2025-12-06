"""Advent of Code 2024 Day 15: Warehouse Woes."""

from __future__ import annotations

import argparse
from pathlib import Path

Point = tuple[int, int]
State = tuple[set[Point], set[Point], Point, int, int]
Data = tuple[list[str], str]


def parse_input(raw: str) -> Data:
    """
    Parse the warehouse layout and movement sequence.

    Args:
        raw: Input text containing the grid and move list separated by a blank line.

    Returns:
        Tuple containing the grid lines and the concatenated moves string.
    """
    sections = raw.strip().split("\n\n")
    grid_lines = sections[0].splitlines()
    moves = "".join(sections[1].splitlines())
    return grid_lines, moves


def build_state(grid_lines: list[str], expand: bool = False) -> State:
    """
    Build the simulation state from grid lines.

    Args:
        grid_lines: List of grid rows.
        expand: Whether to double the width for the wide warehouse.

    Returns:
        Tuple containing boxes, walls, robot position, grid width, and height.
    """
    lines = grid_lines
    if expand:
        new_lines: list[str] = []
        for line in grid_lines:
            expanded = (
                line.replace("#", "##").replace("O", "[]").replace(".", "..").replace("@", "@.")
            )
            new_lines.append(expanded)
        lines = new_lines

    boxes: set[Point] = set()
    walls: set[Point] = set()
    robot: Point = (0, 0)
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch == "#":
                walls.add((x, y))
            elif ch == "O":
                boxes.add((x, y))
            elif ch == "[":
                boxes.add((x, y))
            elif ch == "@":
                robot = (x, y)

    width = len(lines[0])
    height = len(lines)
    return boxes, walls, robot, width, height


DIRS = {"^": (0, -1), "v": (0, 1), "<": (-1, 0), ">": (1, 0)}


def simulate_part_one(state: State, moves: str) -> set[Point]:
    """
    Run the original simulation, treating each box as single-tile.

    Args:
        state: Tuple with current boxes, walls, robot position, width, and height.
        moves: Movement string from the parsed input.

    Returns:
        Set of boxes after performing the move sequence.
    """
    boxes, walls, robot, _, _ = state
    boxes = set(boxes)
    rx, ry = robot
    for move in moves:
        dx, dy = DIRS[move]
        nx, ny = rx + dx, ry + dy
        if (nx, ny) in walls:
            continue
        if (nx, ny) not in boxes:
            rx, ry = nx, ny
            continue
        # push chain of boxes
        cx, cy = nx, ny
        while (cx, cy) in boxes:
            cx += dx
            cy += dy
        if (cx, cy) in walls:
            continue
        # shift boxes
        while (cx, cy) != (nx, ny):
            px, py = cx - dx, cy - dy
            boxes.remove((px, py))
            boxes.add((cx, cy))
            cx, cy = px, py
        rx, ry = nx, ny
    return boxes


def box_for_cell(cell: Point, boxes: set[Point]) -> Point | None:
    """
    Identify the box occupying or touching a cell.

    Args:
        cell: Target coordinate to inspect.
        boxes: Set of box edge positions.

    Returns:
        The coordinate of the box's left edge if one occupies or straddles `cell`.
    """
    if cell in boxes:
        return cell
    left = (cell[0] - 1, cell[1])
    if left in boxes:
        return left
    return None


def simulate_part_two(state: State, moves: str) -> set[Point]:
    """
    Run the expanded simulation with wide boxes.

    Args:
        state: Tuple with box positions, walls, robot location, width, and height.
        moves: Movement string for the robot.

    Returns:
        Set of boxes after executing the expanded rules.
    """
    boxes, walls, robot, _, _ = state
    boxes = set(boxes)  # left edges only
    rx, ry = robot
    for move in moves:
        dx, dy = DIRS[move]
        nx, ny = rx + dx, ry + dy
        if (nx, ny) in walls:
            continue
        target_box = box_for_cell((nx, ny), boxes)
        if target_box is None:
            rx, ry = nx, ny
            continue

        if dy == 0:  # horizontal push
            chain: list[Point] = [target_box]
            cx = target_box[0] + (2 if dx == 1 else -1)
            cy = target_box[1]
            while True:
                cell = (cx, cy)
                if cell in walls:
                    chain = []
                    break
                b = box_for_cell(cell, boxes)
                if b is None:
                    break
                chain.append(b)
                cx = b[0] + (2 if dx == 1 else -1)
            if not chain:
                continue
            for bx, by in reversed(chain):
                boxes.remove((bx, by))
                boxes.add((bx + dx, by))
            rx, ry = nx, ny
        else:  # vertical push
            queue: list[Point] = [target_box]
            move_boxes: set[Point] = {target_box}
            blocked = False
            while queue and not blocked:
                bx, by = queue.pop()
                for ox in (0, 1):
                    cell = (bx + ox, by + dy)
                    if cell in walls:
                        blocked = True
                        break
                    neighbor_box = box_for_cell(cell, boxes)
                    if neighbor_box is not None and neighbor_box not in move_boxes:
                        move_boxes.add(neighbor_box)
                        queue.append(neighbor_box)
            if blocked:
                continue
            for bx, by in sorted(move_boxes, key=lambda p: p[1], reverse=dy == -1):
                boxes.remove((bx, by))
                boxes.add((bx, by + dy))
            rx, ry = nx, ny
    return boxes


def gps_sum(boxes: set[Point]) -> int:
    """
    Compute the GPS sum for a set of boxes.

    Args:
        boxes: Set of box coordinates.

    Returns:
        Sum of ``100*y + x`` for each box coordinate.
    """
    return sum(100 * y + x for x, y in boxes)


def solve_part_one(data: Data) -> int:
    """
    Compute the GPS sum for part one.

    Args:
        data: Tuple containing grid lines and the move string.

    Returns:
        GPS sum after running the standard simulation.
    """
    grid_lines, moves = data
    state = build_state(grid_lines, expand=False)
    final_boxes = simulate_part_one(state, moves)
    return gps_sum(final_boxes)


def solve_part_two(data: Data) -> int:
    """
    Compute the GPS sum for the expanded warehouse in part two.

    Args:
        data: Tuple containing grid lines and the move string.

    Returns:
        GPS sum after running the expanded simulation.
    """
    grid_lines, moves = data
    state = build_state(grid_lines, expand=True)
    final_boxes = simulate_part_two(state, moves)
    return gps_sum(final_boxes)

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
