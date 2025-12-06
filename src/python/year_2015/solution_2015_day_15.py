"""Science for Hungry People -- Advent of Code 2015 Day 15."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Ingredient:
    """Ingredient attributes per teaspoon."""

    name: str
    capacity: int
    durability: int
    flavor: int
    texture: int
    calories: int


def parse_input(raw: str) -> list[Ingredient]:
    """Parse ingredient lines into objects.

    Args:
        raw (str): Raw puzzle input.

    Returns:
        list[Ingredient]: Parsed ingredients.
    """
    ingredients: list[Ingredient] = []
    for line in raw.strip().splitlines():
        name, rest = line.split(": ")
        parts = rest.replace(",", "").split()
        values = {parts[i]: int(parts[i + 1]) for i in range(0, len(parts), 2)}
        ingredients.append(
            Ingredient(
                name=name,
                capacity=values["capacity"],
                durability=values["durability"],
                flavor=values["flavor"],
                texture=values["texture"],
                calories=values["calories"],
            )
        )
    return ingredients


def score(amounts: list[int], ingredients: list[Ingredient]) -> int:
    """Score a set of ingredient amounts.

    Args:
        amounts (list[int]): Teaspoons assigned per ingredient.
        ingredients (list[Ingredient]): Ingredient definitions in matching order.

    Returns:
        int: Product of clamped property totals.
    """
    totals = {"capacity": 0, "durability": 0, "flavor": 0, "texture": 0}
    for amt, ing in zip(amounts, ingredients):
        totals["capacity"] += amt * ing.capacity
        totals["durability"] += amt * ing.durability
        totals["flavor"] += amt * ing.flavor
        totals["texture"] += amt * ing.texture
    product = 1
    for value in totals.values():
        product *= max(0, value)
    return product


def total_calories(amounts: list[int], ingredients: list[Ingredient]) -> int:
    """Compute total calories for the mixture.

    Args:
        amounts (list[int]): Teaspoons assigned per ingredient.
        ingredients (list[Ingredient]): Ingredient definitions in matching order.

    Returns:
        int: Total calories for the mixture.
    """
    return sum(amt * ing.calories for amt, ing in zip(amounts, ingredients))


def search(ingredients: list[Ingredient], calories_target: int | None = None) -> int:
    """Find the best score with optional calorie constraint.

    Args:
        ingredients (list[Ingredient]): Ingredient definitions.
        calories_target (int | None): Required calorie total, if any.

    Returns:
        int: Highest achievable score under the constraints.
    """
    n = len(ingredients)
    best = 0

    def backtrack(idx: int, remaining: int, amounts: list[int]) -> None:
        nonlocal best
        if idx == n - 1:
            amounts.append(remaining)
            if calories_target is None or total_calories(amounts, ingredients) == calories_target:
                best = max(best, score(amounts, ingredients))
            amounts.pop()
            return

        for amt in range(remaining + 1):
            amounts.append(amt)
            backtrack(idx + 1, remaining - amt, amounts)
            amounts.pop()

    backtrack(0, 100, [])
    return best


def solve_part_one(ingredients: list[Ingredient]) -> int:
    """Best score without calorie restriction."""
    return search(ingredients)


def solve_part_two(ingredients: list[Ingredient]) -> int:
    """Best score constrained to 500 calories."""
    return search(ingredients, calories_target=500)

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
