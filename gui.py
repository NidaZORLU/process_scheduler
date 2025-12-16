import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt

from utils import load_processes_from_json, clone_process_list
from schedulers import fcfs, sjf, round_robin, priority_non_preemptive


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
        self.root.geometry("900x600")

        # Üst çerçeve: algoritma seçimi + quantum
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Algorithm:").pack(side=tk.LEFT)

        self.algorithm_var = tk.StringVar()
        self.algorithm_combo = ttk.Combobox(
            top_frame,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=25,
        )
        self.algorithm_combo.current(0)
        self.algorithm_combo.pack(side=tk.LEFT, padx=5)
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        ttk.Label(top_frame, text="Quantum (for RR):").pack(side=tk.LEFT, padx=(20, 5))
        self.quantum_var = tk.StringVar(value="2")
        self.quantum_entry = ttk.Entry(top_frame, textvariable=self.quantum_var, width=5)
        self.quantum_entry.pack(side=tk.LEFT)

        run_button = ttk.Button(top_frame, text="Run Simulation", command=self.run_simulation)
        run_button.pack(side=tk.LEFT, padx=20)

        # Orta çerçeve: process sonuç tablosu
        mid_frame = ttk.Frame(root, padding=10)
        mid_frame.pack(fill=tk.BOTH, expand=True)

        # Priority rubrikte var diye gösteriyoruz
        columns = ("pid", "arrival", "burst", "priority", "start", "finish", "waiting", "turnaround")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", height=15)

        headers = {
            "pid": "PID",
            "arrival": "Arrival",
            "burst": "Burst",
            "priority": "Priority",
            "start": "Start",
            "finish": "Finish",
            "waiting": "Waiting",
            "turnaround": "Turnaround",
        }

        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=100, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Alt çerçeve: metrikler
        bottom_frame = ttk.Frame(root, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.metrics_label = ttk.Label(bottom_frame, text="Metrics: -", anchor="w")
        self.metrics_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        gantt_button = ttk.Button(bottom_frame, text="Show Gantt Chart", command=self.show_gantt_chart)
        gantt_button.pack(side=tk.RIGHT)

        # Gantt verisini saklamak için
        self.last_gantt = None

        # İlk açılışta quantum'u doğru state'e al
        self.on_algorithm_change()

    def on_algorithm_change(self, event=None):
        algo_name = self.algorithm_var.get() or self.algorithm_combo.get()
        is_rr = (algo_name == "Round Robin")
        self.quantum_entry.configure(state=("normal" if is_rr else "disabled"))

    def _run_rr_safely(self, func, proc_list, q):
        """
        round_robin imzası iki türlü olabiliyor:
        - round_robin(proc_list, quantum=2)
        - round_robin(proc_list, 2)
        İkisini de dene.
        """
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

        # Algoritmayı çağır (TEK blok)
        if algo_name == "Round Robin":
            try:
                q = int(self.quantum_var.get())
                if q <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantum must be a positive integer.")
                return

            gantt, result = self._run_rr_safely(func, proc_list, q)
        else:
            gantt, result = func(proc_list)

        # Treeview'i temizle
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Sonuçları tabloya yaz
        for p in result:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    getattr(p, "pid", "-"),
                    getattr(p, "arrival_time", "-"),
                    getattr(p, "burst_time", "-"),
                    getattr(p, "priority", "-"),
                    getattr(p, "start_time", "-"),
                    getattr(p, "completion_time", "-"),
                    getattr(p, "waiting_time", "-"),
                    getattr(p, "turnaround_time", "-"),
                ),
            )

        # METRİKLERİ HESAPLA
        waiting_times = [getattr(p, "waiting_time", 0) for p in result]
        turnaround_times = [getattr(p, "turnaround_time", 0) for p in result]
        burst_times = [getattr(p, "burst_time", 0) for p in result]
        completion_times = [getattr(p, "completion_time", 0) for p in result]

        avg_waiting = (sum(waiting_times) / len(waiting_times)) if waiting_times else 0.0
        avg_turnaround = (sum(turnaround_times) / len(turnaround_times)) if turnaround_times else 0.0

        # CPU utilization: makespan üzerinden hesaplamak daha doğru
        if gantt:
            # gantt tuple formatı: (start, end, pid) veya (pid, start, end) olabilir
            makespan = 0.0
            for item in gantt:
                if isinstance(item, dict):
                    s = float(item.get("start", item.get("start_time", 0)))
                    e = float(item.get("end", item.get("finish", s)))
                else:
                    a, b, c = item
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        s, e = float(a), float(b)
                    else:
                        s, e = float(b), float(c)
                makespan = max(makespan, e)
        else:
            makespan = float(max(completion_times)) if completion_times else 0.0

        busy_time = float(sum(burst_times))
        cpu_util = (100.0 * busy_time / makespan) if makespan > 0 else 0.0

        text = (
            f"Metrics:  "
            f"Avg Waiting = {avg_waiting:.2f},  "
            f"Avg Turnaround = {avg_turnaround:.2f},  "
            f"CPU Utilization = {cpu_util:.2f}%"
        )
        self.metrics_label.config(text=text)

        # Gantt'ı sakla
        self.last_gantt = gantt

    def show_gantt_chart(self):
        if not self.last_gantt:
            messagebox.showinfo("Info", "Run a simulation first.")
            return

        fig, ax = plt.subplots(figsize=(10, 3))

        def parse_item(item):
            if isinstance(item, dict):
                pid = item.get("pid") or item.get("process") or "P?"
                start = item.get("start") or item.get("start_time") or 0
                end = item.get("end") or item.get("finish") or (start + item.get("duration", 0))
                return str(pid), float(start), float(end)

            a, b, c = item
            # (start, end, pid)  or (pid, start, end)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                start, end, pid = a, b, c
            else:
                pid, start, end = a, b, c
            return str(pid), float(start), float(end)

        y_positions = {}
        current_y = 10

        for item in self.last_gantt:
            pid, start, end = parse_item(item)
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

    # macOS'te pencere bazen arkada açılır; öne al
    root.lift()
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))

    app = SchedulerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
