
def fcfs(processes):
    """
    FCFS (First Come First Served) CPU scheduling algorithm.
    Girdi: Process listesi
    Çıktı: (gantt_list, processes)
    gantt_list -> [(pid, start, finish), ...]
    """
    # Arrival time'a göre sırala
    processes.sort(key=lambda p: p.arrival_time)

    time = 0
    gantt = []

    for p in processes:
        # CPU boşta ve process henüz gelmemişse
        if time < p.arrival_time:
            time = p.arrival_time

        p.start_time = time
        time += p.burst_time
        p.completion_time = time

        # Gantt chart bilgisi
        gantt.append((p.pid, p.start_time, p.completion_time))

        # Metrikler
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time
        p.response_time = p.start_time - p.arrival_time

    return gantt, processes


def sjf(processes):
    """
    Non-preemptive Shortest Job First scheduling.
    Girdi: Process listesi
    Çıktı: (gantt_list, processes)
    """
    time = 0
    gantt = []
    completed = 0
    n = len(processes)

    # Başlangıçta arrival_time'a göre kaba sıralama yap
    processes.sort(key=lambda p: p.arrival_time)

    ready = []

    while completed < n:
        # 1) Zamanı gelmiş tüm process'leri ready listesine ekle
        for p in processes:
            if (p.arrival_time <= time) and (p.start_time is None) and (p not in ready):
                ready.append(p)

        # 2) Eğer ready boşsa → CPU idle, zamanı ilerlet
        if not ready:
            time += 1
            continue

        # 3) Burst time en küçük olanı seç
        ready.sort(key=lambda p: p.burst_time)
        current = ready.pop(0)

        # 4) Bu process başlasın
        current.start_time = time
        time += current.burst_time
        current.completion_time = time

        # metrikler
        current.turnaround_time = current.completion_time - current.arrival_time
        current.waiting_time = current.start_time - current.arrival_time
        current.response_time = current.start_time - current.arrival_time

        # gantt
        gantt.append((current.pid, current.start_time, current.completion_time))

        completed += 1

    return gantt, processes
def priority_non_preemptive(processes):
    """
    Priority Scheduling (Non-preemptive)
    Lower number = higher priority.
    Tie-break: arrival_time -> pid
    Returns:
      gantt: list of tuples (start, end, pid_or_IDLE)
      processes: same list with computed times
    """
    # reset
    for p in processes:
        p.start_time = None
        p.completion_time = None
        p.waiting_time = 0
        p.turnaround_time = 0
        p.response_time = None

    time = 0
    completed = 0
    n = len(processes)
    gantt = []

    remaining = {p.pid: p.burst_time for p in processes}

    while completed < n:
        ready = [p for p in processes if p.arrival_time <= time and remaining[p.pid] > 0]

        if not ready:
            next_arrival = min(
                (p.arrival_time for p in processes if remaining[p.pid] > 0),
                default=None
            )
            if next_arrival is None:
                break
            if next_arrival > time:
                gantt.append((time, next_arrival, "IDLE"))
                time = next_arrival
            continue

        chosen = min(ready, key=lambda p: (p.priority, p.arrival_time, p.pid))

        if chosen.start_time is None:
            chosen.start_time = time
            chosen.response_time = chosen.start_time - chosen.arrival_time

        run = remaining[chosen.pid]  # non-preemptive: finish it
        gantt.append((time, time + run, chosen.pid))
        time += run

        remaining[chosen.pid] = 0
        chosen.completion_time = time
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time

        completed += 1

    return gantt, processes


def round_robin(processes, quantum=2):
    """
    Round Robin CPU scheduling.
    Girdi: process listesi, time quantum
    Çıktı: (gantt_list, processes)
    """
    time = 0
    gantt = []
    queue = []
    n = len(processes)
    completed = 0

    # arrival_time'a göre sırala
    processes.sort(key=lambda p: p.arrival_time)

    # ilk gelenleri sıraya al
    idx = 0
    while idx < n and processes[idx].arrival_time <= time:
        queue.append(processes[idx])
        idx += 1

    last_pid = None
    start_slice = 0

    while completed < n:
        if not queue:
            # hiç ready yoksa zamanı ilerlet, yeni gelen varsa kuyruğa ekle
            time += 1
            while idx < n and processes[idx].arrival_time <= time:
                queue.append(processes[idx])
                idx += 1
            continue

        current = queue.pop(0)

        # yeni bir process CPU'ya giriyorsa gantt bloğunu yönet
        if last_pid != current.pid:
            if last_pid is not None:
                gantt.append((last_pid, start_slice, time))
            start_slice = time
            last_pid = current.pid

            if current.start_time is None:
                current.start_time = time  # response time için

        # bu dilimde çalışacağı süre
        run_time = min(quantum, current.remaining_time)
        current.remaining_time -= run_time
        time += run_time

        # bu süre içinde yeni gelen process'leri kuyruğa ekle
        while idx < n and processes[idx].arrival_time <= time:
            queue.append(processes[idx])
            idx += 1

        if current.remaining_time > 0:
            # bitmediyse kuyruğun sonuna at
            queue.append(current)
        else:
            # tamamlandı
            current.completion_time = time
            current.turnaround_time = time - current.arrival_time
            current.waiting_time = current.turnaround_time - current.burst_time
            current.response_time = current.start_time - current.arrival_time
            completed += 1

    # son gantt bloğunu kapat
    if last_pid is not None:
        gantt.append((last_pid, start_slice, time))

    return gantt, processes


