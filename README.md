# Browser Tab Page Replacement Simulator

An Operating Systems mini project. It treats browser tabs as memory pages and
simulates how **FIFO**, **LRU**, **Optimal** and **Clock (Second Chance)**
page replacement decide which tab to unload when memory is full.

| Browser idea | OS idea |
|---|---|
| Tab | Page |
| Slot for an active tab | Frame |
| Opening / switching to a tab | Page reference |
| Tab reloaded after being unloaded | Page fault |

## Setup

```bash
python -m venv .venv
# Windows:   .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Needs Python 3.8+.

## Run

```bash
python main.py                                   # interactive menu
python main.py --preset textbook --frames 3      # one preset
python main.py --seq "A B C A B D A D B C" --frames 3 --steps
python main.py --preset belady --sweep 6 --save  # faults vs frames chart
python main.py --preset cyclic --save --no-plot  # save PNG without a pop-up
```

Presets: `demo`, `textbook`, `revisit`, `random`, `cyclic`, `belady`.
Saved charts go to `outputs/`.

## Test

```bash
python -m unittest -v
```

## Project structure

```
main.py              command line + interactive menu
tabsim/
  policies.py        ReplacementPolicy + FIFO, LRU, Optimal, Clock
  simulator.py       Simulator engine, Step and Result records
  workloads.py       input parsing, validation, preset workloads
  reporter.py        console tables and matplotlib charts
tests/               unit tests (textbook values, Belady's anomaly, invariants)
outputs/             generated charts
```

## Simplifying assumptions

Every tab costs exactly one frame, the frame count is fixed during a run, and
the full request sequence is known in advance (needed for Optimal). Real
browsers use memory-pressure heuristics instead; this is the classic OS model
wrapped in a browser story.
