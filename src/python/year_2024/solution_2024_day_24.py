"""Advent of Code 2024 Day 24: Crossed Wires."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

Gate = Tuple[str, str, str]


def collect_z_wires(gates: Dict[str, Gate]) -> list[str]:
    """
    Return sorted ``z`` wire names present in the gate map.

    Args:
        gates: Map of gate outputs to their (operator, input_a, input_b) tuples.

    Returns:
        Sorted list of wire names that begin with ``z``.
    """
    return sorted((name for name in gates if name.startswith("z")), key=lambda s: int(s[1:]))


def parse_input(raw: str) -> tuple[Dict[str, int], Dict[str, Gate]]:
    """
    Parse the gate definitions and initial wire values.

    Args:
        raw: Puzzle input with two sections separated by a blank line.

    Returns:
        Tuple containing the initial wire values and gate map.
    """
    first, second = raw.strip().split("\n\n")
    values: Dict[str, int] = {}
    for line in first.splitlines():
        name, val = line.split(": ")
        values[name] = int(val)

    gates: Dict[str, Gate] = {}
    for line in second.splitlines():
        a, op, b, _, out = line.split()
        gates[out] = (op, a, b)
    return values, gates


def simulate(values: Dict[str, int], gates: Dict[str, Gate]) -> Dict[str, int]:
    """
    Run the gate simulation until all wires resolve.

    Args:
        values: Map of wire names to initial bits.
        gates: Gate definitions keyed by output wire.

    Returns:
        All resolved wire values after the simulation.
    """
    resolved = dict(values)
    pending = dict(gates)
    while pending:
        progressed = False
        for out, (op, a, b) in list(pending.items()):
            if a in resolved and b in resolved:
                av, bv = resolved[a], resolved[b]
                if op == "AND":
                    resolved[out] = av & bv
                elif op == "OR":
                    resolved[out] = av | bv
                elif op == "XOR":
                    resolved[out] = av ^ bv
                else:
                    raise ValueError(op)
                pending.pop(out)
                progressed = True
        if not progressed:
            raise RuntimeError("Stalled simulation")
    return resolved


def read_output(resolved: Dict[str, int]) -> int:
    """
    Read the concatenated value from wires that start with ``z``.

    Args:
        resolved: Simulation output from `simulate`.

    Returns:
        Decimal number formed by the ``z`` wires.
    """
    z_wires = sorted((w for w in resolved if w.startswith("z")), key=lambda s: int(s[1:]))
    result = 0
    for i, wire in enumerate(z_wires):
        result |= (resolved[wire] & 1) << i
    return result


def set_xy_values(
    base: Dict[str, int],
    x_wires: list[str],
    y_wires: list[str],
    x_val: int,
    y_val: int,
) -> Dict[str, int]:
    """
    Override the ``x`` and ``y`` wire bits with a new combination.

    Args:
        base: Original wire values to build upon.
        x_wires: Names of ``x`` wires sorted by index.
        y_wires: Names of ``y`` wires sorted by index.
        x_val: Integer value to assign to ``x`` wires.
        y_val: Integer value to assign to ``y`` wires.

    Returns:
        Copy of ``base`` with ``x``/``y`` wires updated.
    """
    values = dict(base)
    for i, name in enumerate(x_wires):
        values[name] = (x_val >> i) & 1
    for i, name in enumerate(y_wires):
        values[name] = (y_val >> i) & 1
    return values


def collect_xy_wires(values: Dict[str, int]) -> tuple[list[str], list[str]]:
    """
    Return sorted lists of ``x`` and ``y`` wire names by index.

    Args:
        values: Map of initial wire values used to locate ``x``/``y`` wires.

    Returns:
        Tuple containing (sorted x wire names, sorted y wire names).
    """
    x_wires = sorted((name for name in values if name.startswith("x")), key=lambda n: int(n[1:]))
    y_wires = sorted((name for name in values if name.startswith("y")), key=lambda n: int(n[1:]))
    return x_wires, y_wires


def expected_z_bit(x_val: int, y_val: int, bit: int) -> int:
    """
    Compute the expected bit of the sum for a particular ``z`` wire.

    Args:
        x_val: Integer value assigned to the ``x`` wires.
        y_val: Integer value assigned to the ``y`` wires.
        bit: Index of the ``z`` wire whose expected bit to compute.

    Returns:
        ``0`` or ``1`` representing the expected bit of ``x_val + y_val``.
    """
    return ((x_val + y_val) >> bit) & 1


def sample_combos(num_x: int, num_y: int, max_bit: int) -> list[tuple[int, int]]:
    """
    Return deterministic sample pairs of ``x`` and ``y`` values.

    Args:
        num_x: Number of ``x`` wires available.
        num_y: Number of ``y`` wires available.
        max_bit: Highest ``z`` bit index that must match the sum.

    Returns:
        List of tuples containing sample (x, y) integer pairs.
    """
    combos = {(0, 0)}
    combos.add((1, 1))
    if num_x >= 1:
        combos.add((1 << (num_x - 1), 0))
    if num_y >= 1:
        combos.add((0, 1 << (num_y - 1)))
    combos.add(((1 << max(1, num_x)) - 1, (1 << max(1, num_y)) - 1))
    for bit in range(max_bit + 1):
        if bit < num_x:
            combos.add((1 << bit, 0))
        if bit < num_y:
            combos.add((0, 1 << bit))
        if bit < num_x and bit < num_y:
            combos.add((1 << bit, 1 << bit))
    return list(combos)


def build_wire_vectors(
    base_values: Dict[str, int],
    gates: Dict[str, Gate],
    x_wires: list[str],
    y_wires: list[str],
    z_wires: list[str],
    combos: list[tuple[int, int]],
) -> tuple[Dict[str, List[int]], Dict[str, List[int]]]:
    """
    Return the wire output vectors and expected ``z`` bit vectors for all combos.

    Args:
        base_values: Initial wire assignments.
        gates: Map of gate definitions keyed by output wire.
        x_wires: Sorted names of ``x`` wires.
        y_wires: Sorted names of ``y`` wires.
        z_wires: Sorted names of ``z`` wires to validate.
        combos: Sample ``(x, y)`` value pairs to simulate.

    Returns:
        Tuple containing:

        - Map of each wire name to the list of observed bits.
        - Map of each ``z`` wire to the list of expected bits.
    """
    wire_vectors: Dict[str, List[int]] = {}
    expected: Dict[str, List[int]] = {z: [] for z in z_wires}
    for x_val, y_val in combos:
        values = set_xy_values(base_values, x_wires, y_wires, x_val, y_val)
        resolved = simulate(values, gates)
        for wire, bit in resolved.items():
            wire_vectors.setdefault(wire, []).append(bit)
        for z in z_wires:
            bit_index = int(z[1:])
            expected[z].append(expected_z_bit(x_val, y_val, bit_index))
    return wire_vectors, expected


def swap_gates(gates: Dict[str, Gate], swaps: list[tuple[str, str]]) -> Dict[str, Gate]:
    """
    Return a new gate map with the specified outputs swapped.

    Args:
        gates: Original gate definitions keyed by output wire.
        swaps: Pairs of output wire names whose gate definitions should swap.

    Returns:
        Copy of ``gates`` with entries swapped for each provided pair.
    """
    new = dict(gates)
    for a, b in swaps:
        new[a], new[b] = new[b], new[a]
    return new


def find_swaps(base_values: Dict[str, int], gates: Dict[str, Gate]) -> list[tuple[str, str]]:
    """
    Locate the four pairs of outputs whose wires were swapped.

    Args:
        base_values: Initial wire values.
        gates: Gate definitions.

    Returns:
        List of four (wire_a, wire_b) swap pairs.
    """
    x_wires, y_wires = collect_xy_wires(base_values)
    z_wires = collect_z_wires(gates)
    max_bit = max(int(name[1:]) for name in z_wires) if z_wires else 0
    combos = sample_combos(len(x_wires), len(y_wires), max_bit)
    wire_vectors, expected = build_wire_vectors(
        base_values, gates, x_wires, y_wires, z_wires, combos
    )
    mismatch_z = [z for z in z_wires if wire_vectors.get(z) != expected[z]]
    swaps: list[tuple[str, str]] = []
    if not mismatch_z:
        return swaps

    wires = list(wire_vectors.keys())
    current_mismatches = len(mismatch_z)

    def mismcount_after_swap(a: str, b: str) -> int:
        mismatch = 0
        for z in z_wires:
            vector = wire_vectors[z]
            if z == a:
                vector = wire_vectors[b]
            elif z == b:
                vector = wire_vectors[a]
            if vector != expected[z]:
                mismatch += 1
        return mismatch

    for _ in range(4):
        best_pair: tuple[str, str] | None = None
        best_mismatch = current_mismatches
        for i, a in enumerate(wires):
            for b in wires[i + 1 :]:
                if a == b:
                    continue
                new_count = mismcount_after_swap(a, b)
                if new_count < best_mismatch:
                    best_mismatch = new_count
                    best_pair = (a, b)
        if not best_pair:
            break
        swaps.append(best_pair)
        a, b = best_pair
        wire_vectors[a], wire_vectors[b] = wire_vectors[b], wire_vectors[a]
        current_mismatches = best_mismatch
        if current_mismatches == 0:
            break

    return swaps


def format_swaps(swaps: list[tuple[str, str]]) -> str:
    """
    Return the final string of sorted wire names joined by commas.

    Args:
        swaps: Swap pairs returned by ``find_swaps``.

    Returns:
        Comma-separated sorted wire names that were swapped.
    """
    wires = sorted({wire for pair in swaps for wire in pair})
    return ",".join(wires)


def solve_part_one(data: tuple[Dict[str, int], Dict[str, Gate]]) -> int:
    """
    Compute the output number shown on the ``z`` wires.

    Args:
        data: Tuple containing the initial wire values and gate definitions.

    Returns:
        Decimal number formed by the final ``z`` wire bits.
    """
    values, gates = data
    resolved = simulate(values, gates)
    return read_output(resolved)


def solve_part_two(data: tuple[Dict[str, int], Dict[str, Gate]]) -> str:
    """
    Identify swapped wire pairs and report their sorted names.

    Args:
        data: Tuple containing the initial wire values and gate definitions.

    Returns:
        Comma-separated sorted names of wires involved in swaps.
    """
    values, gates = data
    swaps = find_swaps(values, gates)
    return format_swaps(swaps)

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
