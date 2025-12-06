"""Immune System Simulator 20XX -- Advent of Code 2018 Day 24."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class Group:
    """Combat group belonging to an army."""

    army: str
    units: int
    hp: int
    attack: int
    attack_type: str
    initiative: int
    weaknesses: set[str]
    immunities: set[str]

    def effective_power(self) -> int:
        """Total attack power of the group."""
        return self.units * self.attack

    def damage_to(self, other: "Group") -> int:
        """Potential damage this group would deal to another."""
        if self.attack_type in other.immunities:
            return 0
        dmg = self.effective_power()
        if self.attack_type in other.weaknesses:
            dmg *= 2
        return dmg


def parse_group(line: str, army: str) -> Group:
    """Parse a single group line for the given army."""
    pattern = re.compile(
        r"(\d+) units each with (\d+) hit points"
        r"(?: \(([^)]+)\))? with an attack that does (\d+) (\w+) damage at initiative (\d+)"
    )
    m = pattern.match(line)
    assert m
    units, hp, special, attack, attack_type, init = m.groups()
    weaknesses: set[str] = set()
    immunities: set[str] = set()
    if special:
        for part in special.split(";"):
            part = part.strip()
            if part.startswith("weak to"):
                weaknesses = set(part.replace("weak to", "").strip().split(", "))
            elif part.startswith("immune to"):
                immunities = set(part.replace("immune to", "").strip().split(", "))
    return Group(
        army=army,
        units=int(units),
        hp=int(hp),
        attack=int(attack),
        attack_type=attack_type,
        initiative=int(init),
        weaknesses=weaknesses,
        immunities=immunities,
    )


def parse_input(raw: str) -> List[Group]:
    """Parse both armies from the raw input."""
    sections = raw.strip().split("\n\n")
    groups: List[Group] = []
    for section in sections:
        lines = section.strip().splitlines()
        army = lines[0][:-1]
        for line in lines[1:]:
            groups.append(parse_group(line, army))
    return groups


def simulate(groups: List[Group]) -> Tuple[str | None, int]:
    """Simulate the battle and return the winner and remaining units."""
    while True:
        # target selection
        selection_order = sorted(groups, key=lambda g: (-g.effective_power(), -g.initiative))
        targets: dict[int, int] = {}
        chosen = set()
        for idx, attacker in enumerate(selection_order):
            options = [
                (attacker.damage_to(defender), defender.effective_power(), defender.initiative, j)
                for j, defender in enumerate(groups)
                if defender.army != attacker.army
                and j not in chosen
                and attacker.damage_to(defender) > 0
            ]
            if not options:
                continue
            options.sort(reverse=True)
            _, _, _, target_idx = options[0]
            targets[id(attacker)] = target_idx
            chosen.add(target_idx)

        # attacking
        any_killed = False
        for attacker in sorted(groups, key=lambda g: -g.initiative):
            target_idx = targets.get(id(attacker))
            if target_idx is None:
                continue
            if attacker.units <= 0:
                continue
            defender = groups[target_idx]
            damage = attacker.damage_to(defender)
            killed = min(defender.units, damage // defender.hp)
            if killed:
                any_killed = True
            defender.units -= killed
        groups = [g for g in groups if g.units > 0]

        armies = {g.army for g in groups}
        if len(armies) == 1:
            winner = armies.pop()
            return winner, sum(g.units for g in groups)
        if not any_killed:
            return None, sum(g.units for g in groups)


def solve_part_one(groups: List[Group]) -> int:
    """Units remaining after the battle."""
    winner, units = simulate([Group(**vars(g)) for g in groups])  # type: ignore[arg-type]
    return units


def solve_part_two(groups: List[Group]) -> int:
    """Units remaining when immune system wins with minimal boost."""
    boost = 1
    while True:
        boosted = []
        for g in groups:
            new_g = Group(**vars(g))
            if new_g.army.startswith("Immune"):
                new_g.attack += boost
            boosted.append(new_g)
        winner, units = simulate(boosted)
        if winner and winner.startswith("Immune"):
            return units
        boost += 1

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
