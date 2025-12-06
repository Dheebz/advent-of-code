"""Beverage Bandits -- Advent of Code 2018 Day 15."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class Unit:
    """Combat unit on the grid."""

    kind: str
    x: int
    y: int
    hp: int = 200
    attack: int = 3
    alive: bool = True

    def pos(self) -> Tuple[int, int]:
        """Return current (x, y) position."""
        return self.x, self.y


def parse_input(raw: str) -> Tuple[List[str], List[Unit]]:
    """Parse the map and units from the raw input."""
    grid = [list(line.strip()) for line in raw.strip().splitlines()]
    units: List[Unit] = []
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char in "EG":
                units.append(Unit(char, x, y))
                grid[y][x] = "."
    return ["".join(row) for row in grid], units


def in_reading_order(units: List[Unit]) -> List[Unit]:
    """Return living units sorted by reading order."""
    return sorted([u for u in units if u.alive], key=lambda u: (u.y, u.x))


def adjacent_positions(x: int, y: int) -> List[Tuple[int, int]]:
    """Return adjacent coordinates in reading order."""
    return [(x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)]


def find_move(grid: List[str], units: List[Unit], unit: Unit) -> Tuple[int, int]:
    """Find the square the unit should move to this turn."""
    occupied: Set[Tuple[int, int]] = {u.pos() for u in units if u.alive}
    targets = [u for u in units if u.alive and u.kind != unit.kind]
    if not targets:
        return unit.x, unit.y

    target_positions = {
        pos for t in targets for pos in adjacent_positions(t.x, t.y) if pos not in occupied
    }
    if not target_positions:
        return unit.x, unit.y

    queue = deque([(unit.x, unit.y, 0)])
    seen = {(unit.x, unit.y)}
    paths: Dict[Tuple[int, int], Tuple[int, int]] = {}
    found_dist = None
    choices: List[Tuple[int, int]] = []

    while queue:
        x, y, dist = queue.popleft()
        if found_dist is not None and dist > found_dist:
            break
        if (x, y) in target_positions:
            found_dist = dist
            choices.append((y, x))  # for sorting
            continue
        for nx, ny in adjacent_positions(x, y):
            if (nx, ny) in seen:
                continue
            if grid[ny][nx] != ".":
                continue
            if (nx, ny) in occupied and (nx, ny) != (unit.x, unit.y):
                continue
            seen.add((nx, ny))
            paths[(nx, ny)] = (x, y)
            queue.append((nx, ny, dist + 1))

    if not choices:
        return unit.x, unit.y
    choices.sort()
    target_x, target_y = choices[0][1], choices[0][0]

    # backtrack to find first step
    current = (target_x, target_y)
    while paths.get(current) != (unit.x, unit.y):
        current = paths[current]
    return current


def attack(units: List[Unit], attacker: Unit) -> None:
    """Perform an attack if an enemy is adjacent."""
    enemies = [
        u
        for u in units
        if u.alive
        and u.kind != attacker.kind
        and u.pos() in adjacent_positions(attacker.x, attacker.y)
    ]
    if not enemies:
        return
    target = min(enemies, key=lambda u: (u.hp, u.y, u.x))
    target.hp -= attacker.attack
    if target.hp <= 0:
        target.alive = False


def simulate(
    grid: List[str], units: List[Unit], elf_attack: int = 3, stop_on_elf_death: bool = False
) -> Tuple[int, bool]:
    """Simulate the battle and return (outcome, elf_died_flag)."""
    for u in units:
        if u.kind == "E":
            u.attack = elf_attack

    full_rounds = 0
    while True:
        for unit in in_reading_order(units):
            if not unit.alive:
                continue
            if not any(u.alive and u.kind != unit.kind for u in units):
                total_hp = sum(u.hp for u in units if u.alive)
                return full_rounds * total_hp, False
            move_to = find_move(grid, units, unit)
            unit.x, unit.y = move_to
            attack(units, unit)
            if stop_on_elf_death and any(u.kind == "E" and not u.alive for u in units):
                return 0, True
        full_rounds += 1


def solve_part_one(parsed: Tuple[List[str], List[Unit]]) -> int:
    """Outcome of the battle with default attack power."""
    grid, units = parsed
    return simulate(grid, [Unit(u.kind, u.x, u.y) for u in units])[0]


def solve_part_two(parsed: Tuple[List[str], List[Unit]]) -> int:
    """Outcome with increased elf power so no elves die."""
    grid, units = parsed
    elf_count = sum(1 for u in units if u.kind == "E")
    attack_power = 4
    while True:
        sim_units = [Unit(u.kind, u.x, u.y) for u in units]
        outcome, elf_died = simulate(
            grid, sim_units, elf_attack=attack_power, stop_on_elf_death=True
        )
        if not elf_died and sum(1 for u in sim_units if u.kind == "E" and u.alive) == elf_count:
            return outcome
        attack_power += 1

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
