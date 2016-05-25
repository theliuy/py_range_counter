#!/usr/bin/env bash

pwd = `pwd`
for (( counter_size=5000; counter_size<=1600000; counter_size+=50000 )); do
    echo ${counter_size};
    python ./performance_cmp.py --p_query 40 --p_incr 40 --p_decr 20 --n ${counter_size} --opts 10000 --repeat 3 >> /tmp/range_counter_perf.csv;
done