from utils import load_processes_from_json, clone_process_list
from schedulers import fcfs, sjf, round_robin, priority_non_preemptive
from metrics import calculate_metrics
from gantt import draw_gantt  # sende hangi dosyadaysa ona göre

def print_results(title, gantt, processes, chart_filename=None):
    print(f"\n--- {title} ---")
    for p in processes:
        print(
            f"{p.pid}: start={p.start_time}, finish={p.completion_time}, "
            f"waiting={p.waiting_time}, ta={p.turnaround_time}, resp={p.response_time}"
        )

    print("\nGantt Chart:")
    print(gantt)

    avg_w, avg_ta, avg_r = calculate_metrics(processes)
    print(
        f"\nAverages -> Waiting={avg_w:.2f}, "
        f"Turnaround={avg_ta:.2f}, Response={avg_r:.2f}"
    )

    if chart_filename is not None:
        draw_gantt(gantt, title, chart_filename)
        print(f"Gantt chart saved to {chart_filename}")


def main():
    processes = load_processes_from_json("data/processes.json")

    # FCFS
    proc_fcfs = clone_process_list(processes)
    gantt_fcfs, res_fcfs = fcfs(proc_fcfs)
    print_results("FCFS SONUCU", gantt_fcfs, res_fcfs, chart_filename="charts/fcfs.png")

    # SJF (non-preemptive)
    proc_sjf = clone_process_list(processes)
    gantt_sjf, res_sjf = sjf(proc_sjf)
    print_results("SJF SONUCU", gantt_sjf, res_sjf, chart_filename="charts/sjf.png")

    # Priority (Non-preemptive)
    proc_prio = clone_process_list(processes)
    gantt_prio, res_prio = priority_non_preemptive(proc_prio)
    print_results("PRIORITY SONUCU", gantt_prio, res_prio, chart_filename="charts/priority.png")

    # Round Robin
    proc_rr = clone_process_list(processes)
    gantt_rr, res_rr = round_robin(proc_rr, quantum=2)
    print_results("ROUND ROBIN SONUCU (q=2)", gantt_rr, res_rr, chart_filename="charts/rr_q2.png")


if __name__ == "__main__":
    main()
