"""Browser Tab Page Replacement Simulator - command line entry point.

Interactive menu:   python main.py
One-shot examples:  python main.py --preset textbook --frames 3
                    python main.py --seq "A B C A B D A D B C" --frames 3 --steps
                    python main.py --preset belady --sweep 6 --save
"""

import argparse
import os

from tabsim import reporter
from tabsim.workloads import PRESETS, get_preset, parse_input, validate

OUT_DIR = "outputs"


def run_and_report(sequence, frames, label, steps=False, plot=True, save=False):
    validate(sequence, frames)
    print(f"\nWorkload : {label}")
    print(f"Sequence : {' '.join(sequence)}")
    print(f"Frames   : {frames}")
    results = reporter.run_all(sequence, frames)
    if steps:
        for r in results:
            reporter.print_steps(r, frames)
    reporter.print_summary(results, title=f"Summary ({label}, {frames} frames)")
    if plot or save:
        slug = label.lower().replace(" ", "_")
        path = os.path.join(OUT_DIR, f"faults_{slug}_{frames}frames.png") if save else None
        reporter.plot_faults(results, f"Page faults - {label} ({frames} frames)", path, show=plot)


def run_sweep(sequence, label, max_frames, plot=True, save=False):
    print(f"\nFault counts for '{label}' as frames grow from 1 to {max_frames}:")
    print(f"{'Frames':<8}" + "".join(f"{c.name:>9}" for c in reporter.ALL_POLICIES))
    for n in range(1, max_frames + 1):
        row = reporter.run_all(sequence, n)
        print(f"{n:<8}" + "".join(f"{r.faults:>9}" for r in row))
    if plot or save:
        slug = label.lower().replace(" ", "_")
        path = os.path.join(OUT_DIR, f"sweep_{slug}.png") if save else None
        reporter.plot_sweep(sequence, max_frames, f"Faults vs frames - {label}", path, show=plot)


def ask_int(prompt, default):
    raw = input(f"{prompt} [{default}]: ").strip()
    return int(raw) if raw else default


def menu():
    while True:
        print("\n=== Browser Tab Page Replacement Simulator ===")
        print("1. Run a preset workload")
        print("2. Enter my own tab sequence")
        print("3. Run ALL presets (summary tables)")
        print("4. Frame sweep (faults vs frames, shows Belady's anomaly)")
        print("5. Quit")
        choice = input("Choose 1-5: ").strip()
        try:
            if choice == "1":
                for name, (desc, _, _) in PRESETS.items():
                    print(f"  {name:<9} - {desc}")
                name = input("Preset name: ").strip().lower() or "demo"
                desc, seq, default_frames = get_preset(name)
                frames = ask_int("Number of frames", default_frames)
                steps = input("Show step-by-step tables? (y/N): ").strip().lower() == "y"
                run_and_report(seq, frames, name, steps=steps, save=True)
            elif choice == "2":
                seq = parse_input(input("Tab sequence (e.g. A B C A B D): "))
                frames = ask_int("Number of frames", 3)
                run_and_report(seq, frames, "custom", steps=True, save=True)
            elif choice == "3":
                for name in PRESETS:
                    _, seq, frames = get_preset(name)
                    run_and_report(seq, frames, name, plot=False, save=True)
            elif choice == "4":
                name = input("Preset name for the sweep [belady]: ").strip().lower() or "belady"
                _, seq, _ = get_preset(name)
                run_sweep(seq, name, ask_int("Maximum frames", 6), save=True)
            elif choice == "5":
                print("Goodbye!")
                return
            else:
                print("Please enter a number from 1 to 5.")
        except ValueError as err:
            print(f"Input error: {err}")


def main():
    parser = argparse.ArgumentParser(description="Browser Tab Page Replacement Simulator")
    parser.add_argument("--preset", choices=list(PRESETS), help="use a built-in workload")
    parser.add_argument("--seq", help='tab sequence, e.g. "A B C A B D"')
    parser.add_argument("--frames", type=int, help="number of frames (active-tab slots)")
    parser.add_argument("--steps", action="store_true", help="print step-by-step tables")
    parser.add_argument("--sweep", type=int, metavar="MAX", help="sweep frames 1..MAX instead of one run")
    parser.add_argument("--save", action="store_true", help=f"save charts into ./{OUT_DIR}/")
    parser.add_argument("--no-plot", action="store_true", help="do not open chart windows")
    args = parser.parse_args()

    if not args.preset and args.seq is None:
        try:
            menu()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
        return

    try:
        if args.preset:
            _, sequence, default_frames = get_preset(args.preset)
            label = args.preset
        else:
            sequence, default_frames, label = parse_input(args.seq), 3, "custom"
        frames = args.frames if args.frames is not None else default_frames
        if args.sweep:
            run_sweep(sequence, label, args.sweep, plot=not args.no_plot, save=args.save)
        else:
            run_and_report(sequence, frames, label, steps=args.steps, plot=not args.no_plot, save=args.save)
    except ValueError as err:
        parser.error(str(err))


if __name__ == "__main__":
    main()
