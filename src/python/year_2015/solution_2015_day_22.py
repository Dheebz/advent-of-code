"""Wizard Simulator 20XX -- Advent of Code 2015 Day 22."""

from __future__ import annotations

import argparse
import heapq
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple, cast

QueueItem = tuple[int, int, Literal[True] | Literal[False], "State"]


@dataclass(frozen=True)
class State:
    """Snapshot of the battle state."""

    player_hp: int
    player_mana: int
    boss_hp: int
    shield_timer: int
    poison_timer: int
    recharge_timer: int


def parse_input(raw: str) -> Tuple[int, int]:
    """Parse boss hit points and damage."""
    lines = raw.strip().splitlines()
    boss_hp = int(lines[0].split(": ")[1])
    boss_damage = int(lines[1].split(": ")[1])
    return boss_hp, boss_damage


def apply_effects(state: State) -> State:
    """Apply active effects and decrement their timers."""
    boss_hp = state.boss_hp
    player_mana = state.player_mana
    shield = max(0, state.shield_timer - 1)
    poison = max(0, state.poison_timer - 1)
    recharge = max(0, state.recharge_timer - 1)

    if state.poison_timer:
        boss_hp -= 3
    if state.recharge_timer:
        player_mana += 101

    return State(
        player_hp=state.player_hp,
        player_mana=player_mana,
        boss_hp=boss_hp,
        shield_timer=shield,
        poison_timer=poison,
        recharge_timer=recharge,
    )


def armor_from_shield(state: State) -> int:
    """Return current armor bonus from shield."""
    return 7 if state.shield_timer else 0


def minimal_mana_to_win(boss_hp: int, boss_damage: int, hard_mode: bool = False) -> int:
    """Search for the minimal mana cost to win the fight."""
    spells = {
        "missile": (53, 0),
        "drain": (73, 0),
        "shield": (113, 6),
        "poison": (173, 6),
        "recharge": (229, 5),
    }

    start = State(
        player_hp=50,
        player_mana=500,
        boss_hp=boss_hp,
        shield_timer=0,
        poison_timer=0,
        recharge_timer=0,
    )
    heap: list[QueueItem] = [(0, 0, True, start)]  # cost, tie, player_turn, state

    seen = {}

    counter = 1
    while heap:
        spent, _, player_turn, state = heapq.heappop(heap)
        key = (player_turn, state)
        if key in seen and seen[key] <= spent:
            continue
        seen[key] = spent

        if player_turn and hard_mode:
            if state.player_hp <= 1:
                continue
            state = State(
                player_hp=state.player_hp - 1,
                player_mana=state.player_mana,
                boss_hp=state.boss_hp,
                shield_timer=state.shield_timer,
                poison_timer=state.poison_timer,
                recharge_timer=state.recharge_timer,
            )

        state = apply_effects(state)
        if state.boss_hp <= 0:
            return spent

        if player_turn:
            for name, (cost, duration) in spells.items():
                if cost > state.player_mana:
                    continue
                if name == "shield" and state.shield_timer:
                    continue
                if name == "poison" and state.poison_timer:
                    continue
                if name == "recharge" and state.recharge_timer:
                    continue

                next_state = State(
                    player_hp=state.player_hp,
                    player_mana=state.player_mana - cost,
                    boss_hp=state.boss_hp,
                    shield_timer=state.shield_timer,
                    poison_timer=state.poison_timer,
                    recharge_timer=state.recharge_timer,
                )

                if name == "missile":
                    next_state = State(
                        player_hp=next_state.player_hp,
                        player_mana=next_state.player_mana,
                        boss_hp=next_state.boss_hp - 4,
                        shield_timer=next_state.shield_timer,
                        poison_timer=next_state.poison_timer,
                        recharge_timer=next_state.recharge_timer,
                    )
                elif name == "drain":
                    next_state = State(
                        player_hp=next_state.player_hp + 2,
                        player_mana=next_state.player_mana,
                        boss_hp=next_state.boss_hp - 2,
                        shield_timer=next_state.shield_timer,
                        poison_timer=next_state.poison_timer,
                        recharge_timer=next_state.recharge_timer,
                    )
                elif name == "shield":
                    next_state = State(
                        player_hp=next_state.player_hp,
                        player_mana=next_state.player_mana,
                        boss_hp=next_state.boss_hp,
                        shield_timer=duration,
                        poison_timer=next_state.poison_timer,
                        recharge_timer=next_state.recharge_timer,
                    )
                elif name == "poison":
                    next_state = State(
                        player_hp=next_state.player_hp,
                        player_mana=next_state.player_mana,
                        boss_hp=next_state.boss_hp,
                        shield_timer=next_state.shield_timer,
                        poison_timer=duration,
                        recharge_timer=next_state.recharge_timer,
                    )
                elif name == "recharge":
                    next_state = State(
                        player_hp=next_state.player_hp,
                        player_mana=next_state.player_mana,
                        boss_hp=next_state.boss_hp,
                        shield_timer=next_state.shield_timer,
                        poison_timer=next_state.poison_timer,
                        recharge_timer=duration,
                    )

                heapq.heappush(heap, cast(QueueItem, (spent + cost, counter, False, next_state)))
                counter += 1
        else:
            damage = max(1, boss_damage - armor_from_shield(state))
            next_hp = state.player_hp - damage
            if next_hp > 0:
                next_state = State(
                    player_hp=next_hp,
                    player_mana=state.player_mana,
                    boss_hp=state.boss_hp,
                    shield_timer=state.shield_timer,
                    poison_timer=state.poison_timer,
                    recharge_timer=state.recharge_timer,
                )
                heapq.heappush(heap, cast(QueueItem, (spent, counter, True, next_state)))
                counter += 1

    raise RuntimeError("No winning path found")


def solve_part_one(data: tuple[int, int]) -> int:
    """Return the least mana to win."""
    boss_hp, boss_damage = data
    return minimal_mana_to_win(boss_hp, boss_damage, hard_mode=False)


def solve_part_two(data: tuple[int, int]) -> int:
    """Return the least mana to win in hard mode."""
    boss_hp, boss_damage = data
    return minimal_mana_to_win(boss_hp, boss_damage, hard_mode=True)

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
