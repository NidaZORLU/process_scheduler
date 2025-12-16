# metrics.py

def calculate_metrics(processes):
    """
    Her process listesinden ortalama waiting, turnaround ve response hesaplar.
    """
    n = len(processes)

    avg_waiting = sum(p.waiting_time for p in processes) / n
    avg_turnaround = sum(p.turnaround_time for p in processes) / n
    avg_response = sum(p.response_time for p in processes) / n

    return avg_waiting, avg_turnaround, avg_response
