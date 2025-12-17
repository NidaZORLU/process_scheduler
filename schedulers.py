# schedulers.py

def fcfs(processes):
    """
    First-Come, First-Served (Non-preemptive)
    Gantt format: [(pid, start, end), ...]  (IDLE included)
    """
    for p in processes:
        p.reset()

    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    gantt = []

    for p in processes:
        if time < p.arrival_time:
            gantt.append(("IDLE", time, p.arrival_time))
            time = p.arrival_time

        p.start_time = time
        p.response_time = p.start_time - p.arrival_time

        time += p.burst_time
        p.completion_time = time

        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time

        gantt.append((p.pid, p.start_time, p.completion_time))

    return gantt, processes


def sjf(processes):
    """
    Shortest Job First (Non-preemptive)
    Tie-break: FCFS (arrival_time)
    Gantt format: [(pid, start, end), ...]
    """
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
        # Add newly arrived processes to ready queue
        for p in processes:
            if p.arrival_time <= time and p.pid not in added:
                ready.append(p)
                added.add(p.pid)

        if not ready:
            # No process ready -> CPU idle for 1 time unit
            time += 1
            continue

        # Pick shortest burst; tie-break by arrival_time then pid for deterministic output
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

    Starvation detection:
      - If a process waits in ready queue for >= starvation_threshold time,
        process.starvation_risk is set True.

    Aging (anti-starvation):
      - If enable_aging=True, an effective_priority is computed:
          waited = time - arrival_time   (process hasn't started yet)
          steps = waited // aging_interval
          effective_priority = max(0, base_priority - steps * aging_boost)
      - Selection uses effective_priority instead of base priority.
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
            # Jump to next arrival (include IDLE block)
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

        # Starvation mark + effective priority calculation
        for p in ready:
            waited = time - p.arrival_time

            # starvation mark
            p.starvation_risk = (waited >= starvation_threshold)

            # effective priority (aging) or base priority
            if enable_aging:
                steps = (waited // aging_interval) if aging_interval > 0 else 0
                p.effective_priority = max(0, p.priority - steps * aging_boost)
            else:
                p.effective_priority = p.priority

        # Choose process with best (lowest) effective priority; tie-break FCFS
        chosen = min(ready, key=lambda p: (p.effective_priority, p.arrival_time, p.pid))

        if chosen.start_time is None:
            chosen.start_time = time
            chosen.response_time = chosen.start_time - chosen.arrival_time

        run = remaining[chosen.pid]  # non-preemptive -> run to completion
        gantt.append((chosen.pid, time, time + run))

        time += run
        remaining[chosen.pid] = 0

        chosen.completion_time = time
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time

        completed += 1

    return gantt, processes


def round_robin(processes, quantum=3):
    """
    Round Robin (Preemptive)
    quantum must be provided (default=3 for report requirement).
    Gantt format: [(pid, start, end), ...]
    """
    for p in processes:
        p.reset()

    time = 0
    gantt = []
    queue = []

    processes.sort(key=lambda p: p.arrival_time)
    n = len(processes)
    idx = 0
    completed = 0

    # initially add processes that arrived at time 0
    while idx < n and processes[idx].arrival_time <= time:
        queue.append(processes[idx])
        idx += 1

    while completed < n:
        if not queue:
            # CPU idle for 1 unit, wait for arrivals
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

        # add newly arrived processes during this slice
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
