def calculate_metrics(processes, gantt, starvation_threshold=10):
    n = len(processes)
    avg_w = sum(p.waiting_time for p in processes)/n
    avg_t = sum(p.turnaround_time for p in processes)/n
    avg_r = sum(p.response_time for p in processes)/n
    max_w = max(p.waiting_time for p in processes)
    starved = [p.pid for p in processes if p.waiting_time >= starvation_threshold]

    makespan = max(e for _,_,e in gantt)
    busy = sum(e-s for pid,s,e in gantt if pid!="IDLE")
    cpu = (busy/makespan)*100 if makespan>0 else 0

    return avg_w, avg_t, avg_r, max_w, starved, cpu
