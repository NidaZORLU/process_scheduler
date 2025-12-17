import argparse, os
from utils import load_processes_from_txt, clone_process_list
from schedulers import fcfs, sjf, round_robin, priority_non_preemptive
from metrics import calculate_metrics

def print_gantt(g):
    s=""; 
    for pid,a,b in g: s+=f"[{a}]--{pid}--"
    print(s+f"[{g[-1][2]}]")

def print_table(ps):
    print("PID | Finish | Turnaround | Waiting")
    print("-----------------------------------")
    for p in ps:
        print(f"{p.pid:3} | {p.completion_time:6} | {p.turnaround_time:10} | {p.waiting_time:7}")

def run(name, func, ps, *args):
    g, r = func(ps, *args)
    print(f"\n--- {name} ---")
    print_gantt(g)
    print_table(r)
    aw, at, ar, mw, starved, cpu = calculate_metrics(r, g)
    print(f"Avg TA={at:.2f}, Avg W={aw:.2f}, CPU={cpu:.1f}%")
    if starved: print("Starvation:", starved)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--tq", type=int, default=3)
    args = ap.parse_args()

    base = load_processes_from_txt(args.file)

    run("FCFS", fcfs, clone_process_list(base))
    run("SJF", sjf, clone_process_list(base))
    run("PRIORITY", priority_non_preemptive, clone_process_list(base))
    run(f"RR tq={args.tq}", round_robin, clone_process_list(base), args.tq)

if __name__ == "__main__":
    main()
