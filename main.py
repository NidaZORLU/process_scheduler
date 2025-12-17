import argparse
from utils import load_processes_from_txt, clone_process_list
from schedulers import fcfs, sjf, round_robin, priority_non_preemptive
from metrics import calculate_metrics


def gantt_to_text(gantt):
    parts = []
    for pid, start, end in gantt:
        parts.append(f"[{start}]--{pid}--")
    parts.append(f"[{gantt[-1][2]}]")
    return "".join(parts)


def print_table(processes):
    print("Process | Finish Time | Turnaround Time | Waiting Time")
    print("-----------------------------------------------------")
    for p in processes:
        print(f"{p.pid:<7} | {p.completion_time:<11} | {p.turnaround_time:<14} | {p.waiting_time}")


def run_and_print(name, func, proc_list, *args, starvation_threshold=10, **kwargs):
    gantt, result = func(proc_list, *args, **kwargs)

    print(f"\n--- Scheduling Algorithm: {name} ---")
    print("Gantt Chart:")
    print(gantt_to_text(gantt))
    print()
    print_table(result)

    m = calculate_metrics(result, gantt=gantt, starvation_threshold=starvation_threshold)

    print(f"\nAverage Turnaround Time: {m['avg_turnaround']:.2f}")
    print(f"Average Waiting Time: {m['avg_waiting']:.2f}")
    print(f"CPU Utilization: {m['cpu_util']:.1f}%")

    if m["starved_count"] > 0:
        print(f"⚠ Starvation detected for: {m['starved_pids']} (max_wait={m['max_waiting']:.2f})")


def main():
    parser = argparse.ArgumentParser(description="Process Scheduling Simulator")
    parser.add_argument("file", help="Input process file (.txt)")
    parser.add_argument("--tq", type=int, default=3, help="Time quantum for Round Robin (default: 3)")
    parser.add_argument("--starve", type=int, default=10, help="Starvation threshold (default: 10)")
    args = parser.parse_args()

    if args.tq <= 0:
        raise ValueError("Time quantum must be a positive integer.")

    base = load_processes_from_txt(args.file)

    run_and_print("FCFS", fcfs, clone_process_list(base), starvation_threshold=args.starve)
    run_and_print("SJF", sjf, clone_process_list(base), starvation_threshold=args.starve)
    run_and_print(
        "Priority (Non-preemptive)",
        priority_non_preemptive,
        clone_process_list(base),
        starvation_threshold=args.starve,
        enable_aging=False,
        aging_interval=1,
        aging_boost=1
    )

    run_and_print(
        f"Round Robin (tq={args.tq})",
        round_robin,
        clone_process_list(base),
        args.tq,
        starvation_threshold=args.starve
    )


if __name__ == "__main__":
    main()
