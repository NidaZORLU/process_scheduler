# models.py

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority

        # Simülasyon sırasında doldurulanlar:
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.response_time = None

        # Preemptive algoritmalar için:
        self.remaining_time = burst_time

    def reset(self):
        """Aynı process listesini farklı algoritmalar için temizler."""
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.response_time = None
        self.remaining_time = self.burst_time

    def __repr__(self):
        return (f"Process(pid={self.pid}, at={self.arrival_time}, "
                f"bt={self.burst_time}, prio={self.priority})")
