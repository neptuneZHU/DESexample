__author__ = 'sware'

import sys

handle = file(sys.argv[1], 'r')
map = {}
for line in handle:
    split = line.split(',')
    epucks, slots = int(split[0].split(':')[1]), int(split[1].split(':')[1])
    num, ttime, tbweight, tbcweight, tpweight, tpbcweight = map.get((epucks, slots), (0, 0, 0, 0, 0, 0))
    lbe, time = int(split[2].split(':')[1]), float(split[7].split(':')[1])
    if split[5].split(':')[1] != 'inf':
        bweight, bcweight = int(split[5].split(':')[1]), int(split[6][8:])
        tbcweight += bcweight
        tbweight += bweight
        pweight = 0
        pcweight = 0
        tpweight += pweight
        tpbcweight += pcweight
        ttime += time
        num += 1
        map[(epucks, slots)] = (num, ttime, tbweight, tbcweight, tpweight, tpbcweight)
keys = list(map.keys())
keys.sort(key=lambda tup: (tup[1], tup[0]))
handle.close()
handle = file(sys.argv[2] + '.csv', 'w')
handle.write('Lot, ttime, pathweight\n')
time = 0
for i, (epucks, slots) in enumerate(keys):
    num, ttime, tbweight, tbcweight, tpweight, tpbcweight = map[(epucks, slots)]
    time += ttime
    handle.write('{},{},{}\n'.format(i + 1, time, tbcweight))
handle.close()