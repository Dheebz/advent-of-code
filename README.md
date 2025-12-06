Advent of Code solutions implemented in Python, one module per day with shared parsing/CLI conventions.

## Prerequisites
- Runs on the standard library; no extra packages are required.

## Project layout
- `src/python/year_YYYY/` — year folders containing:
  - `solution_YYYY_day_DD.py` modules that expose `parse_input`, `solve_part_one`, `solve_part_two`, and the required CLI helpers.
  - `input_YYYY_day_DD.txt` files with the canonical puzzle inputs.
  - `article_YYYY_day_DD.md` write-ups describing each puzzle.

## Running solutions
From the repository root, choose one of the supported entry points:

1. Run a single day module directly, letting its bundled CLI pick the matching input file and print both parts:
   ```sh
   python src/python/year_2015/solution_2015_day_01.py
   ```
2. Use the centralized runner when you want to drive multiple days in one command:
   ```sh
   python runner.py --year 2015 --day 1
   ```
3. Extend the runner invocation with `--part`, `--input`, or omit `--day` to control which parts and inputs run:
   ```sh
   python runner.py --year 2022 --part 1 --input __inputs__/year_2022/input_2022_day_05.txt
   ```

## Adding new days
1. Copy a nearby solution file as a template and implement the logic following the shared structure.
2. Place the new input in the same year folder and name it `input_YYYY_day_DD.txt`.

