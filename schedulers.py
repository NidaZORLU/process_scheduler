def fcfs(processes):
    for p in processes: p.reset()
    processes.sort(key=lambda p: p.arrival_time)
    time = 0; gantt = []

    for p in processes:
        if time < p.arrival_time:
            gantt.append(("IDLE", time, p.arrival_time))
            time = p.arrival_time
        p.start_time = time
        p.response_time = time - p.arrival_time
        time += p.burst_time
        p.completion_time = time
        p.turnaround_time = time - p.arrival_time
        p.waiting_time = p.start_time - p.arrival_time
        gantt.append((p.pid, p.start_time, p.completion_time))
    return gantt, processes


def sjf(processes):
    for p in processes: p.reset()
    time = 0; gantt = []; done = 0; n = len(processes)
    ready = []; added = set()
    processes.sort(key=lambda p: p.arrival_time)

    while done < n:
        for p in processes:
            if p.arrival_time <= time and p.pid not in added:
                ready.append(p); added.add(p.pid)
        if not ready:
            time += 1; continue
        ready.sort(key=lambda p: (p.burst_time, p.arrival_time))
        c = ready.pop(0)
        c.start_time = time
        c.response_time = time - c.arrival_time
        time += c.burst_time
        c.completion_time = time
        c.turnaround_time = time - c.arrival_time
        c.waiting_time = c.start_time - c.arrival_time
        gantt.append((c.pid, c.start_time, c.completion_time))
        done += 1
    return gantt, processes


def priority_non_preemptive(processes):
    for p in processes: p.reset()
    time = 0; gantt = []; done = 0; n = len(processes)

    while done < n:
        ready = [p for p in processes if p.arrival_time <= time and p.remaining_time > 0]
        if not ready:
            time += 1; continue
        ready.sort(key=lambda p: (p.priority, p.arrival_time))
        c = ready[0]
        if c.start_time is None:
            c.start_time = time
            c.response_time = time - c.arrival_time
        run = c.remaining_time
        gantt.append((c.pid, time, time + run))
        time += run
        c.remaining_time = 0
        c.completion_time = time
        c.turnaround_time = time - c.arrival_time
        c.waiting_time = c.turnaround_time - c.burst_time
        done += 1
    return gantt, processes


def round_robin(processes, quantum):
    for p in processes: p.reset()
    time = 0; gantt = []; q = []; done = 0
    processes.sort(key=lambda p: p.arrival_time)
    i = 0; n = len(processes)

    while done < n:
        while i < n and processes[i].arrival_time <= time:
            q.append(processes[i]); i += 1
        if not q:
            time += 1; continue
        c = q.pop(0)
        if c.start_time is None:
            c.start_time = time
            c.response_time = time - c.arrival_time
        run = min(quantum, c.remaining_time)
        gantt.append((c.pid, time, time + run))
        time += run
        c.remaining_time -= run
        while i < n and processes[i].arrival_time <= time:
            q.append(processes[i]); i += 1
        if c.remaining_time > 0:
            q.append(c)
        else:
            c.completion_time = time
            c.turnaround_time = time - c.arrival_time
            c.waiting_time = c.turnaround_time - c.burst_time
            done += 1
    return gantt, processes
