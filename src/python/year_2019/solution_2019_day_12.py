"""The N-Body Problem -- Advent of Code 2019 Day 12."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import List, Tuple

Vec3 = Tuple[int, int, int]


def parse_input(raw: str) -> List[Vec3]:
    """Parse moon positions from the input.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        List[Vec3]: Initial positions for each moon.
    """
    moons = []
    pattern = re.compile(r"<x=(-?\d+), y=(-?\d+), z=(-?\d+)>")
    for line in raw.strip().splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        moons.append(tuple(int(value) for value in match.groups()))
    return moons


def step(positions: List[Vec3], velocities: List[Vec3]) -> None:
    """Advance the simulation by one time step.

    Args:
        positions (List[Vec3]): Current positions (mutated in place).
        velocities (List[Vec3]): Current velocities (mutated in place).
    """
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            px, py, pz = positions[i]
            qx, qy, qz = positions[j]
            vx, vy, vz = velocities[i]
            wx, wy, wz = velocities[j]
            if px < qx:
                vx += 1
                wx -= 1
            elif px > qx:
                vx -= 1
                wx += 1
            if py < qy:
                vy += 1
                wy -= 1
            elif py > qy:
                vy -= 1
                wy += 1
            if pz < qz:
                vz += 1
                wz -= 1
            elif pz > qz:
                vz -= 1
                wz += 1
            velocities[i] = (vx, vy, vz)
            velocities[j] = (wx, wy, wz)
    for i in range(len(positions)):
        px, py, pz = positions[i]
        vx, vy, vz = velocities[i]
        positions[i] = (px + vx, py + vy, pz + vz)


def total_energy(positions: List[Vec3], velocities: List[Vec3]) -> int:
    """Compute total system energy.

    Args:
        positions (List[Vec3]): Positions of moons.
        velocities (List[Vec3]): Velocities of moons.

    Returns:
        int: Sum of potential * kinetic for all moons.
    """
    energy = 0
    for (x, y, z), (vx, vy, vz) in zip(positions, velocities):
        potential = abs(x) + abs(y) + abs(z)
        kinetic = abs(vx) + abs(vy) + abs(vz)
        energy += potential * kinetic
    return energy


def solve_part_one(initial_positions: List[Vec3], steps_count: int = 1000) -> int:
    """Simulate the system and return total energy.

    Args:
        initial_positions (List[Vec3]): Starting moon positions.
        steps_count (int, optional): Steps to simulate. Defaults to 1000.

    Returns:
        int: Total energy after simulation.
    """
    positions = initial_positions.copy()
    velocities: List[Vec3] = [(0, 0, 0) for _ in positions]
    for _ in range(steps_count):
        step(positions, velocities)
    return total_energy(positions, velocities)


def lcm(a: int, b: int) -> int:
    """Compute least common multiple.

    Args:
        a (int): First value.
        b (int): Second value.

    Returns:
        int: LCM of the two values.
    """
    return abs(a * b) // math.gcd(a, b)


def find_axis_cycle(initial_pos: List[int], initial_vel: List[int]) -> int:
    """Find cycle length for a single axis.

    Args:
        initial_pos (List[int]): Starting positions along the axis.
        initial_vel (List[int]): Starting velocities along the axis.

    Returns:
        int: Number of steps until the state repeats.
    """
    positions = initial_pos.copy()
    velocities = initial_vel.copy()
    seen = 0
    while True:
        # apply gravity
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                if positions[i] < positions[j]:
                    velocities[i] += 1
                    velocities[j] -= 1
                elif positions[i] > positions[j]:
                    velocities[i] -= 1
                    velocities[j] += 1
        # apply velocity
        for i in range(len(positions)):
            positions[i] += velocities[i]
        seen += 1
        if positions == initial_pos and velocities == initial_vel:
            return seen


def solve_part_two(initial_positions: List[Vec3]) -> int:
    """Determine when the entire system repeats.

    Args:
        initial_positions (List[Vec3]): Starting moon positions.

    Returns:
        int: Steps until the system returns to its initial state.
    """
    xs = [p[0] for p in initial_positions]
    ys = [p[1] for p in initial_positions]
    zs = [p[2] for p in initial_positions]
    cycle_x = find_axis_cycle(xs, [0] * len(xs))
    cycle_y = find_axis_cycle(ys, [0] * len(ys))
    cycle_z = find_axis_cycle(zs, [0] * len(zs))
    return lcm(lcm(cycle_x, cycle_y), cycle_z)

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
