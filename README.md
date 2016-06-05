# py_range_counter

##  Introduction

`PyRangeCounter` is a counter-like module. It is designed for the case,
caller can increment/decrement counters of a continuous range. E.g. 
increment the i-th to j-th counters by X.

It provides interfaces to,

- init N consequential counters from [0 ... N);
- increment/decrement counters on a given range;
- query counts by index

## Usage

```python
import py_range_counter

# Initialize 1000 counters. The index is from 0 to 999
counter = py_range_counter.RangeCounter(1000)

# Increment counters 100 to 915 by 5
counter.increment(100, 915, count=5)

# Decrement counters 50 to 800 by 6
# Notice that counter[i] is always greater or equal to 0
# In this case counter[50] is 0
counter.decrement(50, 800, 6)

# Query counter 512
a = counter[512]

# Get a copy of all counter values
counter_values = counter.all()
```

## Performance

Instead of an organic integer array keeping all the counters, `PyRangeCounter`
is implemented as a tree. The idea is quite simple. Every tree node represents
a range, and its children represents a subset of it's range. Leaf nodes 
have the count of a single index. When increment() or decrement() is applied, 
it is applied to corresponding nodes and their children. The sum of the path to
leaves donate the actual count of an index. Let's say we initialized 4 counters,
the data structure shows as below. The value of `[0,2)` donates the count of
both index 0 and 1. If we apply an increment on range [0,2], both the value of 
node `[0,2)` and leave node `2` will be incremented.


```
               [0, 4)
             /        \
         [0, 2)      [2, 4)
         /    \      /     \
        0      1    2       3
```

`PyRangeCounter` uses O(N) space, (The actual spaces usage is close to
2N.) and provides,

| Operation  | Time Complexity (Avg)   | Time Complexity (Worst) | Stable |
|------------|-------------------------|-------------------------|--------|
| Increment  | O(log N) + O(log N)     | O(log N) + O(log N)     | Yes    |
| Decrement  | O(log N) + O(log N)     | O(log N) + O(N)         | No     |
| Query      | O(log log N) + O(log N) | O(log log N) + O(log N) | Yes    |
| All        | O(N)                    | O(N)                    | Yes    |


_Notice_: Let's say it contains N counters.

### Is it good?

![Alt text](/perf/perf.png?raw=true "Performance")

It is not that bad. Comparing to other 2 counters. `ArrayCounter` is
implemented as an array, and `DictCounter` is a dict-ish counter class.
When the number of counters comes to 16k, `RangeCounter` saves 99% of
time comparing to other two counters. See `perf/...` for details.

In the performance test, 40% of operations are `query`, 40% are `increment`
and 20% are `decrement` (similar to a real world case in my project).
