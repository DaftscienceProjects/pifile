import time
from functools import wraps
from pprint import pprint
from prettytable import PrettyTable

PROF_DATA = {}


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        print "ENTERING " + fn.__name__
        start_time = time.time()
        ret = fn(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print "EXITING " + fn.__name__ + "Time: " + str(elapsed_time)
        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling


def print_prof_data():
    x = PrettyTable(["Function", "Calls", "Max", "Avg", "Tot"])
    x.align["Function"] = "l"  # Left align city names
    for fname, data in PROF_DATA.items():
        max_time = format(max(data[1])*1000, '.3f')
        avg_time = format(sum(data[1])*1000 / len(data[1]),'.3f')
        total_time = format(sum(data[1])*1000, '.3f')
        x.padding_width = 1
        x.add_row([fname, data[0], max_time, avg_time, total_time])
    print x


        # pprint(data)


def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}
