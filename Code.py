#single-server-queue 
#Assignment1ModelingAndSimulation
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
    return "0" * d["digits"] if x == d["top"] else str(x).zfill(d["digits"])


def build_distribution(name, lo, hi):
    values = list(range(lo, hi + 1))
    k = len(values)
    same = ask_yes_no(f"Are the {name} probabilities the same?")
    if same:
        probs = [Decimal(1) / k] * k                       # 1 divided by the number of possible times
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


def get_times(d, name, n):
    mode = ask_mode(name)
    digits_list, times = [], []
    for c in range(1, n + 1):
        if mode == "times":
            digits_list.append(None)
            times.append(ask_time(f"{name.capitalize()} time of customer {c}: "))
            continue
        if mode == "generate":
            rd = random.randint(1, d["top"])                        
        else:
            rd = ask_digit(f"Random digit of customer {c} ({name}): ", d)  
        row = next(r for r, (lo, hi) in enumerate(d["intervals"]) if lo <= rd <= hi)
        digits_list.append(rd)
        times.append(d["values"][row])                               
    return digits_list, times


while True:
    try:
        n = int(input("Number of customers: "))
        if n >= 1:
            break
    except ValueError:
        pass
    print("Please enter a whole number (1 or more).")

ia_min, ia_max = ask_range("interarrival")
sv_min, sv_max = ask_range("service")

IA = build_distribution("interarrival", ia_min, ia_max)
print_table("INTERARRIVAL-TIME TABLE", IA)
SV = build_distribution("service", sv_min, sv_max)
print_table("SERVICE-TIME TABLE", SV)

ia_rd, ia_time = get_times(IA, "interarrival", n)
sv_rd, sv_time = get_times(SV, "service", n)

arrivals, clock = [], 0
for c in range(n):
    clock += ia_time[c]                          
    arrivals.append(clock)

begins, ends, waits, systems, idles = [], [], [], [], []
prev_end = 0                                     
for c in range(n):
    begin = max(arrivals[c], prev_end)            
    end = begin + sv_time[c]
    begins.append(begin)
    ends.append(end)
    waits.append(begin - arrivals[c])             
    systems.append(end - arrivals[c])             
    idles.append(begin - prev_end)                
    prev_end = end

head = ["Customer", "RD (Inter)", "Interarrival", "Arrival", "RD (Serv)", "Service",
        "Svc Start", "Svc End", "Waiting", "In System", "Idle"]
print()
print(" ".join(f"{h:>12}" for h in head))
for c in range(n):
    r1 = "-" if ia_rd[c] is None else show(IA, ia_rd[c])
    r2 = "-" if sv_rd[c] is None else show(SV, sv_rd[c])
    row = [c + 1, r1, ia_time[c], arrivals[c], r2, sv_time[c], begins[c], ends[c], waits[c], systems[c], idles[c]]
    print(" ".join(f"{v:>12}" for v in row))

waited = [w for w in waits if w > 0]                      
run_time = ends[-1]                                        
avg_wait = sum(waits) / n                                 
avg_service = sum(sv_time) / n                            
p_wait = len(waited) / n                                  
p_idle = sum(idles) / run_time if run_time else 0         
avg_between = sum(ia_time[1:]) / (n - 1) if n > 1 else 0 
avg_wait_waiters = sum(waited) / len(waited) if waited else 0  
avg_system = sum(systems) / n                              
print("\nPERFORMANCE MEASURES")
print("-" * 52)
print(f"Average waiting time                    : {avg_wait:.4f}")
print(f"Average service time                    : {avg_service:.4f}")
print(f"Probability of waiting                  : {p_wait:.4f}")
print(f"Probability of server idle time         : {p_idle:.4f}")
print(f"Average time between arrivals           : {avg_between:.4f}")
print(f"Average waiting time (customers who wait): {avg_wait_waiters:.4f}")
print(f"Average time spent in the system        : {avg_system:.4f}")
