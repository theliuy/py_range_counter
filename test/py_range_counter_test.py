import os
import random
import sys
import unittest

_PY_PATH = os.path.join([os.path.realpath(__file__), '..'])
if _PY_PATH not in sys.path:
    sys.path.insert(0, _PY_PATH)

from py_range_counter import RangeCounter


class PyRangeCounterTests(unittest.TestCase):

    def test_basic(self):
        n = 100
        times = 1000
        counts = range(1, 10)
        rc = RangeCounter(n)

        self.assertEqual(rc.n, n)

        expected = [0] * n
        for i in range(times):
            # print(rc._trees[0]._nodes)

            count = random.choice(counts)
            a, b = self._rand_range(0, n - 1)

            rc.increment(a, b, count)
            # print('increment [%s, %s] by %s' % (a, b, count))

            for j in range(0, n):
                if a <= j <= b:
                    expected[j] += count
                self.assertEqual(rc[j], expected[j], "index[%s] rc:%s expected[%s]" % (j, rc[j], expected[j]))

            count = random.randint(1, count)
            a, b = self._rand_range(0, n - 1)

            rc.decrement(a, b, count)

            for j in range(0, n):
                if a <= j <= b:
                    expected[j] = max(0, expected[j] - count)
                self.assertEqual(rc[j], expected[j], "index[%s] rc:%s expected:%s" % (j, rc[j], expected[j]))
            self.assertEqual(rc.all(), expected)

    def test_out_of_range(self):
        rc = RangeCounter(20)
        self.assertRaises(ValueError, rc.increment, 21, 25)
        self.assertRaises(ValueError, rc.increment, 1, 25)
        self.assertRaises(ValueError, rc.__getitem__, 22)

    @staticmethod
    def _rand_range(start, end):
        a, b = random.randint(start, end), random.randint(start, end)
        return min(a, b), max(a, b)


if __name__ == "__main__":
    unittest.main()
