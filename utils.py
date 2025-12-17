from models import Process

def load_processes_from_txt(path):
    processes = []
    with open(path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            pid, at, bt, pr = [x.strip() for x in line.split(",")]
            processes.append(Process(pid, at, bt, pr))
    return processes

def clone_process_list(processes):
    return [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
