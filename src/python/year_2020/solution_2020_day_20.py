"""Jurassic Jigsaw -- Advent of Code 2020 Day 20."""

from __future__ import annotations

import argparse
from collections import defaultdict
from math import prod, sqrt
from pathlib import Path
from typing import Dict, List, Tuple

Tile = List[str]
Orientation = Tuple[int, Tile]


def parse_input(raw: str) -> Dict[int, Tile]:
    """Return tiles keyed by ID."""
    tiles: Dict[int, Tile] = {}
    for block in raw.strip().split("\n\n"):
        lines = block.strip().splitlines()
        tile_id = int(lines[0][5:-1])
        tiles[tile_id] = lines[1:]
    return tiles


def rotate(tile: Tile) -> Tile:
    """
    Rotate a tile 90 degrees clockwise.

    Args:
        tile: List of strings representing the tile rows.

    Returns:
        New tile rotated clockwise.
    """
    return [
        "".join(tile[len(tile) - 1 - r][c] for r in range(len(tile))) for c in range(len(tile[0]))
    ]


def flip(tile: Tile) -> Tile:
    """
    Flip a tile horizontally.

    Args:
        tile: List of strings representing the tile rows.

    Returns:
        New tile mirrored left-to-right.
    """
    return [row[::-1] for row in tile]


def orientations(tile: Tile) -> List[Tile]:
    """
    Generate all unique orientations for a tile (rotations + flips).

    Args:
        tile: Tile to orient.

    Returns:
        List of tiles for each orientation.
    """
    seen = []
    current = tile
    for _ in range(4):
        seen.append(current)
        seen.append(flip(current))
        current = rotate(current)
    # remove duplicates
    unique = []
    seen_set = set()
    for t in seen:
        key = tuple(t)
        if key not in seen_set:
            seen_set.add(key)
            unique.append(t)
    return unique


def edges(tile: Tile) -> Tuple[str, str, str, str]:
    """
    Extract the border strings from a tile.

    Args:
        tile: Tile represented as rows of characters.

    Returns:
        Tuple containing the top, right, bottom, and left edges.
    """
    top = tile[0]
    bottom = tile[-1]
    left = "".join(row[0] for row in tile)
    right = "".join(row[-1] for row in tile)
    return top, right, bottom, left


def find_corners(tiles: Dict[int, Tile]) -> List[int]:
    """
    Identify corner tiles by counting unmatched edges.

    Args:
        tiles: Dictionary of tile ID to tile data.

    Returns:
        List of IDs corresponding to corner tiles.
    """
    edge_map: Dict[str, List[int]] = defaultdict(list)
    for tile_id, tile in tiles.items():
        for edge in edges(tile):
            edge_map[edge].append(tile_id)
            edge_map[edge[::-1]].append(tile_id)
    corners = []
    for tile_id, tile in tiles.items():
        unmatched = 0
        for edge in edges(tile):
            if len(edge_map[edge]) == 1:
                unmatched += 1
        if unmatched == 2:
            corners.append(tile_id)
    return corners


def assemble_image(tiles: Dict[int, Tile]) -> List[List[Tuple[int, Tile]]]:
    """
    Assemble the tiles into a complete image grid.

    Args:
        tiles: Mapping from tile ID to tile contents.

    Returns:
        2D grid of (tile ID, tile) pairs in arranged order.
    """
    size = int(sqrt(len(tiles)))
    grid: List[List[Tuple[int, Tile]]] = [[(-1, []) for _ in range(size)] for _ in range(size)]
    used: set[int] = set()

    def fits(tile: Tile, row: int, col: int) -> bool:
        top, right, bottom, left = edges(tile)
        if row > 0:
            above_id, above_tile = grid[row - 1][col]
            if above_id != -1 and edges(above_tile)[2] != top:
                return False
        if col > 0:
            left_id, left_tile = grid[row][col - 1]
            if left_id != -1 and edges(left_tile)[1] != left:
                return False
        return True

    tile_orients: Dict[int, List[Tile]] = {tid: orientations(tile) for tid, tile in tiles.items()}

    def backtrack(pos: int) -> bool:
        if pos == size * size:
            return True
        row, col = divmod(pos, size)
        for tile_id, variants in tile_orients.items():
            if tile_id in used:
                continue
            for variant in variants:
                if fits(variant, row, col):
                    grid[row][col] = (tile_id, variant)
                    used.add(tile_id)
                    if backtrack(pos + 1):
                        return True
                    used.remove(tile_id)
                    grid[row][col] = (-1, [])
        return False

    if not backtrack(0):
        raise ValueError("no arrangement found")
    return grid


def remove_borders(tile: Tile) -> Tile:
    """
    Crop the border rows and columns from a tile.

    Args:
        tile: Tile to trim.

    Returns:
        Tile without its outermost border.
    """
    return [row[1:-1] for row in tile[1:-1]]


def stitch_image(grid: List[List[Tuple[int, Tile]]]) -> Tile:
    """
    Stitch the arranged grid into a single image.

    Args:
        grid: Grid of arranged tiles.

    Returns:
        Combined tile as a list of strings.
    """
    rows = []
    for row_tiles in grid:
        stripped = [remove_borders(tile) for _, tile in row_tiles]
        for i in range(len(stripped[0])):
            rows.append("".join(tile[i] for tile in stripped))
    return rows


SEA_MONSTER = [
    "                  # ",
    "#    ##    ##    ###",
    " #  #  #  #  #  #   ",
]
MONSTER_OFFSETS = [
    (r, c) for r, line in enumerate(SEA_MONSTER) for c, ch in enumerate(line) if ch == "#"
]


def count_monsters(image: Tile) -> int:
    """
    Count how many sea monsters appear in the image.

    Args:
        image: Combined image tile.

    Returns:
        Number of sea monster patterns found.
    """
    count = 0
    height = len(image)
    width = len(image[0])
    for r in range(height - 2):
        for c in range(width - 19):
            if all(image[r + dr][c + dc] == "#" for dr, dc in MONSTER_OFFSETS):
                count += 1
    return count


def water_roughness(image: Tile) -> int:
    """
    Compute the water roughness metric after locating sea monsters.

    Args:
        image: Combined image tile.

    Returns:
        Number of '#' characters not part of any sea monster.
    """
    for oriented in orientations(image):
        monsters = count_monsters(oriented)
        if monsters:
            hashes = sum(row.count("#") for row in oriented)
            return hashes - monsters * len(MONSTER_OFFSETS)
    raise ValueError("no sea monsters found")


def solve_part_one(tiles: Dict[int, Tile]) -> int:
    """
    Compute the product of the IDs of the corner tiles.

    Args:
        tiles: Mapping from ID to tile data.

    Returns:
        Product of the four corner tile IDs.
    """
    return prod(find_corners(tiles))


def solve_part_two(tiles: Dict[int, Tile]) -> int:
    """
    Calculate the water roughness after assembling and searching for sea monsters.

    Args:
        tiles: Mapping from ID to tile data.

    Returns:
        Water roughness metric (hashes not part of sea monsters).
    """
    grid = assemble_image(tiles)
    image = stitch_image(grid)
    return water_roughness(image)

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
