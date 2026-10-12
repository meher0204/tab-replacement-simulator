# Browser Tab Page Replacement Simulator

A Python-based educational simulator that compares **FIFO, LRU, Optimal and Clock** page-replacement policies using browser-tab workloads.

## Desktop console (recommended)

The project includes a graphical desktop console, so you can choose workloads, enter a sequence, set the number of frames, compare policies, and inspect each step without typing command-line options.

### macOS

1. Open the project folder in Finder.
2. If this is the first run, install the dependency once from Terminal:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Double-click `Run_Simulator.command` to open the desktop simulator. If macOS blocks it, right-click the file and choose **Open**.

If you already use a project virtual environment named `.venv`, the launcher will use it automatically.

### Windows / Linux

Install the dependency once:

```bash
python -m pip install -r requirements.txt
```

Then launch the desktop console:

```bash
python gui.py
```

Tkinter is included with most standard Python installations. On some Linux distributions it may need to be installed separately (for example, the `python3-tk` package).

## Using the desktop console

1. Choose a preset workload or select `custom`.
2. Enter a tab sequence, such as `A B C A B D` (spaces or commas are accepted).
3. Choose a frame count from 1 to 20.
4. Click **Run comparison**.
5. Compare hits, faults and ratios in the results table, inspect the fault chart, and choose a policy to view its step-by-step trace.

## Terminal / command-line mode (optional)

The original command-line interface is still available:

```bash
python main.py
python main.py --preset textbook --frames 3
python main.py --seq "A B C A B D" --frames 3 --steps
```

## Policies

- **FIFO:** evicts the tab loaded earliest.
- **LRU:** evicts the tab that has not been used for the longest time.
- **Optimal:** evicts the tab whose next use is farthest in the future; this is a theoretical benchmark.
- **Clock:** uses a circular pointer and reference bits to give recently used tabs a second chance.

## Project structure

```text
tab-replacement-simulator/
├── gui.py                    # Desktop GUI / visual console
├── Run_Simulator.command     # macOS double-click launcher
├── main.py                   # Original command-line interface
├── requirements.txt          # Python dependencies
├── tabsim/
│   ├── policies.py           # FIFO, LRU, Optimal and Clock policies
│   ├── simulator.py          # Shared simulation engine
│   ├── workloads.py          # Presets, parsing and validation
│   └── reporter.py           # Text reports and chart helpers
├── tests/
│   └── test_policies.py      # Unit tests
└── outputs/                  # Optional saved charts
```

## Tests

Run the test suite with:

```bash
python -m pytest -q
```

## Project scope

This is a simplified educational model: each tab occupies one frame. It demonstrates classical operating-systems replacement policies; it does not reproduce a real browser's memory-management implementation.
