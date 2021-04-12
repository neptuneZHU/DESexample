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
        pweight = float(bweight) / float(lbe) - 1
        pcweight = float(bcweight) / float(lbe) - 1
        tpweight += pweight
        tpbcweight += pcweight
        ttime += time
        num += 1
        map[(epucks, slots)] = (num, ttime, tbweight, tbcweight, tpweight, tpbcweight)
keys = list(map.keys())
keys.sort(key=lambda tup: (tup[1], tup[0]))
handle.close()
handle = file(sys.argv[1] + '.csv', 'w')
handle.write('ep, size, num, ttime, tbweight, tbcweight, tpweight, tpbcweight\n')
for epucks, slots in keys:
    num, ttime, tbweight, tbcweight, tpweight, tpbcweight = map[(epucks, slots)]
    ttime /= num
    tbweight /= float(num)
    tbcweight /= float(num)
    tpweight /= num
    tpbcweight /= num
    handle.write('{},{},{},{},{},{},{},{}\n'.format(epucks, slots, num, ttime, tbweight, tbcweight, tpweight, tpbcweight))
handle.close()