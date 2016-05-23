""" py_range_counter

    A counter class supports,
    - Init N consequential counters from [0 ... N)
    - Increment/Decrement counters on a given range
    - Query counts by index

"""

from __future__ import division
import bisect
import collections


class _FCTree(object):
    """ Full & complete tree

        We use full and complete binary tree to store counters.

        :type _leaves: int
        :type _nodes: [int]
    """

    def __init__(self, leaves):
        """

        :param leaves: number of leaves
        :type leaves: int
        """
        self._leaves = leaves
        self._nodes = [0] * (leaves * 2 - 1)

    def __getitem__(self, index):
        leave_index = index + self._leaves - 1
        result = 0
        while True:
            result += self._nodes[leave_index]

            if not leave_index:
                return result

            leave_index = (leave_index - 1) // 2

    def increment(self, start, end, count):
        track = collections.deque()
        track.append((0, 0, self._leaves - 1))

        while track:
            i, left, right = track.popleft()

            if left > end or right < start:
                continue

            if start <= left <= right <= end:
                self._nodes[i] += count
                continue

            mid = left + (right - left) // 2

            if i < self._leaves - 1:
                track.append((i * 2 + 1, left, mid))  # left child
                track.append((i * 2 + 2, mid + 1, right))  # right child

    def decrement(self, start, end, count):
        self._decrement(0, 0, self._leaves - 1, start, end, 0, count)

    def _decrement(self,
                   root, left, right, start, end,
                   left_over, to_deduct):
        start = max(left, start)
        end = min(end, right)

        track = collections.deque()
        track.append((root, left, right, left_over, to_deduct))

        while track:
            i, l, r, o, d = track.popleft()

            self._nodes[i] += o
            if l > end or r < start:
                continue

            m = l + (r - l) // 2
            if start <= l <= r <= end:
                if d <= 0 or d <= self._nodes[i]:
                    self._nodes[i] -= d
                    continue
                else:  # d > self._nodes[i] >= 0
                    d -= self._nodes[i]
                    self._nodes[i] = 0

                    if i < self._leaves - 1:
                        track.append((i * 2 + 1, l, m, 0, d))
                        track.append((i * 2 + 2, m + 1, r, 0, d))
            elif i < self._leaves - 1:  # [l, r] and [start, end] are interleaved
                o = self._nodes[i]
                self._nodes[i] = 0

                self._decrement(i * 2 + 1, l, m, start, end, o, d)
                self._decrement(i * 2 + 2, m + 1, r, start, end, o, d)

    @property
    def leaves(self):
        return self._leaves

    @property
    def number_of_nodes(self):
        return self._leaves * 2 - 1


class RangeCounter(object):
    """

        :type _trees: [_FCTree]
        :type _offsets: [int]
        :type _n: n
    """

    def __init__(self, n):
        """

        :param n: number of counters
        :type n: int
        """

        if not n > 0:
            raise ValueError("the number of counters must be positive.")

        trees = []
        offsets = []
        self._n = n

        base = 1
        offset = 0
        while base <= self._n:
            if self._n & base:
                trees.append(_FCTree(base))
                offsets.append(offset)
                offset += base
            base <<= 1

        self._trees = tuple(trees)
        self._offsets = tuple(offsets)

    @property
    def n(self):
        return self._n

    def increment(self, start, end, count=1):
        """ Increments [counter[start], counter[end]] by count

        :param start: scope starts at
        :type start: int
        :param end: scope ends at
        :type end: int
        :param count: increment by
        :type count: int
        :return:
        :raise ValueError: if the count is not positive or start/end is out of range
        """

        if count <= 0:
            raise ValueError("count must be positive.")

        self._validate_index(start)
        self._validate_index(end)

        left_bond = self._left_bound(start)
        right_bond = self._left_bound(end)
        while left_bond <= right_bond:
            offset = self._offsets[left_bond]
            tree = self._trees[left_bond]
            tree.increment(max(offset, start) - offset,
                           min(end - offset, tree.leaves - 1),
                           count)

            left_bond += 1

    def decrement(self, start, end, count=1):
        """ Decrements [counter[start], counter[end]] by count

        :param start: scope starts at
        :type start: int
        :param end: scope ends at
        :type end: int
        :param count: decrement by
        :type count: int
        :return:
        :raise ValueError: if the count is not positive or start/end is out of range
        """

        if count <= 0:
            raise ValueError("count must be positive")

        self._validate_index(start)
        self._validate_index(end)

        left_bond = self._left_bound(start)
        right_bond = self._left_bound(end)
        while left_bond <= right_bond:
            offset = self._offsets[left_bond]
            tree = self._trees[left_bond]
            tree.decrement(max(offset, start) - offset,
                           min(end - offset, tree.leaves - 1),
                           count)

            left_bond += 1

    def __getitem__(self, index):
        """ Get the number of counter[index]

        :param index: the index of a counter
        :type index: int
        :return: int
        :raise ValueError: if index is out of range
        """

        self._validate_index(index)
        tree_index = self._left_bound(index)
        return self._trees[tree_index][index - self._offsets[tree_index]]

    def __iter__(self):
        """ Iterate through counters.

            WARNING:
                The performance is bad. RangeCounter is not designed to be iterated
                frequently. It provides a O(N * log N) time complexity when iterating
                through all counters. (Let's say we initialize N counters)

        :return : int
        """
        for i in range(self._n):
            yield self[i]

    def _validate_index(self, index):
        if not 0 <= index < self._n:
            raise ValueError("index[%s] is out of range[0...%s]." % (index, self._n))

    def _left_bound(self, index):
        i = bisect.bisect_right(self._offsets, index)
        return i if i == 0 else i - 1
