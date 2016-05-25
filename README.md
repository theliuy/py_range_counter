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
```

## Performance

`PyRangeCounter` uses O(N) space, (The actual spaces usage is close to
2N.) and provides,

| Operation  | Time Complexity (Avg)   | Time Complexity (Worst) | Stable |
|------------|-------------------------|-------------------------|--------|
| Increment  | O(log N) + O(log N)     | O(log N) + O(log N)     | Yes    |
| Decrement  | O(log N) + O(log N)     | O(log N) + O(N)         | No     |
| Query      | O(log log N) + O(log N) | O(log log N) + O(log N) | Yes    |


_Notice_: Let's say it contains N counters.

### Compare to traditional counters

Working on it!