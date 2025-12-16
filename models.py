# models.py

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        self.priority = int(priority)

        # Simülasyon sırasında doldurulanlar:
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.response_time = None

        # Preemptive algoritmalar için:
        self.remaining_time = self.burst_time

        # Starvation / Aging için:
        self.starvation_risk = False   # True ise "çok bekledi" etiketi
        self.effective_priority = self.priority  # aging varsa değişebilir

    def reset(self):
        """Aynı process listesini farklı algoritmalar için temizler."""
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.response_time = None
        self.remaining_time = self.burst_time

        self.starvation_risk = False
        self.effective_priority = self.priority

    def __repr__(self):
        return (
            f"Process(pid={self.pid}, at={self.arrival_time}, "
            f"bt={self.burst_time}, prio={self.priority})"
        )
