"""Browser-session simulation using the project's existing replacement policies."""
import tkinter as tk
from tkinter import ttk, messagebox
from tabsim.policies import ALL_POLICIES
from tabsim.simulator import Simulator
from tabsim.workloads import parse_input, validate


class BrowserModeWindow(tk.Toplevel):
    """Estimate tab restoration impact under a fixed active-tab capacity."""
    def __init__(self, master):
        super().__init__(master)
        self.title("Browser Session Simulation")
        self.geometry("850x570")
        self.minsize(720, 480)
        self.transient(master)
        self.sequence = tk.StringVar(value="MAIL DOCS VIDEO MUSIC MAIL CHAT DOCS MAP MAIL")
        self.capacity = tk.IntVar(value=4)
        self.memory = tk.DoubleVar(value=350)
        self.restore = tk.DoubleVar(value=120)
        self.status = tk.StringVar(value="A page fault models a tab that must be restored into an active slot.")
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Browser Session Simulation", font=("Helvetica", 19, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Model tab suspension and restoration under a fixed active-tab memory budget.").pack(anchor="w", pady=(3, 12))
        controls = ttk.LabelFrame(outer, text="Session settings", padding=12)
        controls.pack(fill="x")
        ttk.Label(controls, text="Tab visit sequence (spaces or commas)").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.sequence).grid(row=1, column=0, columnspan=4, sticky="ew", pady=(4, 10))
        ttk.Label(controls, text="Active tab slots").grid(row=2, column=0, sticky="w")
        ttk.Spinbox(controls, from_=1, to=20, textvariable=self.capacity, width=8).grid(row=3, column=0, sticky="w", pady=(4, 0))
        ttk.Label(controls, text="Assumed MB per active tab").grid(row=2, column=1, sticky="w", padx=(12, 0))
        ttk.Spinbox(controls, from_=1, to=10000, increment=50, textvariable=self.memory, width=10).grid(row=3, column=1, sticky="w", padx=(12, 0), pady=(4, 0))
        ttk.Label(controls, text="Restore cost per fault (ms)").grid(row=2, column=2, sticky="w", padx=(12, 0))
        ttk.Spinbox(controls, from_=0, to=10000, increment=10, textvariable=self.restore, width=10).grid(row=3, column=2, sticky="w", padx=(12, 0), pady=(4, 0))
        ttk.Button(controls, text="Compare policies", command=self.run_comparison).grid(row=3, column=3, sticky="e", padx=(12, 0))
        controls.columnconfigure(0, weight=1)
        ttk.Label(outer, text="Browser impact comparison", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(16, 6))
        cols = ("policy", "faults", "restores", "memory", "restore_time", "hit_rate")
        self.table = ttk.Treeview(outer, columns=cols, show="headings", height=8)
        for col, label, width in [
            ("policy", "Policy", 100), ("faults", "Faults", 70), ("restores", "Restorations", 100),
            ("memory", "Active memory (MB)", 130), ("restore_time", "Estimated restore cost (ms)", 165),
            ("hit_rate", "Hit rate", 80),
        ]:
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="center")
        self.table.pack(fill="both", expand=True)
        ttk.Label(outer, textvariable=self.status, wraplength=790, justify="left").pack(anchor="w", pady=(10, 0))
        self.run_comparison()

    def run_comparison(self):
        try:
            sequence = parse_input(self.sequence.get())
            capacity = int(self.capacity.get())
            memory_mb = float(self.memory.get())
            restore_ms = float(self.restore.get())
            validate(sequence, capacity)
            if memory_mb <= 0 or restore_ms < 0:
                raise ValueError("Memory per tab must be positive and restore cost cannot be negative.")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Check session settings", str(exc), parent=self)
            return
        for item in self.table.get_children():
            self.table.delete(item)
        results = [Simulator(sequence, capacity, policy()).run() for policy in ALL_POLICIES]
        distinct_tabs = len(set(sequence))
        active_memory = min(distinct_tabs, capacity) * memory_mb
        for result in results:
            self.table.insert("", "end", values=(
                result.policy_name, result.faults, result.faults, f"{active_memory:,.0f}",
                f"{result.faults * restore_ms:,.0f}", f"{result.hit_ratio():.1%}"
            ))
        best_faults = min(r.faults for r in results)
        winners = ", ".join(r.policy_name for r in results if r.faults == best_faults)
        self.status.set(
            f"{len(sequence)} requests · {capacity} active slots · {memory_mb:g} MB assumed per tab. "
            f"Lowest estimated restoration cost: {winners} ({best_faults * restore_ms:,.0f} ms). "
            "Memory is a simplified fixed-capacity estimate; restore time is a configurable model, "
            "not measured Chrome/Safari performance. Optimal is a theoretical benchmark using future knowledge."
        )
