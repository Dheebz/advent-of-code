"""Sand Slabs -- Advent of Code 2023 Day 22."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Dict, List, Tuple

Brick = Tuple[int, int, int, int, int, int]  # x1, y1, z1, x2, y2, z2


def parse_input(raw: str) -> List[Brick]:
    """Parse brick coordinates."""
    bricks: List[Brick] = []
    for line in raw.strip().splitlines():
        start, end = line.split("~")
        x1, y1, z1 = (int(v) for v in start.split(","))
        x2, y2, z2 = (int(v) for v in end.split(","))
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        z1, z2 = sorted((z1, z2))
        bricks.append((x1, y1, z1, x2, y2, z2))
    bricks.sort(key=lambda b: b[2])
    return bricks


def settle(bricks: List[Brick]) -> List[Brick]:
    """Drop bricks until they rest."""
    heights: Dict[Tuple[int, int], Tuple[int, int]] = {}  # (x,y) -> (top z, brick id)
    settled: List[Brick] = []
    for idx, brick in enumerate(bricks):
        x1, y1, z1, x2, y2, z2 = brick
        max_under = 0
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                max_under = max(max_under, heights.get((x, y), (0, -1))[0])
        drop = z1 - (max_under + 1)
        new_z1 = z1 - drop
        new_z2 = z2 - drop
        settled_brick = (x1, y1, new_z1, x2, y2, new_z2)
        settled.append(settled_brick)
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                heights[(x, y)] = (new_z2, idx)
    return settled


def overlaps_xy(a: Brick, b: Brick) -> bool:
    """Check if bricks overlap in x,y footprint."""
    return not (a[3] < b[0] or b[3] < a[0] or a[4] < b[1] or b[4] < a[1])


def build_support_graph(bricks: List[Brick]) -> Tuple[Dict[int, List[int]], Dict[int, List[int]]]:
    """Return (supports_from, supported_by)."""
    supports_from: Dict[int, List[int]] = {i: [] for i in range(len(bricks))}
    supported_by: Dict[int, List[int]] = {i: [] for i in range(len(bricks))}
    for i, a in enumerate(bricks):
        for j, b in enumerate(bricks):
            if i == j:
                continue
            if a[5] + 1 == b[2] and overlaps_xy(a, b):
                supports_from[i].append(j)
                supported_by[j].append(i)
    return supports_from, supported_by


def solve_part_one(bricks: List[Brick]) -> int:
    """Bricks that can be safely removed."""
    settled = settle(bricks)
    supports_from, supported_by = build_support_graph(settled)
    safe = 0
    for i, supported in supports_from.items():
        if all(len(supported_by[j]) > 1 for j in supported):
            safe += 1
    return safe


def solve_part_two(bricks: List[Brick]) -> int:
    """Total number of bricks that would fall if each brick were removed."""
    settled = settle(bricks)
    supports_from, supported_by = build_support_graph(settled)
    total = 0
    for start in range(len(settled)):
        falling = set([start])
        queue = deque([start])
        while queue:
            b = queue.popleft()
            for above in supports_from[b]:
                if above in falling:
                    continue
                if all(supporter in falling for supporter in supported_by[above]):
                    falling.add(above)
                    queue.append(above)
        total += len(falling) - 1  # exclude the initial removed brick
    return total

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
