__author__ = 'sware'

import sys

handle = file(sys.argv[1], 'r')
map = {}
for line in handle:
    split = line.split(',')
    epucks, slots = int(split[0].split(':')[1]), int(split[1].split(':')[1])
    num, ttime, tbweight, tsweight, tpweight, tpsweight, bestimprove = map.get((epucks, slots), (0, 0, 0, 0, 0, 0, 1))
    lbe, time = int(split[2].split(':')[1]), float(split[9].split(':')[1])
    if split[8].split(':')[1] != 'inf':
        sweight, bweight = int(split[8].split(':')[1]), int(split[6].split(':')[1])
        tsweight += sweight
        tbweight += bweight
        improve = float(sweight) / float(bweight)
        pweight = float(bweight) / float(lbe) - 1
        psweight = float(sweight) / float(lbe) - 1
        tpweight += pweight
        tpsweight += psweight
        ttime += time
        num += 1
        bestimprove = min(improve, bestimprove)
        map[(epucks, slots)] = (num, ttime, tbweight, tsweight, tpweight, tpsweight, bestimprove)
keys = list(map.keys())
keys.sort(key=lambda tup: (tup[1], tup[0]))
handle.close()
handle = file(sys.argv[1] + '.csv', 'w')
handle.write('ep, size, num, ttime, tbweight, tsweight, tpbweight, tpsweight, bestimprove\n')
for epucks, slots in keys:
    num, ttime, tbweight, tbsweight, tpbweight, tpsweight, bestimprove = map[(epucks, slots)]
    ttime /= num
    tbweight /= float(num)
    tbsweight /= float(num)
    tpbweight /= num
    tpsweight /= num
    handle.write('{},{},{},{},{},{},{},{},{}\n'.format(epucks, slots, num, ttime, tbweight, tbsweight, tpbweight, tpsweight, bestimprove))
handle.close()