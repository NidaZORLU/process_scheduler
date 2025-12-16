import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

from utils import load_processes_from_json, clone_process_list
from schedulers import fcfs, sjf, round_robin, priority_non_preemptive
from metrics import calculate_metrics


ALGORITHMS = {
    "FCFS": fcfs,
    "SJF (Non-preemptive)": sjf,
    "Round Robin": round_robin,
    "Priority (Non-preemptive)": priority_non_preemptive,
}


class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduling Simulator")
        self.root.geometry("980x640")

        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algorithm_var = tk.StringVar()
        self.algorithm_combo = ttk.Combobox(
            top_frame,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=28,
        )
        self.algorithm_combo.current(0)
        self.algorithm_combo.pack(side=tk.LEFT, padx=5)
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        ttk.Label(top_frame, text="Quantum (RR):").pack(side=tk.LEFT, padx=(20, 5))
        self.quantum_var = tk.StringVar(value="2")
        self.quantum_entry = ttk.Entry(top_frame, textvariable=self.quantum_var, width=6)
        self.quantum_entry.pack(side=tk.LEFT)

        # Aging checkbox (Priority için)
        self.aging_var = tk.BooleanVar(value=False)
        self.aging_check = ttk.Checkbutton(top_frame, text="Aging (anti-starvation)", variable=self.aging_var)
        self.aging_check.pack(side=tk.LEFT, padx=(20, 5))

        ttk.Label(top_frame, text="Starvation threshold:").pack(side=tk.LEFT, padx=(10, 5))
        self.starve_thr_var = tk.StringVar(value="10")
        self.starve_thr_entry = ttk.Entry(top_frame, textvariable=self.starve_thr_var, width=6)
        self.starve_thr_entry.pack(side=tk.LEFT)

        run_button = ttk.Button(top_frame, text="Run Simulation", command=self.run_simulation)
        run_button.pack(side=tk.LEFT, padx=20)

        mid_frame = ttk.Frame(root, padding=10)
        mid_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("pid", "arrival", "burst", "priority", "effprio", "start", "finish", "waiting", "turnaround", "starve")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", height=18)

        headers = {
            "pid": "PID",
            "arrival": "Arrival",
            "burst": "Burst",
            "priority": "Priority",
            "effprio": "Eff.Prio",
            "start": "Start",
            "finish": "Finish",
            "waiting": "Waiting",
            "turnaround": "Turnaround",
            "starve": "Starvation?",
        }

        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=90, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        bottom_frame = ttk.Frame(root, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.metrics_label = ttk.Label(bottom_frame, text="Metrics: -", anchor="w")
        self.metrics_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        gantt_button = ttk.Button(bottom_frame, text="Show Gantt Chart", command=self.show_gantt_chart)
        gantt_button.pack(side=tk.RIGHT)

        self.last_gantt = None
        self.on_algorithm_change()

    def on_algorithm_change(self, event=None):
        algo_name = self.algorithm_var.get() or self.algorithm_combo.get()

        is_rr = (algo_name == "Round Robin")
        self.quantum_entry.configure(state=("normal" if is_rr else "disabled"))

        is_prio = (algo_name == "Priority (Non-preemptive)")
        self.aging_check.configure(state=("normal" if is_prio else "disabled"))
        self.starve_thr_entry.configure(state=("normal" if is_prio else "disabled"))

    def _run_rr_safely(self, func, proc_list, q):
        try:
            return func(proc_list, quantum=q)
        except TypeError:
            return func(proc_list, q)

    def run_simulation(self):
        algo_name = self.algorithm_var.get()
        if not algo_name:
            messagebox.showwarning("Warning", "Please select a scheduling algorithm.")
            return

        try:
            processes = load_processes_from_json("data/processes.json")
        except FileNotFoundError:
            messagebox.showerror("Error", "data/processes.json not found.")
            return

        proc_list = clone_process_list(processes)
        func = ALGORITHMS[algo_name]

        if algo_name == "Round Robin":
            try:
                q = int(self.quantum_var.get())
                if q <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantum must be a positive integer.")
                return
            gantt, result = self._run_rr_safely(func, proc_list, q)

        elif algo_name == "Priority (Non-preemptive)":
            try:
                thr = int(self.starve_thr_var.get())
                if thr < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Starvation threshold must be a non-negative integer.")
                return

            gantt, result = priority_non_preemptive(
                proc_list,
                enable_aging=bool(self.aging_var.get()),
                aging_interval=1,
                aging_boost=1,
                starvation_threshold=thr
            )
        else:
            gantt, result = func(proc_list)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in result:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    getattr(p, "pid", "-"),
                    getattr(p, "arrival_time", "-"),
                    getattr(p, "burst_time", "-"),
                    getattr(p, "priority", "-"),
                    getattr(p, "effective_priority", getattr(p, "priority", "-")),
                    getattr(p, "start_time", "-"),
                    getattr(p, "completion_time", "-"),
                    getattr(p, "waiting_time", "-"),
                    getattr(p, "turnaround_time", "-"),
                    "YES" if getattr(p, "starvation_risk", False) else "NO",
                ),
            )

        m = calculate_metrics(result, gantt=gantt)

        text = (
            f"Metrics: Avg Waiting={m['avg_waiting']:.2f}, "
            f"Avg Turnaround={m['avg_turnaround']:.2f}, "
            f"CPU Util={m['cpu_util']:.2f}%, "
            f"Max Wait={m['max_waiting']:.2f}, "
            f"Starved={m['starved_count']} {m['starved_pids']}"
        )
        self.metrics_label.config(text=text)

        self.last_gantt = gantt

    def show_gantt_chart(self):
        if not self.last_gantt:
            messagebox.showinfo("Info", "Run a simulation first.")
            return

        fig, ax = plt.subplots(figsize=(10, 3))

        y_positions = {}
        current_y = 10

        for pid, start, end in self.last_gantt:
            if pid not in y_positions:
                y_positions[pid] = current_y
                current_y += 10
            ax.broken_barh([(start, end - start)], (y_positions[pid], 8))

        ax.set_xlabel("Time")
        ax.set_yticks(list(y_positions.values()))
        ax.set_yticklabels(list(y_positions.keys()))
        ax.set_title("Gantt Chart")
        plt.tight_layout()
        plt.show()


def main():
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    SchedulerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
