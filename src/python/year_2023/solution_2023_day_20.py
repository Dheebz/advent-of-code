"""Pulse Propagation -- Advent of Code 2023 Day 20."""

from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from math import lcm
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Module:
    """
    Represent a logic module in the pulse propagation network.

    Attributes:
        kind: Designator for the gate type, one of ``"broadcaster"``, ``"%"``, or ``"&"``.
        dests: Names of the modules that receive this module's pulses.
        state: Toggle state for throttling modules (``%``).
        memory: Stored inputs for conjunction modules (``&``).
    """

    kind: str  # "broadcaster", "%", "&"
    dests: List[str]
    state: bool = False  # for flip-flop
    memory: Dict[str, bool] = field(default_factory=dict)  # for conjunction


Modules = Dict[str, Module]


def parse_input(raw: str) -> Modules:
    """
    Parse the raw module descriptions into a module map.

    Args:
        raw: Input text containing one module per line followed by its destinations.

    Returns:
        Map of module names to initialized ``Module`` instances.
    """
    modules: Modules = {}
    lines = raw.strip().splitlines()
    for line in lines:
        name_part, dest_part = line.split(" -> ")
        dests = dest_part.split(", ")
        if name_part == "broadcaster":
            name = "broadcaster"
            kind = "broadcaster"
        else:
            kind = name_part[0]
            name = name_part[1:]
        modules[name] = Module(kind, dests)

    # Initialize conjunction memories
    for name, module in modules.items():
        for dest in module.dests:
            if dest in modules and modules[dest].kind == "&":
                modules[dest].memory[name] = False
    return modules


def press_button(modules: Modules) -> Tuple[int, int]:
    """
    Simulate a single button press through the network.

    Args:
        modules: Module graph that reacts to pulses.

    Returns:
        Tuple(low, high) counts of pulses emitted during the press.
    """
    low = high = 0
    queue = deque([("button", "broadcaster", False)])
    while queue:
        src, dest, pulse = queue.popleft()
        if pulse:
            high += 1
        else:
            low += 1
        if dest not in modules:
            continue
        module = modules[dest]
        if module.kind == "broadcaster":
            for nxt in module.dests:
                queue.append((dest, nxt, pulse))
        elif module.kind == "%":
            if pulse:
                continue
            module.state = not module.state
            out = module.state
            for nxt in module.dests:
                queue.append((dest, nxt, out))
        else:  # conjunction
            module.memory[src] = pulse
            out = not all(module.memory.values())
            for nxt in module.dests:
                queue.append((dest, nxt, out))
    return low, high


def solve_part_one(modules: Modules) -> int:
    """
    Multiply the pulse totals after repeating the press 1000 times.

    Args:
        modules: Module graph to simulate.

    Returns:
        Product of the total low and high pulses after 1000 presses.
    """
    mods = deepcopy(modules)
    total_low = total_high = 0
    for _ in range(1000):
        low, high = press_button(mods)
        total_low += low
        total_high += high
    return total_low * total_high


def solve_part_two(modules: Modules) -> int:
    """
    Compute how many presses it takes for rx to observe a low pulse.

    Args:
        modules: Module graph to inspect.

    Returns:
        Press count needed until every tracked input produces a low pulse.
    """
    # Identify the conjunction feeding rx
    target = next(name for name, mod in modules.items() if "rx" in mod.dests)
    inputs = list(modules[target].memory.keys())
    cycles: Dict[str, int] = {}

    mods = deepcopy(modules)
    presses = 0
    while len(cycles) < len(inputs):
        presses += 1
        queue = deque([("button", "broadcaster", False)])
        while queue:
            src, dest, pulse = queue.popleft()
            if dest == target and pulse and src in inputs and src not in cycles:
                cycles[src] = presses
            if dest not in mods:
                continue
            module = mods[dest]
            if module.kind == "broadcaster":
                for nxt in module.dests:
                    queue.append((dest, nxt, pulse))
            elif module.kind == "%":
                if pulse:
                    continue
                module.state = not module.state
                out = module.state
                for nxt in module.dests:
                    queue.append((dest, nxt, out))
            else:
                module.memory[src] = pulse
                out = not all(module.memory.values())
                for nxt in module.dests:
                    queue.append((dest, nxt, out))
    result = 1
    for val in cycles.values():
        result = lcm(result, val)
    return result

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
