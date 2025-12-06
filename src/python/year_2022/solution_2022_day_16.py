"""Proboscidea Volcanium -- Advent of Code 2022 Day 16."""

from __future__ import annotations

import argparse
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Deque, Dict, List, Tuple

ValveMap = Dict[str, Tuple[int, List[str]]]


def parse_input(raw: str) -> ValveMap:
    """Parse valve flow rates and tunnels."""
    valves: ValveMap = {}
    for line in raw.strip().splitlines():
        parts = line.replace(";", "").replace(",", "").split()
        name = parts[1]
        rate = int(parts[4].split("=")[1])
        neighbors = parts[9:]
        valves[name] = (rate, neighbors)
    return valves


def compute_distances(valves: ValveMap) -> Dict[str, Dict[str, int]]:
    """Shortest path between all valves via BFS."""
    dist: Dict[str, Dict[str, int]] = {}
    for start in valves:
        queue: Deque[Tuple[str, int]] = deque([(start, 0)])
        seen = {start}
        dist[start] = {}
        while queue:
            node, d = queue.popleft()
            dist[start][node] = d
            for neighbor in valves[node][1]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, d + 1))
    return dist


def solve_part_one(valves: ValveMap) -> int:
    """Max pressure with one actor in 30 minutes."""
    distances = compute_distances(valves)
    useful = [name for name, (rate, _) in valves.items() if rate > 0]
    bit_index = {name: i for i, name in enumerate(useful)}

    @lru_cache(maxsize=None)
    def dfs(position: str, time_left: int, opened: int) -> int:
        best = 0
        for name in useful:
            bit = 1 << bit_index[name]
            if opened & bit:
                continue
            travel = distances[position][name] + 1
            if travel >= time_left:
                continue
            remaining = time_left - travel
            release = valves[name][0] * remaining
            best = max(best, release + dfs(name, remaining, opened | bit))
        return best

    return dfs("AA", 30, 0)


def solve_part_two(valves: ValveMap) -> int:
    """Max pressure with elephant helper in 26 minutes."""
    distances = compute_distances(valves)
    useful = [name for name, (rate, _) in valves.items() if rate > 0]
    bit_index = {name: i for i, name in enumerate(useful)}
    best_for_mask: Dict[int, int] = {}

    def dfs(position: str, time_left: int, opened: int, pressure: int) -> None:
        best_for_mask[opened] = max(best_for_mask.get(opened, 0), pressure)
        for name in useful:
            bit = 1 << bit_index[name]
            if opened & bit:
                continue
            travel = distances[position][name] + 1
            if travel >= time_left:
                continue
            remaining = time_left - travel
            release = valves[name][0] * remaining
            dfs(name, remaining, opened | bit, pressure + release)

    dfs("AA", 26, 0, 0)

    masks = list(best_for_mask.items())
    masks.sort(key=lambda kv: kv[1], reverse=True)
    best = 0
    for i, (mask1, score1) in enumerate(masks):
        if score1 * 2 < best:
            break
        for mask2, score2 in masks[i:]:
            if mask1 & mask2 == 0:
                best = max(best, score1 + score2)
                break
    return best

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
