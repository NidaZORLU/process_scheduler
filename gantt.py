import matplotlib.pyplot as plt


def draw_gantt(gantt, title: str, filepath: str):
    if not gantt:
        return

    pids = [pid for pid, _, _ in gantt]
    unique = []
    for pid in pids:
        if pid not in unique:
            unique.append(pid)

    pid_to_y = {pid: i for i, pid in enumerate(unique)}

    fig, ax = plt.subplots(figsize=(10, 4))

    for pid, start, end in gantt:
        y = pid_to_y[pid]
        width = end - start
        ax.barh(y, width, left=start, edgecolor="black")
        ax.text(start + width / 2, y, str(pid), ha="center", va="center", fontsize=8)

    ax.set_yticks(list(pid_to_y.values()))
    ax.set_yticklabels(list(pid_to_y.keys()))
    ax.set_xlabel("Time")
    ax.set_ylabel("Process")
    ax.set_title(title)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(filepath)
    plt.close(fig)
