"""Never Tell Me The Odds -- Advent of Code 2023 Day 24."""

from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

Hail = Tuple[int, int, int, int, int, int]  # x, y, z, vx, vy, vz


def parse_input(raw: str) -> List[Hail]:
    """Return hailstones as position and velocity tuples."""
    stones: List[Hail] = []
    for line in raw.strip().splitlines():
        pos_str, vel_str = line.split(" @ ")
        x, y, z = (int(v) for v in pos_str.split(", "))
        vx, vy, vz = (int(v) for v in vel_str.split(", "))
        stones.append((x, y, z, vx, vy, vz))
    return stones


def intersects_2d(a: Hail, b: Hail, lo: int, hi: int) -> bool:
    """Check if two hailstones intersect within the square in future."""
    (x1, y1, _, vx1, vy1, _) = a
    (x2, y2, _, vx2, vy2, _) = b
    denom = vx1 * vy2 - vy1 * vx2
    if denom == 0:
        return False
    t1 = Fraction((x2 - x1) * vy2 - (y2 - y1) * vx2, denom)
    t2 = Fraction((x2 - x1) * vy1 - (y2 - y1) * vx1, denom)
    if t1 <= 0 or t2 <= 0:
        return False
    px = x1 + vx1 * t1
    py = y1 + vy1 * t1
    return lo <= px <= hi and lo <= py <= hi


def cross(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Cross product of two 3D vectors."""
    ax, ay, az = a
    bx, by, bz = b
    return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)


def solve_part_one(stones: List[Hail]) -> int:
    """Count intersections within the test area."""
    area_lo = 200000000000000
    area_hi = 400000000000000
    total = 0
    for i, a in enumerate(stones):
        for b in stones[i + 1 :]:
            if intersects_2d(a, b, area_lo, area_hi):
                total += 1
    return total


def solve_part_two(stones: List[Hail]) -> int:
    """Sum of rock start coordinates by solving 9x9 linear system."""
    # Unknowns: rx, ry, rz, vx, vy, vz, kx, ky, kz where k = r x v
    # For each hailstone p,u: k - r x u - p x v + p x u = 0
    unknowns = 9
    stones_sample = stones[:3]
    matrix: List[List[Fraction]] = []
    for p_x, p_y, p_z, v_x, v_y, v_z in stones_sample:
        u = (v_x, v_y, v_z)
        # cross(r, u) components
        # (ry*u_z - rz*u_y, rz*u_x - rx*u_z, rx*u_y - ry*u_x)
        cu = (
            (0, u[2], -u[1]),  # coefficients for rx, ry, rz
            (-u[2], 0, u[0]),
            (u[1], -u[0], 0),
        )
        # cross(p, v) components: (py*vz - pz*vy, pz*vx - px*vz, px*vy - py*vx)
        cpv = (
            (0, -p_z, p_y),  # coefficients for vx, vy, vz
            (p_z, 0, -p_x),
            (-p_y, p_x, 0),
        )
        const = cross((p_x, p_y, p_z), u)
        for comp in range(3):
            row = [Fraction(0) for _ in range(unknowns)]
            # k components
            row[6 + comp] = Fraction(1)
            # -r x u
            row[0] -= cu[comp][0]
            row[1] -= cu[comp][1]
            row[2] -= cu[comp][2]
            # -p x v
            row[3] -= cpv[comp][0]
            row[4] -= cpv[comp][1]
            row[5] -= cpv[comp][2]
            rhs = Fraction(-const[comp])
            matrix.append(row + [rhs])

    # Gaussian elimination
    m = matrix
    for col in range(unknowns):
        pivot = None
        for row in range(col, len(m)):
            if m[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        m[col], m[pivot] = m[pivot], m[col]
        factor = m[col][col]
        m[col] = [v / factor for v in m[col]]
        for row in range(len(m)):
            if row == col:
                continue
            factor = m[row][col]
            if factor == 0:
                continue
            m[row] = [rv - factor * cv for rv, cv in zip(m[row], m[col])]

    rx, ry, rz = (m[i][-1] for i in range(3))
    return int(rx + ry + rz)

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
