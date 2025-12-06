"""Advent of Code 2024 Day 09: Disk Fragmenter."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

Segment = tuple[int, int, Optional[int]]  # (start, length, file_id)
Data = str


def parse_input(raw: str) -> Data:
    """
    Return the trimmed disk fragment map.

    Args:
        raw: Raw puzzle input consisting of digits.

    Returns:
        Stripped string representing the map.
    """
    return raw.strip()


def expand_blocks(map_str: str) -> list[int]:
    """
    Expand the disk map string into a block-by-block list.

    Args:
        map_str: Stripped fragment string representing alternating file/free lengths.

    Returns:
        List where each index maps to either a file ID or -1 for free space.
    """
    blocks: list[int] = []
    file_id = 0
    for idx, ch in enumerate(map_str.strip()):
        length = int(ch)
        if length == 0:
            continue
        if idx % 2 == 0:
            blocks.extend([file_id] * length)
            file_id += 1
        else:
            blocks.extend([-1] * length)
    return blocks


def checksum_blocks(blocks: list[int]) -> int:
    """
    Aggregate block positions into a checksum.

    Args:
        blocks: Expanded block list with file and free identifiers.

    Returns:
        Integer checksum computed as sum(pos * file_id) for occupied blocks.
    """
    total = 0
    for pos, file_id in enumerate(blocks):
        if file_id != -1:
            total += pos * file_id
    return total


def solve_part_one(data: Data) -> int:
    """
    Compute the checksum after compacting the fragment map.

    Args:
        data: Disk map string returned from `parse_input`.

    Returns:
        Checksum value after pairing free slots with files.
    """
    map_str = data
    blocks = expand_blocks(map_str)
    left = 0
    right = len(blocks) - 1

    while left < right:
        while left < len(blocks) and blocks[left] != -1:
            left += 1
        while right >= 0 and blocks[right] == -1:
            right -= 1
        if left >= right:
            break
        blocks[left], blocks[right] = blocks[right], -1
        left += 1
        right -= 1

    return checksum_blocks(blocks)


def build_segments(map_str: str) -> list[Segment]:
    """
    Convert the map string into explicit segments.

    Args:
        map_str: Disk map string from `parse_input`.

    Returns:
        List of (start, length, file_id) entries describing the disk layout.
    """
    segments: list[Segment] = []
    pos = 0
    file_id = 0
    for idx, ch in enumerate(map_str.strip()):
        length = int(ch)
        if length == 0:
            continue
        if idx % 2 == 0:
            segments.append((pos, length, file_id))
            file_id += 1
        else:
            segments.append((pos, length, None))
        pos += length
    return segments


def merge_free(segments: list[Segment]) -> list[Segment]:
    """
    Merge consecutive free segments to maintain compact representation.

    Args:
        segments: Sorted list of disk segments.

    Returns:
        List with adjacent free segments merged.
    """
    merged: list[Segment] = []
    for seg in sorted(segments, key=lambda s: s[0]):
        if (
            merged
            and seg[2] is None
            and merged[-1][2] is None
            and merged[-1][0] + merged[-1][1] == seg[0]
        ):
            last = merged[-1]
            merged[-1] = (last[0], last[1] + seg[1], last[2])
        else:
            merged.append(seg)
    return merged


def checksum_segments(segments: list[Segment]) -> int:
    """
    Compute checksum information from segment metadata.

    Args:
        segments: List of disk segments.

    Returns:
        Checksum calculated using segment positions and lengths.
    """
    total = 0
    for start, length, file_id in segments:
        if file_id is None:
            continue
        total_len = length
        total += file_id * (total_len * start + total_len * (total_len - 1) // 2)
    return total


def solve_part_two(data: Data) -> int:
    """
    Rebuild invalid segments greedily and compute checksum.

    Args:
        data: Disk map string from `parse_input`.

    Returns:
        Checksum after rebalancing the layout.
    """
    map_str = data
    segments = build_segments(map_str)
    max_file_id = max(seg[2] for seg in segments if seg[2] is not None)

    for target in range(max_file_id, -1, -1):
        seg_idx = next(i for i, seg in enumerate(segments) if seg[2] == target)
        file_start, file_len, _ = segments[seg_idx]

        best_idx: Optional[int] = None
        for i, seg in enumerate(segments[:seg_idx]):
            if seg[2] is None and seg[1] >= file_len:
                best_idx = i
                break
        if best_idx is None:
            continue

        free_seg = segments[best_idx]
        new_file = (free_seg[0], file_len, target)

        if free_seg[1] == file_len:
            segments.pop(best_idx)
            if best_idx < seg_idx:
                seg_idx -= 1
        else:
            segments[best_idx] = (free_seg[0] + file_len, free_seg[1] - file_len, None)

        segments[seg_idx] = (file_start, file_len, None)

        insert_pos = 0
        while insert_pos < len(segments) and segments[insert_pos][0] < new_file[0]:
            insert_pos += 1
        segments.insert(insert_pos, new_file)

        segments = merge_free(segments)

    return checksum_segments(segments)

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
