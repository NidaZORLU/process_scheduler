Process Scheduling Simulator
This project is a CPU Process Scheduling Simulator developed as part of the CS 305 – Operating Systems course assignment. The simulator implements and compares several classical CPU scheduling algorithms by simulating their execution and computing key performance metrics.
Supported Scheduling Algorithms

The simulator implements the following scheduling algorithms as required by the assignment:
First-Come, First-Served (FCFS) – Non-preemptive
Shortest Job First (SJF) – Non-preemptive
Priority Scheduling – Non-preemptive (lower number indicates higher priority)
Round Robin (RR) – Preemptive, with configurable time quantum

Input File Format
The simulator uses plain text input files, as specified in the assignment instructions.
Each line of the input file represents a process in the following format:
Process_ID, Arrival_Time, Burst_Time, Priority
Example (processes.txt):
P1,0,8,3
P2,1,4,1
P3,2,9,4
P4,3,5,2

How to Run the Simulator (Command Line)
Command-line execution is the primary and required mode for evaluation.
Run all scheduling algorithms with a time quantum of 3:
 
    python main.py data/processes.txt --tq 3

This command runs all four scheduling algorithms sequentially and prints the following to the console:
The name of the scheduling algorithm
A text-based Gantt chart including idle periods
A table showing per-process Finish Time, Turnaround Time, and Waiting Time
Average Turnaround Time
Average Waiting Time
CPU Utilization


Demonstrating Starvation
To demonstrate the starvation problem, as required in the discussion section of the assignment, a specially designed input file is provided.
Run starvation demonstration:

  python main.py data/starvation.txt --tq 3

The starvation.txt file is intentionally constructed to highlight starvation in Priority Scheduling, where a low-priority process experiences excessive waiting time due to the continuous arrival of higher-priority processes.
This execution is used to support the starvation analysis in the report.


Round Robin Time Quantum Experiments
To analyze the effect of different time quantum values on fairness and performance in the Round Robin algorithm, the simulator can be executed with different quantum values:

   python main.py data/processes.txt --tq 1
   
   python main.py data/processes.txt --tq 5

These experiments help illustrate the trade-off between responsiveness and throughput in Round Robin scheduling.

Graphical User Interface (Optional Enhancement)
In addition to the required command-line simulator, an optional graphical user interface (GUI) is provided for visualization purposes.

   python gui.py

The GUI allows users to:
Select a scheduling algorithm
Configure the Round Robin time quantum
Set a starvation threshold
View Gantt charts interactively
The GUI is provided as a supplementary visualization tool.
All official results and evaluations are based on the command-line execution using plain text input files, in accordance with the assignment requirements.


Notes
Context-switching overhead is assumed to be zero.
Ties in scheduling decisions are resolved using FCFS order.
The simulator is implemented in Python and does not require external dependencies for command-line execution.
The processes.json file is retained for GUI-based demonstrations but is not used in the required command-line evaluation.



