"""Desktop GUI for the Browser Tab Page Replacement Simulator.

Run with: python3 gui.py
The GUI wraps the existing simulator; it does not duplicate policy logic.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from tabsim.policies import ALL_POLICIES
from tabsim.simulator import Simulator
from tabsim.workloads import PRESETS, get_preset, parse_input, validate
from tabsim.browser_mode import BrowserModeWindow

BG = "#f4f6fa"
CARD = "#ffffff"
INK = "#172033"
MUTED = "#64748b"
ACCENT = "#3157a4"


class SimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Browser Tab Page Replacement Simulator")
        self.geometry("1120x790")
        self.minsize(920, 680)
        self.configure(bg=BG)
        self.results = []
        self._setup_style()
        self._build_ui()
        self._load_preset("demo")
        self.run_simulation()

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=INK, font=("Helvetica", 10))
        style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), foreground=INK, background=BG)
        style.configure("Sub.TLabel", font=("Helvetica", 10), foreground=MUTED, background=BG)
        style.configure("CardTitle.TLabel", font=("Helvetica", 11, "bold"), background=CARD, foreground=INK)
        style.configure("TButton", font=("Helvetica", 10), padding=(12, 7))
        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", font=("Helvetica", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#244583")])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=27, background=CARD, fieldbackground=CARD)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("TLabelframe", background=BG)
        style.configure("TLabelframe.Label", background=BG, foreground=INK, font=("Helvetica", 10, "bold"))

    def _build_ui(self):
        outer = ttk.Frame(self, padding=(22, 18))
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Browser Tab Page Replacement Simulator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Compare FIFO, LRU, Optimal and Clock without using command-line options.", style="Sub.TLabel").pack(anchor="w", pady=(3, 15))

        controls = ttk.Frame(outer, style="Card.TFrame", padding=14)
        controls.pack(fill="x", pady=(0, 12))
        ttk.Label(controls, text="Workload", background=CARD).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.preset_var = tk.StringVar(value="demo")
        preset_values = list(PRESETS.keys()) + ["custom"]
        self.preset_box = ttk.Combobox(controls, textvariable=self.preset_var, values=preset_values, state="readonly", width=15)
        self.preset_box.grid(row=1, column=0, sticky="ew", padx=(0, 18), pady=(5, 0))
        self.preset_box.bind("<<ComboboxSelected>>", self._preset_changed)

        ttk.Label(controls, text="Tab sequence (spaces or commas)", background=CARD).grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.sequence_var = tk.StringVar()
        self.sequence_entry = ttk.Entry(controls, textvariable=self.sequence_var)
        self.sequence_entry.grid(row=1, column=1, sticky="ew", padx=(0, 18), pady=(5, 0))

        ttk.Label(controls, text="Frames", background=CARD).grid(row=0, column=2, sticky="w")
        self.frames_var = tk.IntVar(value=3)
        self.frames_spin = ttk.Spinbox(controls, from_=1, to=20, textvariable=self.frames_var, width=5)
        self.frames_spin.grid(row=1, column=2, sticky="w", pady=(5, 0))

        self.run_button = ttk.Button(controls, text="Run comparison", style="Accent.TButton", command=self.run_simulation)
        self.run_button.grid(row=1, column=3, sticky="e", padx=(18, 0), pady=(5, 0))
        ttk.Button(controls, text="Browser mode", command=self.open_browser_mode).grid(row=1, column=4, sticky="e", padx=(8, 0), pady=(5, 0))
        controls.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(outer, textvariable=self.status_var, style="Sub.TLabel").pack(anchor="w", pady=(0, 8))

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, style="Card.TFrame", padding=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = ttk.Frame(body, style="Card.TFrame", padding=12)
        right.pack(side="right", fill="both", expand=True)

        ttk.Label(left, text="Policy comparison", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        columns = ("policy", "hits", "faults", "hit_ratio", "fault_ratio")
        self.summary = ttk.Treeview(left, columns=columns, show="headings", height=7, selectmode="browse")
        for col, title, width in [
            ("policy", "Policy", 100), ("hits", "Hits", 55), ("faults", "Faults", 65),
            ("hit_ratio", "Hit %", 70), ("fault_ratio", "Fault %", 75),
        ]:
            self.summary.heading(col, text=title)
            self.summary.column(col, width=width, anchor="center")
        self.summary.pack(fill="x")
        self.summary.bind("<<TreeviewSelect>>", self._show_selected_trace)

        ttk.Label(left, text="Step-by-step trace", style="CardTitle.TLabel").pack(anchor="w", pady=(16, 8))
        trace_bar = ttk.Frame(left, style="Card.TFrame")
        trace_bar.pack(fill="x", pady=(0, 6))
        ttk.Label(trace_bar, text="Policy:", background=CARD).pack(side="left", padx=(0, 6))
        self.trace_policy_var = tk.StringVar(value="FIFO")
        self.trace_policy_box = ttk.Combobox(trace_bar, textvariable=self.trace_policy_var, values=[c.name for c in ALL_POLICIES], state="readonly", width=12)
        self.trace_policy_box.pack(side="left")
        self.trace_policy_box.bind("<<ComboboxSelected>>", self._show_selected_trace)
        trace_cols = ("step", "tab", "frames", "result", "evicted")
        self.trace = ttk.Treeview(left, columns=trace_cols, show="headings", height=11)
        for col, title, width in [("step", "#", 42), ("tab", "Tab", 55), ("frames", "Frames after request", 190), ("result", "Status", 70), ("evicted", "Evicted", 65)]:
            self.trace.heading(col, text=title)
            self.trace.column(col, width=width, anchor="center")
        self.trace.tag_configure("fault", foreground="#b42318")
        self.trace.tag_configure("hit", foreground="#18794e")
        trace_scroll = ttk.Scrollbar(left, orient="vertical", command=self.trace.yview)
        self.trace.configure(yscrollcommand=trace_scroll.set)
        self.trace.pack(side="left", fill="both", expand=True)
        trace_scroll.pack(side="right", fill="y")

        ttk.Label(right, text="Page faults by policy", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        self.figure = Figure(figsize=(5.1, 4.2), dpi=100, facecolor=CARD)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.insight_var = tk.StringVar(value="Run a workload to see a summary.")
        insight = ttk.Label(right, textvariable=self.insight_var, wraplength=420, justify="left", background=CARD, foreground=MUTED)
        insight.pack(fill="x", pady=(8, 2), anchor="w")

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(footer, text="Tip: choose 'custom' to enter your own sequence. Example: A B C A B D", style="Sub.TLabel").pack(side="left")
        ttk.Button(footer, text="Reset", command=self.reset_inputs).pack(side="right")

    def open_browser_mode(self):
        BrowserModeWindow(self)

    def _load_preset(self, name):
        if name not in PRESETS:
            return
        _, sequence, frames = get_preset(name)
        self.sequence_var.set(" ".join(sequence))
        self.frames_var.set(frames)

    def _preset_changed(self, _event=None):
        name = self.preset_var.get()
        if name in PRESETS:
            self._load_preset(name)
        else:
            self.sequence_entry.focus_set()
            self.sequence_entry.selection_range(0, tk.END)

    def reset_inputs(self):
        self.preset_var.set("demo")
        self._load_preset("demo")
        self.status_var.set("Inputs reset to the demo workload.")
        self.run_simulation()

    def run_simulation(self):
        try:
            sequence = parse_input(self.sequence_var.get())
            frames = int(self.frames_var.get())
            validate(sequence, frames)
            self.results = [Simulator(sequence, frames, policy()).run() for policy in ALL_POLICIES]
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Check your inputs", str(exc) or "Enter a whole number of frames from 1 to 20.", parent=self)
            return

        for item in self.summary.get_children():
            self.summary.delete(item)
        for result in self.results:
            self.summary.insert("", "end", iid=result.policy_name, values=(
                result.policy_name, result.hits, result.faults,
                f"{result.hit_ratio():.1%}", f"{result.fault_ratio():.1%}"
            ))
        self.trace_policy_var.set("FIFO")
        self._draw_chart()
        self._show_trace("FIFO")
        best = min(result.faults for result in self.results)
        winners = [result.policy_name for result in self.results if result.faults == best]
        self.insight_var.set(f"Lowest page faults: {', '.join(winners)} ({best}). Optimal is a theoretical benchmark because it uses future knowledge. Results are for this workload only.")
        self.status_var.set(f"Completed: {len(sequence)} requests · {frames} frames · {len(self.results)} policies compared")

    def _draw_chart(self):
        self.ax.clear()
        names = [r.policy_name for r in self.results]
        faults = [r.faults for r in self.results]
        colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2"]
        bars = self.ax.bar(names, faults, color=colors)
        self.ax.bar_label(bars, padding=3, fontsize=9)
        self.ax.set_ylabel("Page faults")
        self.ax.set_ylim(0, max(faults or [1]) * 1.22 + 0.5)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_facecolor(CARD)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _show_selected_trace(self, _event=None):
        selected = self.summary.selection()
        policy_name = selected[0] if selected else self.trace_policy_var.get()
        if selected and policy_name in [r.policy_name for r in self.results]:
            self.trace_policy_var.set(policy_name)
        self._show_trace(self.trace_policy_var.get())

    def _show_trace(self, policy_name):
        result = next((r for r in self.results if r.policy_name == policy_name), None)
        for item in self.trace.get_children():
            self.trace.delete(item)
        if result is None:
            return
        for step in result.steps:
            frame_text = "  |  ".join(frame if frame is not None else "–" for frame in step.frames)
            status = "HIT" if step.is_hit else "FAULT"
            self.trace.insert("", "end", values=(step.index, step.tab, frame_text, status, step.evicted or "–"), tags=("hit" if step.is_hit else "fault",))


def main():
    app = SimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
