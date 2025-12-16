from utils import load_processes_from_json, clone_process_list
from schedulers import fcfs, sjf, round_robin, priority_non_preemptive
from metrics import calculate_metrics
from gantt import draw_gantt


def print_results(title, gantt, processes, chart_filename=None):
    print(f"\n--- {title} ---")
    for p in processes:
        print(
            f"{p.pid}: start={p.start_time}, finish={p.completion_time}, "
            f"waiting={p.waiting_time}, ta={p.turnaround_time}, resp={p.response_time}, "
            f"starvation_risk={getattr(p, 'starvation_risk', False)}"
        )

    m = calculate_metrics(processes, gantt=gantt)
    print(
        f"\nAverages -> Waiting={m['avg_waiting']:.2f}, "
        f"Turnaround={m['avg_turnaround']:.2f}, Response={m['avg_response']:.2f}, "
        f"CPU Util={m['cpu_util']:.2f}%"
    )

    if m["starved_count"] > 0:
        print(f"⚠️ Starvation risk detected for: {m['starved_pids']} (max_wait={m['max_waiting']:.2f})")

    if chart_filename is not None:
        draw_gantt(gantt, title, chart_filename)
        print(f"Gantt chart saved to {chart_filename}")


def main():
    processes = load_processes_from_json("data/processes.json")

    # FCFS
    proc_fcfs = clone_process_list(processes)
    gantt_fcfs, res_fcfs = fcfs(proc_fcfs)
    print_results("FCFS SONUCU", gantt_fcfs, res_fcfs, chart_filename="charts/fcfs.png")

    # SJF
    proc_sjf = clone_process_list(processes)
    gantt_sjf, res_sjf = sjf(proc_sjf)
    print_results("SJF SONUCU", gantt_sjf, res_sjf, chart_filename="charts/sjf.png")

    # PRIORITY - aging kapalı (starvation gör)
    proc_prio = clone_process_list(processes)
    gantt_prio, res_prio = priority_non_preemptive(
        proc_prio,
        enable_aging=False,
        starvation_threshold=10
    )
    print_results("PRIORITY SONUCU (AGING OFF)", gantt_prio, res_prio, chart_filename="charts/priority_no_aging.png")

    # PRIORITY - aging açık (anti-starvation)
    proc_prio2 = clone_process_list(processes)
    gantt_prio2, res_prio2 = priority_non_preemptive(
        proc_prio2,
        enable_aging=True,
        aging_interval=1,
        aging_boost=1,
        starvation_threshold=10
    )
    print_results("PRIORITY SONUCU (AGING ON)", gantt_prio2, res_prio2, chart_filename="charts/priority_aging.png")

    # RR
    proc_rr = clone_process_list(processes)
    gantt_rr, res_rr = round_robin(proc_rr, quantum=2)
    print_results("ROUND ROBIN SONUCU (q=2)", gantt_rr, res_rr, chart_filename="charts/rr_q2.png")


if __name__ == "__main__":
    main()
