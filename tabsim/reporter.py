"""Output: console tables and matplotlib charts."""

import os

from .policies import ALL_POLICIES
from .simulator import Simulator

COLORS = {"FIFO": "#4C72B0", "LRU": "#55A868", "Optimal": "#C44E52", "Clock": "#8172B2"}
# Distinct line styles so policies with identical fault counts stay visible.
LINE_STYLES = {
    "FIFO": dict(marker="s", markersize=11, linestyle="-", linewidth=2),
    "LRU": dict(marker="^", markersize=8, linestyle="-", linewidth=2),
    "Optimal": dict(marker="D", markersize=7, linestyle="-", linewidth=2),
    "Clock": dict(marker="o", markersize=5, linestyle="--", linewidth=1.5),
}


def run_all(sequence, frame_count):
    """Run every policy on the same input and return a list of Results."""
    return [Simulator(sequence, frame_count, cls()).run() for cls in ALL_POLICIES]


def print_steps(result, frame_count):
    """Step-by-step frame table for one policy."""
    cell = 4
    print(f"\n=== {result.policy_name} (frames = {frame_count}) ===")
    header = f"{'Step':>4} {'Tab':>4} | " + " ".join(f"F{i + 1}".center(cell) for i in range(frame_count))
    print(header + " | Result  Evicted")
    print("-" * (len(header) + 18))
    for s in result.steps:
        frames = " ".join((f or "-").center(cell) for f in s.frames)
        outcome = "HIT   " if s.is_hit else "FAULT "
        evicted = s.evicted if s.evicted else "-"
        print(f"{s.index:>4} {s.tab:>4} | {frames} | {outcome}  {evicted}")
    print(f"Hits: {result.hits}  Faults: {result.faults}  Hit ratio: {result.hit_ratio():.1%}")


def print_summary(results, title="Comparison"):
    print(f"\n{title}")
    print(f"{'Policy':<10}{'Hits':>6}{'Faults':>8}{'Hit %':>9}{'Fault %':>9}")
    print("-" * 42)
    for r in results:
        print(f"{r.policy_name:<10}{r.hits:>6}{r.faults:>8}{r.hit_ratio():>9.1%}{r.fault_ratio():>9.1%}")
    best = min(r.faults for r in results)
    winners = [r.policy_name for r in results if r.faults == best and r.policy_name != "Optimal"]
    if winners:
        print(f"Best practical policy (fewest faults, Optimal excluded): {', '.join(winners)}")


def _plt():
    import matplotlib
    if not os.environ.get("DISPLAY") and os.name != "nt" and os.uname().sysname != "Darwin":
        matplotlib.use("Agg")  # no screen available (e.g. server)
    import matplotlib.pyplot as plt
    return plt


def plot_faults(results, title, save_path=None, show=True):
    """Bar chart: page faults per policy."""
    plt = _plt()
    names = [r.policy_name for r in results]
    faults = [r.faults for r in results]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(names, faults, color=[COLORS.get(n, "#777777") for n in names])
    for bar, value in zip(bars, faults):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.1, str(value), ha="center", va="bottom")
    ax.set_ylabel("Page faults (tab reloads)")
    ax.set_title(title)
    ax.set_ylim(0, max(faults) * 1.2 + 1)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _finish(fig, plt, save_path, show)


def plot_sweep(sequence, max_frames, title, save_path=None, show=True):
    """Line chart: faults vs number of frames, one line per policy."""
    plt = _plt()
    sizes = list(range(1, max_frames + 1))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for cls in ALL_POLICIES:
        name = cls.name
        faults = [Simulator(sequence, n, cls()).run().faults for n in sizes]
        ax.plot(sizes, faults, label=name, color=COLORS.get(name), **LINE_STYLES.get(name, {}))
    ax.set_xlabel("Number of frames (active tabs)")
    ax.set_ylabel("Page faults")
    ax.set_title(title)
    ax.set_xticks(sizes)
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _finish(fig, plt, save_path, show)


def _finish(fig, plt, save_path, show):
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150)
        print(f"Chart saved to {save_path}")
    if show:
        plt.show()
    plt.close(fig)
