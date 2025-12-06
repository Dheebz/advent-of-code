"""Snowverload -- Advent of Code 2023 Day 25."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple

Graph = Dict[str, Set[str]]


def parse_input(raw: str) -> Graph:
    """Return undirected graph."""
    graph: Graph = {}
    for line in raw.strip().splitlines():
        left, right = line.split(": ")
        for dest in right.split():
            graph.setdefault(left, set()).add(dest)
            graph.setdefault(dest, set()).add(left)
    return graph


def stoer_wagner(graph: Graph) -> Tuple[int, Set[str]]:
    """Return (min_cut_weight, partition) using Stoer-Wagner."""
    # work directly with labels to avoid index bookkeeping
    adjacency: Dict[str, Dict[str, int]] = {v: {u: 1 for u in graph[v]} for v in graph}
    groups: Dict[str, Set[str]] = {v: {v} for v in graph}

    best_weight = float("inf")
    best_partition: Set[str] = set()

    while len(adjacency) > 1:
        used: Set[str] = set()
        costs: Dict[str, int] = {v: 0 for v in adjacency}
        order: List[str] = []
        for _ in range(len(adjacency)):
            v_pick = max((v for v in adjacency if v not in used), key=lambda v: costs[v])
            used.add(v_pick)
            order.append(v_pick)
            for neighbor, weight in adjacency[v_pick].items():
                if neighbor not in used:
                    costs[neighbor] += weight

        s, t = order[-2], order[-1]
        cut_weight = costs[t]
        if cut_weight < best_weight:
            best_weight = cut_weight
            best_partition = set(groups[t])

        # merge t into s
        for neighbor, weight in list(adjacency[t].items()):
            if neighbor == s:
                continue
            merged = adjacency[s].get(neighbor, 0) + weight
            adjacency[s][neighbor] = merged
            adjacency[neighbor][s] = merged
        adjacency[s].pop(t, None)
        for neighbor in list(adjacency.keys()):
            adjacency[neighbor].pop(t, None)
        groups[s].update(groups[t])
        adjacency.pop(t)
        groups.pop(t)

    return int(best_weight), best_partition


def solve_part_one(graph: Graph) -> int:
    """Product of component sizes after removing min cut of size 3."""
    weight, partition = stoer_wagner(graph)
    if weight != 3:
        raise ValueError("Unexpected cut weight")
    size_a = len(partition)
    size_b = len(graph) - size_a
    return size_a * size_b


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
