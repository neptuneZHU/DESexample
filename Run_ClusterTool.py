__author__ = 'sware'

import sys

from SimonStuff import incrementalimprovement

tablename = sys.argv[1]
recipenames = []
for i in range(2, len(sys.argv)+1):
    if i == len(sys.argv) or sys.argv[i].isdigit():
        break
    recipenames.append(sys.argv[i])

incrementalimprovement.create_path_real_clusters_reticle_alignment_window_files(tablename, recipenames, sys.argv[i:])
