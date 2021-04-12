import automata,copy, heapq, random, weighted_frontend
from automata import taskresource, maxplus, data_structure, collection, weighted_structure, \
                            compute_weight, conversion, weighted_product, algorithm, common, \
                            weighted_supervisor, abstraction, product
from sets import Set
from time import time

def tau_abstracted_greedy_supervisor(comp_list, req_list, comp_mut_ex, evt_pairs):
    if not comp_mut_ex == "type1" and not comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
    common.print_line("Computing event data...")
    result = taskresource.compute_custom_eventdata_extended(comp_list, evt_pairs, comp_mut_ex)
    if result is None:
        return None
    eventdata, cliques = result
    for comp in comp_list:
        if not has_shared_events(comp, comp_list):
            common.print_line("Computing maximal time optimal automata for component %d..." % (comp_list.index(comp)+1))
            time_opt_sup = get_time_optimal_sup(comp.copy(), eventdata, len(cliques))
            reduce_with_sup(comp, time_opt_sup)
    common.print_line("Reducing automata to single minimal conflict path automata...")
    for comp in comp_list:
        if not has_shared_events(comp, comp_list):
            minimal_conflict_path_automaton(comp, comp_list, evt_pairs)
##            comp.save_as_dot("comp_as_dot_" + comp.name + ".dot")
    while len(comp_list) > 1:
        common.print_line("Doing tau abstraction and product computation, %d components left..." % len(comp_list))
        print comp_list[0]
        do_tau_abstraction(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs)
        
        print comp_list[0]
        if len(comp_list) == 2:
            do_tau_abstraction(comp_list, comp_list[1], eventdata, len(cliques), evt_pairs)
##            comp_list[1].save_as_dot("comp2_abstracted.dot")
        print comp_list[1]
        new_plant = weighted_product.n_ary_weighted_product(comp_list[0:2],
                                                 algorithm.EQUAL_WEIGHT_EDGES, True)
        eureka_state_collision(new_plant)
        comp_list = comp_list[2:]
        comp_list.insert(0,new_plant)
        comp_list[0].reduce(True, True)
##        comp_list[0].save_as_dot("comp_abstracted_as_dot_" + str(len(comp_list)) + "_components.dot")
    time_opt_sup = get_greedy_time_optimal_sup(comp_list[0].copy(), eventdata, len(cliques))
##    time_opt_sup.save_as_dot("tau_optimal_sup.dot")
    return comp_list[0]
    
def testpath(complist, path, eventdata, heap_len):
  pathstate = path.initial
  statetuple = []
  weight = maxplus.make_rowmat(0,heap_len)
  for aut in complist:
    statetuple.append(aut.initial)
  while not pathstate.marked:
    event = None
    newstatetuple = []
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      event = edge.label
    weight = maxplus.otimes_mat_mat(weight ,eventdata[event].matHat)
    for i in range(len(complist)):
      state = statetuple[i]
      if event not in complist[i].alphabet:
        newstatetuple.append(state)
      else:
        for edge in state.get_outgoing():
          if edge.label == event:
            newstatetuple.append(edge.succ)
            break
    statetuple = newstatetuple
  for state in statetuple:
    if not state.marked:
      print "there is a bug here"
      return
  print "this path is correct"
  print "weight: " + str(weight)
  return
  
def calc_makespan(aut, eventdata, heap_len):
  matrix = maxplus.make_rowmat(0,heap_len)
  makespan = calc_makespan_recurse(aut.initial, eventdata, matrix)
  print "makespan: " + str(makespan)
  
def calc_makespan_recurse(state, eventdata, matrix):
  if len(state.get_outgoing()) == 0:
    maxval = 0
    for i in range(len(matrix.data)):
        for j in range(len(matrix.data[i])):
            maxval = maxplus.maximum(maxval, matrix.data[i][j])
    return maxval
  maxval = 0
  for edge in state.get_outgoing():
    newmatrix = maxplus.otimes_mat_mat(matrix, eventdata[edge.label].matHat)
    maxval = maxplus.maximum(maxval, calc_makespan_recurse(edge.succ, eventdata, newmatrix))
  return maxval
  
def testpathvec(complist, path, eventdata, heap_len, resultfile):
  pathstate = path.initial
  statetuple = []
  weight = maxplus.matrix_to_vector(maxplus.make_rowmat(0,heap_len))
  for aut in complist:
    statetuple.append(aut.initial)
  while not pathstate.marked:
    event = None
    newstatetuple = []
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      event = edge.label
    weight = maxplus.newtimes_vec_vec(weight ,eventdata[event].matHat)
    for i in range(len(complist)):
      state = statetuple[i]
      if event not in complist[i].alphabet:
        newstatetuple.append(state)
      else:
        for edge in state.get_outgoing():
          if edge.label == event:
            newstatetuple.append(edge.succ)
            break
    statetuple = newstatetuple
  for state in statetuple:
    if not state.marked:
      print "there is a bug here"
      return
  print "this path is correct"
  print "weight: " + str(weight)
  resultfile.write("weight: " + str(calc_ceil(weight)))
  resultfile.write("\n")
  return
  
def findpathweight(path, eventdata, heap_len):
  pathstate = path.initial
  weight = maxplus.matrix_to_vector(maxplus.make_rowmat(0,heap_len))
  while not pathstate.marked:
    event = None
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      event = edge.label
    weight = maxplus.newtimes_vec_vec(weight ,eventdata[event].matHat)
  print "weight: " + str(weight)
  resultfile.write("weight: " + str(calc_ceil(weight)))
  resultfile.write("\n")
  return calc_ceil(weight)
  
def getpathexecutiontime(path, eventdata, heap_len):
  pathstate = path.initial
  weight = maxplus.matrix_to_vector(maxplus.make_rowmat(0,heap_len))
  while not pathstate.marked:
    event = None
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      event = edge.label
    weight = maxplus.newtimes_vec_vec(weight ,eventdata[event].matHat)
  return max(weight.data)
    
def clustersort(aut):
  return int(aut.name[len(aut.name)-2:])
  
def namesort(aut):
  return aut.name
  
def prog_distributed_supervisor(comp_list, eventdata, cliques):
  clusters =[]
  non_progressive_events_cluster = []
  non_progressive_events_cluster.append
  for i in range(3):
    clusters.append([])
    non_progressive_events_cluster.append(set())
    for aut in comp_list:
      if int(aut.name[len(aut.name)-2:][0]) == (i + 1) and not aut.name.startswith("TBR"):
        clusters[i].append(aut)
      if int(aut.name[len(aut.name)-2:][0]) == (i) and aut.name.startswith("TB") and "spec" not in aut.name:
        clusters[i].append(aut)
      if aut.name.startswith("job-number") and i == 0:
        clusters[i].append(aut)
    print "cluster:" + str(i) 
    for aut in clusters[i]:
      print aut.name
  #non_progressive_events_cluster[0].add(comp_list[0].collection.events['R2-drop-B1'])
  non_progressive_events_cluster[0].add(comp_list[0].collection.events['R2-drop-B1'])
  non_progressive_events_cluster[0].add(comp_list[0].collection.events['R2-pick-B1'])
  non_progressive_events_cluster[1].add(comp_list[0].collection.events['R1-pick-P11'])
  non_progressive_events_cluster[1].add(comp_list[0].collection.events['R1-drop-B1'])
  non_progressive_events_cluster[1].add(comp_list[0].collection.events['R3-drop-B2'])
  non_progressive_events_cluster[1].add(comp_list[0].collection.events['R3-pick-B2'])
  #non_progressive_events_cluster[1].add(comp_list[0].collection.events['R3-pick-P33'])
  non_progressive_events_cluster[2].add(comp_list[0].collection.events['R2-pick-P21'])
  non_progressive_events_cluster[2].add(comp_list[0].collection.events['R2-drop-B2'])
  #non_progressive_events_cluster[2].add(comp_list[0].collection.events['R4-drop-B3'])
  #non_progressive_events_cluster[3].add(comp_list[0].collection.events['R3-drop-B3'])
  non_progressive_events_sup = []
  non_progressive_events_sup.append(set())
  #non_progressive_events_sup[0].add(comp_list[0].collection.events['R3-drop-B2'])
  non_progressive_events_sup.append(set())
  #non_progressive_events_sup[1].add(comp_list[0].collection.events['R4-drop-B3'])
  non_progressive_events_sup.append(set())
  supervisors = []
  for i in range(len(clusters)):
    new_plant = weighted_product.n_ary_weighted_product(clusters[i],
                                                        algorithm.EQUAL_WEIGHT_EDGES)
##    new_plant.save_as_dot("progplantbeforereduce" + str(i) + ".dot")
    new_plant.reduce(True, True)
    print "plant"
    print new_plant
##    new_plant.save_as_dot("progplant" + str(i) + ".dot")
    supervisors.append(get_greedy_time_optimal_sup_progressive2(new_plant, eventdata, len(cliques), non_progressive_events_cluster[i]))
    print "sup"
    print supervisors[i]
##    supervisors[i].save_as_dot("progsup" + str(i) + ".dot")
  bigsup = supervisors[0]
  bigsup = weighted_product.n_ary_weighted_product(supervisors, algorithm.EQUAL_WEIGHT_EDGES)
  print "big sup"
  print bigsup
  print "after restrict"
  blocking = bigsup.getblocking()
  for state in blocking:
    path = bigsup.get_path(state)
    for state, event in path:
      print bigsup.state_names[state.number]
      print event
    oui =io 
  bigsup.reduce(True, True)
##  bigsup.save_as_dot("bigsup.dot")
  print bigsup  
  bigsup = get_greedy_time_optimal_sup(bigsup, eventdata, len(cliques))
##  bigsup.save_as_dot("biggreedsup.dot")
  print "after greed"
  print bigsup                                                                                         
  # for i in range(1,len(supervisors)):
    # bigsup = weighted_product.n_ary_weighted_product((bigsup, supervisors[i]), algorithm.EQUAL_WEIGHT_EDGES)
    # print "big sup"
    # print bigsup
    # print "after restrict"
    # bigsup.reduce(True, True)
    # print bigsup                               
    # print non_progressive_events_sup[i-1]  
    # bigsup = get_greedy_time_optimal_sup_progressive(bigsup, eventdata, len(cliques),non_progressive_events_sup[i-1])  
    # print "after greed"
    # print bigsup                                                                                                        
  path = restrictpath(bigsup)
  testpath(comp_list, path, eventdata, len(cliques))
  ioe =iod
  
def explicitly_disable_events2(aut, cranes, events):
  slot = int(aut.name[-3:])
  for evt in events:
    if evt in aut.alphabet or int(evt.name.split("-")[-3]) < slot:
      continue
    crane = int(evt.name[1])
    aut.alphabet.add(evt)
    state = aut.get_state(1)
    aut.add_edge_data(state, state, evt, 1)
    for c in range(cranes):
      if c + 1 == crane:
        continue
      for i in range(3):
        state = aut.get_state(i + c*3 + 2)
        aut.add_edge_data(state, state, evt, 1)
        
def tau_abstracted_greedy_supervisor_cranes(comp_list, req_list, evt_pairs, name, order):
  comp_mut_ex = "type2"
  remove_always_disabled_events(comp_list)
  common.print_line("Computing event data...")
  a = comp_list[0].collection.make_event("a", True, True, False)
  b = comp_list[0].collection.make_event("b", True, True, False)
  c = comp_list[0].collection.make_event("c", True, True, False)
  d = comp_list[0].collection.make_event("d", True, True, False)
  res1 = [a,c,d]
  res2 = [b,c,d]
  resources = [res1, res2]
  zeromat = maxplus.Matrix([[0,0],[0,0]])
  amat = taskresource.ExtendedEventData(a, 200, resources).matHat
  bmat = taskresource.ExtendedEventData(b, 300, resources).matHat
  cmat = taskresource.ExtendedEventData(c, 260, resources).matHat
  dmat = taskresource.ExtendedEventData(d, 200, resources).matHat
  print "a:" + str(taskresource.ExtendedEventData(a, 200, resources))
  print "b:" + str(taskresource.ExtendedEventData(b, 300, resources))
  print "c:" + str(taskresource.ExtendedEventData(c, 280, resources))
  print "d:" + str(taskresource.ExtendedEventData(d, 200, resources))
  abmat = maxplus.otimes_mat_mat(bmat, amat)
  abdmat = maxplus.otimes_mat_mat(dmat, abmat)
  dbmat = maxplus.otimes_mat_mat(dmat, bmat)
  dbamat = maxplus.otimes_mat_mat(dbmat, amat)
  dcmat = maxplus.otimes_mat_mat(dmat, cmat)
  zdbamat = maxplus.otimes_mat_mat(dbamat, zeromat)
  zdcmat = maxplus.otimes_mat_mat(dcmat, zeromat)
  dcdcmat = maxplus.otimes_mat_mat(cmat, dcmat)
  dbadbamat = maxplus.otimes_mat_mat(abmat, dbamat)
  print "ba:" + str(abmat)
  print "d(ba):" + str(abdmat)
  print "db:" + str(dbmat)
  print "(db)a:" + str(dbamat)
  print "cdc:" + str(dcdcmat)
  print "badba:" + str(dbadbamat)
  print "zdba:" + str(zdbamat)
  print "zdc:" + str(zdcmat)
  #aoii = ai
  plant_list = []
  result = taskresource.compute_custom_eventdata_extended([cs_aut for cs_aut in plant_list if "CS" in cs_aut.name], evt_pairs, comp_mut_ex)
  evts = set()
  for aut in plant_list:
    if aut.name.startswith("SC"):
      evts.update(aut.alphabet)
  for aut in plant_list:
    if "CS" in aut.name:
      explicitly_disable_events2(aut, 3, evts)
  copylist = []
  for aut in comp_list:
    print aut.name
    #if aut.name == "TC_in00" or aut.name == "TC_out00":
      #continue
    copylist.append(get_automaton_copy(aut))
  #comp_list = sorted(comp_list, key=clustersort)
  #comp_list.insert(0, comp_list.pop())
  #comp_list = list(comp_list)
  #comp_list = list(reversed(comp_list))
  for aut in comp_list:
    print aut.name
  if result is None:
      return None
  eventdata, cliques = result
  #prog_distributed_supervisor(comp_list, eventdata, cliques)
  for event in eventdata:
      eventdata[event].matHat = maxplus.matrix_to_vector(eventdata[event].matHat)
  orig_alphabet = Set([])
  #this is needed for bisimulation for some reason
  tau = comp_list[0].collection.make_event("tau", True, True, False)
  for aut in comp_list:
    aut.alphabet.add(tau)
    orig_alphabet.update(aut.alphabet)
  compnums = []
  temp = []
  for string in order:
    comps = set(string.split(","))
    for aut in comp_list:
      if aut.name in comps:
        temp.append(aut)
    compnums.append((0,len(comps)))
  comp_list = temp
  #compnums = [len(comp_list)]
  #ant_algorithm2(comp_list, eventdata, len(cliques))
  #path = restrictpath(tau_abstracted_greedy_supervisor_recurse_subsetcons(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums, set()))
  path = tau_abstracted_greedy_supervisor_recurse(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums)
  resultsfile = file(name, 'w')
  pathtime = -time()
  #path = tau_abstracted_greedy_supervisor_recurse_weak_bisim(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums, [], resultsfile)
  pathtime += time()
  resultsfile.write("time: " + str(pathtime))
  resultsfile.write("\n")
  testpathvec(copylist, path, eventdata, len(cliques), resultsfile)
  resultsfile.close()
  #testpath(copylist, path, eventdata, len(cliques))
  return path
    
def tau_abstracted_greedy_supervisor2(comp_list, req_list, comp_mut_ex, evt_pairs, name):
  if not comp_mut_ex == "type1" and not comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
  remove_always_disabled_events(comp_list)
  common.print_line("Computing event data...")
  a = comp_list[0].collection.make_event("a", True, True, False)
  b = comp_list[0].collection.make_event("b", True, True, False)
  c = comp_list[0].collection.make_event("c", True, True, False)
  d = comp_list[0].collection.make_event("d", True, True, False)
  res1 = [a,c,d]
  res2 = [b,c,d]
  resources = [res1, res2]
  zeromat = maxplus.Matrix([[0,0],[0,0]])
  amat = taskresource.ExtendedEventData(a, 200, resources).matHat
  bmat = taskresource.ExtendedEventData(b, 300, resources).matHat
  cmat = taskresource.ExtendedEventData(c, 260, resources).matHat
  dmat = taskresource.ExtendedEventData(d, 200, resources).matHat
  print "a:" + str(taskresource.ExtendedEventData(a, 200, resources))
  print "b:" + str(taskresource.ExtendedEventData(b, 300, resources))
  print "c:" + str(taskresource.ExtendedEventData(c, 280, resources))
  print "d:" + str(taskresource.ExtendedEventData(d, 200, resources))
  abmat = maxplus.otimes_mat_mat(bmat, amat)
  abdmat = maxplus.otimes_mat_mat(dmat, abmat)
  dbmat = maxplus.otimes_mat_mat(dmat, bmat)
  dbamat = maxplus.otimes_mat_mat(dbmat, amat)
  dcmat = maxplus.otimes_mat_mat(dmat, cmat)
  zdbamat = maxplus.otimes_mat_mat(dbamat, zeromat)
  zdcmat = maxplus.otimes_mat_mat(dcmat, zeromat)
  dcdcmat = maxplus.otimes_mat_mat(cmat, dcmat)
  dbadbamat = maxplus.otimes_mat_mat(abmat, dbamat)
  print "ba:" + str(abmat)
  print "d(ba):" + str(abdmat)
  print "db:" + str(dbmat)
  print "(db)a:" + str(dbamat)
  print "cdc:" + str(dcdcmat)
  print "badba:" + str(dbadbamat)
  print "zdba:" + str(zdbamat)
  print "zdc:" + str(zdcmat)
  #aoii = ai
  plant_list = []
  for aut in comp_list:
    if not aut.name.startswith("TBR"):
      plant_list.append(aut)
  result = taskresource.compute_custom_eventdata_extended(plant_list, evt_pairs, comp_mut_ex)
  copylist = []
  for aut in comp_list:
    print aut.name
    #if aut.name == "TC_in00" or aut.name == "TC_out00":
      #continue
    copylist.append(get_automaton_copy(aut))
  #comp_list = sorted(comp_list, key=clustersort)
  print "startted sort"
  comp_list = sorted(comp_list, key=namesort)
  print "finished sort"
  #comp_list.insert(0, comp_list.pop())
  #comp_list = list(comp_list)
  #comp_list = list(reversed(comp_list))
  for aut in comp_list:
    print aut.name
  if result is None:
      return None
  eventdata, cliques = result
  #prog_distributed_supervisor(comp_list, eventdata, cliques)
  for event in eventdata:
      eventdata[event].matHat = maxplus.matrix_to_vector(eventdata[event].matHat)
  orig_alphabet = Set([])
  #this is needed for bisimulation for some reason
  tau = comp_list[0].collection.make_event("tau", True, True, False)
  for aut in comp_list:
    aut.alphabet.add(tau)
    orig_alphabet.update(aut.alphabet)
  compnums = []
  compnums.append((0,20))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  #compnums = []
  #compnums.append((0,11))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,12))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums = []
  #compnums.append((0,11))
  ##compnums.append((0,8))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,11))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,15))
  #compnums.append((0,8))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,15))
  #compnums.append((0,10))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,8))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,9))
  #compnums.append((0,11)) 
  #compnums.append((0,2))
  #compnums.append((0,9))
  # compnums = []
  # compnums.append((0,8))
  # compnums.append((1,8))
  # compnums.append((0,3))
  # compnums.append((1,11))
  # compnums.append((0,3))
  # compnums.append((0,2))  
  # compnums = []
  # compnums.append((0,20))
  # compnums.append((0,12))
  # compnums.append((0,12))
  # compnums.append((0,12))
  # compnums.append((0,12))
  # compnums.append((0,12))
  # compnums = []
  # compnums.append((0,8))
  # compnums.append((1,9))
  # compnums.append((2,12))
  # compnums.append((1,3))
  # compnums.append((0,2))
  # compnums.append((0,2))  
  # compnums = []
  # compnums.append((0,26))
  # compnums.append((0,2))
  #compnums = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
  #compnums = [8,9,11,2]
  #compnums = [len(comp_list)]
  #ant_algorithm2(comp_list, eventdata, len(cliques))
  #path = restrictpath(tau_abstracted_greedy_supervisor_recurse_subsetcons(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums, set()))
  #path = tau_abstracted_greedy_supervisor_recurse(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums)
  resultsfile = file(name, 'w')
  pathtime = -time()
  path = tau_abstracted_greedy_supervisor_recurse_weak_bisim(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums, [], resultsfile)
  pathtime += time()
  resultsfile.write("time: " + str(pathtime))
  resultsfile.write("\n")
  testpathvec(copylist, path, eventdata, len(cliques), resultsfile)
  resultsfile.close()
  #testpath(copylist, path, eventdata, len(cliques))
  return path
  
def generaterandompath(aut):
  path = []
  visited = Set()
  state = aut.initial
  while not state.marked:
    visited.add(state)
    edges = []
    for edge in state.get_outgoing():
      if edge.succ not in visited:
        edges.append(edge)
    if len(edges) == 0:
      return None        
    edgeindex = random.randrange(len(edges))
    edge = edges[edgeindex]
    path.append(edge)
    state = edge.succ
  return path
  
def generaterandompathaut(aut):
  path = []
  visited = Set()
  state = aut.initial
  while not state.marked:
    visited.add(state)
    edges = []
    for edge in state.get_outgoing():
      if edge.succ not in visited:
        edges.append(edge)
    if len(edges) == 0:
      return None        
    edgeindex = random.randrange(len(edges))
    edge = edges[edgeindex]
    path.append(edge)
    state = edge.succ
  for state in aut.get_states():
    for edge in list(state.get_outgoing()):
      if edge not in path:
        aut.remove_edge(edge)
  return aut
  
def generate_aut_from_path_events_weighted(path, alphabet, collection, weights):
  aut = weighted_structure.WeightedAutomaton(alphabet.copy(), collection)
  state = aut.add_new_state(len(path) == 0, aut.get_num_states())
  aut.initial = state
  for i in range(len(path)):
    nextstate = aut.add_new_state(i + 1 == len(path), aut.get_num_states())
    event = path[i]
    aut.add_edge_data(state, nextstate, event, weights[event])
    state = nextstate
  return aut
  
def generate_aut_from_path_events_weighted_dontcare(path, alphabet, collection):
  aut = weighted_structure.WeightedAutomaton(alphabet.copy(), collection)
  state = aut.add_new_state(len(path) == 0, aut.get_num_states())
  aut.initial = state
  for i in range(len(path)):
    nextstate = aut.add_new_state(i + 1 == len(path), aut.get_num_states())
    event = path[i]
    aut.add_edge_data(state, nextstate, event, 1)
    state = nextstate
  return aut
  
def generate_aut_from_path(path, alphabet, collection):
  aut = weighted_structure.WeightedAutomaton(alphabet.copy(), collection)
  state = aut.add_new_state(len(path) == 0, aut.get_num_states())
  aut.initial = state
  for i in range(len(path)):
    edge = path[i]
    if edge.label not in alphabet:
      continue
    nextstate = aut.add_new_state(i + 1 == len(path), aut.get_num_states())
    aut.add_edge_data(state, nextstate, edge.label, edge.weight)
    state = nextstate
  return aut
  
def tau_abstracted_greedy_supervisor_not_weighted(comp_list, req_list, comp_mut_ex, evt_pairs):
  if not comp_mut_ex == "type1" and not comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
  common.print_line("Computing event data...")
  #result = taskresource.compute_custom_eventdata_extended(comp_list, evt_pairs, comp_mut_ex)
  copylist = []
  newcomp_list = []
  for aut in comp_list:
    print aut.name
    copylist.append(get_automaton_copy(aut))
  #comp_list = sorted(comp_list, key=clustersort)
  #comp_list.insert(0, comp_list.pop())
  #comp_list = list(reversed(comp_list))
  tick = comp_list[0].collection.make_event("tick", True, True, False)
  for aut in comp_list:
    print aut.name
    newcomp_list.append(convert_weighted_to_tick(aut, tick))
  comp_list = newcomp_list
  #if result is None:
  #    return None
  #eventdata, cliques = result
  orig_alphabet = Set([])
  #this is needed for bisimulation for some reason
  tau = comp_list[0].collection.make_event("tau", True, True, False)
  for aut in comp_list:
    aut.alphabet.add(tau)
    orig_alphabet.update(aut.alphabet)
  compnums = [8,9,11,2]
  #compnums = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
  #compnums = [len(comp_list)]
  path = restrictpath(tau_abstracted_greedy_supervisor_recurse_not_weighted(comp_list, evt_pairs, orig_alphabet,0, compnums, tau))
  testpath(copylist, path, eventdata, len(cliques))
  return path
  
def vec_to_mat(vec, resources):
  mat = maxplus.make_matrix(maxplus.EPSILON,
                            len(resources), len(resources))

  for ridx, rres in enumerate(resources): # Row iterator
      for cidx, cres in enumerate(resources): # Column iterator
          if ridx == cidx: # Main diagonal
              mat.set(ridx, cidx, vec.data[ridx])
          else:
              if vec.data[ridx] != 0 and vec.data[cidx] != 0:
                  mat.set(ridx, cidx, maxplus.maximum(vec.data[ridx], vec.data[cidx]))
              else:
                  mat.set(ridx, cidx, maxplus.EPSILON)
  qtilde = [x for x in vec.data]
  qcheck = [-x if x != 0 else maxplus.EPSILON for x in vec.data]
  q_check_mat = maxplus.ColumnMatrix(qcheck)
  q_tilde_mat = maxplus.RowMatrix(qtilde)
  multiply = maxplus.otimes_mat_mat(q_check_mat, q_tilde_mat)
  qq = maxplus.oplus_mat_mat(maxplus.make_unit_matrix(len(resources)),
                             multiply)
  return maxplus.otimes_mat_mat(mat, qq)
    
def tau_abstracted_greedy_supervisor_recurse(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums):
    if len(comp_list) == 1:
      print "last automaton"
      comp_list[0].reduce(True, True)
      #weighted_frontend.save_weighted_automaton(comp_list[0], "Supervisor is saved in %s\n", "supnonblockingnewwaver.cfg")
      print comp_list[0]
##      comp_list[0].save_as_dot("lastaut.dot")
      path = restrictpath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)))
      #for event in eventdata:
        #eventdata[event].matHat = vec_to_mat(eventdata[event].matHat, cliques)
      #print comp_list[0].collection.events
      #non_prog = set([comp_list[0].collection.events['NewWaver']])
      #path = get_greedy_time_optimal_sup_progressive(comp_list[0], eventdata, len(cliques),non_prog)
      #weighted_frontend.save_weighted_automaton(path, "Supervisor is saved in %s\n", "supgreedyoptimalprogwaver.cfg")
      #print path
##      #path.save_as_dot("endsup.dot")
      #aue =iai
      path = restrictpath(path)
      return path
      #return get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques))
    else:
      old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      print "start abstraction"
      #prochack(comp_list[0], find_local_alphabet(comp_list, comp_list[0], evt_pairs))
      print comp_list[0]
      #do_tau_abstraction(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs)
      #do_tau_abstraction2(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs, depth)
      #do_tau_abstraction3(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs, depth)
      #comp_list[0] = subsetconstruction(comp_list[0], find_local_alphabet(comp_list, comp_list[0], evt_pairs), depth)
      comp_list[0] = subsetconstruction(comp_list[0], get_local_events(comp_list[0], comp_list), depth)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
##      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
##      comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      #pruneunlikely(comp_list[0], eventdata, cliques, orig_alphabet)
      #comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      first, last = compnums[depth]
      if last > len(comp_list):
        last = len(comp_list)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
      #                                              algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[0:compnums[depth]],
       #                                          algorithm.EQUAL_WEIGHT_EDGES)
      new_plant = synchronousproduct(comp_list[first:last], depth)
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      print "synchronous before reduce"
      print new_plant
      new_plant.reduce(True, True)
      print "synchronous after reduce"
      print new_plant
      print "depth:" + str(depth)
      #comp_list.pop(0)
      #comp_list.pop(0)
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums)
      print "path returned"
      if path == None:
        return path
##      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
##      old_aut.save_as_dot("G1" + str(depth) + ".dot")
##      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      patholdsync.reduce(True, True)
      print "looks like:" + str(depth)
      print patholdsync
##      patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      path = restrictpath(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
      return path
      #return get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques))
      
def tau_abstracted_greedy_supervisor_recurse_subsetcons(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums, join):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      prochack(comp_list[0],set())
##      comp_list[0].save_as_dot("lastaut.dot")
      #path = restrictpath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)))
      print "join:" + str(join)
      #path = get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques))
      
      path = get_greedy_time_optimal_sup_progressive2(comp_list[0], eventdata, len(cliques), join)
      path = restrictpath_multi(path, join)
      path = abstraction.automaton_abstraction_weighted(path)
      #path = heapsofpiecesdijkstras_prog_reverse(comp_list[0], len(cliques), eventdata, join)
      return path
      #return get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques))
    else:
      old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      print "start abstraction"
      print comp_list[0]
      comp_list[0] = subsetconstruction(comp_list[0], get_local_events(comp_list[0], comp_list), depth)
      newjoin = set()
      for evt in comp_list[0].alphabet:
        newjoin.add(evt)
      print comp_list[0]
##      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
##      comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      first, last = compnums[depth]
      if last > len(comp_list):
        last = len(comp_list)
      new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
                                                    algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[0:compnums[depth]],
       #                                          algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = synchronousproduct(comp_list[0:2], depth)
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      print "synchronous before reduce"
      print new_plant
      new_plant.reduce(True, True)
      print "synchronous after reduce"
      print new_plant
      print "depth:" + str(depth)
      #comp_list.pop(0)
      #comp_list.pop(0)
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse_subsetcons(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums, newjoin)
      print "path returned"
      if path == None:
        return path
##      path.save_as_dot("beforproj" + str(depth) + ".dot")
      tosync = [old_aut, path]
##      old_aut.save_as_dot("G1" + str(depth) + ".dot")
##      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      patholdsync.reduce(True, True)
      print "looks like:" + str(depth)
      print patholdsync
      prochack(patholdsync, set())
##      patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      print "join:" + str(join)
      #join = set()
      #path = get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques))
      path = get_greedy_time_optimal_sup_progressive2(patholdsync, eventdata, len(cliques), join)
      path = restrictpath_multi(path, join)
      path = abstraction.automaton_abstraction_weighted(path)
      # if depth != 0:
        # path = heapsofpiecesdijkstras_prog_reverse(patholdsync, len(cliques), eventdata, join)  
      # else:
        # path = get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques))
##      path.save_as_dot("path" + str(depth) + ".dot")
      return path
      #return get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques))
      
def prochack(aut,local_alphabet):
  edgestoremove = []
  containsP32 = False
  for state in aut.get_states():
    removenonproc = False
    for edge in state.get_outgoing():
      if edge.label.name.startswith("Proc"):
        removenonproc = True
    if removenonproc:
      for edge in state.get_outgoing():
        if not edge.label.name.startswith("Proc"):
          edgestoremove.append(edge)
      continue
    removenondrop = False
    for edge in state.get_outgoing():
      if edge.label in local_alphabet and "drop" in edge.label.name:
        removenondrop = True
    if removenondrop:
      for edge in state.get_outgoing():
        if edge.label not in local_alphabet or "drop" not in edge.label.name:
          edgestoremove.append(edge)
      continue
    removenonpick = False
    for edge in state.get_outgoing():
      if "pick-P32" in edge.label.name:
          containsP32 = True
      if edge.label in local_alphabet and "pick" in edge.label.name and "pick-P32" not in edge.label.name:
        print edge.label.name
        removenonpick = True
        continue
    if removenonpick:
      for edge in state.get_outgoing():
        if edge.label not in local_alphabet:# or ("pick" not in edge.label.name or "pick-P32" in edge.label.name):
          edgestoremove.append(edge)
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
##  aut.save_as_dot("afterprochack.dot")
  
      
# def prochack(aut, local_alphabet):
  # edgestoremove = []
  # for state in aut.get_states():
    # removenonproc = False
    # for edge in state.get_outgoing():
      # if edge.label.name.startswith("Proc"):
        # removenonproc = True
    # if removenonproc:
      # for edge in state.get_outgoing():
        # if not edge.label.name.startswith("Proc") and edge.label not in local_alphabet:
          # edgestoremove.append(edge)
  # for edge in edgestoremove:
    # aut.remove_edge(edge)
    
   
def tau_abstracted_greedy_supervisor_recurse_ant(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums, originals):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
##      comp_list[0].save_as_dot("lastaut.dot")
      originals.append(comp_list[0])
      temp = []
      for aut in reversed(originals):
        temp.append(aut)
      originals = temp
      ant_algorithm(originals, eventdata, len(cliques))
      #return get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques))
    else:
      old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      originals.append(old_aut)
      print "start abstraction"
      print comp_list[0]
      #do_tau_abstraction(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs)
      #do_tau_abstraction2(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs, depth)
      #comp_list[0] = subsetconstruction(comp_list[0], find_local_alphabet(comp_list, comp_list[0], evt_pairs), depth)
      comp_list[0] = subsetconstruction(comp_list[0], get_local_events(comp_list[0], comp_list), depth)
      maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
##      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
##      comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      first, last = compnums[depth]
      if last > len(comp_list):
        last = len(comp_list)
      new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
                                                    algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[0:compnums[depth]],
       #                                          algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = synchronousproduct(comp_list[0:2], depth)
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      print "synchronous before reduce"
      print new_plant
      new_plant.reduce(True, True)
      print "synchronous after reduce"
      print new_plant
      print "depth:" + str(depth)
      #comp_list.pop(0)
      #comp_list.pop(0)
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse_ant(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums, originals)
      print "path returned"
      if path == None:
        return path
##      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
##      old_aut.save_as_dot("G1" + str(depth) + ".dot")
##      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      patholdsync.reduce(True, True)
      print "looks like:" + str(depth)
      print patholdsync
##      patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      return restrictpath(get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques)))
      #return get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques))
      
def antrun2(aut, origaut, pheromone):
  path = []
  visited = Set()
  state = aut.initial
  origstate = origaut.initial
  usededges = Set()
  while not state.marked:
    visited.add(state)
    edges = []
    pheromonetrail = 0
    for edge in state.get_outgoing():
      if edge.succ not in visited:
        edges.append(edge)
        pheromonetrail += 1
        tup = (origstate, edge.label)
        if tup in pheromone:
          pheromonetrail += pheromone[tup]
          #print "using: " + str(pheromone[tup])
    if len(edges) == 0:
      return None        
    randnumber = random.uniform(0,pheromonetrail)
    pheromonetrail = 0
    needededge = None
    for edge in edges:
      pheromonetrail += 1
      tup = (origstate, edge.label)
      if tup in pheromone:
        pheromonetrail += pheromone[tup]
      if pheromonetrail >= randnumber:
        needededge = edge
        break
    path.append(needededge)
    usededges.add((origstate, needededge.label))
    for edge in origstate.get_outgoing():
      if edge.label == needededge.label:
        origstate = edge.succ
        break
    state = needededge.succ
  return path, usededges
      
def antpath(aut, pheromone):
  path = []
  visited = Set()
  string = None
  state = aut.initial
  while not state.marked:
    visited.add(state)
    edges = []
    pheromonetrail = 0
    for edge in state.get_outgoing():
      if edge.succ not in visited:
        edges.append(edge)
        pheromonetrail += 1
        tup = (aut, edge.label, string)
        if tup in pheromone:
          pheromonetrail += pheromone[tup]
          #print "using: " + str(pheromone[tup])
    if len(edges) == 0:
      return None        
    randnumber = random.uniform(0,pheromonetrail)
    pheromonetrail = 0
    needededge = None
    for edge in edges:
      pheromonetrail += 1
      tup = (aut, edge.label, string)
      if tup in pheromone:
        pheromonetrail += pheromone[tup]
      if pheromonetrail >= randnumber:
        needededge = edge
        break
    path.append(needededge)
    state = needededge.succ
    string = FrozenLink(string, needededge.label)
  return path
  
def antpath(aut, pheromone, weight_map, Q):
  path = []
  visited = Set()
  string = None
  state = aut.initial
  while not state.marked:
    visited.add(state)
    edges = []
    pheromonetrail = 0
    for edge in state.get_outgoing():
      if edge.succ not in visited:
        edges.append(edge)
        pheromonetrail += Q/weight_map[edge.succ]
        tup = (aut, edge.label, string)
        if tup in pheromone:
          pheromonetrail += pheromone[tup]
          #print "using: " + str(pheromone[tup])
    if len(edges) == 0:
      return None        
    randnumber = random.uniform(0,pheromonetrail)
    pheromonetrail = 0
    needededge = None
    for edge in edges:
      pheromonetrail += Q/weight_map[edge.succ]
      tup = (aut, edge.label, string)
      if tup in pheromone:
        pheromonetrail += pheromone[tup]
      if pheromonetrail >= randnumber:
        needededge = edge
        break
    path.append(needededge)
    state = needededge.succ
    string = FrozenLink(string, needededge.label)
  return path
  
def ismarked(statetuple):
  for state in statetuple:
    if not state.marked:
      return False
  return True
  
#this function assumes deterministic automata
def antpath3(automata, alphabet, pheromone):
  path = []
  visited = Set()
  string = None
  statetuple = []
  successormap = {}
  for aut in automata:
    for state in aut.get_states():
      for edge in state.get_outgoing():
        successormap[(state, edge.label)] = edge.succ
    statetuple.append(aut.initial)
  while not ismarked(statetuple):
    statetuple = tuple(statetuple)
    visited.add(statetuple)
    possiblesuccessors = {}
    pheromonetrail = 0
    for event in alphabet:
      newtuple = []
      for i in range(len(statetuple)):
        if event not in automata[i].alphabet:
          newtuple.append(statetuple[i])
        elif (statetuple[i], event) in successormap:
          newtuple.append(successormap[(statetuple[i], event)])
        else:
          newtuple = None
          break
      if newtuple != None:
        newtuple = tuple(newtuple)
        if newtuple in visited:
          continue
        phertup = (event, string)
        pheromonetrail += 1
        if phertup in pheromone:
          pheromonetrail += pheromone[phertup]
        possiblesuccessors[event] = newtuple
    if len(possiblesuccessors) == 0:
      return path, False        
    randnumber = random.uniform(0,pheromonetrail)
    pheromonetrail = 0
    neededevent = None
    for event in possiblesuccessors:
      pheromonetrail += 1
      phertup = (event, string)
      if phertup in pheromone:
        pheromonetrail += pheromone[tup]
      if pheromonetrail >= randnumber:
        neededevent = event
        break
    path.append(neededevent)
    statetuple = possiblesuccessors[neededevent]
    string = FrozenLink(string, neededevent)
  return path
      
def ant_algorithm2(automata, eventdata, heap_len):
  pheromone = {}
  NUMANTS = 500
  Q = float(400)
  P = .8
  bestpath = None
  bestexec = None
  antaut = 0
  alphabet = Set()
  blocking = Set() 
  for aut in automata:
    print "antaut:" + str(antaut) + " : " + str(aut)
##    aut.save_as_dot("antaut"+ str(antaut) + ".dot")
    alphabet.update(aut.alphabet)
    antaut += 1
  while True:
    newpheromone = {}
    runtot = 0
    antrun = 0
    for ant in range(NUMANTS):
      path = antpath3(automata, alphabet, pheromone,blocking)
      if path[1] == False:
        continue
      antrun += 1
      pathaut = generate_aut_from_path_events(path,alphabet, automata[0].collection)
      exectime = getpathexecutiontime(finpathaut, eventdata, heap_len)
      pathaut.clear()
      if bestexec == None or exectime < bestexec:
        bestpath = finpath
        bestexec = exectime
      #print exectime
      runtot += exectime
      exectime = Q/(exectime-70)
      string = None
      for event in path:
        tup = (event, string)
        if tup not in newpheromone:
          if tup not in pheromone:
            oldpheromone = 0
          else:
            oldpheromone = pheromone[tup] * P
        else:
          oldpheromone = newpheromone[tup]
        newpheromone[(event,string)] = oldpheromone + exectime
        string = FrozenLink(string, edge.label)
    pheromone = newpheromone
    print "successful runs: " + str(antrun)
    if (antrun != 0):
      print "runavg: " + str(runtot/antrun)
    print "current best exec:" + str(bestexec)
      
def ant_algorithm(automata, eventdata, heap_len, orig_alphabet):
  pheromone = {}
  NUMANTS = 10
  Q = float(400)
  P = .8
  bestpath = None
  bestexec = None
  antaut = 0
  for aut in automata:
    print "antaut:" + str(antaut) + " : " + str(aut)
##    aut.save_as_dot("antaut"+ str(antaut) + ".dot")
    antaut += 1
  while True:
    newpheromone = {}
    runtot = 0
    antrun = 0
    for ant in range(NUMANTS):
      print antrun
      paths = []
      weight_map = get_greedy_time_optimal_weights_vector(automata[0], eventdata, heap_len)
      for key in weight_map:
        if weight_map[key] == 0:
          weight_map[key] = 1
      paths.append(antpath(automata[0], pheromone, weight_map, Q/2))
      #paths.append(antpath(automata[0], pheromone))
      alphabet = automata[0].alphabet.intersection(orig_alphabet)
      if paths[0] == None:
        continue
      antrun += 1
      for i in range(1, len(automata)):
        aut = automata[i]
        pathaut = generate_aut_from_path(paths[i-1], alphabet, aut.collection)
        sync = weighted_product.n_ary_weighted_product([aut,pathaut],algorithm.EQUAL_WEIGHT_EDGES)
        sync.reduce(True, True)
        weight_map = get_greedy_time_optimal_weights_vector(sync, eventdata, heap_len)
        for key in weight_map:
          if weight_map[key] == 0:
            weight_map[key] = 1
        alphabet = sync.alphabet.intersection(orig_alphabet)
        paths.append(antpath(sync, pheromone, weight_map, Q/2))
        #paths.append(antpath(sync, pheromone))
        #sync.clear()
        #pathaut.clear()
      finpath = paths[len(paths)-1]
      finpathaut = generate_aut_from_path(finpath,alphabet, automata[len(paths)-1].collection)
      exectime = getpathexecutiontime(finpathaut, eventdata, heap_len)
      if bestexec == None or exectime < bestexec:
        bestpath = finpath
        bestexec = exectime
      #print exectime
      runtot += exectime
      exectime = Q/(exectime-70)
      for i in range(len(paths)):
        path = paths[i]
        aut = automata[i]
        string = None
        for edge in path:
          tup = (aut, edge.label, string)
          if tup not in newpheromone:
            if tup not in pheromone:
              oldpheromone = 0
            else:
              oldpheromone = pheromone[tup] * P
          else:
            oldpheromone = newpheromone[tup]
          newpheromone[(aut,edge.label,string)] = oldpheromone + exectime
          string = FrozenLink(string, edge.label)
    pheromone = newpheromone
    print "runavg: " + str(runtot/antrun)
    print "current best exec:" + str(bestexec)
        
      
def tau_abstracted_greedy_supervisor_recurse_shotgun(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
##      comp_list[0].save_as_dot("lastaut.dot")
      bestpath = restrictpath(get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques)))
      otherpaths = []
      for i in range(100):
        path = generaterandompath(comp_list[0])
        if path != None:
          otherpaths.append(generate_aut_from_path(path, comp_list[0].alphabet, comp_list[0].collection))
      return bestpath, otherpaths
      #return get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques))
    else:
      old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      old_aut = previousaut
      #old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
##      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      local_alphabet = get_local_events(comp_list[0], comp_list)
      preserve = comp_list[0].alphabet.difference(local_alphabet)
      comp_list[0], state_to_stateset, tau = abstraction.abstraction_with_partitions(comp_list[0], preserve)
##      comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      replace_tau(comp_list[0], previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet, depth)
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      first, last = compnums[depth]
      if last > len(comp_list):
        last = len(comp_list)
      new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
                                                    algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[0:compnums[depth]],
       #                                          algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = synchronousproduct(comp_list[0:2], depth)
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      print "synchronous before reduce"
      print new_plant
      new_plant.reduce(True, True)
      print "synchronous after reduce"
      print new_plant
      print "depth:" + str(depth)
      #comp_list.pop(0)
      #comp_list.pop(0)
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      bestpath, otherpaths = tau_abstracted_greedy_supervisor_recurse_shotgun(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums)
      print "path returned"
      if bestpath == None:
        return bestpath
      otherpaths.append(bestpath)
      newbest = None
      execution = None
      newother = []
      syncs = []
      for path in otherpaths:
##        path.save_as_dot("beforproj" + str(depth) + ".dot")
        path = project(path, orig_alphabet)
        #print "alphabet"
        #print path.alphabet
        tosync = [old_aut, path]
##        old_aut.save_as_dot("G1" + str(depth) + ".dot")
##        path.save_as_dot("G2" + str(depth) + ".dot")
        #old_aut.collection = tosync
        #path.collection = tosync
        patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
        patholdsync.reduce(True, True)
        print "looks like:" + str(depth)
        print patholdsync
##        patholdsync.save_as_dot("sync" + str(depth) + ".dot")
        curpath = restrictpath(get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques)))
        exectime = getpathexecutiontime(curpath, eventdata, len(cliques))
        if execution == None or execution > exectime:
          execution = exectime
          newbest = curpath
        syncs.append(patholdsync)
      if (depth == 0):
        return newbest
      for i in range(100):
        randindex = random.randrange(len(syncs))
        sync = syncs[randindex]
        path = generaterandompath(sync)
        if path != None:
          newother.append(generate_aut_from_path(path, sync.alphabet, sync.collection))
      return newbest, newother
      #return get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques))
      
def tau_abstracted_greedy_supervisor_recurse_weak_bisim(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums, originals, resultfile):
    print "weak bisim"
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
##      comp_list[0].save_as_dot("lastaut.dot")
      path = comp_list[0]
      #return heapsofpiecespath(comp_list[0], len(cliques), eventdata)
      #return heapsofpiecespath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)), len(cliques), eventdata)
      return restrictpath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)))
      #pruneunlikely(path, eventdata, cliques, set())
##      #path.save_as_dot("last_path")
      #return path
      #return get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques))
    else:
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      old_aut = previousaut
      originals.append(get_automaton_copy(old_aut))
      #old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      for state in comp_list[0].get_states():
        comp_list[0].state_names[state.number] = str(state.number)
##      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      local_alphabet = get_local_events(comp_list[0], comp_list)
      preserve = comp_list[0].alphabet.difference(local_alphabet)
      #comp_list[0], state_to_stateset, tau = abstraction.abstraction_with_partitions(comp_list[0], preserve)
      tup, tau = subsetconstruction_with_partitions(comp_list[0], local_alphabet, depth), None
      if tup != comp_list[0]:
        comp_list[0], state_to_stateset = tup
        print "finish weak bisim"
##        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
        #comp_list[0] = replace_tau6(comp_list[0], previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet, depth)
        print "finish replace tau"
      maketausequal(comp_list[0], orig_alphabet, eventdata)
##      comp_list[0].save_as_dot("what" + str(depth) + ".dot")
      comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      first, last = compnums[depth]
      if last > len(comp_list):
        last = len(comp_list)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
                                                          #algorithm.EQUAL_WEIGHT_EDGES)
      
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[0:compnums[depth]],
      #                                                    algorithm.EQUAL_WEIGHT_EDGES)
      #temp = synchronousproduct(comp_list[first+1:last], depth)
      #temp.reduce(True, True)
      #new_plant = synchronousproduct([comp_list[first], temp], depth)
      for aut in comp_list[first:last]:
        print aut.name
      new_plant = synchronousproduct(comp_list[first:last], depth)
      resultfile.write("comp size: " + str(new_plant.get_num_states()))
      resultfile.write("\n")
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      print "synchronous before reduce"
      print new_plant
      new_plant.reduce(True, True)
      print "synchronous after reduce"
      print new_plant
      print "depth:" + str(depth)
      #comp_list.pop(0)
      #comp_list.pop(0)
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse_weak_bisim(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums, originals, resultfile)
      print "path returned"
      if path == None:
        return path
      if depth == 0:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project(path, orig_alphabet)
      #path = subsetconstruction(path, path.alphabet.difference(orig_alphabet), depth)
      #print "alphabet"
      #print path.alphabet
      origpath = get_automaton_copy(path)
      tosync = [old_aut, path]
      localevpath = get_local_events(path, tosync)
      print localevpath
      tup = subsetconstruction_with_partitions(path, localevpath, depth+10000)
      path = replace_tau6(tup[0], path, tup[1], tau, eventdata, cliques, localevpath, depth+100000)
      #path = tup[0]
      tosync = [old_aut, path]
##      old_aut.save_as_dot("G1" + str(depth) + ".dot")
##      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      resultfile.write("comp size path return: " + str(patholdsync.get_num_states()))
      resultfile.write("\n")
      patholdsync.reduce(True, True)
      print "looks like:" + str(depth)
      print patholdsync
      #path = heapsofpiecespath(patholdsync, len(cliques), eventdata)
      path = restrictpath(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
      #path = generaterandompathaut(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
      tosync = [path, old_aut]
      localevpath = get_local_events(path, tosync)
      print localevpath
      path = subsetconstruction(path, localevpath, depth + 200000)
      path = mergepaths(path, origpath, eventdata, len(cliques))
      #tosync = [path, old_aut]
      #localevpath = get_local_events(path, tosync)
      #print localevpath
      #path = subsetconstruction(path, localevpath, depth + 200000)
      #tosync = [path, origpath]
#      #path.save_as_dot("taupath.dot")
#      #origpath.save_as_dot("origpath.dot")
      #patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
#      #patholdsync.save_as_dot("pathsync.dot")
      #resultfile.write("comp size path return: " + str(patholdsync.get_num_states()))
      #resultfile.write("\n")
      #patholdsync.reduce(True, True)
      #print "looks like:" + str(depth)
      #print patholdsync
      #patholdsync = restrictpath(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
      #return patholdsync
      return path
      
def tau_abstracted_greedy_supervisor_recurse_weak_bisim_orig(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums, originals, resultfile):
    print "weak bisim"
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
##      comp_list[0].save_as_dot("lastaut.dot")
      path = comp_list[0]
      #return heapsofpiecespath(comp_list[0], len(cliques), eventdata)
      #return heapsofpiecespath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)), len(cliques), eventdata)
      return restrictpath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)))
      #pruneunlikely(path, eventdata, cliques, set())
##      #path.save_as_dot("last_path")
      #return path
      #return get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques))
    else:
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      old_aut = previousaut
      originals.append(get_automaton_copy(old_aut))
      #old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      for state in comp_list[0].get_states():
        comp_list[0].state_names[state.number] = str(state.number)
##      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      local_alphabet = get_local_events(comp_list[0], comp_list)
      preserve = comp_list[0].alphabet.difference(local_alphabet)
      #comp_list[0], state_to_stateset, tau = abstraction.abstraction_with_partitions(comp_list[0], preserve)
      tup, tau = subsetconstruction_with_partitions(comp_list[0], local_alphabet, depth), None
      if tup != comp_list[0]:
        comp_list[0], state_to_stateset = tup
        print "finish weak bisim"
##        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
        comp_list[0] = replace_tau6(comp_list[0], previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet, depth)
        print "finish replace tau"
      maketausequal(comp_list[0], orig_alphabet, eventdata)
##      comp_list[0].save_as_dot("what" + str(depth) + ".dot")
      comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      first, last = compnums[depth]
      if last > len(comp_list):
        last = len(comp_list)
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
                                                          #algorithm.EQUAL_WEIGHT_EDGES)
      
      #new_plant = weighted_product.n_ary_weighted_product(comp_list[0:compnums[depth]],
      #                                                    algorithm.EQUAL_WEIGHT_EDGES)
      #temp = synchronousproduct(comp_list[first+1:last], depth)
      #temp.reduce(True, True)
      #new_plant = synchronousproduct([comp_list[first], temp], depth)
      new_plant = synchronousproduct(comp_list[first:last], depth)
      resultfile.write("comp size: " + str(new_plant.get_num_states()))
      resultfile.write("\n")
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      print "synchronous before reduce"
      print new_plant
      new_plant.reduce(True, True)
      print "synchronous after reduce"
      print new_plant
      print "depth:" + str(depth)
      #comp_list.pop(0)
      #comp_list.pop(0)
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse_weak_bisim_orig(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums, originals, resultfile)
      print "path returned"
      if path == None:
        return path
##      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project(path, orig_alphabet)
      if depth == 0:
        return path
      #path = subsetconstruction(path, path.alphabet.difference(orig_alphabet), depth)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
##      old_aut.save_as_dot("G1" + str(depth) + ".dot")
##      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      resultfile.write("comp size path return: " + str(patholdsync.get_num_states()))
      resultfile.write("\n")
      patholdsync.reduce(True, True)
      print "looks like:" + str(depth)
      print patholdsync
      if depth < 0:
        #pruneunlikely(patholdsync, eventdata, cliques, set())
##        patholdsync.save_as_dot("sync" + str(depth) + ".dot")
        #return patholdsync
        return get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques))
        #return heapsofpiecespath(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)), len(cliques), eventdata)
        #return heapsofpiecespath(patholdsync, len(cliques), eventdata)
      else:
        #return restrictpath(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
        return generaterandompathaut(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
      #return path
      
def calcstarttime(currentcontours, used):
  maxcont = 0
  for i in range(len(used)):
    if used[i]:
      maxcont = maxcont if currentcontours.data[i] < maxcont else currentcontours.data[i]
  return maxcont
  
def pathauttoeventlist(aut):
  pathstate = aut.initial
  events = []
  while not pathstate.marked:
    for edge in pathstate.get_outgoing():
      events.append(edge.label)
      pathstate = edge.succ
      break
  return events
  
def find_time_optimal_path_shuffle(aut, orig_auts, eventdata, heap_len):
    path = restrictpath(get_greedy_time_optimal_sup(aut, eventdata, heap_len))
    while orig_auts:
      orig = orig_auts.pop()
      origpath = get_automaton_copy(path)
      tosync = [old_aut, path]
      localevpath = get_local_events(path, tosync)
      print localevpath
      tup = subsetconstruction_with_partitions(path, localevpath, 0)
      path = replace_tau6(tup[0], path, tup[1], tau, eventdata, cliques, localevpath, 0)
      tosync = [old_aut, path]
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      resultfile.write("comp size path return: " + str(patholdsync.get_num_states()))
      resultfile.write("\n")
      patholdsync.reduce(True, True)
      print "looks like:" + str(depth)
      print patholdsync
      path = restrictpath(get_greedy_time_optimal_sup_vector(patholdsync, eventdata, len(cliques)))
      tosync = [path, old_aut]
      localevpath = get_local_events(path, tosync)
      print localevpath
      path = subsetconstruction(path, localevpath, depth)
      path = mergepaths(path, origpath, eventdata, len(cliques))

def mergepaths(path1, path2, eventdata, heap_len):
  sharedevents = path1.alphabet.intersection(path2.alphabet)
  unionevents = path1.alphabet.union(path2.alphabet)
  weights = {}
  for state in path1.get_states():
    for edge in state.get_outgoing():
      weights[edge.label] = edge.weight
  for state in path2.get_states():
    for edge in state.get_outgoing():
      weights[edge.label] = edge.weight    
  coll = path1.collection
  path1 = pathauttoeventlist(path1)
  path2 = pathauttoeventlist(path2)
  weight = maxplus.matrix_to_vector(maxplus.make_rowmat(0,heap_len))
  index1 = 0
  index2 = 0
  newpath = []
  while (index1 < len(path1) and index2 < len(path2)):
    if (path1[index1] == path2[index2]):
      newpath.append(path1[index1])
      index1 += 1
      index2 += 1
    elif (path1[index1] in sharedevents):
      newpath.append(path2[index2])
      index2 += 1
    elif (path2[index2] in sharedevents):
      newpath.append(path1[index1])
      index1 += 1
    else:
      p1start = calcstarttime(weight, eventdata[path1[index1]].used)
      p2start = calcstarttime(weight, eventdata[path2[index2]].used)
      if p1start <= p2start:
        newpath.append(path1[index1])
        index1 += 1
      else:
        newpath.append(path2[index2])
        index2 += 1
    weight = maxplus.newtimes_vec_vec(weight, eventdata[newpath[len(newpath)-1]].matHat)
  if index2 < len(path2):
    path1 = path2
    index1 = index2
  while index1 < len(path1):
    newpath.append(path1[index1])
    index1 += 1
  return generate_aut_from_path_events_weighted(newpath, unionevents, coll, weights)
      
def tau_abstracted_greedy_supervisor_recurse_not_weighted(comp_list, evt_pairs, orig_alphabet, depth, compnums, tau):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
##      comp_list[0].save_as_dot("lastaut.dot")
      return restrictpath(get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques)))
    else:
      old_aut = get_automaton_copy_not_weighted(comp_list[0])#copy.deepcopy(comp_list[0])
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      local = get_local_events(comp_list[0], comp_list)
      local.add(tau)
      #comp_list[0] = subsetconstructionnotweighted(comp_list[0], local, depth)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      if True:#previousaut == comp_list[0]:
        print "didn't subset construct"
##        comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
        comp_list[0] = abstraction.abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
##        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      else:
##        comp_list[0].save_as_dot("beforehopcroft" + str(depth) + ".dot")
        #comp_list[0] = hopcroft(comp_list[0])
        comp_list[0].alphabet.add(tau)
        abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
##        comp_list[0].save_as_dot("afterhopcroft" + str(depth) + ".dot")
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      print compnums[depth]
      print "synchronise"
      new_plant = product.n_ary_unweighted_product(comp_list[0:compnums[depth]])
      print "end synchronise"
      #new_plant = synchronousproduct(comp_list[0:2], depth)
##      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      new_plant.reduce(True, True)
      print "depth:" + str(depth)
      print comp_list[0].alphabet
      print comp_list[1].name
      print comp_list[1].alphabet
      #comp_list.pop(0)
      #comp_list.pop(0)
      comp_list = comp_list[compnums[depth]:len(comp_list)]
      comp_list.insert(0,new_plant)
##      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse_not_weighted(comp_list, evt_pairs, orig_alphabet, depth+1, compnums, tau)
      print "path returned"
      if path == None:
        return path
##      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project(path, orig_alphabet)
      print "alphabet"
      print path.alphabet
      tosync = [old_aut, path]
##      old_aut.save_as_dot("G1" + str(depth) + ".dot")
##      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = product.n_ary_product(tosync)
      print "looks like: "
      print patholdsync
##      patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      return restrictpath(get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques)))
      
class hashcachingtuple(tuple):
  
  def __init__(self, values):
    super(hashcachingtuple, self).__init__(values)
    self.hashcache = super(hashcachingtuple, self).__hash__()
    
  def __hash__(self):
    return self.hashcache
      
def synchronousproduct(auts, depth):
  initstate = []
  newalphabet = Set()
  transmap = []
  transweight = []
  enabled = []
  exectime = -time()
  print "begin transmap"
  for i in range(len(auts)):
    aut = auts[i]
    initstate.append(aut.initial)
    newalphabet.update(aut.alphabet)
    transmap.append({})
    transweight.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
        transweight[i][state, edge.label, edge.succ] = edge.weight
        enabled[i][state].add(edge.label)
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i].alphabet)
    for state in auts[i].get_states():
      enabled[i][state].update(nonlocalevents)
  print "end transmap"
  exectime += time()
  print "time: " + str(exectime)
  inittuple = tuple(initstate)
  dictionary = {}
  aut_sync = weighted_structure.WeightedAutomaton(newalphabet, aut.collection)
  initstate = aut_sync.add_new_state(allmarked(inittuple), aut_sync.get_num_states())
  aut_sync.initial = initstate
  dictionary[inittuple] = initstate
  tovisit = [inittuple]
  transitions = 0
  edgestoadd = []
  exectime = -time()
  print "add edges"
  succcalctime = 0
  addstatetime = 0
  calccurrenab = 0
  count = 0
  while len(tovisit) != 0:
    count += 1
    statetuple = tovisit.pop()
    calccurrenab -= time()
    currenabled = set(enabled[0][statetuple[0]])
    for i in range(1,len(enabled)):
      currenabled.intersection_update(enabled[i][statetuple[i]])
    calccurrenab += time()
    for event in currenabled:
      hassuccs = True
      successorlists = []
      indexs = []
      for i in range(len(transmap)):
        indexs.append(0)
        if event not in auts[i].alphabet:
          successorlists.append([statetuple[i]])
          continue
        if (statetuple[i], event) not in transmap[i]:
          hassuccs = False
          break
        successorlists.append(transmap[i][(statetuple[i], event)])
      if not hassuccs:
        continue
      succcalctime -= time()
      #successors = calcsuccessors(statetuple, event, transmap, auts)
      successors = []
      while True:
        succtuple = []
        needtoincrement = True
        for i in xrange(len(indexs)):
          succtuple.append(successorlists[i][indexs[i]])
          if needtoincrement:
            indexs[i] += 1
            if indexs[i] >= len(successorlists[i]):
              indexs[i] = 0
            else:
              needtoincrement = False
        successors.append(hashcachingtuple(succtuple))
        if needtoincrement:
          break
      succcalctime += time()
      addstatetime -= time()
      for succtuple in successors:
        if succtuple not in dictionary:
          newstate = aut_sync.add_new_state(allmarked(succtuple), aut_sync.get_num_states())
          dictionary[succtuple] = newstate
          tovisit.append(succtuple)
        weight = calcweight(statetuple, succtuple, event, transweight)
        edgestoadd.append(weighted_structure.WeightedEdge(dictionary[statetuple], dictionary[succtuple], event, weight))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
    #  print "succcalctime" +str(succcalctime)
    #  print "addstatetime" +str(addstatetime)
    #  print "calccurrenab" +str(calccurrenab)
  print "end add edges"
  exectime += time()
  print succcalctime
  print addstatetime
  print calccurrenab
  print "time: " + str(exectime)
  exectime = -time()
  print "added edges"
  aut_sync.add_edges(edgestoadd)
  print "end add edges"
  exectime += time()
  print "time: " + str(exectime)
  #if depth == 5:
    #auia = aieia      
  return aut_sync
  
def allmarked(statetuple):
  for state in statetuple:
    if not state.marked:
      return False
  return True
  
def calcsuccessors(statetuple, event, transmap, auts):
  succs = Set()
  for i in range(len(auts)):
    if (event not in auts[i].alphabet):
      continue
    if (statetuple[i],event) not in transmap[i]:
      return succs
  return calcsuccessors2(statetuple, event, transmap, auts, succs, 0, [])
  
def calcsuccessors2(statetuple, event, transmap, auts, succs, i, l):
  if i >= len(auts):
    succs.add(tuple(l))
    return succs
  if (event in auts[i].alphabet):
    autsuccs = transmap[i][statetuple[i],event]
  else:
    autsuccs = Set([statetuple[i]])
  for state in autsuccs:
    l.append(state)
    calcsuccessors2(statetuple, event, transmap, auts, succs, i+1, l)
    l.pop()
  return succs
  
def calcweight(statetuple, succtuple, event, transweight):
  weight = 0
  for i in range(len(statetuple)):
    if (statetuple[i], event, succtuple[i]) in transweight[i]:
      weight = max(weight, transweight[i][statetuple[i], event, succtuple[i]])
  return weight
      
def findlocalreachable(stateset, localevents):
  stateset = set(stateset)
  tovisit = list(stateset);
  while len(tovisit) != 0:
    state = tovisit.pop()
    for edge in state.get_outgoing():
      if edge.label in localevents:
        if edge.succ not in stateset:
          stateset.add(edge.succ)
          tovisit.append(edge.succ)
  return frozenset(stateset)
  
def containsmarked(stateset):
  for state in stateset:
    if state.marked:
      return True
  return False
  
def get_local_events(aut, otherauts):
  localevents = copy.copy(aut.alphabet)
  for oaut in otherauts:
    if oaut != aut:
      for event in oaut.alphabet:
        localevents.discard(event)
  return localevents
    
  
def subsetconstruction(aut, localevents, depth):
##  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  aut_new = weighted_structure.WeightedAutomaton(copy.copy(aut.alphabet), aut.collection)
  #aut_new.alphabet = aut_new.alphabet.difference_update(localevents);
  for event in localevents:
    aut_new.alphabet.remove(event)
  initialset = Set([aut.initial])
  initialset = findlocalreachable(initialset, localevents)
  initstate = aut_new.add_new_state(containsmarked(initialset),aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    weightdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = Set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
          weightdictionary[edge.label] = edge.weight
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = findlocalreachable(targetstateset, localevents)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() >= aut.get_num_states()):
              return aut
          aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event, weightdictionary[event])
##  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new
  
def subsetconstruction_entrance_partitions(aut, localevents, depth):
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
##  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  aut_new = weighted_structure.WeightedAutomaton(copy.copy(aut.alphabet), aut.collection)
  partitions = {}
  #aut_new.alphabet = aut_new.alphabet.difference_update(localevents);
  for event in localevents:
    aut_new.alphabet.remove(event)
  initialset = frozenset([aut.initial])
  #initialset = findlocalreachable(initialset, localevents)
  initstate = aut_new.add_new_state(containsmarked(initialset),aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  partitions[initstate] = initialset
  tovisit = [initialset]
  while len(tovisit) != 0:
    entranceset = tovisit.pop()
    stateset = findlocalreachable(entranceset, localevents)
    dictionary[entranceset].marked = containsmarked(stateset)
    succdictionary = {}
    weightdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = Set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
          weightdictionary[edge.label] = edge.weight
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = frozenset(succdictionary[event])
          #targetstateset = findlocalreachable(targetstateset, localevents)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            partitions[newstate] = targetstateset
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() > aut.get_num_states()):
              return aut
          #print dictionary[entranceset]
          #print dictionary[targetstateset]
          aut_new.add_edge_data(dictionary[entranceset], dictionary[targetstateset], event, weightdictionary[event])
##  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new, partitions
  
def subsetconstruction_with_partitions(aut, localevents, depth):
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
##  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  aut_new = weighted_structure.WeightedAutomaton(copy.copy(aut.alphabet), aut.collection)
  partitions = {}
  #aut_new.alphabet = aut_new.alphabet.difference_update(localevents);
  for event in localevents:
    aut_new.alphabet.remove(event)
  initialset = Set([aut.initial])
  initialset = findlocalreachable(initialset, localevents)
  initstate = aut_new.add_new_state(containsmarked(initialset),aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  partitions[initstate] = initialset
  tovisit = [initialset]
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    weightdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = Set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
          weightdictionary[edge.label] = edge.weight
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = findlocalreachable(targetstateset, localevents)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            partitions[newstate] = targetstateset
            tovisit.append(targetstateset)
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event, weightdictionary[event])
##  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new, partitions
  
def subsetconstructionnotweighted(aut, localevents, depth):
##  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  aut_new = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  #aut_new.alphabet = aut_new.alphabet.difference_update(localevents);
  for event in localevents:
    aut_new.alphabet.remove(event)
  initialset = Set([aut.initial])
  initialset = findlocalreachable(initialset, localevents)
  initstate = aut_new.add_new_state(containsmarked(initialset),aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  numstates = 0
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    numstates += 1
    if (numstates % 100 == 0):
      print numstates
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = Set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = findlocalreachable(targetstateset, localevents)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() > aut.get_num_states()):
              return aut
          aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
##  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new
          

def get_automaton_copy(aut):
  aut_copy = weighted_structure.WeightedAutomaton(copy.copy(aut.alphabet), aut.collection)
  dictionary = {}
  for state in aut.get_states():
    newstate = aut_copy.add_new_state(state.marked, state.number)
    dictionary[state.number] = newstate
  for state in aut.get_states():
    for edge in state.get_outgoing():
      aut_copy.add_edge_data(dictionary[edge.pred.number], dictionary[edge.succ.number], edge.label, edge.weight)
  aut_copy.set_initial(dictionary[aut.initial.number])
  return aut_copy
  
def get_automaton_copy_not_weighted(aut):
  aut_copy = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  dictionary = {}
  for state in aut.get_states():
    newstate = aut_copy.add_new_state(state.marked, state.number)
    dictionary[state.number] = newstate
  for state in aut.get_states():
    for edge in state.get_outgoing():
      aut_copy.add_edge_data(dictionary[edge.pred.number], dictionary[edge.succ.number], edge.label)
  aut_copy.set_initial(dictionary[aut.initial.number])
  return aut_copy

def restrictpath(path):
  state = path.initial
  while not state.marked:
    first = True
    edgestoremove = []
    for edge in list(state.get_outgoing()):
      if (first):
        state = edge.succ
        first = False
      else:
        edgestoremove.append(edge)
    for edge in edgestoremove:
      path.remove_edge(edge)
  path.reduce(True, True)
  return path
  
def restrictpath_multi(path, non_prog_events):
  state = path.initial
  added = set()
  added.add(state)
  queue = [state]
  while len(queue) != 0:
    state = queue.pop()
    if state.marked == True:
      continue
    first = True
    edgestoremove = []
    edgetokeep = None
    for edge in state.get_outgoing():
      if edge.label in non_prog_events:
        if edge.succ not in added:
          queue.append(edge.succ)
          added.add(edge.succ)
        continue
      if edge.succ in added:
        first = False
        edgetokeep = edge
    for edge in state.get_outgoing():
      if edge.label in non_prog_events:
        if edge.succ not in added:
          queue.append(edge.succ)
          added.add(edge.succ)
        continue
      if (first):
        if edge.succ not in added:
          queue.append(edge.succ)
        first = False
      else:
        if not edgetokeep is edge:
          edgestoremove.append(edge)
    for edge in edgestoremove:
      path.remove_edge(edge)
  path.reduce(True, True)
  return path
  
def maketausequal(aut, alphabet, eventdata):
##  aut.save_as_dot("beforemakeequal.dot")
  dictionary = {}
  tausmadeequal = 0
  for event in aut.alphabet:
    if event in alphabet:
      continue
    if eventdata[event].matHat in dictionary:
      dictionary[eventdata[event].matHat].append(event)
      tausmadeequal += 1
    else:
      dictionary[eventdata[event].matHat] = [event]
  print "tausmadeequal:" + str(tausmadeequal)
  edgestoadd = []
  edgestoremove = []
  for state in aut.get_states():
    for edge in state.get_outgoing():
      if edge.label not in alphabet:
        edgestoremove.append(edge)
        tup = edge.pred, edge.succ, dictionary[eventdata[edge.label].matHat][0], edge.weight
        edgestoadd.append(tup)
  for edge in edgestoremove:
    aut.remove_edge(edge)
  for edge in edgestoadd:
    pred, succ, event, weight = edge
    aut.add_edge_data(pred, succ, event, weight)
##  aut.save_as_dot("aftermakeequal.dot")
  return aut

def project(path, alphabet):
  #note this assumes a single path automaton
  #print path
##  path.save_as_dot("project.dot")
  state = path.initial
  prevedge = None
  while True:
    edge = None
    for stedge in state.get_outgoing():
      edge = stedge
    #print edge
    if (edge != None):
      path.remove_edge(edge)
    if (edge == None or edge.label in alphabet):
      if (prevedge != None):
        path.add_edge_data(prevedge.pred, state, prevedge.label, prevedge.weight)
      else:
        path.set_initial(edge.pred)
      prevedge = edge
    if (edge == None):
      break
    else:
      state = edge.succ
  path.reduce(True, True)
##  path.save_as_dot("projectafter.dot")
  path.alphabet.intersection_update(alphabet)
  return path

def has_shared_events(aut, comp_list):
    for evt in aut.alphabet:
        for comp in comp_list:
            if aut is not comp:
                if evt in comp.alphabet:
                    return True
    return False


def eureka_state_collision(plant):
    removing_states = []
    for state_num, state in plant._states.iteritems():
        state_names = []
        for name in plant.state_names[state_num].split("-"):
            for name2 in name.split("_"):
                state_names.append(name2)
        if len(set(state_names)) != len(state_names):
            removing_states.append(state)
    for state in removing_states:
        if state is plant.initial:
            print "whoops, we're deleting the initial state, check your initial states"
        plant.remove_state(state)
    return plant

def convert_weighted_to_tick(aut, tick):
##  aut.save_as_dot("tick" + aut.name + "before.dot")
  new_aut = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  new_aut.alphabet.add(tick)
  dictionary = {}
  for state in aut.get_states():
    newstate = new_aut.add_new_state(state.marked, new_aut.get_num_states())
    dictionary[state] = newstate
  for state in aut.get_states():
    new_aut.add_edge_data(dictionary[state], dictionary[state], tick)
    for edge in state.get_outgoing():
      succstate = new_aut.add_new_state(False, new_aut.get_num_states())
      new_aut.add_edge_data(dictionary[edge.pred], succstate, edge.label)
      weight = edge.weight
      while weight > 1:
        nextstate = new_aut.add_new_state(False, new_aut.get_num_states())
        weight -= 1
        new_aut.add_edge_data(succstate, nextstate, tick)
        succstate = nextstate
      new_aut.add_edge_data(succstate, dictionary[edge.succ], tick)
  new_aut.set_initial(dictionary[aut.initial])
##  new_aut.save_as_dot("tick" + aut.name + "after.dot")
  return new_aut

def do_tau_abstraction(aut_list, selected_aut, eventdata, heap_len, evt_pairs):
    #local_alphabet = find_local_alphabet(aut_list, selected_aut, evt_pairs)
    local_alphabet = get_local_events(selected_aut, aut_list)
    
    # Find critical states
    critical_states, semi_critical_states = find_critical_states(selected_aut, local_alphabet)
    
    combinations = len(critical_states)*len(critical_states.union(semi_critical_states))
    #combinations = len(critical_states)*len(semi_critical_states)
    print combinations
    count = 0
    for end_state in critical_states:
        for start_state in semi_critical_states.union(critical_states):
            if combinations > 10000:
                count += 1
                if combinations < 100000 and count % -(-combinations/10) == 0:
                    common.print_line("Calculated tau transitions for %d%% of combinations" % (count*100/combinations))
                
                if combinations >= 100000 and count % -(-combinations/100) == 0:
                    common.print_line("Calculated tau transitions for %d%% of combinations" % (count*100/combinations))
            if start_state is not end_state: # We're not trying to create loops
               path = []
               # Find shortest path for each combination of critical states in each automaton
               #add_abstracted_tau(selected_aut,eventdata,start_state,end_state,path)
               # testing without this
               local_aut = create_local_automaton(selected_aut, local_alphabet, start_state, end_state)
               if local_aut is not None:
                   time_opt_local_aut = get_greedy_time_optimal_sup(local_aut, eventdata, heap_len)
                   path = find_single_tau_path(time_opt_local_aut, start_state)
                   if path is not None:
                       # If a path is found, determine if it's worthy to create a tau transition
                       find_local_paths(selected_aut, eventdata, path, critical_states.union(semi_critical_states))
    
    # Remove all non-critical states and local transitions from each automaton
    non_critical_states = []
    for state in selected_aut.get_states():
        if state not in critical_states.union(semi_critical_states):
            non_critical_states.append(state)
    for state in non_critical_states:
        selected_aut.remove_state(state)
    removable_edges = []
    for state in selected_aut.get_states():
        for edge in state.get_outgoing():
            if edge.label in local_alphabet:
                removable_edges.append(edge)
    for edge in removable_edges:
        selected_aut.remove_edge(edge)
    selected_aut.alphabet.difference_update(local_alphabet)
    
#def replace_tau(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
#  djikstratime = 0
#  dictionary = {}
#  edgestoremove = []
#  edgestoadd = []
#  tauedgestoadd = []
##  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
#  usedentrance = {}
#  for state in state_to_stateset:
#    if state != current_aut.initial:
#      usedentrance[state] = set()
#    else:
#      usedentrance[state] = set([previousaut.initial])
#  statestocheck = []
#  cummat = 0
#  visited = set()
#  #for state in current_aut.get_states():
#  statestocheck.append(current_aut.initial)
#  visited.add(current_aut.initial)
#  while len(statestocheck) != 0:
#    state = statestocheck.pop()
#    print "bigstate: " + str(state)
#    print ""
#    for edge in state.get_outgoing():      
#      source_partition = usedentrance[state]
#      target_partition = state_to_stateset[edge.succ]
#      print "source partition: " + str(source_partition)
#      print "target partition: " + str(target_partition) 
#      print "event: " + str(edge.label)
#      target_set = Set()
#      minmatrix, minused, minceil = (None, None, 999999999)
#      maxmatrix, maxused, maxceil = (None, None, 0)
#      for target in target_partition:
#        target_set.add(target)
#      entranceset = set()
#      for pred in source_partition:
#        if pred not in dictionary:
#          dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
#        djikstradistances, reachablecritical, cummat = dictionary[pred]
#        for succ in djikstradistances:
#          #if succ == pred: 
#            #continue
#          for succedge in succ.get_outgoing(edge.label):
#            if succedge.succ in target_partition:
#              matrix, dataused = djikstradistances[succ]
#              print matrix
#              print dataused
#              ceil = calc_ceil(matrix)
#              print ceil
#              print minceil
#              if (minceil > ceil):
#                minmatrix,minused, minceil  = (matrix, dataused, ceil)
#                entranceset = set()
#                entranceset.add(succedge.succ)
#                print "pred: " + str(pred) + " succ:" + str(succ) + " vec:" + str(minmatrix)
#              if (minceil == ceil):
#                entranceset.add(succedge.succ)
#      usedmatrix = minmatrix
#      usedused = minused
#      usedentrance[edge.succ] = usedentrance[edge.succ].union(entranceset)
#      if edge.succ not in visited:
#        visited.add(edge.succ)
#        statestocheck.append(edge.succ)
#      print "minceil: " + str(minceil)
#      if minceil != 0:
#        edgestoremove.append(edge)
#        newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
#        tauedgestoadd.append((state, newstate, usedused, usedmatrix))
#        edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
#  for edge in edgestoremove:
#    current_aut.remove_edge(edge)
#  for (pred, succ, used, matrix) in tauedgestoadd:
#    print "not used state: " + str(pred)
#    for i in range(len(used)):
#      if not used[i]:
#        matrix.data[i] = 0
#    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
#  for (pred, succ, event, weight) in edgestoadd:
#    current_aut.add_edge_data(pred, succ, event, weight)
###  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
#  return current_aut

def pruneunlikely(aut, eventdata, cliques, orig_alphabet):
  distancetoo = get_greedy_time_optimal_weights_vector_reversed(aut, eventdata, len(cliques))
  distancefrom = get_greedy_time_optimal_weights_vector(aut, eventdata, len(cliques))
  minceil = calc_ceil(distancefrom[aut.initial])
  for state in distancetoo:
    matrixtoo = distancetoo[state]
    matrixfrom = distancefrom[state]
    matrix = maxplus.newtimes_vec_vec(matrixtoo, matrixfrom)
    ceil = calc_ceil(matrix)
    #print minceil
    #print ceil
    if ceil > minceil +5:
      print "rem"
      for edge in list(state.get_incoming()):
        aut.remove_edge(edge)
    #ceil_current = calc_ceil(matrixfrom)
    
    #edgestoremove = []
    # for edge in state.get_outgoing():
      # if edge.label not in orig_alphabet:
        # matrixfrom = distancefrom[edge.succ]
        # matrixfrom = maxplus.reverse_times_vec_vec(eventdata[edge.label].matHat, matrixfrom)
        # ceil_target = calc_ceil(matrixfrom)
        # if ceil_target >= ceil_current + 15:
          # edgestoremove.append(edge)
    #for edge in edgestoremove:
      #aut.remove_edge(edge)
  aut.reduce(True, True)

def splitautomaton(current_aut, previousaut, state_to_stateset, eventdata, cliques, local_alphabet):
  statestoadd = {}
  statestocheck = []
  dictionary = {}
  cummat = 0
  for state in current_aut.get_states():
    statestoadd[state] = set()
    statestocheck.append(state)
  for state in statestocheck:#current_aut.get_states():
    #print "bigstate: " + str(state)
    #print ""
    for edge in state.get_outgoing():
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        #print "source partition: " + str(source_partition)
        #print "target partition: " + str(target_partition) 
        target_set = Set()
        heapminstate = []
        #minstateceil, minstate = None, None
        maxmatrix, maxused, maxceil = (None, None, 0)
        for target in target_partition:
          target_set.add(target)
        for pred in source_partition:
          haspredecessor = False
          for prededge in pred.get_incoming():
            if prededge.label not in local_alphabet:
              haspredecessor = True
              break
          if not haspredecessor:
            continue
          if pred not in dictionary:
            dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          minmatrix, minused, minceil = (None, None, 999999999)
          for succ in djikstradistances:
            if succ == pred: 
              continue
            for succedge in succ.get_outgoing(edge.label):
              if succedge.succ in target_partition:
                matrix, dataused = djikstradistances[succ]
                ceil = calc_ceil(matrix)
                if (minceil > ceil):
                  minmatrix,minused, minceil  = (matrix, dataused, ceil)
          if minmatrix != None:
            if maxmatrix == None:
              maxmatrix, maxused, maxceil = minmatrix, minused, minceil
            elif minceil >= maxceil:
              maxmatrix, maxused, maxceil = minmatrix, minused, minceil
            heapq.heappush(heapminstate, (minceil, pred))
        usedmatrix = maxmatrix
        usedused = maxused
        if usedmatrix != None:
          for i in range(5):
            if len(heapminstate) == 0:
              break
            minceil, minstate = heapq.heappop(heapminstate)
            if minceil != maxceil:
              statestoadd[state].add(minstate)
  for state in statestoadd:
    states = statestoadd[state]
    tuplist = []
    statestoadd[state] = tuplist
    for entrance in states:
      new_state = current_aut.add_new_state(state.marked, current_aut.get_num_states())
      tuplist.append(new_state)
      state_to_stateset[new_state] = set([entrance])
  for state in statestoadd:
    edgestoadd = []
    for edge in state.get_outgoing():
      for succ in statestoadd[edge.succ]:
        edgestoadd.append((state, succ, edge.label, edge.weight))
      for pred in statestoadd[state]:
        edgestoadd.append((pred, edge.succ, edge.label, edge.weight))
        for succ in statestoadd[edge.succ]:
          edgestoadd.append((pred, succ, edge.label, edge.weight))
    for pred, succ, evt, weight in edgestoadd:
      current_aut.add_edge_data(pred, succ, evt, weight)
  

def replace_tau2(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
  djikstratime = 0
  dictionary = {}
  edgestoremove = []
  edgestoadd = []
  tauedgestoadd = []
##  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
  usedentrance = {}
  for state in state_to_stateset:
    if state != current_aut.initial:
      usedentrance[state] = set()
    else:
      usedentrance[state] = set([previousaut.initial])
  statestocheck = []
  cummat = 0
  visited = set()
  #for state in current_aut.get_states():
  statestocheck.append(current_aut.initial)
  visited.add(current_aut.initial)
  while len(statestocheck) != 0:
    state = statestocheck.pop()
    print "bigstate: " + str(state)
    print ""
    for edge in state.get_outgoing():      
      source_partition = usedentrance[state]
      if len(usedentrance[edge.succ]) != 0:
        target_partition = usedentrance[edge.succ]
      else:
        target_partition = state_to_stateset[edge.succ]
      print "source partition: " + str(source_partition)
      print "target partition: " + str(target_partition) 
      print "event: " + str(edge.label)
      target_set = Set()
      minmatrix, minused, minceil = (None, None, 999999999)
      maxmatrix, maxused, maxceil = (None, None, 0)
      for target in target_partition:
        target_set.add(target)
      entranceset = set()
      for pred in source_partition:
        if pred not in dictionary:
          dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
        djikstradistances, reachablecritical, cummat = dictionary[pred]
        for mid in djikstradistances:
          #if succ == pred: 
            #continue
          for succedge in mid.get_outgoing(edge.label):
            #print "succedge: " + str(succedge)
            if succedge.succ not in dictionary:
              dictionary[succedge.succ] = heapsofpiecesdijkstras_vec(previousaut, succedge.succ, len(cliques), eventdata, local_alphabet, None, cummat)
            djikstradistances2, reachablecritical2, cummat2 = dictionary[succedge.succ]
            for succ in djikstradistances2:
              #print "succ: " + str(succ)
              if succ in target_set:
                matrixpred, predused = djikstradistances[mid]
                matrixsucc, succused = djikstradistances2[succ]
                matrix = matrixpred
                #matrix = maxplus.newtimes_vec_vec(matrix, eventdata[edge.label].matHat)
                matrix = maxplus.newtimes_vec_vec(matrix, matrixsucc)
                ceil = calc_ceil(matrix)
                if (minceil > ceil):
                  dataused = []
                  eventused = eventdata[edge.label].used
                  for i in range(len(predused)):
                    dataused.append(predused[i] or succused[i])
                  minmatrix, minused, minceil  = (matrix, dataused, ceil)
                  entranceset = set()
                  entranceset.add(succ)
                  print "pred: " + str(pred) + " succ:" + str(succ) + " vec:" + str(minmatrix)
                #if (minceil == ceil):
                  #entranceset.add(succedge.succ)
      usedmatrix = minmatrix
      usedused = minused
      usedentrance[edge.succ] = usedentrance[edge.succ].union(entranceset)
      if edge.succ not in visited:
        visited.add(edge.succ)
        statestocheck.append(edge.succ)
      print "minceil: " + str(minceil)
      if minceil != 0:
        edgestoremove.append(edge)
        newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
        tauedgestoadd.append((state, newstate, usedused, usedmatrix))
        edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
  for edge in edgestoremove:
    current_aut.remove_edge(edge)
  for (pred, succ, used, matrix) in tauedgestoadd:
    print "not used state: " + str(pred)
    for i in range(len(used)):
      if not used[i]:
        matrix.data[i] = 0
    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
  for (pred, succ, event, weight) in edgestoadd:
    current_aut.add_edge_data(pred, succ, event, weight)
##  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
  return current_aut
  
def replace_tau5(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
  djikstratime = 0
  dictionary = {}
  edgestoremove = []
  edgestoadd = []
  tauedgestoadd = []
##  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
  #current_aut, state_to_stateset = merge_and_update_stateset(current_aut, state_to_stateset)
  splitautomaton(current_aut, previousaut, state_to_stateset, eventdata, cliques, local_alphabet)
  statestocheck = []
  cummat = 0
  visited = set()
  #for state in current_aut.get_states():
  statestocheck.append(current_aut.initial)
  visited.add(current_aut.initial)
  while len(statestocheck) != 0:
    state = statestocheck.pop()
    for edge in state.get_outgoing():      
      source_partition = state_to_stateset[state]
      target_partition = state_to_stateset[edge.succ]
      target_set = Set()
      minmatrix, minused, minceil = (None, None, 999999999)
      maxmatrix, maxused, maxceil = (None, None, 0)
      for target in target_partition:
        target_set.add(target)
      for pred in source_partition:
        if pred not in dictionary:
          dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
        djikstradistances, reachablecritical, cummat = dictionary[pred]
        for mid in djikstradistances:
          for succedge in mid.get_outgoing(edge.label):
            #print "succedge: " + str(succedge)
            if succedge.succ not in dictionary:
              dictionary[succedge.succ] = heapsofpiecesdijkstras_vec(previousaut, succedge.succ, len(cliques), eventdata, local_alphabet, None, cummat)
            djikstradistances2, reachablecritical2, cummat2 = dictionary[succedge.succ]
            for succ in djikstradistances2:
              #print "succ: " + str(succ)
              if succ in target_set:
                matrixpred, predused = djikstradistances[mid]
                matrixsucc, succused = djikstradistances2[succ]
                matrix = matrixpred
                #matrix = maxplus.newtimes_vec_vec(matrix, eventdata[edge.label].matHat)
                matrix = maxplus.newtimes_vec_vec(matrix, matrixsucc)
                ceil = calc_ceil(matrix)
                if (minceil > ceil):
                  dataused = []
                  eventused = eventdata[edge.label].used
                  for i in range(len(predused)):
                    dataused.append(predused[i] or succused[i])
                  minmatrix, minused, minceil  = (matrix, dataused, ceil)
                #if (minceil == ceil):
                  #entranceset.add(succedge.succ)
      usedmatrix = minmatrix
      usedused = minused
      if edge.succ not in visited:
        visited.add(edge.succ)
        statestocheck.append(edge.succ)
      if usedmatrix == None:
        edgestoremove.append(edge)
      elif minceil != 0:
        edgestoremove.append(edge)
        newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
        tauedgestoadd.append((state, newstate, usedused, usedmatrix))
        edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
  for edge in edgestoremove:
    current_aut.remove_edge(edge)
  for (pred, succ, used, matrix) in tauedgestoadd:
    for i in range(len(used)):
      if not used[i]:
        matrix.data[i] = 0
    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
  for (pred, succ, event, weight) in edgestoadd:
    current_aut.add_edge_data(pred, succ, event, weight)
##  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
  return current_aut
  
def merge_and_update_stateset(aut, state_to_stateset):
  aut, partitions, tau = abstraction.abstraction_with_partitions(aut, aut.alphabet)
  new_state_to_stateset = {}
  for state in aut.get_states():
    part = partitions[state]
    new_set = set()
    new_state_to_stateset[state] = new_set
    for midstate in part:
      state_set = state_to_stateset[midstate]
      for finstate in state_set:
        new_set.add(finstate)
  return aut, new_state_to_stateset
  
def replace_tau3(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
  djikstratime = 0
  dictionary = {}
  edgestoremove = []
  edgestoadd = []
  tauedgestoadd = []
  current_aut, state_to_stateset = merge_and_update_stateset(current_aut, state_to_stateset)
  #splitautomaton(current_aut, previousaut, state_to_stateset, eventdata, cliques, local_alphabet)
  for state in current_aut.get_states():
    current_aut.state_names[state.number] = str(state.number)
  for state in previousaut.get_states():
    previousaut.state_names[state.number] = str(state.number)
  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
  previousaut.save_as_dot("reptaubefore" + str(depth) + "prev.dot")
  statestocheck = []
  cummat = 0
  for state in current_aut.get_states():
    statestocheck.append(state)
  for state in statestocheck:#current_aut.get_states():
    #print "bigstate: " + str(state)
    #print ""
    for edge in state.get_outgoing():
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        #print "source partition: " + str(source_partition)
        #print "target partition: " + str(target_partition) 
        target_set = Set()
        maxmatrix, maxused, maxceil = (None, None, None)
        for target in target_partition:
          target_set.add(target)
        for pred in source_partition:
          haspredecessor = False
          if pred == previousaut.initial:
            haspredecessor = True
          else:
            for prededge in pred.get_incoming():
              if prededge.label not in local_alphabet:
                haspredecessor = True
                break
          if not haspredecessor:
            continue
          if pred not in dictionary:
            dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          minmatrix, minused, minceil = (None, None, None)
          #print djikstradistances
          for succ in djikstradistances:
            for succedge in succ.get_outgoing(edge.label):
              if succedge.succ in target_partition:
                matrix, dataused = djikstradistances[succ]
                ceil = calc_ceil(matrix)
                if minceil == None or minceil > ceil:
                  minmatrix,minused, minceil  = (matrix, dataused, ceil)
          if minmatrix != None:
            if maxmatrix == None:
              maxmatrix, maxused, maxceil = minmatrix, minused, minceil
            elif minceil >= maxceil:
              maxmatrix, maxused, maxceil = minmatrix, minused, minceil
        usedmatrix = maxmatrix
        usedused = maxused
        #print usedmatrix
        if maxceil != 0 :
          edgestoremove.append(edge)
          if maxceil != None:
            newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
            tauedgestoadd.append((state, newstate, usedused, usedmatrix))
            edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
  for edge in edgestoremove:
    current_aut.remove_edge(edge)
  for (pred, succ, used, matrix) in tauedgestoadd:
    for i in range(len(used)):
      if not used[i]:
        matrix.data[i] = 0
    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
  for (pred, succ, event, weight) in edgestoadd:
    current_aut.add_edge_data(pred, succ, event, weight)
  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
  return current_aut
  
def replace_tau(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
  djikstratime = 0
  dictionary = {}
  edgestoremove = []
  edgestoadd = []
  tauedgestoadd = []
##  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
  statestocheck = []
  cummat = 0
  for state in current_aut.get_states():
    statestocheck.append(state)
  for state in statestocheck:#current_aut.get_states():
    #print "bigstate: " + str(state)
    #print ""
    for edge in state.get_outgoing():
      if edge.label == tau:
        edgestoremove.append(edge)
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        minmatrix, minused, minceil = (None, None, 999999999)
        maxmatrix, maxused, maxceil = (None, None, 0)
        for pred in source_partition:
          if pred not in dictionary:
            djikstratime -= time()
            dictionary[pred] = heapsofpiecesdijkstras(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
            djikstratime += time()
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          for succ in target_partition:
            if succ in djikstradistances:
              matrix, dataused = djikstradistances[succ]
              ceil = calc_ceil(matrix)
              if (minceil > ceil):
                minmatrix,minused, minceil  = (matrix, dataused, ceil)
              if (maxceil < ceil):
                maxmatrix, maxused, maxceil = (matrix, dataused, ceil)
        tauedgestoadd.append((state, edge.succ, maxused, maxmatrix))
      else:
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        #print "source partition: " + str(source_partition)
        #print "target partition: " + str(target_partition) 
        target_set = Set()
        maxmatrix, maxused, maxceil = (None, None, 0)
        for target in target_partition:
          target_set.add(target)
        for pred in source_partition:
          haspredecessor = False
          for prededge in pred.get_incoming():
            if prededge.label not in local_alphabet:
              haspredecessor = True
              break
          if pred not in dictionary:
            dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          minmatrix, minused, minceil = (None, None, 999999999)
          for succ in djikstradistances:
            if succ == pred: 
              continue
            for succedge in succ.get_outgoing(edge.label):
              if succedge.succ in target_partition:
                matrix, dataused = djikstradistances[succ]
                ceil = calc_ceil(matrix)
                if (minceil > ceil):
                  minmatrix,minused, minceil  = (matrix, dataused, ceil)
          if minmatrix != None:
            if maxmatrix == None:
              maxmatrix, maxused, maxceil = minmatrix, minused, minceil
            elif minceil >= maxceil:
              maxmatrix, maxused, maxceil = minmatrix, minused, minceil
        usedmatrix = maxmatrix
        usedused = maxused
        if usedmatrix != None:
          #print usedmatrix
          edgestoremove.append(edge)
          newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
          tauedgestoadd.append((state, newstate, usedused, usedmatrix))
          edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
  for edge in edgestoremove:
    current_aut.remove_edge(edge)
  for (pred, succ, used, matrix) in tauedgestoadd:
    for i in range(len(used)):
      if not used[i]:
        matrix.data[i] = 0
    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
  for (pred, succ, event, weight) in edgestoadd:
    current_aut.add_edge_data(pred, succ, event, weight)
##  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
  return current_aut
  
def replace_tau4(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
  djikstratime = 0
  dictionary = {}
  edgestoremove = []
  edgestoadd = []
  tauedgestoadd = []
##  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
  statestocheck = []
  cummat = 0
  for state in current_aut.get_states():
    statestocheck.append(state)
  for state in statestocheck:#current_aut.get_states():
    #print "bigstate: " + str(state)
    #print ""
    for edge in state.get_outgoing():
      if edge.label == tau:
        edgestoremove.append(edge)
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        minmatrix, minused, minceil = (None, None, 999999999)
        maxmatrix, maxused, maxceil = (None, None, 0)
        for pred in source_partition:
          if pred not in dictionary:
            djikstratime -= time()
            dictionary[pred] = heapsofpiecesdijkstras(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
            djikstratime += time()
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          for succ in target_partition:
            if succ in djikstradistances:
              matrix, dataused = djikstradistances[succ]
              ceil = calc_ceil(matrix)
              if (minceil > ceil):
                minmatrix,minused, minceil  = (matrix, dataused, ceil)
              if (maxceil < ceil):
                maxmatrix, maxused, maxceil = (matrix, dataused, ceil)
        tauedgestoadd.append((state, edge.succ, maxused, maxmatrix))
      else:
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        #print "source partition: " + str(source_partition)
        #print "target partition: " + str(target_partition) 
        target_set = Set()
        maxmatrix, maxused, maxceil = (None, None, 0)
        minmatrix, minused, minceil = (None, None, 999999999)
        for target in target_partition:
          target_set.add(target)
        for pred in source_partition:
          haspredecessor = False
          for prededge in pred.get_incoming():
            if prededge.label not in local_alphabet:
              haspredecessor = True
              break
          if pred not in dictionary:
            dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          for succ in djikstradistances:
            if succ == pred: 
              continue
            for succedge in succ.get_outgoing(edge.label):
              if succedge.succ in target_partition:
                matrix, dataused = djikstradistances[succ]
                ceil = calc_ceil(matrix)
                if (minceil > ceil):
                  minmatrix,minused, minceil  = (matrix, dataused, ceil)
                if maxmatrix == None or ceil > maxceil:
                  maxmatrix, maxused, maxceil = (matrix, dataused, ceil)
        if maxceil != 0:
          usedmatrix = diff_matrix(maxmatrix, minmatrix, 0)
          usedused = maxused
          #print usedmatrix
          edgestoremove.append(edge)
          newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
          tauedgestoadd.append((state, newstate, usedused, usedmatrix))
          edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
  for edge in edgestoremove:
    current_aut.remove_edge(edge)
  for (pred, succ, used, matrix) in tauedgestoadd:
    for i in range(len(used)):
      if not used[i]:
        matrix.data[i] = 0
    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
  for (pred, succ, event, weight) in edgestoadd:
    current_aut.add_edge_data(pred, succ, event, weight)
##  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
  return current_aut
  
def replace_tau6(current_aut, previousaut, state_to_stateset, tau, eventdata, cliques, local_alphabet,depth):
  djikstratime = 0
  dictionary = {}
  edgestoremove = []
  edgestoadd = []
  tauedgestoadd = []
  current_aut.save_as_dot("reptaubefore" + str(depth) + ".dot")
  previousaut.save_as_dot("reptaubefore" + str(depth) + "prev.dot")
  current_aut, state_to_stateset = merge_and_update_stateset(current_aut, state_to_stateset)
  localused = None
  for event in local_alphabet:
    used = eventdata[event].used
    if localused == None:
      localused = list(used)
    else:
      for i in range(len(used)):
        localused[i] = used[i] or localused[i]
  statestocheck = []
  cummat = 0
  for state in current_aut.get_states():
    statestocheck.append(state)
  for state in statestocheck:#current_aut.get_states():
    #print "bigstate: " + str(state)
    #print ""
    for edge in state.get_outgoing():
        source_partition = state_to_stateset[state]
        target_partition = state_to_stateset[edge.succ]
        #print "source partition: " + str(source_partition)
        #print "target partition: " + str(target_partition) 
        target_set = Set()
        maxmatrix, maxused, maxceil = (None, None, 0)
        minmatrix, minused, minceil = (None, None, 999999999)
        for target in target_partition:
          target_set.add(target)
        for pred in source_partition:
          haspredecessor = previousaut.initial == pred
          if not haspredecessor:
            for prededge in pred.get_incoming():
              if prededge.label not in local_alphabet:
                haspredecessor = True
                break
          if not haspredecessor:
            continue
          minmaxmatrix,minmaxused, minmaxceil = (None, None, 999999999)
          if pred not in dictionary:
            dictionary[pred] = heapsofpiecesdijkstras_vec(previousaut, pred, len(cliques), eventdata, local_alphabet, None, cummat)
          djikstradistances, reachablecritical, cummat = dictionary[pred]
          for succ in djikstradistances:
            if succ == pred: 
              continue
            for succedge in succ.get_outgoing(edge.label):
              if succedge.succ in target_partition:
                matrix, dataused = djikstradistances[succ]
                ceil = calc_ceil(matrix)
                if (minceil > ceil):
                  minmatrix,minused, minceil  = (matrix, dataused, ceil)
                if minmaxceil == None or minmaxceil > ceil:
                  minmaxmatrix,minmaxused, minmaxceil  = (matrix, dataused, ceil)
          if minmaxmatrix != None:
            if maxmatrix == None:
              maxmatrix, maxused, maxceil = minmaxmatrix, minmaxused, minmaxceil
            elif minmaxceil >= maxceil:
              maxmatrix, maxused, maxceil = minmaxmatrix, minmaxused, minmaxceil
        if maxceil != 0:
          #if (depth > 100001):
          #  usedmatrix = diff_matrix(maxmatrix, minmatrix, 1)
          #else:
          #  usedmatrix = diff_matrix(maxmatrix, minmatrix, 0.28)
          usedmatrix = diff_matrix(maxmatrix, minmatrix, .25)
          #usedused = maxused
          usedused = localused
          #print usedmatrix
          edgestoremove.append(edge)
          newstate = current_aut.add_new_state(state.marked, current_aut.get_num_states())
          tauedgestoadd.append((state, newstate, usedused, usedmatrix))
          edgestoadd.append((newstate, edge.succ, edge.label, edge.weight))
  for edge in edgestoremove:
    current_aut.remove_edge(edge)
  for (pred, succ, used, matrix) in tauedgestoadd:
    for i in range(len(used)):
      if not used[i]:
        matrix.data[i] = 0
    add_tau_transition(current_aut, eventdata, pred, succ, used, matrix, depth)
  for (pred, succ, event, weight) in edgestoadd:
    current_aut.add_edge_data(pred, succ, event, weight)
  current_aut.save_as_dot("reptauafter" + str(depth) + ".dot")
  return current_aut
        
def diff_matrix(max_matrix, min_matrix, percent):
  vec = []
  min_matrix = maxplus.Vector(list(min_matrix.data))
  #for i in range(len(max_matrix.data)):
   # min_matrix.data[i] = 0
  for i in range(len(max_matrix.data)):
    #print str(max_matrix.data[i]) + "," + str(min_matrix.data[i])
    diff = max_matrix.data[i] - min_matrix.data[i]
    diff = diff * percent
    diff += min_matrix.data[i]
    vec.append(diff)
  return maxplus.Vector(vec)
    
def do_tau_abstraction2(aut_list, selected_aut, eventdata, heap_len, evt_pairs, depth):
##    selected_aut.save_as_dot("tau_abstract_before"+ str(depth) + ".dot")
    #local_alphabet = find_local_alphabet(aut_list, selected_aut, evt_pairs)
    local_alphabet = get_local_events(selected_aut, aut_list)
    starttime = time()
    djikstratime = 0
    addtautransitiontime = 0 
    cummat = 0
    cacheused = 0
    cache = {}
    # Find critical states
    critical_states, semi_critical_states = find_critical_states2(selected_aut, local_alphabet)
    
    combinations = len(critical_states)*len(critical_states.union(semi_critical_states))
    #combinations = len(critical_states)*len(semi_critical_states)
    print combinations
    count = 0 
    transitionstoadd = []
    for start_state in semi_critical_states:
    #for start_state in semi_critical_states.union(critical_states):
      count += 1
      if count %100 == 0:
        print "tottime: " + str(time() - starttime)
        print djikstratime
        print cummat
        print count
      djikstratime -= time()
      djikstradistances,reachablecritical,cummat = heapsofpiecesdijkstras_vec(selected_aut, start_state, heap_len, eventdata, local_alphabet,critical_states, cummat)
      djikstratime += time()
      for end_state in reachablecritical:
        if end_state not in djikstradistances or end_state == start_state:
          continue
        matrix, dataused = djikstradistances[end_state]
        transitionstoadd.append((start_state, end_state, dataused, matrix))
    # Remove all non-critical states and local transitions from each automaton
    non_critical_states = []
    for start_state, end_state, dataused, matrix in transitionstoadd:
      #print dataused
      #print matrix.data
      for i in range(len(dataused)):
        if not dataused[i]:
          matrix.data[i] = 0
      #print matrix.data
      add_tau_transition(selected_aut, eventdata, start_state, end_state, dataused, matrix, depth)
    for state in selected_aut.get_states():
        if state not in critical_states.union(semi_critical_states):
            non_critical_states.append(state)
    for state in non_critical_states:
        selected_aut.remove_state(state)
    removable_edges = []
    for state in selected_aut.get_states():
        for edge in state.get_outgoing():
            if edge.label in local_alphabet:
                removable_edges.append(edge)
    for edge in removable_edges:
        selected_aut.remove_edge(edge)
    selected_aut.alphabet.difference_update(local_alphabet)
##    selected_aut.save_as_dot("tau_abstract_after"+ str(depth) + ".dot")
    
def do_tau_abstraction3(aut_list, selected_aut, eventdata, heap_len, evt_pairs, depth):
##    selected_aut.save_as_dot("tau_abstract_before"+ str(depth) + ".dot")
    #local_alphabet = find_local_alphabet(aut_list, selected_aut, evt_pairs)
    local_alphabet = get_local_events(selected_aut, aut_list)
    starttime = time()
    djikstratime = 0
    addtautransitiontime = 0 
    cummat = 0
    cacheused = 0
    cache = {}
    # Find critical states
    critical_states, semi_critical_states = find_critical_states2(selected_aut, local_alphabet)
    currtime = -time()
    distances = matrix_shortest_path(selected_aut, eventdata, heap_len, local_alphabet)
    currtime += time()
    print "matrix calc took: " + str(currtime)
    #combinations = len(critical_states)*len(critical_states.union(semi_critical_states))
    #combinations = len(critical_states)*len(semi_critical_states)
    #print combinations
    count = 0 
    transitionstoadd = []
    for start_state in semi_critical_states:
    #for start_state in semi_critical_states.union(critical_states):
      if start_state not in distances:
        continue
      statedistances = distances[start_state]
      for end_state in critical_states:
        if end_state == start_state or end_state not in statedistances:
          continue
        matrix, dataused = statedistances[end_state]
        transitionstoadd.append((start_state, end_state, dataused, matrix))
    # Remove all non-critical states and local transitions from each automaton
    for start_state, end_state, dataused, matrix in transitionstoadd:
      add_tau_transition(selected_aut, eventdata, start_state, end_state, dataused, matrix, depth)
    non_critical_states = []
    for state in selected_aut.get_states():
        if state not in critical_states.union(semi_critical_states):
            non_critical_states.append(state)
    for state in non_critical_states:
        selected_aut.remove_state(state)
    removable_edges = []
    for state in selected_aut.get_states():
        for edge in state.get_outgoing():
            if edge.label in local_alphabet:
                removable_edges.append(edge)
    for edge in removable_edges:
        selected_aut.remove_edge(edge)
    selected_aut.alphabet.difference_update(local_alphabet)
##    selected_aut.save_as_dot("tau_abstract_after"+ str(depth) + ".dot")
    
def orarray(arr1, arr2):
  newarr = []
  for i in range(len(arr1)):
    newarr.append(arr1[i] or arr2[i])
  return newarr
  
def calc_ceil(vec):
  if vec == None:
    return 0
  ceil = maxplus.EPSILON
  for val in vec.data:
    ceil = maxplus.maximum(ceil, val)
  return ceil
    
def matrix_shortest_path(aut, eventdata, heap_len, local_alphabet):
  #matrix = [[None for y in xrange(aut.get_num_states())] for x in xrange(aut.get_num_states())]
  matrix = {}
  zerorow = maxplus.make_rowmat(0, heap_len)
  allunesed = [False for x in xrange(heap_len)]
  changed = True
  count = 0
  for state in aut.get_states():
    matrix[state.number] = {}
    matrix[state.number][state.number] = (0, zerorow, allunesed)
    for edge in state.get_outgoing():
      if edge.succ == state or edge.label not in local_alphabet:
        continue
      if state.number not in matrix or edge.succ.number not in matrix[state.number]:
        matrix[state.number][edge.succ.number] = (calc_ceil(eventdata[edge.label].matHat), eventdata[edge.label].matHat, eventdata[edge.label].used)
      else:
        ceil, vect = matrix[state.number][edge.succ.number]
        newceil = calc_ceil(eventdata[edge.label].matHat)
        if ceil > newceil:
          matrix[state.number][edge.succ.number] = (newceil, eventdata[edge.label].matHat, eventdata[edge.label].used)
  while changed:
    print count
    count += 1
    newmatrix = {}
    for x in matrix:
      newmatrix[x] = {}
      for y in matrix[x]:
        newmatrix[x][y] = matrix[x][y]
    changed = False
    for state in aut.get_states():
      for edge in state.get_outgoing():
        if edge.succ == state or edge.label not in local_alphabet:
          continue
        for z in matrix[edge.succ.number]:
          if z == state.number or z == edge.succ.number:
            continue
          else:
            throw, succzvec, succzused = matrix[edge.succ.number][z]
            newvec = maxplus.newtimes_vec_vec(eventdata[edge.label].matHat, succzvec)
            newceil = calc_ceil(newvec)
            if z not in newmatrix[state.number]:
              newmatrix[state.number][z] = (newceil, newvec, orarray(eventdata[edge.label].used, succzused))
              changed = True
            else:
              ceil, vec, throw = newmatrix[state.number][z]
              if ceil > newceil:
                newmatrix[state.number][z] = (newceil, newvec, orarray(eventdata[edge.label].used, succzused))
                changed = True
    matrix = newmatrix
  distances = {}
  for x in matrix:
    distances[aut.get_state(x)] = {}
    for y in matrix[x]:
      throw, vec, used = matrix[x][y]
      distances[aut.get_state(x)][aut.get_state(y)] = (vec, used)
  return distances

def find_local_alphabet(aut_list, selected_aut, evt_pairs):
    # Determining total used alphabet for each automaton (automaton alphabet may be bigger than the total used alphabet after reduction)
    total_alphabet = {}
    if True: # If for some reason you want to use the entire (possibly too big) automaton alphabet set this to False
        for aut in aut_list:
            total_alphabet[aut] = set()
            for state in aut.get_states():
                for edge in state.get_outgoing():
                    total_alphabet[aut].add(edge.label)
    else:
        for aut in aut_list:
            total_alphabet[aut] = aut.alphabet
    # Create set of all events in mutual exclusion pairs
    # Only adding events from relevant mutual exclusion pairs (some sets may be unused after automaton reduction)
    mut_ex_evt_list = set()
    if True: # If for some reason you want to use all (possibly containing irrelevant events) pairs, set this to False
        for pair in evt_pairs:
            if searchDict(total_alphabet,pair[0],None) is not None:
                if searchDict(total_alphabet,pair[1],searchDict(total_alphabet,pair[0],None)) is not None:
                    mut_ex_evt_list.add(pair[0])
                    mut_ex_evt_list.add(pair[1])
    else:
        for pair in evt_pairs:
            for evt in pair:
                mut_ex_evt_list.add(evt)
        
    
    # Determining local alphabet for each automaton
    local_alphabet = set()
    for evt in total_alphabet[selected_aut]:
        if evt in mut_ex_evt_list:
            continue
        evt_is_local = True
        for comp in aut_list:
            if comp is not selected_aut:
                if evt in total_alphabet[comp]:
                    evt_is_local = False
                    break
        if evt_is_local:
            local_alphabet.add(evt)
    return local_alphabet


def searchDict(dict, searchFor, exeptItem):
    for item in dict:
        if item is not exeptItem:
            if searchFor in dict[item]:
                return item
    return None

def find_local_paths(aut, eventdata, path, critical_states):
    local_evt_path = []
    new_path = True
    for edge in path:
        if new_path:
            start_state = edge.pred
            new_path = False
        local_evt_path.append(edge.label)
        if edge.succ in critical_states:
            end_state = edge.succ
            add_abstracted_tau_paths(aut, eventdata, start_state, end_state, local_evt_path)
            local_evt_path = []
            new_path = True

def add_abstracted_tau(aut, eventdata, start_state, end_state, evt_path):
    new_tau_evt_name = "tau" + aut.name
    for evt in evt_path:
        if evt.name.find("tau") == 0:
            new_tau_evt_name = new_tau_evt_name + "-(" + evt.name + ")"
        else:
            new_tau_evt_name = new_tau_evt_name + "-" + evt.name
    new_tau_evt = aut.collection.make_event(new_tau_evt_name, True, True, False)
    if not new_tau_evt in aut.alphabet:
        aut.alphabet.add(new_tau_evt)
    aut.add_edge_data(start_state, end_state, new_tau_evt, 1)
    # fake init of ExtendedEventData
    tau_evt_data = taskresource.ExtendedEventData(new_tau_evt, 100, set([frozenset(aut.alphabet)]))
    # setting of actual resources and Matrix
    tau_evt_data.used = []
    for i in range(len(eventdata[next(iter(eventdata))].used)):
        tau_evt_data.used.append(False)
        for j in range(len(evt_path)):
            if eventdata[evt_path[j]].used[i] == True:
                tau_evt_data.used[i] = True
                break
    tau_evt_data.matHat = maxplus.make_unit_matrix(len(eventdata[next(iter(eventdata))].used))
    for i in range(0, len(evt_path)):
        tau_evt_data.matHat = maxplus.otimes_mat_mat(tau_evt_data.matHat,eventdata[evt_path[i]].matHat)
    for i in range(len(tau_evt_data.matHat.data)):
        for j in range(len(tau_evt_data.matHat.data[i])):
            tau_evt_data.duration = maxplus.maximum(tau_evt_data.duration, tau_evt_data.matHat.data[i][j])
    eventdata[new_tau_evt] = tau_evt_data
    
class TauEventData(taskresource.ExtendedEventData):
    def __init__(self, event):
        """
        Constructor.

        @param event: Event.
        @type  event: L{Event}

        @param duration: Duration of the use.
        @type  duration: C{int} or C{float}

        @param resources: Available resources (alphabets).
        @type  resources: C{list} of C{set} of L{Event}
        """
        self.event = event
        self.duration = None
        self.used = None

        self.matHat = None
    
def add_tau_transition(aut, eventdata, start_state, end_state, dataused, matrix, depth):
    new_tau_evt_name = "tau" + str(start_state) + ":" + str(end_state) + ":" + str(depth) + ":" + str(matrix)
    
    new_tau_evt = aut.collection.make_event(new_tau_evt_name, True, True, False)
    if not new_tau_evt in aut.alphabet:
        aut.alphabet.add(new_tau_evt)
    aut.add_edge_data(start_state, end_state, new_tau_evt, 1)
    # fake init of ExtendedEventData
    tau_evt_data = TauEventData(new_tau_evt)
    #tau_evt_data = taskresource.ExtendedEventData(new_tau_evt, 100, set([frozenset(aut.alphabet)]))
    # setting of actual resources and Matrix
    tau_evt_data.used = dataused
    tau_evt_data.matHat = matrix
    #for i in range(len(tau_evt_data.matHat.data)):
        #for j in range(len(tau_evt_data.matHat.data[i])):
            #tau_evt_data.duration = maxplus.maximum(tau_evt_data.duration, tau_evt_data.matHat.data[i][j])
    for val in tau_evt_data.matHat.data:
      tau_evt_data.duration = maxplus.maximum(tau_evt_data.duration, val)
    eventdata[new_tau_evt] = tau_evt_data

def add_abstracted_tau_paths(aut, eventdata, start_state, end_state, evt_path):
    new_tau_evt_name = "tau"
    for evt in evt_path:
        if evt.name.find("tau") == 0:
            new_tau_evt_name = new_tau_evt_name + "-(" + evt.name + ")"
        else:
            new_tau_evt_name = new_tau_evt_name + "-" + evt.name
    new_tau_evt = aut.collection.make_event(new_tau_evt_name, True, True, False)
    if not new_tau_evt in aut.alphabet:
        aut.alphabet.add(new_tau_evt)
    aut.add_edge_data(start_state, end_state, new_tau_evt, 1)
    # fake init of ExtendedEventData
    tau_evt_data = taskresource.ExtendedEventData(new_tau_evt, 100, set([frozenset(aut.alphabet)]))
    # setting of actual resources and Matrix
    tau_evt_data.used = []
    for i in range(len(eventdata[evt_path[0]].used)):
        tau_evt_data.used.append(False)
        for j in range(len(evt_path)):
            if eventdata[evt_path[j]].used[i] == True:
                tau_evt_data.used[i] = True
                break
    tau_evt_data.matHat = eventdata[evt_path[0]].matHat
    for i in range(1, len(evt_path)):
        tau_evt_data.matHat = maxplus.otimes_mat_mat(tau_evt_data.matHat,eventdata[evt_path[i]].matHat)
    for i in range(len(tau_evt_data.matHat.data)):
        for j in range(len(tau_evt_data.matHat.data[i])):
            tau_evt_data.duration = maxplus.maximum(tau_evt_data.duration, tau_evt_data.matHat.data[i][j])
    eventdata[new_tau_evt] = tau_evt_data
    
def heapsofpiecesdijkstras(aut, start_state, heap_len, eventdata, local_alphabet, critical_states, cummat):
  if (critical_states == None):
    critical_states = Set()
  distances = {}
  matrix = None
  visited = Set()
  queue = []
  used = []
  reachablecritical = []
  for i in range(heap_len):
    used.append(False)
  tup = (0, 0, matrix, used, start_state)
  cummat -= time() 
  heapq.heappush(queue, tup)
  cummat += time()
  number = 1
  while len(queue) != 0:
    
    ceiling, throwaway, matrix, used, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = (matrix, used)
    if state in critical_states and state != start_state:
      reachablecritical.append(state)
      #continue
    for edge in state.get_outgoing():
      
      if edge.succ in visited or edge.label not in local_alphabet:
        continue
      if (matrix == None):
        newmatrix = eventdata[edge.label].matHat
      else:
        newmatrix = maxplus.otimes_mat_mat(matrix,eventdata[edge.label].matHat)
      newused = []
      cummat -= time()
      for i in range(len(eventdata[edge.label].used)):
        newused.append(used[i] or eventdata[edge.label].used[i])
      cummat += time()
      newceil = maxplus.EPSILON
      for val in newmatrix.data:
        newceil = maxplus.maximum(newceil, val)
      #for i in range(len(newmatrix.data)):
        #for j in range(len(newmatrix.data[i])):
            #newceil = maxplus.maximum(newceil, newmatrix.data[i][j])
      tup = (newceil, number, newmatrix, newused, edge.succ)
      number += 1
      heapq.heappush(queue, tup)
      
  return distances, reachablecritical, cummat
  
def heapsofpiecesdijkstras_prog_reverse(aut, heap_len, eventdata, non_prog_events):
  print "reverse"
  distances = {}
  outgoing = {}
  matrix = None
  visited = Set()
  queue = []
  #tup = (0, False, 0, matrix, start_state, None)
  #heapq.heappush(queue, tup)
  number = 1
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
    if state.marked:
      tup = (0, False, 0, matrix, state, None)
      heapq.heappush(queue, tup)
##  aut.save_as_dot("djikbefore.dot")
  while len(queue) != 0:
    ceiling, throwaway1, throwaway2, matrix, state, edge = heapq.heappop(queue)
    if (state in visited):
      assert(edge != None)
      if edge.label not in non_prog_events and state not in distances:
        print "adding edge not otherwise added"
        distances[state] = ceiling
        outgoing[state].append(edge)
      if ceiling <= distances[state] or edge.label in non_prog_events:
        print "edge:" + str(edge)
        print "ceil: " + str(ceiling)
        print "distceil: " + str(distances[state])
        outgoing[state].append(edge)
      continue
    visited.add(state)
    if edge == None or edge.label not in non_prog_events:
      distances[state] = ceiling
    outgoing[state] = [edge]
    for edge in state.get_incoming():
      newmatrix = None
      if (matrix == None):
        newmatrix = eventdata[edge.label].matHat
      else:
        newmatrix = maxplus.otimes_mat_mat(eventdata[edge.label].matHat, matrix)
      newceil = maxplus.EPSILON
      for i in range(len(newmatrix.data)):
        for j in range(len(newmatrix.data[i])):
            newceil = maxplus.maximum(newceil, newmatrix.data[i][j])
      tup = (newceil, edge.label in non_prog_events, number, newmatrix, edge.pred, edge)
      number += 1
      print "added tup: " + str(tup)
      heapq.heappush(queue, tup)
  for state in aut.get_states():
    distance = distances[state] if state in distances else None
    #print "state: " + str(state.number) + ":" + str(distance)
  edgestoremove = []
  for state in aut.get_states():
    if state not in outgoing:
      edgestoremove += state.get_outgoing()
      continue
    for edge in state.get_outgoing():
      keepedge = False
      for keeping in outgoing[state]:
        if keeping is edge:
          keepedge = True
          break
      if not keepedge:
        edgestoremove.append(edge)
  print "toremove: " + str(len(edgestoremove))
  for edge in edgestoremove:
    aut.remove_edge(edge)
##  aut.save_as_dot("djikafter.dot")
  aut.reduce(True, True)
  return aut
  
def heapsofpiecespath(aut, heap_len, eventdata):
  distances = {}
  incoming = {}
  matrix = None
  visited = Set()
  queue = []
  used = []  
  start_state = aut.initial
  tup = (0, 0, matrix, start_state, None)
  heapq.heappush(queue, tup)
  number = 1
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
##  aut.save_as_dot("djikbefore.dot")
  while len(queue) != 0:
    ceiling, throwaway1, matrix, state, edge = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = ceiling
    incoming[state] = edge
    if state.marked:
      break
    for edge in state.get_outgoing():
      newmatrix = None
      if (matrix == None):
        newmatrix = eventdata[edge.label].matHat
      else:
        newmatrix = maxplus.newtimes_vec_vec(matrix,eventdata[edge.label].matHat)
      newceil = maxplus.EPSILON
      for i in range(len(newmatrix.data)):
        newceil = maxplus.maximum(newceil, newmatrix.data[i])
      tup = (newceil, number, newmatrix, edge.succ, edge)
      number += 1
      heapq.heappush(queue, tup)
  for state in aut.get_states():
    distance = distances[state] if state in distances else None
  edgestoremove = []
  for state in aut.get_states():
    for edge in state.get_incoming():
      if state in incoming and edge is incoming[state]:
        continue
      edgestoremove.append(edge)
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  return aut
  
def heapsofpiecesdijkstras_prog(aut, heap_len, eventdata, non_prog_events):
  distances = {}
  incoming = {}
  matrix = None
  visited = Set()
  queue = []
  used = []  
  start_state = aut.initial
  tup = (0, False, 0, matrix, start_state, None)
  heapq.heappush(queue, tup)
  number = 1
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
##  aut.save_as_dot("djikbefore.dot")
  while len(queue) != 0:
    ceiling, throwaway1, throwaway2, matrix, state, edge = heapq.heappop(queue)
    if (state in visited):
      assert(edge != None)
      if edge.label not in non_prog_events and state not in distances:
        print "adding edge not otherwise added"
        distances[state] = ceiling
        incoming[state].append(edge)
      if ceiling <= distances[state] or edge.label in non_prog_events:
        print "edge:" + str(edge)
        print "ceil: " + str(ceiling)
        print "distceil: " + str(distances[state])
        incoming[state].append(edge)
      continue
    visited.add(state)
    if edge == None or edge.label not in non_prog_events:
      distances[state] = ceiling
    incoming[state] = [edge]
    if state.marked:
      continue
    for edge in state.get_outgoing():
      newmatrix = None
      if (matrix == None):
        newmatrix = eventdata[edge.label].matHat
      else:
        newmatrix = maxplus.otimes_mat_mat(matrix,eventdata[edge.label].matHat)
      newceil = maxplus.EPSILON
      for i in range(len(newmatrix.data)):
        for j in range(len(newmatrix.data[i])):
            newceil = maxplus.maximum(newceil, newmatrix.data[i][j])
      tup = (newceil, edge.label in non_prog_events, number, newmatrix, edge.succ, edge)
      number += 1
      heapq.heappush(queue, tup)
  for state in aut.get_states():
    distance = distances[state] if state in distances else None
    print "state: " + str(state.number) + ":" + str(distance)
  edgestoremove = []
  for state in aut.get_states():
    for edge in state.get_incoming():
      keepedge = False
      for keeping in incoming[state]:
        if keeping is edge:
          keepedge = True
          break
      if not keepedge:
        edgestoremove.append(edge)
  print "toremove: " + str(len(edgestoremove))
  for edge in edgestoremove:
    aut.remove_edge(edge)
##  aut.save_as_dot("djikafter.dot")
  aut.reduce(True, True)
  return aut
  
def djikstraheapsfrom(aut, eventdata, heap_len):
  distances = {}
  vec = []
  for i in range(heap_len):
    vec.append(0)
  matrix = maxplus.Vector(vec)
  number = 0
  visited = Set()
  queue = []
  for state in aut.get_states():
    if state.marked:
      tup = (0, number, matrix, state)
      heapq.heappush(queue, tup)
      number += 1
  while len(queue) != 0:    
    ceiling, throwaway, matrix, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = matrix
    for edge in state.get_incoming():
      if edge.pred in visited:
        continue
      newmatrix = maxplus.reverse_times_vec_vec(eventdata[edge.label].matHat, matrix)
      newceil = calc_ceil(newmatrix)
      tup = (newceil, number, newmatrix, edge.pred)
      number += 1
      heapq.heappush(queue, tup)
      
  return distances
  
def djikstraheapstoo(aut, eventdata, heap_len):
  distances = {}
  vec = []
  for i in range(heap_len):
    vec.append(0)
  matrix = maxplus.Vector(vec)
  visited = Set()
  queue = []
  tup = (0, 0, matrix, aut.initial)
  heapq.heappush(queue, tup)
  number = 1
  while len(queue) != 0:    
    ceiling, throwaway, matrix, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = matrix
    for edge in state.get_outgoing():
      if edge.succ in visited:
        continue
      newmatrix = maxplus.newtimes_vec_vec(matrix,eventdata[edge.label].matHat)
      newceil = calc_ceil(newmatrix)
      tup = (newceil, number, newmatrix, edge.succ)
      number += 1
      heapq.heappush(queue, tup)
      
  return distances
  
def heapsofpiecesdijkstras_vec(aut, start_state, heap_len, eventdata, local_alphabet, critical_states, cummat):
  if (critical_states == None):
    critical_states = Set()
  distances = {}
  vec = []
  for i in range(heap_len):
    vec.append(0)
  matrix = maxplus.Vector(vec)
  visited = Set()
  queue = []
  used = []
  reachablecritical = []
  for i in range(heap_len):
    used.append(False)
  tup = (0, 0, matrix, used, start_state)
  cummat -= time() 
  heapq.heappush(queue, tup)
  cummat += time()
  number = 1
  while len(queue) != 0:
    
    ceiling, throwaway, matrix, used, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = (matrix, used)
    if state in critical_states and state != start_state:
      reachablecritical.append(state)
      #continue
    for edge in state.get_outgoing():
      
      if edge.succ in visited or edge.label not in local_alphabet:
        continue
      if (matrix == None):
        newmatrix = eventdata[edge.label].matHat
      else:
        newmatrix = maxplus.newtimes_vec_vec(matrix,eventdata[edge.label].matHat)
      newused = []
      cummat -= time()
      for i in range(len(eventdata[edge.label].used)):
        newused.append(used[i] or eventdata[edge.label].used[i])
      cummat += time()
      newceil = maxplus.EPSILON
      for val in newmatrix.data:
        newceil = maxplus.maximum(newceil, val)
      #for i in range(len(newmatrix.data)):
        #for j in range(len(newmatrix.data[i])):
            #newceil = maxplus.maximum(newceil, newmatrix.data[i][j])
      tup = (newceil, number, newmatrix, newused, edge.succ)
      number += 1
      heapq.heappush(queue, tup)
      
  return distances, reachablecritical, cummat

def dijkstras_path(aut, start_state, end_state):
    distances = {end_state: 0}
    last_added = [end_state]
    while len(last_added) > 0:
        new_added = []
        for state in last_added:
            for edge in state.get_incoming():
                if edge.pred not in distances:
                    distances[edge.pred] = edge.weight + distances[state]
                    new_added.append(edge.pred)
                elif distances[edge.pred] > edge.weight + distances[state]:
                    distances[edge.pred] = edge.weight + distances[state]
                    new_added.append(edge.pred)
        last_added = new_added
    if start_state in distances:
        path = []
        while start_state != end_state:
            for edge in start_state.get_outgoing():
                if edge.succ in distances and distances[edge.succ] == distances[start_state] - edge.weight:
                    path.append(edge.label)
                    start_state = edge.succ
                    break
        return path
    else:
        return None

def create_local_automaton(aut, local_alphabet, start_state, end_state):
    # creating temporary automaton
    temp_coll = collection.Collection()
    temp_automaton = weighted_structure.WeightedAutomaton(local_alphabet, temp_coll)
    for state in aut.get_states():
        ns = temp_automaton.add_new_state(state == end_state, state.number)
    for state in aut.get_states():
        for edge in state.get_outgoing():
            if edge.label in local_alphabet:
                new_edge = edge.copy(temp_automaton.get_state(edge.pred.number),
                                     temp_automaton.get_state(edge.succ.number))
                temp_automaton.add_edge(new_edge)

    temp_automaton.initial = temp_automaton.get_state(start_state.number)
    temp_automaton.reduce(True, True)
    if temp_automaton.get_num_states() == 0:
        return None
    else:
        return temp_automaton

def get_time_optimal_sup(aut, eventdata, heap_len, initial_weight = None):
    
    if initial_weight is None:
        marker_valfn = lambda state: 0
        weight_map = compute_weight.compute_state_weights(aut, marker_valfn)
        initial_weight = weight_map[aut.initial]
        if initial_weight is maxplus.INFINITE: # Infinite weight initial state.
            return None
        del weight_map
    # XXX Optimization: do heap computation while unfolding the automaton.
    unfolded = compute_weight.unfold_automaton_heaps(aut, initial_weight, eventdata, heap_len, False)
##    unfolded.save_as_dot("unfolded.dot")

    wsup3 = compute_weight.compute_weighted_supremal(aut, unfolded, False)
    aut.clear()
    unfolded.clear()
    del aut
    del unfolded

    unfolded2 = compute_weight.unfold_automaton_heaps(wsup3, initial_weight, eventdata, heap_len, False)
    wsup3.clear()
    del wsup3

    heap_info = taskresource.compute_heap_states(unfolded2, eventdata, heap_len)
    del eventdata

    # Convert unfolded2 to weighted unfolded automaton with 0 at the edges.
    wunfolded2 = conversion.add_weights(unfolded2, edge_weight = 0)
    wunfolded2_info = {}
    for state, wght in heap_info.iteritems():
        wunfolded2_info[wunfolded2.get_state(state.number)] = wght
    unfolded2.clear()
    del unfolded2
    # Compute weight of initial state.
    m_valfn = lambda s: taskresource.compute_heap_height(wunfolded2_info[s])
    weightmap = compute_weight.compute_state_weights(wunfolded2, m_valfn)
    m_valfn = None
    wunfolded2_info = None

    pruned = taskresource.prune_tree_automaton(wunfolded2, weightmap)
    # initial_weight = weightmap[wunfolded2.initial]
    del weightmap
    wunfolded2.clear()
    del wunfolded2
    
    return pruned

def get_greedy_time_optimal_weights(aut, eventdata, heap_len):
    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_correctly(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False)
    for key in weight_map:
      weight_map[key] = compute_weight.compute_norm(weight_map[key], 300)
    return weight_map

def get_greedy_time_optimal_sup(aut, eventdata, heap_len):

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_correctly(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,1,False)
    wsup = weighted_supervisor.reduce_automaton_greedy_correctly(aut, weight_map, eventdata,
                                                heap_len, 1)
    return wsup
    
def get_greedy_time_optimal_weights_vector(aut, eventdata, heap_len):
    col_zero_mat = maxplus.matrix_to_vector(maxplus.make_rowmat(0, heap_len))
    col_epsilon_mat =maxplus.matrix_to_vector(maxplus.make_rowmat(maxplus.EPSILON, heap_len))
    print "col_zero_mat" + str(col_zero_mat)
    print "col_epsioln_mat" + str(col_epsilon_mat)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_vector2(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False)
    return weight_map
    
def get_greedy_time_optimal_weights_vector_reversed(aut, eventdata, heap_len):
    col_zero_mat = maxplus.matrix_to_vector(maxplus.make_rowmat(0, heap_len))
    col_epsilon_mat =maxplus.matrix_to_vector(maxplus.make_rowmat(maxplus.EPSILON, heap_len))
    print "col_zero_mat" + str(col_zero_mat)
    print "col_epsioln_mat" + str(col_epsilon_mat)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_vector2_reverse(aut, marker_valfn,
                                                                             nonmarker_valfn,  
                                                                             heap_len, eventdata,300,False)
    return weight_map

    
def get_greedy_time_optimal_sup_progressive(aut, eventdata, heap_len, non_progressive_events):

    col_zero_mat = maxplus.matrix_to_vector(maxplus.make_rowmat(0, heap_len))
    col_epsilon_mat =maxplus.matrix_to_vector(maxplus.make_rowmat(maxplus.EPSILON, heap_len))
    print "col_zero_mat" + str(col_zero_mat)
    print "col_epsioln_mat" + str(col_epsilon_mat)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_progressive(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False, non_progressive_events)
    wsup = weighted_supervisor.reduce_automaton_greedy_progressive(aut, weight_map, eventdata,
                                                                   heap_len, 300, non_progressive_events)
    return wsup
    
def get_greedy_time_optimal_sup_progressive2(aut, eventdata, heap_len, non_progressive_events):

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_progressive2(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False, non_progressive_events)
    wsup = weighted_supervisor.reduce_automaton_greedy_progressive2(aut, weight_map, eventdata,
                                                                   heap_len, 300, non_progressive_events)
    return wsup
    
def get_greedy_time_optimal_sup_vector(aut, eventdata, heap_len):

    col_zero_mat = maxplus.matrix_to_vector(maxplus.make_rowmat(0, heap_len))
    col_epsilon_mat =maxplus.matrix_to_vector(maxplus.make_rowmat(maxplus.EPSILON, heap_len))
    print "col_zero_mat" + str(col_zero_mat)
    print "col_epsioln_mat" + str(col_epsilon_mat)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_vector2(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False)
    wsup = weighted_supervisor.reduce_automaton_greedy_vector(aut, weight_map, eventdata,
                                                heap_len, 300)
    return wsup

def get_greedy_time_optimal_sup_vector_keep_extra(aut, eventdata, heap_len):

    col_zero_mat = maxplus.matrix_to_vector(maxplus.make_rowmat(0, heap_len))
    col_epsilon_mat =maxplus.matrix_to_vector(maxplus.make_rowmat(maxplus.EPSILON, heap_len))
    print "col_zero_mat" + str(col_zero_mat)
    print "col_epsioln_mat" + str(col_epsilon_mat)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_vector2(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False)
    wsup = weighted_supervisor.reduce_automaton_greedy_vector_take_extra(aut, weight_map, eventdata,
                                                heap_len, 300,0)
    return wsup


def reduce_with_sup(comp, time_opt_sup):
    to_be_done = [(comp.initial, time_opt_sup.initial)]
    removable_edges = []
    visited = set()
    visited.add(comp.initial)
    while len(to_be_done) > 0:
        new_to_be_done = []
        for state, sup_state in to_be_done:
            for edge in state.get_outgoing():
                if edge.label in collect_outgoing_labels(sup_state):
                    if edge.succ not in visited:
                        visited.add(edge.succ)
                        for sup_edge in sup_state.get_outgoing():
                            if sup_edge.label == edge.label:
                                new_to_be_done.append((edge.succ, sup_edge.succ))
                                break
                else:
                    if edge not in removable_edges:
                        removable_edges.append(edge)
        to_be_done = new_to_be_done
    for edge in removable_edges:
        comp.remove_edge(edge)
    comp.reduce(True, True)
    
def minimal_conflict_path_automaton(selected_comp, comp_list, evt_pairs):
    # determine used events in automata
    total_alphabet = {}
    for comp in comp_list:
        total_alphabet[comp] = set()
        for state in comp.get_states():
            for edge in state.get_outgoing():
                total_alphabet[comp].add(edge.label)
    # Create conflict weighted automaton
    conflict_weighted = selected_comp.copy()
    for state in conflict_weighted.get_states():
        for edge in state.get_outgoing():
            confliction_weight = 0
            for pair in evt_pairs:
                if edge.label in pair:
                    label_index = pair.index(edge.label)
                    for comp in comp_list:
                        if comp is not selected_comp:
                            if pair[1 - label_index] in total_alphabet[comp]:
                                confliction_weight += 1
            for comp in comp_list: # This part is for the EPUCK format
                if comp is not selected_comp:
                    state_name_comparing = []
                    for state2 in comp.get_states():
                        for name in comp.state_names[state2.number].split("_"):
                            state_name_comparing.append(name)
                    for name in selected_comp.state_names[edge.succ.number].split("_"):
                        state_name_comparing.append(name)
                    if len(state_name_comparing) > len(set(state_name_comparing)):
                        confliction_weight += 1
            edge.weight = confliction_weight
        if state.marked:
            end_state = state
    # determine a path with lowest conflict weight
    path = dijkstras_path(conflict_weighted, conflict_weighted.initial, end_state)
    current_state = selected_comp.initial
    removable_edges = []
    for evt in path:
        for edge in current_state.get_outgoing():
            if edge.label == evt:
                next_state = edge.succ
            elif edge not in removable_edges:
                removable_edges.append(edge)
        current_state = next_state
    for edge in removable_edges:
        selected_comp.remove_edge(edge)
    selected_comp.reduce(True, True)

def collect_outgoing_labels(state):
    outgoing_labels = set()
    for edge in state.get_outgoing():
        outgoing_labels.add(edge.label)
    return outgoing_labels

def find_single_tau_path(pruned, start_state):
    mirror_state = pruned.initial
    real_state = start_state
    step_done = False
    path = []
    while not mirror_state.marked:
        for mirror_edge in mirror_state.get_outgoing():
            if step_done:
                step_done = False
                break
            for real_edge in real_state.get_outgoing():
                if real_edge.label == mirror_edge.label:
                    path.append(real_edge)
                    mirror_state = mirror_edge.succ
                    real_state = real_edge.succ
                    step_done = True
                    break
    return path

def find_critical_states(aut, local_alphabet):
    critical_states = set()
    semi_critical_states = set()
    for state in aut.get_states():
        if state.marked: # If a state is marked, it's critical
            critical_states.add(state)
            continue
        for edge in state.get_outgoing():
            if edge.label not in local_alphabet: # If a state has a global event on an outgoing edge, it's critical
                critical_states.add(state)
                break
        if state not in critical_states:
            for edge in state.get_incoming():
                if edge.label not in local_alphabet: # If a state has a global event on an incoming edge, it's semi-critical
                    semi_critical_states.add(state)
                    break
    if aut.initial not in critical_states: # If the initial state isn't in the critical state set yet, add it
        semi_critical_states.add(aut.initial)
    return critical_states, semi_critical_states
    
def find_critical_states2(aut, local_alphabet):
    critical_states = set()
    semi_critical_states = set()
    for state in aut.get_states():
        if state.marked: # If a state is marked, it's critical
            critical_states.add(state)
        for edge in state.get_outgoing():
            if edge.label not in local_alphabet: # If a state has a global event on an outgoing edge, it's critical
                critical_states.add(state)
                break
        for edge in state.get_incoming():
            if edge.label not in local_alphabet: # If a state has a global event on an incoming edge, it's semi-critical
                semi_critical_states.add(state)
                break
    if aut.initial not in semi_critical_states: # If the initial state isn't in the critical state set yet, add it
        semi_critical_states.add(aut.initial)
    return critical_states, semi_critical_states
    
class FrozenLink:

  def __init__(self, parent, event):
    self.mParent = parent
    self.mEvent = event
    if (self.mParent == None):
      self.mHash = self.mEvent.__hash__()
    else:
      self.mHash = self.mParent.__hash__() * 7 + self.mEvent.__hash__()
    
  def __hash__(self):
    return self.mHash
  
  def __eq__(self, other):
    return other != None and self.mEvent == other.mEvent and self.mParent == other.mParent

def remove_always_disabled_events(auts):
  always_disabled = set()
  # for each automaton checks whether an evt is always disabled
  for aut in auts:
    has_transition = set()
    for state in aut.get_states():
      for edge in state.get_outgoing():
        has_transition.add(edge.label)
    disabled_in_aut = aut.alphabet.difference(has_transition)
    #print disabled_in_aut
    always_disabled.update(disabled_in_aut)
  print always_disabled
  # removes all outgoing transition for always disabled events
  for aut in auts:
    aut.alphabet = aut.alphabet.difference(always_disabled)
    for state in aut.get_states():
      for edge in list(state.get_outgoing()):
        if edge.label in always_disabled:
          aut.remove_edge(edge)
          
def convert_orders_to_auts(craneorders, eventmap, alphabets, collection):
  auts =[]
  for i, orders in enumerate(craneorders):
    events = []
    for name in orders:
      events.append(eventmap["C" + str(i + 1) + name])
    auts.append(generate_aut_from_path_events_weighted_dontcare(events, alphabets[i], collection))
  return auts
      
def get_shortest_path(auts, eventdata, heap_len, craneorders, eventmap, alphabets):
  print "craneorders"
  print craneorders
  orderings = convert_orders_to_auts(craneorders, eventmap, alphabets, auts[0].collection)
  tocompose = list(auts) + orderings
  for i, aut in enumerate(tocompose):
    aut.save_as_dot("aut" + str(i).zfill(2) + ".dot")
  sync = synchronousproduct(tocompose)
  for aut in orderings:
    aut.save_as_dot("order.dot")
    aut.clear()
  path = restrictpath(get_greedy_time_optimal_sup_vector(sync, eventdata, heap_len))
  return path, findpathweight(path, eventdata, heap_len)
      
def simulated_anealling(auts, eventdata, heap_len, events, eventmap, cranes, tick):
  tocompose = []
  newauts = []
  for aut in auts:
    if not aut.name.startswith("SC"):
      tocompose.append(aut)
    else:
      newauts.append(aut)
  sync = synchronousproduct(tocompose)
  newauts.append(sync)
  order = random.sample(events, len(events))
  print "order"
  print order
  CraneOrders = [[] for i in range(cranes)]
  alphabets = [set() for i in range(cranes)]
  for aut in auts:
    for event in aut.alphabet:
      if "pick" in event.name:
        alphabets[int(event.name[1])-1].add(event)
  for event in order:
    index = random.randint(0, cranes-1)
    CraneOrders[index].append(event)
  temperature = 1.0
  bestshortestpath, bestweight = get_shortest_path(auts, tick, CraneOrders, eventmap, alphabets)
  currpath, currweight = bestshortestpath, bestweight
  decr = .01
  while temperature > 0:
    rand = random.random()
    origcranes = copy.deepcopy(CraneOrders)
    if rand <= .5 or cranes == 1:
      index = random.randint(0, len(CraneOrders)-1)
      if len(CraneOrders[index]) >= 2: 
        index2 = random.randint(0, len(CraneOrders[index]) - 2)  
        tmp = CraneOrders[index][index2]
        CraneOrders[index][index2] = CraneOrders[index][index2+1]
        CraneOrders[index][index2+1] = tmp
    else:
      swap = random.sample(range(cranes), 2)
      index = random.randint(0, len(CraneOrders[swap[0]]) - 1)
      index2 = float(index) / float(len(CraneOrders[swap[0]])) if len(CraneOrders[swap[0]]) != 0 else 0
      index2 = int(len(CraneOrders[swap[0]]) * index2)
      CraneOrders[swap[1]].insert(index2, CraneOrders[swap[0]].pop(index))
    path, weight = get_shortest_path(auts, tick, CraneOrders, eventmap, alphabets)
    if bestweight > weight:
      bestshortestpath, bestweight = path, weight
    if currweight > weight or random.random() < temperature:
      currweight = weight
    else:
      CraneOrders = origcranes
    temperature -= decr
    print (bestweight, currweight, temperature)