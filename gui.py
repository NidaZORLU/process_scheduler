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
        self.root.minsize(780, 520)

        controls = ttk.Frame(root, padding=10)
        controls.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(controls, text="Algorithm:").pack(side=tk.LEFT)
        self.algorithm_var = tk.StringVar(value=list(ALGORITHMS.keys())[0])
        self.algorithm_combo = ttk.Combobox(
            controls,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=22,
        )
        self.algorithm_combo.pack(side=tk.LEFT, padx=5)
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        ttk.Label(controls, text="Quantum (RR):").pack(side=tk.LEFT, padx=(12, 5))
        self.quantum_var = tk.StringVar(value="3")
        self.quantum_entry = ttk.Entry(controls, textvariable=self.quantum_var, width=6)
        self.quantum_entry.pack(side=tk.LEFT)

        self.aging_var = tk.BooleanVar(value=False)
        self.aging_check = ttk.Checkbutton(
            controls, text="Aging (anti-starvation)", variable=self.aging_var
        )
        self.aging_check.pack(side=tk.LEFT, padx=(12, 5))

        ttk.Label(controls, text="Starvation threshold:").pack(side=tk.LEFT, padx=(12, 5))
        self.starve_thr_var = tk.StringVar(value="10")
        self.starve_thr_entry = ttk.Entry(controls, textvariable=self.starve_thr_var, width=6)
        self.starve_thr_entry.pack(side=tk.LEFT)

        buttons = ttk.Frame(root, padding=(10, 0, 10, 10))
        buttons.pack(side=tk.TOP, fill=tk.X)

        self.run_button = ttk.Button(buttons, text="Run Simulation", command=self.run_simulation)
        self.run_button.pack(side=tk.RIGHT)

        self.gantt_button = ttk.Button(buttons, text="Show Gantt Chart", command=self.show_gantt_chart)
        self.gantt_button.pack(side=tk.RIGHT, padx=(0, 10))

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
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load input: {e}")
            return

        proc_list = clone_process_list(processes)
        func = ALGORITHMS[algo_name]

        try:
            if algo_name == "Round Robin":
                q = int(self.quantum_var.get())
                if q <= 0:
                    raise ValueError
                gantt, result = self._run_rr_safely(func, proc_list, q)

            elif algo_name == "Priority (Non-preemptive)":
                thr = int(self.starve_thr_var.get())
                if thr < 0:
                    raise ValueError

                gantt, result = priority_non_preemptive(
                    proc_list,
                    enable_aging=bool(self.aging_var.get()),
                    aging_interval=1,
                    aging_boost=1,
                    starvation_threshold=thr
                )
            else:
                gantt, result = func(proc_list)

        except ValueError:
            messagebox.showerror("Error", "Quantum/threshold must be a valid non-negative integer (quantum > 0).")
            return
        except Exception as e:
            messagebox.showerror("Simulation Error", str(e))
            return

        self.last_gantt = gantt

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

        try:
            m = calculate_metrics(result, gantt=gantt)
            text = (
                f"Metrics: Avg Waiting={m['avg_waiting']:.2f}, "
                f"Avg Turnaround={m['avg_turnaround']:.2f}, "
                f"CPU Util={m['cpu_util']:.2f}%, "
                f"Max Wait={m['max_waiting']:.2f}, "
                f"Starved={m['starved_count']} {m['starved_pids']}"
            )
        except Exception as e:
            text = f"Metrics: error ({e})"
        self.metrics_label.config(text=text)

    def show_gantt_chart(self):
        # More robust check: allow empty list vs None
        if self.last_gantt is None or len(self.last_gantt) == 0:
            messagebox.showinfo("Info", "Run a simulation first.")
            return

        try:
            plt.close("all")

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

        except Exception as e:
            messagebox.showerror("Gantt Error", f"Failed to render chart: {e}")


def main():
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    SchedulerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
