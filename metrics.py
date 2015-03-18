import time
from functools import wraps
from pprint import pprint
from prettytable import PrettyTable

PROF_DATA = {}


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        print "--- start "+ fn.__name__+ "---"
        start_time = time.time()
        ret = fn(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print fn.__name__+": " + format(elapsed_time, '.5f')
        print "--- end "+ fn.__name__+ "---"
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
        max_time = format(max(data[1]), '.4f')
        avg_time = format(sum(data[1]) / len(data[1]),'.4f')
        total_time = format(sum(data[1]), '.4f')
        # One space between column edges and contents (default)
        x.padding_width = 1
        x.add_row([fname, data[0], max_time, avg_time, total_time])
        # print "%d called %s times.\t\t" % (data[0], fname),
        # print 'Max: %.3f\t,Avg: %.3f\t, Tot: %.3f\t,' % (max_time, avg_time, total_time)
    print x


        # pprint(data)


def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}
