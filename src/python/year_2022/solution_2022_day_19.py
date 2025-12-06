"""Not Enough Minerals -- Advent of Code 2022 Day 19."""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

Blueprint = Dict[str, Tuple[int, int, int]]  # ore, clay, obsidian cost


def parse_input(raw: str) -> List[Blueprint]:
    """Parse blueprint costs."""
    blueprints: List[Blueprint] = []
    for line in raw.strip().splitlines():
        parts = line.replace(":", "").replace(",", "").split()
        ore_robot = (int(parts[6]), 0, 0)
        clay_robot = (int(parts[12]), 0, 0)
        obs_robot = (int(parts[18]), int(parts[21]), 0)
        geo_robot = (int(parts[27]), 0, int(parts[30]))
        blueprints.append(
            {
                "ore": ore_robot,
                "clay": clay_robot,
                "obsidian": obs_robot,
                "geode": geo_robot,
            }
        )
    return blueprints


def max_geodes(bp: Blueprint, time_limit: int) -> int:
    """Compute max geodes collectible within time limit."""
    max_ore_cost = max(cost[0] for cost in bp.values())
    max_clay_cost = bp["obsidian"][1]
    max_obs_cost = bp["geode"][2]

    best_so_far = [0]

    @lru_cache(maxsize=None)
    def dfs(
        time_left: int,
        ore: int,
        clay: int,
        obs: int,
        geodes: int,
        ore_r: int,
        clay_r: int,
        obs_r: int,
        geo_r: int,
    ) -> int:
        if time_left == 0:
            return geodes

        # optimistic upper bound to prune
        max_possible = geodes + geo_r * time_left + (time_left * (time_left - 1)) // 2
        if max_possible <= best_so_far[0]:
            return geodes

        # clamp resources to avoid unneeded stockpiling
        ore = min(ore, time_left * max_ore_cost - ore_r * (time_left - 1))
        clay = min(clay, time_left * max_clay_cost - clay_r * (time_left - 1))
        obs = min(obs, time_left * max_obs_cost - obs_r * (time_left - 1))

        best = geodes  # assume we build nothing else
        # Decide what to build this minute
        build_options = []
        if ore >= bp["geode"][0] and obs >= bp["geode"][2]:
            build_options = ["geode"]
        else:
            if ore_r < max_ore_cost and ore >= bp["ore"][0]:
                build_options.append("ore")
            if clay_r < max_clay_cost and ore >= bp["clay"][0]:
                build_options.append("clay")
            if obs_r < max_obs_cost and ore >= bp["obsidian"][0] and clay >= bp["obsidian"][1]:
                build_options.append("obsidian")
            build_options.append(None)

        for choice in build_options:
            n_ore, n_clay, n_obs, n_geo = ore, clay, obs, geodes
            n_ore_r, n_clay_r, n_obs_r, n_geo_r = ore_r, clay_r, obs_r, geo_r
            if choice:
                cost = bp[choice]
                n_ore -= cost[0]
                n_clay -= cost[1]
                n_obs -= cost[2]
            # collect resources
            n_ore += ore_r
            n_clay += clay_r
            n_obs += obs_r
            n_geo += geo_r

            if choice == "ore":
                n_ore_r += 1
            elif choice == "clay":
                n_clay_r += 1
            elif choice == "obsidian":
                n_obs_r += 1
            elif choice == "geode":
                n_geo_r += 1

            best = max(
                best,
                dfs(
                    time_left - 1,
                    n_ore,
                    n_clay,
                    n_obs,
                    n_geo,
                    n_ore_r,
                    n_clay_r,
                    n_obs_r,
                    n_geo_r,
                ),
            )

        best_so_far[0] = max(best_so_far[0], best)
        return best

    return dfs(time_limit, 0, 0, 0, 0, 1, 0, 0, 0)


def solve_part_one(blueprints: List[Blueprint]) -> int:
    """Quality level sum for 24 minutes."""
    total = 0
    for idx, bp in enumerate(blueprints, start=1):
        total += idx * max_geodes(bp, 24)
    return total


def solve_part_two(blueprints: List[Blueprint]) -> int:
    """Product of max geodes for first three blueprints in 32 minutes."""
    product = 1
    for bp in blueprints[:3]:
        product *= max_geodes(bp, 32)
    return product

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
