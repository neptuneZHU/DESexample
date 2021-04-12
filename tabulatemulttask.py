__author__ = 'sware'

import sys, collections

handle = file(sys.argv[1], 'r')
tots = collections.defaultdict(lambda : [[0 for _ in range(5)], 0.0])
max_over = collections.defaultdict(lambda : 1.0)
fails = collections.defaultdict(lambda : 0.0)
for s in handle:
    s = s.split(':')
    slots = (int(s[0]), int(s[1]))
    if s[2] == 'fail\n':
        fails[slots] += 1
    else:
        for i in range(2, 6):
            tots[slots][0][i-2] += float(s[i])
        tots[slots][1] += 1.0
        max_over[slots] = max(max_over[slots], float(s[2])/ float(s[4]))
keys = sorted(list(tots.keys()))
handle.close()
handle = file(sys.argv[1] + '.csv', 'w')
for k in keys:
    tots[k][0] = [val / tots[k][1] for val in tots[k][0]]
    iterable = [str(val) for val in list(k) + tots[k][0]] + [str(max_over[k]), str(fails[k])]
    handle.write(','.join(iterable) + '\n')
handle.close()