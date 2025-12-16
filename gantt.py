# gantt.py

import matplotlib.pyplot as plt


def draw_gantt(gantt, title: str, filepath: str):
    """
    gantt: [(pid, start, end), ...]
    title: grafik başlığı
    filepath: kaydedilecek dosya yolu (ör: 'charts/fcfs.png')
    """
    if not gantt:
        return

    # Y ekseninde her process için bir satır
    pids = sorted({pid for pid, start, end in gantt})
    pid_to_y = {pid: i for i, pid in enumerate(pids)}

    fig, ax = plt.subplots()

    for pid, start, end in gantt:
        y = pid_to_y[pid]
        width = end - start
        # Çubuk çiz
        ax.barh(y, width, left=start, edgecolor="black")
        # Çubuğun üstüne process ismini yaz
        ax.text(start + width / 2, y, pid, ha="center", va="center", fontsize=8)

    ax.set_yticks(list(pid_to_y.values()))
    ax.set_yticklabels(pids)
    ax.set_xlabel("Time")
    ax.set_ylabel("Process")
    ax.set_title(title)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(filepath)
    plt.close(fig)
