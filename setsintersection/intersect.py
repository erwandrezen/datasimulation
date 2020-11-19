#!/usr/bin/python3

import sys
import random
import time
from more_itertools import powerset

def intersection(first, *others):
    return set(first).intersection(*others)

n = 3*1000*1000;

population = range(n);

sizes = [1500000,20000,90000,50000,10000,3000];

v = [random.sample (population, k=x) for x in sizes];

print ("===");

t0 = time.time()
res = intersection (*v);
t1 = time.time()

print ("res=", len(res), t1-t0);

tt0 = time.time()
nb=0;
for l in powerset(range(len(sizes))):
    if len(l)>1:
        t0 = time.time()
        res = intersection(*[v[x] for x in l]);        
        t1 = time.time()
        nb += 1;
        print (l, " ", len(res), " ", t1-t0);
tt1 = time.time()

print ("nb=", nb, "time=", tt1-tt0, "mean=",(tt1-tt0)/nb);
