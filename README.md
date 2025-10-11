# Machine Intelligence — Problem Sets

This repository contains programming problem sets and an automatic grader used for the Machine Intelligence course (CMPS402). The included autograder runs unit-style testcases found under each problem set and reports grades per-problem and overall.

## Repository layout
a
- `autograder.sh` — top-level script that iterates over problem-set folders and runs the autograder for each one (bash).
- `psets/` — a folder containing problem set directories. Each problem set contains:
  - `autograder.py` — the per-problem-set autograder CLI (Python)
  - `Instructions.md` — human-friendly instructions for that problem set
  - `testcases/` — JSON testcases used by the autograder
  - solution starter files (e.g. `anagram_check.py`, `caesar.py`, ...)
  - `student_info.json` — student metadata used by the grader

Example tree (one problem set shown):

psets/
└─ Problem Set 0/
    ├─ anagram_check.py
    ├─ autograder.py
    ├─ Instructions.md
    └─ testcases/

## Quickstart — run the autograder (PowerShell)

Prerequisites:

- Python 3.x installed and available on PATH.

Run the autograder for a specific problem set (from repository root) using PowerShell:

```powershell
# change directory to a problem set and run its autograder
Set-Location -Path 'psets/<Problem-Set>'
python autograder.py
```

Command-line options supported by `autograder.py`:

- `-q, --question` — choose which question(s) to grade (default: `all`). You can pass a comma-separated list, e.g. `-q 1,3` or a pattern `-q 1/test1.json`.
- `-d, --debug` — disable timeouts (useful for debugging).
- `-t, --timescale` — scale time limits used by the grader (default: `default` — autocalculates using `speed_test.py`).
- `-s, --solution` — path to solution files (if used by your workflow).

Examples:

```powershell
# Run entire problem set
python autograder.py

# Run only question 1
python autograder.py -q 1

# Run question 1 and use a custom time scale (e.g. make time limits twice as long)
python autograder.py -t 2 -q 1

# Debug a single testcase (disable timeout)
python autograder.py -d -q 1/test1.json
```

The top-level `autograder.sh` script can be used on Unix-like systems to iterate over all problem sets; it calls `python3 autograder.py` inside each problem set folder and records pass/fail in a `grading_status.txt` file.

## How the autograder works (brief)

- Testcases are JSON files located under `psets/<Problem Set>/testcases/`.
- `psets/<Problem Set>/autograder.py` loads `testcases/problems.json` which lists problems and test metadata.
- Each test runs in a separate thread with a timeout. Timeouts are scaled by `speed_test.py` unless `-t` is provided.
- Results are printed to stdout and the autograder exits with the earned total grade as the process exit code.

