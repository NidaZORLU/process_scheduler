# utils.py
import json
from models import Process


def load_processes_from_json(path: str):
    """
    JSON formatı:
    [
      {"pid": "P1", "arrival_time": 0, "burst_time": 8, "priority": 2},
      ...
    ]
    """
    with open(path, "r") as f:
        raw_list = json.load(f)

    processes = []
    for item in raw_list:
        pid = item["pid"]
        at = int(item["arrival_time"])
        bt = int(item["burst_time"])
        prio = int(item.get("priority", 999))  # yoksa en düşük öncelik
        processes.append(Process(pid, at, bt, prio))

    return processes


def clone_process_list(processes):
    cloned = []
    for p in processes:
        q = Process(p.pid, p.arrival_time, p.burst_time, p.priority)
        cloned.append(q)
    return cloned
