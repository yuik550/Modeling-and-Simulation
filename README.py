# Single-server-queue-Modeling-and-Simulation-
A simulation of a single-server queueing system, written in Python.
Assignment 1, Modeling and Simulation, Future University in Egypt.

## What it does
The program simulates customers arriving at one server and builds a full
simulation table (arrival, service start, service end, waiting time, idle time)
from interarrival-time and service-time distributions that the user enters.

## How it works
1. The user enters the interarrival-time table and the service-time table
   (each has its own table, with min/max ranges and a probability per value).
2. The program checks that the probabilities sum to 1. If the sum is more
   than 1 it prints: "The sum of the probabilities is more than one, try to
   enter other probabilities."
3. It builds cumulative probabilities and random-digit ranges for each table.
   The digit 00 stands for 100.
4. For both interarrival and service, the user picks one of three options:
   - the program generates the random digits,
   - the user types the random digits,
   - the user types the times directly.
5. Each random digit is looked up in its table to get the time. Customer 1
   also gets a random digit and an interarrival time.
6. The program prints the simulation table (including an Idle column) and
   the performance measures.

## Performance measures
- Average waiting time
- Probability that a customer waits
- Server utilization / probability of idle server
- Average service time
- Average interarrival time
- Average time a customer spends in the system

(Delete any measure your code doesn't calculate.)

## How to run
1. Install Python 3 from python.org
2. Download `queue_simulation.py`
3. Run:

       python queue_simulation.py

## Example output
(Paste a screenshot or the printed simulation table here.)

## Why I built it
Individual assignment for the Modeling and Simulation course, to understand
how a single-server queue is simulated step by step.
