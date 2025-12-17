# metrics.py

def calculate_metrics(processes, gantt=None, starvation_threshold=10):
    """
    Returns a dictionary of metrics:
      avg_waiting, avg_turnaround, avg_response,
      max_waiting, starved_count, starved_pids,
      cpu_util
    """
    n = len(processes)
    if n == 0:
        return {
            "avg_waiting": 0.0,
            "avg_turnaround": 0.0,
            "avg_response": 0.0,
            "max_waiting": 0.0,
            "starved_count": 0,
            "starved_pids": [],
            "cpu_util": 0.0,
        }

    avg_waiting = sum(p.waiting_time for p in processes) / n
    avg_turnaround = sum(p.turnaround_time for p in processes) / n
    avg_response = sum(p.response_time for p in processes) / n

    max_waiting = max(p.waiting_time for p in processes)

    # starvation: waiting_time threshold'a göre belirle (en doğru ve rapor uyumlu)
    starved_pids = [p.pid for p in processes if p.waiting_time >= starvation_threshold]

    cpu_util = 0.0
    if gantt:
        makespan = max(end for _, _, end in gantt)
        busy = sum((end - start) for pid, start, end in gantt if pid != "IDLE")
        cpu_util = (100.0 * busy / makespan) if makespan > 0 else 0.0

    return {
        "avg_waiting": avg_waiting,
        "avg_turnaround": avg_turnaround,
        "avg_response": avg_response,
        "max_waiting": max_waiting,
        "starved_count": len(starved_pids),
        "starved_pids": starved_pids,
        "cpu_util": cpu_util,
    }
