import argparse
import collections
import gc
import random
import timeit

from py_range_counter import RangeCounter

OPT_QUERY = 0
OPT_INC = 1
OPT_DEC = 2


class WeightedRandomizer:

    def __init__ (self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items ():
            self.__max += weight
            self.__weights.append((self.__max, value))

    def random(self):
        r = random.random() * self.__max
        for ceil, value in self.__weights:
            if ceil > r:
                return value


def generate_operations(
        q_perc, inc_perc, dec_perc,
        n, times, max_steps
        ):
    _Opt = collections.namedtuple('_Opt', ('opt_t', 'opt_args'))
    assert(0 <= q_perc)
    assert(0 <= inc_perc)
    assert(0 <= dec_perc)

    opts = []
    opt_randomizer = WeightedRandomizer({
        OPT_QUERY: q_perc,
        OPT_INC: inc_perc,
        OPT_DEC: dec_perc,
    })
    for i in range(times):
        opt = opt_randomizer.random()
        if opt == OPT_QUERY:
            opt_args = (random.randint(0, n - 1),)
        else:
            s = random.randint(0, n - 1)
            e = random.randint(0, n - 1)
            s = min(s, e)
            e = max(s, e)
            c = random.randint(1, max_steps)
            opt_args = (s, e, c)
        opts.append(_Opt(opt, opt_args))
    return set(opts)


# noinspection PyUnusedLocal
def run_tests(counters, opts):
    for opt in opts:
        if opt.opt_t == OPT_QUERY:
            a = counters[opt.opt_args[0]]
        elif opt.opt_t == OPT_INC:
            counters.increment(*opt.opt_args)
        elif opt.opt_t == OPT_DEC:
            counters.decrement(*opt.opt_args)


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


class ArrayCounters(object):

    def __init__(self, n):
        self.arr = [0] * n

    def increment(self, s, e, c):
        for i in range(s, e + 1):
            self.arr[i] += c

    def decrement(self, s, e, c):
        for i in range(s, e + 1):
            self.arr[i] = max(self.arr[i] - c, 0)

    def __getitem__(self, item):
        return self.arr[item]


class DictCounters(object):

    def __init__(self, n):
        self.d = {i: 0 for i in range(n)}

    def increment(self, s, e, c):
        for i in range(s, e + 1):
            self.d[i] += c

    def decrement(self, s, e, c):
        for i in range(s, e + 1):
            self.d[i] = max(self.d[i] - c, 0)

    def __getitem__(self, item):
        return self.d[item]


def get_opts():
    opt_parser = argparse.ArgumentParser()
    opt_parser.add_argument('--p_query', dest='p_query', metavar='P_QUERY', type=int,
                            help='Percentage of Query operation')
    opt_parser.add_argument('--p_incr', dest='p_incr', metavar='P_INCR', type=int,
                            help='Percentage of Increment operation')
    opt_parser.add_argument('--p_decr', dest='p_decr', metavar='P_DECR', type=int,
                            help='Percentage of Decrement operation')
    opt_parser.add_argument('--n', dest='n', metavar='N', type=int, help='Number of counters')
    opt_parser.add_argument('--opts', dest='opts', metavar='OPTS', type=int, help='Number of operations')
    opt_parser.add_argument('--repeat', dest='repeat', metavar='REPEAT', type=int, help='REPEAT times')

    return opt_parser.parse_args()


def main():
    opt = get_opts()

    oprt = generate_operations(opt.p_query, opt.p_incr, opt.p_decr, opt.n, opt.opts, 5)

    array_counter = ArrayCounters(opt.n)
    wrapped_ac_test = wrapper(run_tests, array_counter, oprt)
    ac_result = timeit.timeit(wrapped_ac_test, gc.enable, number=opt.repeat)
    del array_counter

    dict_counter = DictCounters(opt.n)
    wrapper_dc_test = wrapper(run_tests, dict_counter, oprt)
    dc_result = timeit.timeit(wrapper_dc_test, gc.enable, number=opt.repeat)
    del dict_counter

    range_counter = RangeCounter(opt.n)
    wrapped_rc_test = wrapper(run_tests, range_counter, oprt)
    rc_result = timeit.timeit(wrapped_rc_test, gc.enable, number=opt.repeat)
    del range_counter

    print(', '.join([str(n) for n in [opt.p_query, opt.p_incr, opt.p_decr, opt.n, opt.opts,
                                      rc_result, ac_result, dc_result]]))


if __name__ == '__main__':
    main()
