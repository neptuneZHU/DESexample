from automata import frontend, weighted_frontend, row_vector,tools

reqs = tools.convert("H11 H12 H13 H14 H21 H22 H23 H24 H31 H32 H33 H34 job-number-2")
plant = tools.convert("TC_in TC_out TR1 TR2 TR3 TB1 TB2 TProc_11 TProc_12 TProc_21 TProc_22 TProc_31 TProc_32 TProc_33")


#operator = 0
#rvecs = 0
L = 50

weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "type1","Cluster-Tool-example-sup.cfg", L)
tools.filter_results("Cluster-Tool-example-sup.cfg", "Cluster-Tool-example-sup.cfg-unweighted.cfg" )


#weighted_frontend.LBE_make_greedy_time_optimal_supervisor(plant, reqs, "type1")

weighted_frontend.make_time_optimal_supervisor(plant, reqs, "type1","Cluster-Tool-example-sup.cfg")

