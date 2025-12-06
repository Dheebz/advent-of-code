"""Monkey Map -- Advent of Code 2022 Day 22."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

Facing = int  # 0=right,1=down,2=left,3=up
Vec3 = Tuple[int, int, int]


@dataclass
class CubeFace:
    """
    Describe a cube face discovered on the unfolded map.

    Attributes:
        grid_pos: Coordinate of the face on the unfolded grid.
        right: World vector pointing toward this face's right edge.
        down: World vector pointing toward this face's bottom edge.
        normal: World normal vector pointing out of this face.
        origin: World coordinate of the top-left corner of the face.
    """

    grid_pos: Tuple[int, int]  # face coordinate in the unfolded net
    right: Vec3
    down: Vec3
    normal: Vec3
    origin: Vec3  # world coordinate of top-left corner


def parse_input(raw: str) -> Tuple[List[str], List[str]]:
    """Return map lines and path instructions."""
    board_str, path_str = raw.split("\n\n")
    board = board_str.splitlines()
    return board, list(path_str.strip())


def parse_path(path_tokens: List[str]) -> List[str]:
    """Split the path string into numbers and turns."""
    result: List[str] = []
    num = ""
    for ch in path_tokens:
        if ch.isdigit():
            num += ch
        else:
            if num:
                result.append(num)
                num = ""
            result.append(ch)
    if num:
        result.append(num)
    return result


def wrap_flat(board: List[str], x: int, y: int, facing: Facing) -> Tuple[int, int]:
    """Wrap on the flat map for part 1."""
    if facing == 0:  # right
        nx = next(i for i, ch in enumerate(board[y]) if ch != " ")
        return nx, y
    if facing == 2:  # left
        nx = max(i for i, ch in enumerate(board[y]) if ch != " ")
        return nx, y
    if facing == 1:  # down
        ny = next(i for i, row in enumerate(board) if len(row) > x and row[x] != " ")
        return x, ny
    # up
    ny = max(i for i, row in enumerate(board) if len(row) > x and row[x] != " ")
    return x, ny


def cross(a: Vec3, b: Vec3) -> Vec3:
    """Cross product of two 3D vectors with small integer components."""
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def rotate(vec: Vec3, axis: Vec3, sign: int) -> Vec3:
    """Rotate vec 90 degrees around axis (sign=1 clockwise with right-hand rule)."""
    if vec == axis or vec == (-axis[0], -axis[1], -axis[2]):
        return vec
    return cross(axis, vec) if sign == 1 else cross(vec, axis)


def build_cube(board: List[str], size: int) -> Dict[Tuple[int, int], CubeFace]:
    """Determine face orientations and positions by folding the net."""
    faces: Dict[Tuple[int, int], CubeFace] = {}
    height = len(board)
    width = max(len(row) for row in board)

    # Identify face positions
    available = []
    for fy in range(0, height, size):
        for fx in range(0, width, size):
            if fy < len(board) and fx < len(board[fy]) and board[fy][fx] != " ":
                available.append((fx // size, fy // size))

    start_face_pos = min(available, key=lambda p: (p[1], p[0]))
    faces[start_face_pos] = CubeFace(
        start_face_pos,
        (1, 0, 0),  # right
        (0, 1, 0),  # down
        (0, 0, 1),  # normal
        (0, 0, 0),  # origin
    )

    queue = [start_face_pos]
    while queue:
        fx, fy = queue.pop()
        face = faces[(fx, fy)]
        assert face is not None
        net_origin = face.origin
        for dx, dy, axis, sign in [
            (1, 0, face.down, 1),  # move right across down-axis hinge
            (-1, 0, face.down, -1),  # move left
            (0, 1, face.right, -1),  # move down across right-axis hinge
            (0, -1, face.right, 1),  # move up
        ]:
            npos = (fx + dx, fy + dy)
            if npos in available and npos not in faces:
                new_right = rotate(face.right, axis, sign)
                new_down = rotate(face.down, axis, sign)
                new_normal = rotate(face.normal, axis, sign)

                # Hinge line point (where the two faces touch)
                hinge_point = (
                    face.origin[0]
                    + (face.right[0] * max(dx, 0) + face.down[0] * max(dy, 0)) * size,
                    face.origin[1]
                    + (face.right[1] * max(dx, 0) + face.down[1] * max(dy, 0)) * size,
                    face.origin[2]
                    + (face.right[2] * max(dx, 0) + face.down[2] * max(dy, 0)) * size,
                )
                # Neighbor origin before folding (in the net)
                neighbor_net_origin = (
                    net_origin[0] + face.right[0] * dx * size + face.down[0] * dy * size,
                    net_origin[1] + face.right[1] * dx * size + face.down[1] * dy * size,
                    net_origin[2] + face.right[2] * dx * size + face.down[2] * dy * size,
                )

                def rotate_point(point: Vec3, axis_vec: Vec3, pivot: Vec3, sgn: int) -> Vec3:
                    """Rotate point 90 degrees around axis through pivot."""
                    px, py, pz = point[0] - pivot[0], point[1] - pivot[1], point[2] - pivot[2]
                    ax, ay, az = axis_vec
                    dot = px * ax + py * ay + pz * az
                    cross_vec = (ay * pz - az * py, az * px - ax * pz, ax * py - ay * px)
                    rx = ax * dot + cross_vec[0] * sgn
                    ry = ay * dot + cross_vec[1] * sgn
                    rz = az * dot + cross_vec[2] * sgn
                    return (rx + pivot[0], ry + pivot[1], rz + pivot[2])

                new_origin = rotate_point(neighbor_net_origin, axis, hinge_point, sign)
                faces[npos] = CubeFace(npos, new_right, new_down, new_normal, new_origin)
                queue.append(npos)
    return faces


def step_cube(
    faces: Dict[Tuple[int, int], CubeFace],
    normal_to_face: Dict[Vec3, Tuple[int, int]],
    center_lookup: Dict[Tuple[int, int, int], Tuple[Tuple[int, int], int, int]],
    size: int,
    x: int,
    y: int,
    facing: Facing,
) -> Tuple[int, int, Facing]:
    """Move one step on the folded cube using 3D coordinates."""
    fx, fy = x // size, y // size
    face = faces[(fx, fy)]
    lx, ly = x % size, y % size

    # centers scaled by 2 to keep integer math (0.5 increments)
    wx = face.origin[0] * 2 + face.right[0] * (2 * lx + 1) + face.down[0] * (2 * ly + 1)
    wy = face.origin[1] * 2 + face.right[1] * (2 * lx + 1) + face.down[1] * (2 * ly + 1)
    wz = face.origin[2] * 2 + face.right[2] * (2 * lx + 1) + face.down[2] * (2 * ly + 1)

    if facing == 0:
        dir_vec = face.right
        edge_axis = face.down
        pivot = (
            face.origin[0] * 2 + face.right[0] * (2 * size) + face.down[0] * (2 * ly + 1),
            face.origin[1] * 2 + face.right[1] * (2 * size) + face.down[1] * (2 * ly + 1),
            face.origin[2] * 2 + face.right[2] * (2 * size) + face.down[2] * (2 * ly + 1),
        )
    elif facing == 2:
        dir_vec = (-face.right[0], -face.right[1], -face.right[2])
        edge_axis = face.down
        pivot = (
            face.origin[0] * 2 + face.down[0] * (2 * ly + 1),
            face.origin[1] * 2 + face.down[1] * (2 * ly + 1),
            face.origin[2] * 2 + face.down[2] * (2 * ly + 1),
        )
    elif facing == 1:
        dir_vec = face.down
        edge_axis = face.right
        pivot = (
            face.origin[0] * 2 + face.right[0] * (2 * lx + 1) + face.down[0] * (2 * size),
            face.origin[1] * 2 + face.right[1] * (2 * lx + 1) + face.down[1] * (2 * size),
            face.origin[2] * 2 + face.right[2] * (2 * lx + 1) + face.down[2] * (2 * size),
        )
    else:
        dir_vec = (-face.down[0], -face.down[1], -face.down[2])
        edge_axis = face.right
        pivot = (
            face.origin[0] * 2 + face.right[0] * (2 * lx + 1),
            face.origin[1] * 2 + face.right[1] * (2 * lx + 1),
            face.origin[2] * 2 + face.right[2] * (2 * lx + 1),
        )

    wx += dir_vec[0] * 2
    wy += dir_vec[1] * 2
    wz += dir_vec[2] * 2

    if (wx, wy, wz) in center_lookup:
        target_pos, nlx, nly = center_lookup[(wx, wy, wz)]
        target = faces[target_pos]
        moved_dir = dir_vec
    else:
        sign = 1 if rotate(face.normal, edge_axis, 1) == dir_vec else -1
        rx = wx - pivot[0]
        ry = wy - pivot[1]
        rz = wz - pivot[2]
        ax, ay, az = edge_axis
        dot = rx * ax + ry * ay + rz * az
        cross_vec = (ay * rz - az * ry, az * rx - ax * rz, ax * ry - ay * rx)
        wxr = ax * dot + cross_vec[0] * sign + pivot[0]
        wyr = ay * dot + cross_vec[1] * sign + pivot[1]
        wzr = az * dot + cross_vec[2] * sign + pivot[2]
        target_pos, nlx, nly = center_lookup[(wxr, wyr, wzr)]
        target = faces[target_pos]
        moved_dir = rotate(dir_vec, edge_axis, sign)

    if moved_dir == target.right:
        nfacing = 0
    elif moved_dir == (-target.right[0], -target.right[1], -target.right[2]):
        nfacing = 2
    elif moved_dir == target.down:
        nfacing = 1
    else:
        nfacing = 3

    new_x = target_pos[0] * size + nlx
    new_y = target_pos[1] * size + nly
    return new_x, new_y, nfacing


def walk(
    board: List[str],
    path: List[str],
    wrap_func,
    facing_update=None,
) -> Tuple[int, int, Facing]:
    """Execute the path using provided wrapping logic."""
    x = next(i for i, ch in enumerate(board[0]) if ch != " ")
    y = 0
    facing: Facing = 0
    for instr in path:
        if instr == "L":
            facing = (facing - 1) % 4
        elif instr == "R":
            facing = (facing + 1) % 4
        else:
            steps = int(instr)
            for _ in range(steps):
                if facing == 0:
                    nx, ny = x + 1, y
                elif facing == 1:
                    nx, ny = x, y + 1
                elif facing == 2:
                    nx, ny = x - 1, y
                else:
                    nx, ny = x, y - 1
                nf = facing
                if not (0 <= ny < len(board) and 0 <= nx < len(board[ny]) and board[ny][nx] != " "):
                    result = wrap_func(x, y, facing)
                    if facing_update:
                        nx, ny, nf = result
                    else:
                        nx, ny = result
                if board[ny][nx] == "#":
                    break
                x, y, facing = nx, ny, nf
    return x, y, facing


def password(x: int, y: int, facing: Facing) -> int:
    """Compute the final password."""
    return 1000 * (y + 1) + 4 * (x + 1) + facing


def solve_part_one(data: Tuple[List[str], List[str]]) -> int:
    """Password using flat wrapping."""
    board, path = data
    parsed_path = parse_path(path)

    def flat_wrap(x: int, y: int, facing: Facing) -> Tuple[int, int]:
        return wrap_flat(board, x, y, facing)

    x, y, facing = walk(board, parsed_path, flat_wrap)
    return password(x, y, facing)


def solve_part_two(data: Tuple[List[str], List[str]]) -> int:
    """Password when folding the board into a cube."""
    board, path = data
    parsed_path = parse_path(path)
    face_size = min(len(segment) for row in board for segment in row.split(" ") if segment)
    faces = build_cube(board, face_size)

    normal_to_face = {f.normal: pos for pos, f in faces.items()}
    center_lookup: Dict[Tuple[int, int, int], Tuple[Tuple[int, int], int, int]] = {}
    for fpos, f in faces.items():
        for i in range(face_size):
            for j in range(face_size):
                wx = f.origin[0] * 2 + f.right[0] * (2 * i + 1) + f.down[0] * (2 * j + 1)
                wy = f.origin[1] * 2 + f.right[1] * (2 * i + 1) + f.down[1] * (2 * j + 1)
                wz = f.origin[2] * 2 + f.right[2] * (2 * i + 1) + f.down[2] * (2 * j + 1)
                center_lookup[(wx, wy, wz)] = (fpos, i, j)

    def cube_wrap(x: int, y: int, facing: Facing) -> Tuple[int, int, Facing]:
        return step_cube(faces, normal_to_face, center_lookup, face_size, x, y, facing)

    x, y, facing = walk(board, parsed_path, cube_wrap, facing_update=True)
    return password(x, y, facing)

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
