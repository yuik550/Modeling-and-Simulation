import random
from decimal import Decimal, InvalidOperation


def ask_yes_no(prompt):
    while True:
        answer = input(prompt + " (yes/no): ").strip().lower()
        if answer in ("yes", "no"):
            return answer == "yes"
        print("Please write yes or no.")


def ask_time(prompt):
    while True:
        try:
            t = int(input(prompt))
            if t >= 0:
                return t
        except ValueError:
            pass
        print("Please enter a whole number (0 or more).")


def ask_range(name):
    while True:
        lo = ask_time(f"Minimum {name} time: ")
        hi = ask_time(f"Maximum {name} time: ")
        if lo <= hi:
            return lo, hi
        print("The minimum cannot be bigger than the maximum, try again.")


def show(d, x):
    """Random digit as text; the top value is shown as 00 / 000 ..."""
    return "0" * d["digits"] if x == d["top"] else str(x).zfill(d["digits"])


def build_distribution(name, lo, hi):
    """Builds ONE table (its own probabilities, cumulative, digits and intervals)."""
    values = list(range(lo, hi + 1))
    k = len(values)
    same = ask_yes_no(f"Are the {name} probabilities the same?")
    if same:
        probs = [Decimal(1) / k] * k
    else:
        while True:
            try:
                probs = []
                for v in values:
                    probs.append(Decimal(input(f"Probability of {name} time {v}: ")))
                total = sum(probs)
                if total > 1:
                    raise ValueError("The sum of the probabilities is more than one, try to enter other probabilities.")
                if total < 1:
                    raise ValueError("The sum of the probabilities is less than one, try to enter other probabilities.")
                break
            except InvalidOperation:
                print("Invalid number, try to enter other probabilities.")
            except ValueError as e:
                print(e)
    digits = (2 if k <= 100 else 3) if same else max(2, max(-p.as_tuple().exponent for p in probs))
    top = 10 ** digits
    cums, intervals, cum, prev = [], [], Decimal(0), 0
    for p in probs:
        cum += p
        hi_rd = int((cum * top).to_integral_value())
        cums.append(cum)
        intervals.append((prev + 1, hi_rd))
        prev = hi_rd
    return dict(values=values, probs=probs, cums=cums, intervals=intervals, digits=digits, top=top)


def print_table(title, d):
    print(f"\n{title}")
    print(f"{'Time':>8} {'Prob.':>8} {'Cum. Prob.':>11}   Random-digit interval")
    for i, v in enumerate(d["values"]):
        lo, hi = d["intervals"][i]
        print(f"{v:>8} {float(d['probs'][i]):>8.4f} {float(d['cums'][i]):>11.4f}   {show(d, lo)} - {show(d, hi)}")


def ask_digit(prompt, d):
    """The user types the random digit. 0 / 00 means the top value (100, 1000, ...)."""
    while True:
        try:
            x = int(input(prompt))
            if x == 0:
                x = d["top"]
            if 1 <= x <= d["top"]:
                return x
        except ValueError:
            pass
        print(f"The random digit must be between {show(d, 1)} and {show(d, d['top'])}, try again.")


def ask_mode(name):
    while True:
        print(f"\nHow do you want the {name} times?")
        print("  generate = the program generates the random digits")
        print("  digits   = you type the random digits")
        print(f"  times    = you type the {name} times")
        mode = input("Write generate, digits or times: ").strip().lower()
        if mode in ("generate", "digits", "times"):
            return mode
        print("Please write generate, digits or times.")


def get_draw(d, name, mode, c):
    """One draw for customer c using table d. Returns (random digit or None, time)."""
    if mode == "times":
        return None, ask_time(f"{name.capitalize()} time of customer {c}: ")
    if mode == "generate":
        rd = random.randint(1, d["top"])
    else:
        rd = ask_digit(f"Random digit of customer {c} ({name}): ", d)
    row = next(r for r, (lo, hi) in enumerate(d["intervals"]) if lo <= rd <= hi)
    return rd, d["values"][row]


# ------------------------------------------------------------------ INPUTS
while True:
    try:
        n = int(input("Number of customers: "))
        if n >= 1:
            break
    except ValueError:
        pass
    print("Please enter a whole number (1 or more).")

ia_min, ia_max = ask_range("interarrival")
ab_min, ab_max = ask_range("Abel service")
ba_min, ba_max = ask_range("Baker service")

# ------------------------------------------------------------------ THREE DISTRIBUTION TABLES
IA = build_distribution("interarrival", ia_min, ia_max)
print_table("INTERARRIVAL-TIME TABLE", IA)
AB = build_distribution("Abel service", ab_min, ab_max)
print_table("ABEL SERVICE-TIME TABLE", AB)
BA = build_distribution("Baker service", ba_min, ba_max)
print_table("BAKER SERVICE-TIME TABLE", BA)

tables = [AB, BA]
names = ["Abel", "Baker"]

# ------------------------------------------------------------------ INTERARRIVAL TIMES AND ARRIVALS
ia_mode = ask_mode("interarrival")
ab_mode = ask_mode("Abel service")
ba_mode = ask_mode("Baker service")
modes = [ab_mode, ba_mode]

ia_rd, ia_time = [], []
for c in range(1, n + 1):
    rd, t = get_draw(IA, "interarrival", ia_mode, c)
    ia_rd.append(rd)
    ia_time.append(t)

arrivals, clock = [], 0
for t in ia_time:
    clock += t
    arrivals.append(clock)

# ------------------------------------------------------------------ SIMULATION (two servers)
free = [0, 0]
busy = [0, 0]
served = [0, 0]
svc_sum = [0, 0]
rows = []
waits = []

for c in range(n):
    arr = arrivals[c]
    if free[0] <= arr:
        s = 0
    elif free[1] <= arr:
        s = 1
    else:
        s = 0 if free[0] <= free[1] else 1

    begin = max(arr, free[s])
    rd, svc = get_draw(tables[s], names[s] + " service", modes[s], c + 1)
    end = begin + svc
    wait = begin - arr

    free[s] = end
    busy[s] += svc
    served[s] += 1
    svc_sum[s] += svc
    waits.append(wait)

    r1 = "-" if ia_rd[c] is None else show(IA, ia_rd[c])
    r2 = "-" if rd is None else show(tables[s], rd)
    rows.append((c + 1, r1, ia_time[c], arr, r2, names[s], svc, begin, end, wait))

run_time = max(free)

# ------------------------------------------------------------------ OUTPUT
head = ["Customer", "RD (IAT)", "Interarr.", "Arrival", "RD (Serv)", "Server", "Service", "Start", "End", "Waiting"]
print()
print(" ".join(f"{h:>11}" for h in head))
for row in rows:
    print(" ".join(f"{v:>11}" for v in row))

# ------------------------------------------------------------------ PERFORMANCE MEASURES
waited = [w for w in waits if w > 0]
avg_wait_all = sum(waits) / n
avg_wait_waiters = sum(waited) / len(waited) if waited else 0
avg_between = sum(ia_time[1:]) / (n - 1) if n > 1 else 0

print("\nPERFORMANCE MEASURES")
print("-" * 60)
for s in range(2):
    util = busy[s] / run_time if run_time else 0
    pct = served[s] / n * 100
    avg_svc = svc_sum[s] / served[s] if served[s] else 0
    print(f"{names[s]} utilization                  : {util:.4f}")
    print(f"{names[s]} customers served             : {served[s]} ({pct:.2f}%)")
    print(f"{names[s]} average service time         : {avg_svc:.4f}")
print(f"Average waiting time (all customers)     : {avg_wait_all:.4f}")
print(f"Average waiting time (customers who wait): {avg_wait_waiters:.4f}")
print(f"Average interarrival time               : {avg_between:.4f}")
