# schedulers.py

def fcfs(processes):
    """FCFS (Non-preemptive). Gantt: [(pid, start, end), ...]"""
    for p in processes:
        p.reset()

    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    gantt = []

    for p in processes:
        if time < p.arrival_time:
            # IDLE bloğu (opsiyonel)
            gantt.append(("IDLE", time, p.arrival_time))
            time = p.arrival_time

        p.start_time = time
        p.response_time = p.start_time - p.arrival_time

        time += p.burst_time
        p.completion_time = time

        gantt.append((p.pid, p.start_time, p.completion_time))

        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time

    return gantt, processes


def sjf(processes):
    """SJF (Non-preemptive). Gantt: [(pid, start, end), ...]"""
    for p in processes:
        p.reset()

    time = 0
    gantt = []
    completed = 0
    n = len(processes)

    processes.sort(key=lambda p: p.arrival_time)

    ready = []
    added = set()

    while completed < n:
        # ready'ye yeni gelenleri ekle
        for p in processes:
            if p.arrival_time <= time and p.pid not in added:
                ready.append(p)
                added.add(p.pid)

        if not ready:
            # CPU idle
            time += 1
            continue

        ready.sort(key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        current = ready.pop(0)

        current.start_time = time
        current.response_time = current.start_time - current.arrival_time

        time += current.burst_time
        current.completion_time = time

        current.turnaround_time = current.completion_time - current.arrival_time
        current.waiting_time = current.start_time - current.arrival_time

        gantt.append((current.pid, current.start_time, current.completion_time))
        completed += 1

    return gantt, processes


def priority_non_preemptive(
    processes,
    enable_aging=False,
    aging_interval=1,
    aging_boost=1,
    starvation_threshold=10
):
    """
    Priority Scheduling (Non-preemptive)
    Lower number = higher priority.

    Starvation tespiti:
      - ready'de bekleme süresi >= starvation_threshold ise process.starvation_risk = True

    Anti-starvation (AGING):
      - enable_aging=True ise, process’in effective_priority değeri
        bekledikçe iyileşir (küçülür).
      - Her seçim anında:
          waited = time - arrival_time
          steps = waited // aging_interval
          effective_priority = max(0, base_priority - steps * aging_boost)
    """
    for p in processes:
        p.reset()

    time = 0
    gantt = []
    completed = 0
    n = len(processes)

    remaining = {p.pid: p.burst_time for p in processes}

    while completed < n:
        ready = [p for p in processes if p.arrival_time <= time and remaining[p.pid] > 0]

        if not ready:
            # bir sonraki gelişe zıpla
            next_arrival = min(
                (p.arrival_time for p in processes if remaining[p.pid] > 0),
                default=None
            )
            if next_arrival is None:
                break
            if next_arrival > time:
                gantt.append(("IDLE", time, next_arrival))
                time = next_arrival
            continue

        # starvation risk işaretle + effective priority hesapla
        for p in ready:
            waited = time - p.arrival_time
            if waited >= starvation_threshold:
                p.starvation_risk = True

            if enable_aging:
                steps = (waited // aging_interval) if aging_interval > 0 else 0
                p.effective_priority = max(0, p.priority - steps * aging_boost)
            else:
                p.effective_priority = p.priority

        # seçimi effective priority ile yap
        chosen = min(ready, key=lambda p: (p.effective_priority, p.arrival_time, p.pid))

        chosen.start_time = time
        chosen.response_time = chosen.start_time - chosen.arrival_time

        run = remaining[chosen.pid]  # non-preemptive
        gantt.append((chosen.pid, time, time + run))

        time += run
        remaining[chosen.pid] = 0

        chosen.completion_time = time
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time

        completed += 1

    return gantt, processes


def round_robin(processes, quantum=2):
    """RR (Preemptive). Gantt: [(pid, start, end), ...]"""
    for p in processes:
        p.reset()

    time = 0
    gantt = []
    queue = []
    n = len(processes)
    completed = 0

    processes.sort(key=lambda p: p.arrival_time)

    idx = 0
    while idx < n and processes[idx].arrival_time <= time:
        queue.append(processes[idx])
        idx += 1

    while completed < n:
        if not queue:
            # idle - yeni geleni bekle
            time += 1
            while idx < n and processes[idx].arrival_time <= time:
                queue.append(processes[idx])
                idx += 1
            continue

        current = queue.pop(0)

        if current.start_time is None:
            current.start_time = time
            current.response_time = current.start_time - current.arrival_time

        start = time
        run_time = min(int(quantum), current.remaining_time)
        current.remaining_time -= run_time
        time += run_time
        end = time

        gantt.append((current.pid, start, end))

        while idx < n and processes[idx].arrival_time <= time:
            queue.append(processes[idx])
            idx += 1

        if current.remaining_time > 0:
            queue.append(current)
        else:
            current.completion_time = time
            current.turnaround_time = time - current.arrival_time
            current.waiting_time = current.turnaround_time - current.burst_time
            completed += 1

    return gantt, processes
