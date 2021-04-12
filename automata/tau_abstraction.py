import automata,copy
from automata import taskresource, maxplus, data_structure, collection, weighted_structure, \
                            compute_weight, conversion, weighted_product, algorithm, common, \
                            abstraction, product, weighted_supervisor, progressivetimeoptimalsynthesis,\
                            progressive#, frontend, weighted_supervisor
from sets import Set
import heapq
import random
import cProfile
import collections
from time import time

handle = None
def tau_abstracted_greedy_supervisor(comp_list, req_list, comp_mut_ex, evt_pairs):
    if not comp_mut_ex == "type1" and not comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
    common.print_line("Computing event data...")
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
            comp.save_as_dot("comp_as_dot_" + comp.name + ".dot")
    while len(comp_list) > 1:
        common.print_line("Doing tau abstraction and product computation, %d components left..." % len(comp_list))
        print comp_list[0]
        do_tau_abstraction(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs)
        
        print comp_list[0]
        if len(comp_list) == 2:
            do_tau_abstraction(comp_list, comp_list[1], eventdata, len(cliques), evt_pairs)
            comp_list[1].save_as_dot("comp2_abstracted.dot")
        print comp_list[1]
        new_plant = weighted_product.n_ary_weighted_product(comp_list[0:2],
                                                 algorithm.EQUAL_WEIGHT_EDGES, True)
        eureka_state_collision(new_plant)
        comp_list = comp_list[2:]
        comp_list.insert(0,new_plant)
        comp_list[0].reduce(True, True)
        comp_list[0].save_as_dot("comp_abstracted_as_dot_" + str(len(comp_list)) + "_components.dot")
    time_opt_sup = get_greedy_time_optimal_sup(comp_list[0].copy(), eventdata, len(cliques))
    time_opt_sup.save_as_dot("tau_optimal_sup.dot")
    return comp_list[0]
    
def testpath(complist, path, eventdata, heap_len, resultfile):
  pathstate = path.initial
  statetuple = []
  weight = maxplus.make_rowmat(0,heap_len)
  weight = maxplus.matrix_to_vector(weight)
  for aut in complist:
    statetuple.append(aut.initial)
  while not pathstate.marked:
    event = None
    newstatetuple = []
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      event = edge.label
    #weight = maxplus.otimes_mat_mat(weight ,eventdata[event].matHat)
    weight = maxplus.newtimes_vec_vec(weight ,maxplus.matrix_to_vector(eventdata[event].matHat))
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
  ceil = 0
  for val in weight.data:
    ceil = max(val, ceil)
  #for vec in weight.data:
  #  for val in vec:
  #    ceil = max(val, ceil)
  #resultfile.write("weight: " + str(ceil))
  #resultfile.write("\n")
  #resultfile.close()
  return ceil
  
def testpath_not_weighted(complist, path, tick, resultfile):
  pathstate = path.initial
  statetuple = []
  weight = 0
  depth = 0
  for aut in complist:
    statetuple.append(aut.initial)
  while not pathstate.marked:
    event = None
    newstatetuple = []
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      event = edge.label
    if (event == tick):
      weight += 1
    for i in range(len(complist)):
      state = statetuple[i]
      if event not in complist[i].alphabet:
        newstatetuple.append(state)
      else:
        for edge in state.get_outgoing():
          if edge.label == event:
            newstatetuple.append(edge.succ)
            break
        else:
          print "this path is incorrect"
          print depth
          print pathstate
          print event
          au = ia
    statetuple = newstatetuple
    depth += 1
  for state in statetuple:
    if not state.marked:
      print "there is a bug here"
      return
  print "this path is correct"
  print "weight: " + str(weight)
  resultfile.write("weight: " + str(weight))
  return
    
def clustersort(aut):
  return int(aut.name[len(aut.name)-2:])
  
def namesort(aut):
  return aut.name
    
def tau_abstracted_greedy_supervisor2(comp_list, req_list, comp_mut_ex, evt_pairs):
  if not comp_mut_ex == "type1" and not comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
  common.print_line("Computing event data...")
  result = taskresource.compute_custom_eventdata_extended(comp_list, evt_pairs, comp_mut_ex)
  copylist = []
  for aut in comp_list:
    print aut.name
    copylist.append(get_automaton_copy(aut))
  #comp_list = sorted(comp_list, key=clustersort)
  comp_list = sorted(comp_list, key=namesort)
  #comp_list.insert(0, comp_list.pop())
  #comp_list = list(reversed(comp_list))
  for aut in comp_list:
    print aut.name
  if result is None:
      return None
  eventdata, cliques = result
  orig_alphabet = Set([])
  #this is needed for bisimulation for some reason
  tau = comp_list[0].collection.make_event("tau", True, True, False)
  for aut in comp_list:
    aut.alphabet.add(tau)
    orig_alphabet.update(aut.alphabet)
  compnums = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
  #compnums = [8,9,11,2]
  #compnums = [27]
  path = tau_abstracted_greedy_supervisor_recurse(comp_list, eventdata, cliques, evt_pairs, orig_alphabet,0, compnums)
  testpath(copylist, path, eventdata, len(cliques))
  return path
  
def output_crane_order(auts):
  CS_auts = [aut for aut in auts if aut.name.startswith("CS")]
  D_auts = [aut for aut in auts if aut.name.startswith("D")]
  SC_auts = [aut for aut in auts if aut.name.startswith("SC")]
  first_comp = D_auts[0].name
  first_comp += "".join("," + aut.name for aut in D_auts[1:])
  spec_comp = ""
  handle = file("rem\\steps", 'w')
  handle.write(first_comp + " " + spec_comp + " sup1 abs1\n") 
  for i, CS_aut in enumerate(CS_auts):
    SC_to_add = []
    for SC_aut in SC_auts:
      tokeep = True
      for event in SC_aut.alphabet:
        if ("pick" in event.name or "drop" in event.name) and int(event.name.split("-")[-3]) > (i+1):
          tokeep = False
          break
      if tokeep:
        SC_to_add.append(SC_aut)
    SC_auts = [aut for aut in SC_auts if aut not in SC_to_add]
    comp = "abs" + str(i + 1) + "," + CS_aut.name
    comp += "".join("," + aut.name for aut in SC_to_add)
    handle.write(comp + "  " + "sup" + str(i + 2) + " abs" + str(i + 2) + "\n")
  print str(SC_auts)
  handle.close()
  aiau = aiia

  
def tau_abstracted_greedy_supervisor_not_weighted(comp_list, req_list, comp_mut_ex, evt_pairs, name):
  if not comp_mut_ex == "type1" and not comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
  common.print_line("Computing event data...")
  remove_always_disabled_events(comp_list)
  #for aut in comp_list:
    #frontend.save_automaton(aut, "Supervisor is saved in %s\n", "rem\\" + aut.name + ".cfg")
  #output_crane_order(copy.copy(comp_list)) 
  #result = taskresource.compute_custom_eventdata_extended(comp_list, evt_pairs, comp_mut_ex)
  #if result is None:
  #  eventdata, cliques = result
  copylist = []
  newcomp_list = []
  for aut in comp_list:
    print aut.name
    copylist.append(get_automaton_copy(aut))
  #comp_list = sorted(comp_list, key=clustersort)
  progressive_events = set()
  for event in comp_list[0].collection.events:
    #if event != "R1-pick-C":
    if event != "NewWaver":
      progressive_events.add(comp_list[0].collection.events[event])
  #return progressivetimeoptimalsynthesis.make_prog_supervisor_all_controllable(comp_list, progressive_events)
  #return progressivetimeoptimalsynthesis.make_greedy_prog_supervisor_all_controllable(comp_list, progressive_events)
  #sup = progressivetimeoptimalsynthesis.make_greedy_prog_supervisor_all_controllable(comp_list, progressive_events)
  #progressive.load_test(comp_list, sup, evt_pairs, comp_mut_ex)
  #sup = progressivetimeoptimalsynthesis.make_prog_supervisor_all_controllable(comp_list, progressive_events)
  #progressive.load_test(comp_list, sup, evt_pairs, comp_mut_ex)
  #return sup
  comp_list = sorted(comp_list, key=namesort)
  #comp_list.pop()
  comp_list.insert(0, comp_list.pop())
  comp_list = list(reversed(comp_list))
  tick = comp_list[0].collection.make_event("tick", True, True, False)
  tau = comp_list[0].collection.make_event("tau", True, True, False)
  for aut in comp_list:
    aut.alphabet.add(tau)
  for aut in comp_list:
    print aut.name
    newcomp_list.append(convert_weighted_to_tick(aut, tick))
  comp_list = newcomp_list
  #if result is None:
      #return None
  #eventdata, cliques = result
  orig_alphabet = Set([])
  remove_always_disabled_events(comp_list)
  for aut in comp_list:
    aut.alphabet.add(tau)
    orig_alphabet.update(aut.alphabet)
  compnums = []
  compnums.append((0,8))   
  compnums.append((1,9))
  compnums.append((2,10))
  #compnums.append((2,12))
  compnums.append((3,11))
  #compnums.append((3,13))
  #compnums.append((4,12))
  compnums.append((4,14))
  #compnums.append((5,13))
  #compnums.append((5,15))
  #compnums.append((6,14))
  #compnums.append((6,16))
  #compnums.append((7,17))
  compnums.append(None)
  #compnums.append((0,2))
  #compnums.append((0,2))
  #compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  compnums.append((0,2))
  nonprog = []
  evmap = comp_list[0].collection.events
  nonprog.append(set())
  #nonprog.append(set([evmap['R6-pick-P63']]))
  #nonprog.append(set([evmap['R5-pick-P52'], evmap['R5-pick-P51']]))
  #nonprog.append(set([evmap['R4-pick-P42'], evmap['R4-pick-P41']]))
  #nonprog.append(set([evmap['R3-pick-P32'], evmap['R3-pick-P31']]))
  #nonprog.append(set([evmap['R2-pick-P22'], evmap['R2-pick-P21']]))
  #nonprog.append(set([evmap['R1-pick-P11']]))
  #nonprog.append(set([evmap['R2-pick-P21']]))
  #nonprog.append(set([evmap['R3-pick-P31']]))
  #nonprog.append(set([evmap['R4-pick-P41']]))
  #nonprog.append(set([evmap['R5-pick-P51']]))
  #nonprog.append(set([evmap['R8-drop-B7']]))
  #nonprog.append(set([evmap['R7-drop-B6']]))
  #nonprog.append(set([evmap['R8-pick-B7'], evmap['R7-drop-B6']]))
  #nonprog.append(set([evmap['R7-pick-B6'], evmap['R6-drop-B5']]))
  #nonprog.append(set([evmap['R6-drop-B5']]))
  #nonprog.append(set([evmap['R6-pick-B5'], evmap['R5-drop-B4']]))
  #nonprog.append(set([evmap['R5-drop-B4']]))
  #nonprog.append(set([evmap['R5-pick-B4'], evmap['R4-drop-B3']]))
  #nonprog.append(set([evmap['R4-drop-B3']]))
  #nonprog.append(set([evmap['R4-pick-B3'], evmap['R3-drop-B2']]))
  #nonprog.append(set([evmap['R3-drop-B2']]))
  #nonprog.append(set([evmap['R3-pick-B2'], evmap['R2-drop-B1']]))
  #nonprog.append(set([evmap['R2-pick-B1'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R2-pick-B1'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R3-pick-B2'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R4-pick-B3'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R5-pick-B4'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R6-pick-B5'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R7-pick-B6'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R8-pick-B7'], evmap['R1-drop-C']]))
  #nonprog.append(set([evmap['R2-pick-B1'], evmap['R1-drop-C']])) 
  #nonprog.append(set([evmap['R3-pick-B2'], evmap['R2-drop-B1']]))
  #nonprog.append(set([evmap['R4-pick-B3'], evmap['R3-drop-B2']]))
  #nonprog.append(set([evmap['R5-pick-B4'], evmap['R4-drop-B3']]))
  #nonprog.append(set([evmap['R6-pick-B5'], evmap['R5-drop-B4']]))
  #nonprog.append(set([evmap['R6-drop-B5']]))
  #nonprog.append(set([evmap['R5-drop-B4']]))
  #nonprog.append(set([evmap['R4-drop-B3']]))
  #nonprog.append(set([evmap['R3-drop-B2']]))
  #nonprog.append(set([evmap['R2-drop-B1']]))
  #nonprog.append(set([evmap['R1-pick-C'], evmap['R2-drop-B1']]))
  #nonprog.append(set([evmap['R2-pick-B1'], evmap['R3-drop-B2']]))
  #nonprog.append(set([evmap['R3-pick-B2'], evmap['R4-drop-B3']]))
  #nonprog.append(set([evmap['R4-pick-B3'], evmap['R5-drop-B4']]))
  #nonprog.append(set([evmap['R5-pick-B4']]))
  #nonprog.append(set([evmap['R4-pick-B3']]))
  #nonprog.append(set([evmap['R3-pick-B2']]))
  #nonprog.append(set([evmap['R2-pick-B1']]))                         
  #compnums.append((5,13))
  #compnums.append((6,14))
  #compnums.append((7,15))
  #compnums.append((8,16))
  #compnums.append((9,17))
  #compnums.append((0,14))
  #compnums.append((0,8))
  #compnums.append((1,9))
  #compnums.append((2,10))  
  #compnums.append((3,14))
  # compnums.append((0,2))
  # compnums.append((0,2))
  # compnums = []
  # compnums.append((0,8))
  # compnums.append((1,8))
  # compnums.append((0,3))
  # compnums.append((1,10))
  # compnums.append((0,3))
  # compnums.append((0,2))
  resultsfile = file(name, 'w')
  pathtime = -time()
  print compnums
  for aut in comp_list:
    print aut.name
  path = tau_abstracted_greedy_supervisor_recurse_not_weighted(comp_list, evt_pairs, orig_alphabet,0, compnums, tau, tick, nonprog, resultsfile)
  #path = tau_abstracted_greedy_supervisor_recurse_crane(comp_list, evt_pairs, orig_alphabet,0, compnums, tau, tick, nonprog, resultsfile)
  pathtime += time()
  resultsfile.write("time: " + str(pathtime))
  resultsfile.write("\n")
  path.save_as_dot("suptick.dot")
  #frontend.save_automaton(path, "path", "suptick.cfg")
  testpath_not_weighted(copylist, path, tick, resultsfile)
  orig_alphabet.remove(tick)
  #testpath(copylist, project_not_weighted(path, orig_alphabet), eventdata, len(cliques), resultsfile)
  path.save_as_dot("supnottick.dot")
  return path
  
def create_throughput_automaton(collection, event, number):
  aut = data_structure.Automaton(set([event]), collection)
  aut.initial = aut.add_new_state(number == 0, aut.get_num_states())
  state = aut.initial
  while number != 0:
    number -= 1
    next_state = aut.add_new_state(number == 0, aut.get_num_states())
    aut.add_edge_data(state, next_state, event)
    state = next_state
  aut.save_as_dot("through" + event.name + ".dot")
  return aut
  
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
    
def tau_abstracted_greedy_supervisor_recurse(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth, compnums):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      comp_list[0].save_as_dot("lastaut.dot")
      return restrictpath(get_greedy_time_optimal_sup(comp_list[0], eventdata, len(cliques)))
    else:
      old_aut = get_automaton_copy(comp_list[0])#copy.deepcopy(comp_list[0])
      print "start abstraction"
      print comp_list[0]
      do_tau_abstraction(comp_list, comp_list[0], eventdata, len(cliques), evt_pairs)
      #comp_list[0] = subsetconstruction(comp_list[0], find_local_alphabet(comp_list, comp_list[0], evt_pairs), depth)
      #comp_list[0] = subsetconstruction(comp_list[0], get_local_events(comp_list[0], comp_list), depth)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
      comp_list[0] = abstraction.automaton_abstraction_weighted(comp_list[0])
      comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
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
      new_plant = weighted_product.n_ary_weighted_product(comp_list[first:last],
                                                    algorithm.EQUAL_WEIGHT_EDGES)
      #new_plant = synchronousproduct(comp_list[0:2], depth)
      comp_list[1].save_as_dot("other" + str(depth) + ".dot")
      new_plant.name = str(depth)
      new_plant.reduce(True, True)
      print "depth:" + str(depth)
      #print comp_list[0].alphabet
      print comp_list[1].name
      #print comp_list[1].alphabet
      #comp_list.pop(0)
      #comp_list.pop(0)
      templist = []
      for i in range(first):
        templist.append(comp_list[i])
      for i in range(last, len(comp_list)):
        templist.append(comp_list[i])
      comp_list = templist
      #comp_list = comp_list[compnums[depth]:len(comp_list)]
      comp_list.insert(0,new_plant)
      new_plant.save_as_dot("newplant" + str(depth) + ".dot")
      print "get new path"
      path = tau_abstracted_greedy_supervisor_recurse_crane(comp_list, eventdata, cliques, evt_pairs, orig_alphabet, depth+1, compnums)
      print "path returned"
      if path == None:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project(path, orig_alphabet)
      print "alphabet"
      print path.alphabet
      tosync = [old_aut, path]
      old_aut.save_as_dot("G1" + str(depth) + ".dot")
      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      patholdsync = weighted_product.n_ary_weighted_product(tosync, algorithm.EQUAL_WEIGHT_EDGES)
      print "looks like: "
      print patholdsync
      patholdsync.reduce(True, True)
      patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      return restrictpath(get_greedy_time_optimal_sup(patholdsync, eventdata, len(cliques)))
      
def reversetickdijkstra(aut, tick, tau, fromstate):
  distances = {}
  visited = Set()
  queue = []
  tup = (0, 0, None, fromstate)
  heapq.heappush(queue, tup)
  number = 1
  while len(queue) != 0:
    distance, throwaway, prededge, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = distance
    for edge in state.get_incoming():
      if edge.pred in visited:
        continue
      if edge.label == tick or edge.label == tau:
        if edge.label == tick:
          distance += 1
        number += 1
        heapq.heappush(queue, (distance,number,edge,edge.pred))
  return distances
  
def prunebadticks(aut, tick, tau, depth):
  aut.save_as_dot("prunebadtickbefore" + str(depth) + ".dot")
  dictdistances = {}
  for state in aut.get_states():
    for edge in state.get_outgoing():
      if edge.label != tau and edge.label != tick:
        dictdistances[state] = reversetickdijkstra(aut, tick, tau, state)
        break
  edgestoremove = []
  for state in aut.get_states():
    if state in dictdistances:
      continue
    distancesused = []
    for key in dictdistances:
      if state in dictdistances[key]:
        distancesused.append(key)
    for edge in state.get_outgoing():
      if edge.label == tau or edge.label == tick:
        if edge.succ == state:
          continue
        keep = False
        for key in distancesused:
          if edge.succ not in dictdistances[key]:
            continue
          if edge.label == tau:
            if dictdistances[key][edge.succ] <= dictdistances[key][state]:
              keep = True
              break
          if edge.label == tick:
            if dictdistances[key][edge.succ] < dictdistances[key][state]:
              keep = True
              break
        if not keep:
          edgestoremove.append(edge)
  print "edges pruned:" + str(len(edgestoremove))
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.save_as_dot("prunebadtickafter" + str(depth) + ".dot")
  return aut
  
def get_prog(aut):
  nonprog = set()
  for state in aut.get_states():
    if state.marked:
      for edge in state.get_incoming():
        nonprog.add(edge.label)
  print nonprog
  return nonprog
      
def tau_abstracted_greedy_supervisor_recurse_not_weighted(comp_list, evt_pairs, orig_alphabet, depth, compnums, tau, tick, nonprog, resultfile):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      comp_list[0].save_as_dot("lastaut.dot")
      return tickdijkstrapath(comp_list[0], tick)
    else:
      print comp_list[0]
      old_aut = get_automaton_copy_not_weighted(comp_list[0])#copy.deepcopy(comp_list[0])
      #if depth > 1:
        #prochack2(comp_list[0],get_local_events(comp_list[0], comp_list))
        #comp_list[0] = prune_wait(comp_list[0], tick, depth)
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = prune_wait_non_prog_full2(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))#get_local_events(comp_list[0], comp_list))
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      local = get_local_events(comp_list[0], comp_list)
      local.add(tau)
      #prune_crane(comp_list[0])
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #comp_list[0] = prune_wait_local(comp_list[0], tick, depth, local)
      #prochack2(comp_list[0],get_local_events(comp_list[0], comp_list))
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #prune_long_path(comp_list[0], tick, 924)
      #comp_list[0] = abstraction.abstraction_refined(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
      #comp_list[0] = subsetconstructionnotweighted(comp_list[0], local, depth)
      comp_list[0] = subsetconstructionnotweightedreverse(comp_list[0], local, depth)
      comp_list[0] = subsetconstructionnotweightedreverse(comp_list[0], local, depth)
      resultfile.write("comp size: " + str(comp_list[0].get_num_states()))
      resultfile.write("\n")
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #print nonprog[depth]
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, get_prog(comp_list[0]))
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, nonprog[depth])
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))
      #comp_list[0] = prune_wait_number(comp_list[0], tick, depth, 2)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      if previousaut == comp_list[0]:
        print "didn't subset construct"
        comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
        comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      else:
        comp_list[0].save_as_dot("beforehopcroft" + str(depth) + ".dot")
        #comp_list[0] = hopcroft(comp_list[0])
        #comp_list[0].alphabet.add(tau)
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
        comp_list[0].save_as_dot("afterhopcroft" + str(depth) + ".dot")
      #comp_list[0] = prunebadticks(comp_list[0], tick, tau, depth)
      #abstraction.automaton_abstraction(comp_list[0])
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      #reinsert_tick(comp_list[0], tick)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      if False: #depth >= 1:
        path = astar_crane(comp_list, tick)
      else :
        print compnums[depth]
        for aut in comp_list:
          print aut.name
        if (compnums[depth] == None):
          comp_list.insert(0, comp_list.pop())
          compnums[depth] = (0,2)
        first, last = compnums[depth]
        tocompose = comp_list[first:last]
        print "tocompose:" 
        for aut in tocompose:
          print aut.name
        coll = tocompose[0].collection
        num_wav = 9
        #if depth == 0:
        #  tocompose.append(create_throughput_automaton(coll, coll.events['R1-pick-C'], num_wav))
        #  tocompose.append(create_throughput_automaton(coll, coll.events['R2-drop-B1'], num_wav))
        #elif depth + 1 == len(compnums):
        #  tocompose.append(create_throughput_automaton(coll, coll.events["R" + str(depth + 1) + "-pick-B" + str(depth)], num_wav))
        #else:
        #  tocompose.append(create_throughput_automaton(coll, coll.events["R" + str(depth + 1) + "-pick-B" + str(depth)], num_wav))
        #  tocompose.append(create_throughput_automaton(coll, coll.events["R" + str(depth + 2) + "-drop-B" + str(depth+1)], num_wav))
        new_plant = synchronousproduct(tocompose, 0)
        #if (depth > 2):
        #  state = tocompose[1].initial
        #  tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
        #  for edge in state.get_outgoing():
        #    if edge.succ != state:
        #      nextstate = edge.succ
        #      if edge.label.name.startswith("C1"):
        #        pick1 = edge.label
        #      else:
        #        pick2 = edge.label
        #  for state in aut.get_states():
        #    if state.marked:
        #      for edge in state.get_incoming():
        #        if edge.pred != state:
        #          state = edge.pred
        #          break
        #      break
        #  for edge in state.get_incoming():
        #    if edge.pred != state:
        #      if edge.label.name.startswith("C1"):
        #        drop1 = edge.label
        #      else:
        #        drop2 = edge.label
        #  prune_impossible_events_crane(new_plant, pick1, pick2, drop1, drop2)
        resultfile.write("abstract size: " + str(new_plant.get_num_states()))
        resultfile.write("\n")
        #new_plant = synchronousproduct(comp_list[0:2], depth)
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        new_plant.name = str(depth)
        print "synchronous before reduce"
        print new_plant
        #neverempty(new_plant)
        new_plant.reduce(True, True)
        print "synchronous after reduce"
        print new_plant
        print "depth:" + str(depth)
        #print comp_list[0].alphabet
        print comp_list[1].name
        #print comp_list[1].alphabet
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
        new_plant.save_as_dot("newplant" + str(depth) + ".dot")
        print "get new path"
        path = tau_abstracted_greedy_supervisor_recurse_not_weighted(comp_list, evt_pairs, orig_alphabet, depth+1, compnums, tau, tick, nonprog, resultfile)
      print "path returned"
      if path == None:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      #path = project_not_weighted(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
      old_aut.save_as_dot("G1" + str(depth) + ".dot")
      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      return (get_common_path(old_aut, path, resultfile))
      #patholdsync = product.n_ary_unweighted_product(tosync)
      #print "looks like: "
      #patholdsync.reduce(True, True)
      #print patholdsync
      #patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      #return restrictpath(patholdsync)
      
def pathauttoeventlist(aut):
  pathstate = aut.initial
  events = []
  while not pathstate.marked:
    for edge in pathstate.get_outgoing():
      events.append(edge.label)
      pathstate = edge.succ
      break
  return events
  
def get_common_path(aut, path, resultfile):
  sharedevents = aut.alphabet.intersection(path.alphabet)
  newalphabet = aut.alphabet.union(path.alphabet)
  tovisit = [(aut.initial, 0, None)]
  visited = set([(aut.initial, 0)])
  path = pathauttoeventlist(path)
  while True: #len(tovisit) != 0:
    state, pindex, link = tovisit.pop()
    for i in xrange(pindex, len(path)):
      if path[pindex] not in sharedevents:
        link = (path[pindex], link)
        pindex += 1
      else:
        break
    if state.marked and pindex >= len(path):
      break
    for edge in state.get_outgoing():
      if edge.label not in sharedevents:
        tup = (edge.succ, pindex)
        if tup not in visited:
          visited.add(tup)
          tovisit.append((edge.succ, pindex, (edge.label, link)))
      elif pindex < len(path) and edge.label == path[pindex]:
        tup = (edge.succ, pindex+1)
        if tup not in visited:
          visited.add(tup)
          tovisit.append((edge.succ, pindex+1, (edge.label, link)))
  evlist = []
  while link != None:
    evt, link = link
    evlist.append(evt)
  evlist = list(reversed(evlist))
  resultfile.write("comp size path return: " + str(len(visited)))
  resultfile.write("\n")
  return generate_aut_from_path_events(evlist, newalphabet, aut.collection) 
  
#simplifies a deterministic automaton
def hopcroft2(aut):
  aut_copy = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  print "states before hopcroft:" + str(aut_copy.get_num_states())
  predecessors = {}
  marked = []
  notmarked = []
  partitions = []
  partitions.append(marked)
  partitions.append(notmarked)
  numalready = 0
  numnotalready = 0
  for state in aut.get_states():
    if state.marked:
      marked.append(state)
      state.partition = 0
    else:
      notmarked.append(state)
      state.partition = 1
    for edge in state.get_incoming():
      if (state, edge.label) not in predecessors:
        predecessors[(state, edge.label)] = set()
      predecessors[(state, edge.label)].add(edge.pred)
  W = set()
  if len(marked) <= len(notmarked):
    W.add(0)
  else:
    W.add(1)
  while len(W) != 0:
    currentpart = W.pop()
    A = partitions[currentpart]
    for event in aut.alphabet:
      X = set()
      for target in A:
        if (target, event) not in predecessors:
          continue
        X.update(predecessors[(target, event)])
      checkpartitions = set()
      for pred in X:
        checkpartitions.add(pred.partition)
      for partindex in checkpartitions:
        split1 = []
        split2 = []
        for pred in partitions[partindex]:
          if pred in X:
            numalready += 1
            split1.append(pred)
          else:
            numnotalready += 1
            split2.append(pred)
            pred.partition = len(partitions)
        if len(split2) != 0:
          if partindex in W:
            W.add(len(partitions))
          else:
            if len(split1) <= len(split2):
              W.add(partindex)
            else:
              W.add(len(partitions))
          partitions[partindex] = split1
          partitions.append(split2)
  parttostate = {}
  state_to_state = {}
  print str(numalready) + ":" + str(numnotalready)
  for i in range(len(partitions)):
    state = aut_copy.add_new_state(partitions[i][0].marked, i)
    parttostate[i] = state
  if aut.initial == None:
    aut_copy.initial = None
  else:
    aut_copy.initial = parttostate[aut.initial.partition]
  print "adding edges"
  for i in range(len(partitions)):
    state = partitions[i][0]
    for edge in state.get_outgoing():
      aut_copy.add_edge_data(parttostate[i], parttostate[edge.succ.partition], edge.label)
    for state in partitions[i]:
      state_to_state[state] = parttostate[i]
  print "states after hopcroft:" + str(aut_copy.get_num_states())
  return aut_copy, state_to_state

def hopcroft2_to_be_named(aut):
  aut_copy = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  print "states before hopcroft:" + str(aut_copy.get_num_states())
  predecessors = {}
  langdictionary = {}
  partitions = []
  numalready = 0
  numnotalready = 0
  for state in aut.get_states():
    if state.languages not in langdictionary:
      langdictionary[state.languages] = []
    langdictionary[state.languages].append(state)
    for edge in state.get_incoming():
      if (state, edge.label) not in predecessors:
        predecessors[(state, edge.label)] = set()
      predecessors[(state, edge.label)].add(edge.pred)
  for partition in langdictionary.values():
    for state in partition:
      state.partition = len(partitions)
    partitions.append(partition)
  W = set(range(len(partitions)))
  while len(W) != 0:
    currentpart = W.pop()
    A = partitions[currentpart]
    for event in aut.alphabet:
      X = set()
      for target in A:
        if (target, event) not in predecessors:
          continue
        X.update(predecessors[(target, event)])
      checkpartitions = set()
      for pred in X:
        checkpartitions.add(pred.partition)
      for partindex in checkpartitions:
        split1 = []
        split2 = []
        for pred in partitions[partindex]:
          if pred in X:
            numalready += 1
            split1.append(pred)
          else:
            numnotalready += 1
            split2.append(pred)
            pred.partition = len(partitions)
        if len(split2) != 0:
          if partindex in W:
            W.add(len(partitions))
          else:
            if len(split1) <= len(split2):
              W.add(partindex)
            else:
              W.add(len(partitions))
          partitions[partindex] = split1
          partitions.append(split2)
  parttostate = {}
  state_to_state = {}
  print str(numalready) + ":" + str(numnotalready)
  for i in range(len(partitions)):
    state = aut_copy.add_new_state(partitions[i][0].marked, i)
    parttostate[i] = state
    state.languages = partitions[i][0].languages
  if aut.initial == None:
    aut_copy.initial = None
  else:
    aut_copy.initial = parttostate[aut.initial.partition]
  print "adding edges"
  for i in range(len(partitions)):
    state = partitions[i][0]
    for edge in state.get_outgoing():
      aut_copy.add_edge_data(parttostate[i], parttostate[edge.succ.partition], edge.label)
    for state in partitions[i]:
      state_to_state[state] = parttostate[i]
  print "states after hopcroft:" + str(aut_copy.get_num_states())
  return aut_copy, state_to_state
  
def allmarked(statetuple):
  for state in statetuple:
    if not state.marked:
      return False
  return True
  
def calcsuccessors(statetuple, event, transmap, auts):
  succs = set()
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
    autsuccs = set([statetuple[i]])
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
  
def prune_wait(aut, tick, depth):
  print "pruning wait"
  edgestoremove = []
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
  #print "depth:" + depth
  #print aut
  aut.save_as_dot("prunebefore" + str(depth) + ".dot")
  for state in aut.get_states():
    if state == aut.initial:
      continue
    toremove = aut.alphabet.copy()
    toremove.remove(tick)
    notickpred = True
    for edge in state.get_incoming():
      if edge.label != tick:
        notickpred = True
        break
      if edge.pred == edge.succ:
        continue
      notickpred = False
      toremove2 = set()
      for edge2 in edge.pred.get_outgoing():
        toremove2.add(edge2.label)
      toremove.intersection_update(toremove2)
    if not notickpred:
      for edge in state.get_outgoing():
        if edge.label in toremove:
          edgestoremove.append(edge)
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  aut.save_as_dot("pruneafter" + str(depth) + ".dot")
  return aut
  
def prune_local_memory(aut, local_alphabet):
  for state in aut.get_states():
    has_local = False
    for edge in state.get_outgoing():
      if edge.label in local_alphabet:
        has_local = True
        break
    if has_local:
      for edge in list(state.get_outgoing()):
        if edge.label not in local_alphabet:
          aut.remove_edge(edge)
  
def prune_wait_local(aut, tick, depth, local_alphabet):
  print "pruning wait"
  edgestoremove = []
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
  #print "depth:" + depth
  #print aut
  aut.save_as_dot("prunebefore" + str(depth) + ".dot")
  for state in aut.get_states():
    if state == aut.initial:
      continue
    toremove = local_alphabet.copy()
    if tick in toremove:
      toremove.remove(tick)
    notickpred = True
    for edge in state.get_incoming():
      if edge.label != tick:
        notickpred = True
        break
      if edge.pred == edge.succ:
        continue
      notickpred = False
      toremove2 = set()
      for edge2 in edge.pred.get_outgoing():
        toremove2.add(edge2.label)
      toremove.intersection_update(toremove2)
    if not notickpred:
      for edge in state.get_outgoing():
        if edge.label in toremove:
          edgestoremove.append(edge)
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  aut.save_as_dot("pruneafter" + str(depth) + ".dot")
  return aut
  
def prune_wait_local_full(aut, tick, depth, local_alphabet):
  print "pruning wait"
  edgestoremove = []
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
  #print "depth:" + depth
  #print aut
  aut.save_as_dot("prunebefore" + str(depth) + ".dot")
  statestolookat = [aut.initial]
  visited = set(statestolookat)
  state_num = 0
  for num in aut._states:
    if state_num < num:
      state_num = num
  state_num += 1
  while len(statestolookat) != 0:
    #if aut.get_num_states() > 2000:
      #aut.save_as_dot("pruneafter" + str(depth) + ".dot")
      #aiu =ia
    state = statestolookat.pop()
    toremove = set()
    for edge in state.get_outgoing():
      if edge.label != tick:
        toremove.add(edge.label)
        if edge.succ not in visited:
          statestolookat.append(edge.succ)
          visited.add(edge.succ)
    if len(toremove) == 0:
      for edge in list(state.get_outgoing(tick)):
        if edge.succ not in visited:
          statestolookat.append(edge.succ)
          visited.add(edge.succ)
      continue
    queue = []
    for edge in list(state.get_outgoing(tick)):
      if edge.succ == state:
        continue
      newstate = aut.add_new_state(edge.succ.marked, state_num)
      state_num += 1
      queue.append((edge.succ, newstate))
      aut.add_edge_data(state, newstate, tick)
      aut.remove_edge(edge)
    while len(queue) != 0:
      origstate, nonorig = queue.pop()
      tolook = False
      justselfloop = True
      for edge in origstate.get_outgoing(tick):
        if edge.succ != origstate: 
          newstate = aut.add_new_state(edge.succ.marked, state_num)
          state_num += 1
          queue.append((edge.succ, newstate))
          aut.add_edge_data(nonorig, newstate, tick)
          justselfloop = False
        #else:
          #aut.add_edge_data(nonorig, nonorig, tick)
      for edge in origstate.get_outgoing():
        if edge.label in toremove and not justselfloop:
          continue
        elif edge.label == tick:
          continue
        else:
          aut.add_edge_data(nonorig, edge.succ, edge.label)
          tolook = True
          toremove.add(edge.label)
          if edge.succ not in visited:
            statestolookat.append(edge.succ)
            visited.add(edge.succ)
      if tolook:
        statestolookat.append(nonorig)
        visited.add(nonorig)
  aut.reduce(True, True)
  aut.save_as_dot("pruneafterfull" + str(depth) + ".dot")
  return aut
  
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
          
def prune_wait_non_prog_full2(aut, tick, depth, non_prog):
  print non_prog
  aut.save_as_dot("prunebefore" + str(depth) + ".dot")
  emptyset = frozenset([])
  new_aut = data_structure.Automaton(aut.alphabet, aut.collection)
  init = new_aut.add_new_state(aut.initial.marked, new_aut.get_num_states())
  new_aut.initial = init
  dictionary = {}
  dictionary[(aut.initial, emptyset)] = init
  queue = [(aut.initial, emptyset)]
  while len(queue) != 0:
    state, R = queue.pop()
    predstate = dictionary[(state, R)]
    elig = set()
    for edge in state.get_outgoing():
      elig.add(edge.label)
    Rprime = R.union(non_prog.intersection(elig))
    for edge in state.get_outgoing():
      if edge.label in R:
        continue
      tup = (edge.succ, Rprime) if edge.label == tick else (edge.succ, emptyset) 
      if tup not in dictionary:
        newstate = new_aut.add_new_state(edge.succ.marked, new_aut.get_num_states())
        dictionary[tup] = newstate
        queue.append(tup)
      else: 
        newstate = dictionary[tup]
      new_aut.add_edge_data(predstate, newstate, edge.label)
  new_aut.reduce(True, True)
  new_aut.save_as_dot("pruneafter" + str(depth) + ".dot")
  return new_aut
        
def prune_wait_non_prog_full(aut, tick, depth, non_prog):
  print "pruning wait"
  edgestoremove = []
  for state in aut.get_states():
    aut.state_names[state.number] = str(state.number)
  #print "depth:" + depth
  #print aut
  aut.save_as_dot("prunebefore" + str(depth) + ".dot")
  statestolookat = [aut.initial]
  visited = set(statestolookat)
  state_num = 0
  for num in aut._states:
    if state_num < num:
      state_num = num
  state_num += 1
  while len(statestolookat) != 0:
    #if aut.get_num_states() > 2000:
    #  aut.save_as_dot("pruneafter" + str(depth) + ".dot")
    #  aiu =ia
    state = statestolookat.pop()
    toremove = set()
    for edge in state.get_outgoing():
      if edge.label in non_prog:
        toremove.add(edge.label)
      if edge.succ not in visited:
        statestolookat.append(edge.succ)
        visited.add(edge.succ)
    if len(toremove) == 0:
      for edge in list(state.get_outgoing(tick)):
        if edge.succ not in visited:
          statestolookat.append(edge.succ)
          visited.add(edge.succ)
      continue
    queue = []
    dictionary = {}
    toremove = frozenset(toremove)
    newofoldstate = None
    #dictionary[(state, toremove)] = state
    for edge in list(state.get_outgoing(tick)):
      #if edge.succ == state:
      #  aut.remove_edge(edge)
      #  continue
      if (edge.succ, toremove) not in dictionary:
        newstate = aut.add_new_state(edge.succ.marked, state_num)
        dictionary[(edge.succ, toremove)] = newstate
        state_num += 1
        queue.append((edge.succ, newstate, toremove))
      else:
        newstate = dictionary[(edge.succ, toremove)]
      if edge.succ == state:
        newofoldstate = newstate
      aut.add_edge_data(state, newstate, tick)
      aut.remove_edge(edge)
    while len(queue) != 0:
      origstate, nonorig, toremove = queue.pop()
      if origstate == newofoldstate:
        origstate = state
      #tolook = False
      #justselfloop = True
      for edge in origstate.get_outgoing():
        if edge.label in toremove:
          continue
        elif edge.label == tick:
          continue
        else:
          aut.add_edge_data(nonorig, edge.succ, edge.label)
          #tolook = True
          if (edge.label in non_prog):
            toremove = frozenset(toremove.union([edge.label]))
          if edge.succ not in visited:
            statestolookat.append(edge.succ)
            visited.add(edge.succ)
      for edge in origstate.get_outgoing(tick):
        if True: #edge.succ != origstate:
          succ = edge.succ
          if succ == newofoldstate:
            succ = state
          if (succ, toremove) not in dictionary:
            #print edge.succ
            newstate = aut.add_new_state(edge.succ.marked, state_num)
            dictionary[(succ, toremove)] = newstate
            state_num += 1
            queue.append((succ, newstate, toremove))
          else:
            newstate = dictionary[(succ, toremove)]
          aut.add_edge_data(nonorig, newstate, tick)
          #justselfloop = False
        #else:
          #aut.add_edge_data(nonorig, nonorig, tick)
      #if tolook:
        #statestolookat.append(nonorig)
        #visited.add(nonorig)
  aut.reduce(True, True)
  aut.save_as_dot("pruneafterfull" + str(depth) + ".dot")
  return aut
  
def reinsert_tick(aut, tick):
  for state in aut.get_states():
    hastick = False
    for edge in state.get_outgoing(tick):
      hastick = True
      continue
    if hastick:
      aut.add_edge_data(state, state, tick)
  
def prune_tick(aut, tick, depth):
  edgestoremove = []
  aut.save_as_dot("prunebefore" + str(depth) + ".dot")
  for state in aut.get_states():
    edgeoutgoing = []
    keep = False
    for edge in state.get_outgoing():
      if edge.label != tick:
        edgeoutgoing.append(edge)
      elif edge.succ == state:
        keep = True
    if not keep:
      edgestoremove += edgeoutgoing
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.save_as_dot("pruneafter" + str(depth) + ".dot")
  aut.reduce(True, True)
  return aut
  
def subsetconstruction(aut, localevents, depth):
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  aut_new = weighted_structure.WeightedAutomaton(copy.copy(aut.alphabet), aut.collection)
  #aut_new.alphabet = aut_new.alphabet.difference_update(localevents);
  for event in localevents:
    aut_new.alphabet.remove(event)
  initialset = set([aut.initial])
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
        succdictionary[event] = set()
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
            if (aut_new.get_num_states() > aut.get_num_states()):
              return aut
          aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event, weightdictionary[event])
  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new
  
def prune_crane(aut):
  for state in aut.get_states():
    after_C2 = False
    for edge in state.get_incoming():
      if edge.label.name.startswith("C2"):
        after_C2 = True
        break
    if after_C2:
      for edge in list(state.get_outgoing()):
        if edge.label.name.startswith("C1"):
          aut.remove_edge(edge)
          
def calculate_local_reachable_succ(aut, local_alphabet):
  succ_map = {}
  for state in aut.get_states():
    reachable = set()
    for edge in state.get_outgoing():
      if edge.label in local_alphabet:
        reachable.add(edge.succ)
    succ_map[state] = list(reachable)
  return succ_map
  
def calculate_local_reachable_pred(aut, local_alphabet):
  pred_map = {}
  for state in aut.get_states():
    reachable = set()
    for edge in state.get_incoming():
      if edge.label in local_alphabet:
        reachable.add(edge.pred)
    pred_map[state] = list(reachable)
  return pred_map
    
def find_local_reachable(states, succ_map):
  succs = set(states)
  stack = list(states)
  while stack:
    state = stack.pop()
    im_succs = succ_map[state]
    for succ in im_succs:
      if succ not in succs:
        succs.add(succ)
        stack.append(succ)
  return frozenset(succs)
  
def find_local_reachable_and_enabled(state, local_alphabet):
  succs = set([state])
  stack = [state]
  enabled = set()
  marked = False
  while stack:
    state = stack.pop()
    marked = marked or state.marked
    for edge in state.get_outgoing():
      if edge.label in local_alphabet:
        if edge.succ not in succs:
          succs.add(edge.succ)
          stack.append(edge.succ)
      else: # if succ is not local
        enabled.add(edge.label)
  return frozenset(succs), frozenset(enabled), marked

def subsetconstructionnotweightedreverse(aut, localevents, depth):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  pred_map = calculate_local_reachable_pred(aut, localevents)
  #succ_map = calculate_local_reachable_succ(aut, localevents)
  initialset = set()
  for state in aut.get_states():
    if state.marked:
      initialset.add(state)
  initialset = find_local_reachable(initialset, pred_map)
  initstate = aut_new.add_new_state(aut.initial.marked)
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        if edge.label not in localevents:
          preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(preddictionary[event]) != 0):
          targetstateset = preddictionary[event]
          targetstateset = find_local_reachable(targetstateset, pred_map)
          if targetstateset not in dictionary:
            coninit = False
            for state in targetstateset:
              if aut.initial == state:
                coninit = True
                break
            newstate = aut_new.add_new_state(coninit, aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  aut_new.reduce(True, True)
  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new
  
def subsetconstructionnotweighted(aut, localevents, depth):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  succ_map = calculate_local_reachable_succ(aut, localevents)
  initialset = set([aut.initial])
  initialset = find_local_reachable(initialset, succ_map)
  initstate = aut_new.add_new_state(containsmarked(initialset),aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = find_local_reachable(targetstateset, succ_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  aut_new.add_edges(edgestoadd)
  aut_new.reduce(True, True)
  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new
  
def subsetconstructionnotweighted_find_equiv(aut, localevents, depth = 0):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  succ_map = calculate_local_reachable_succ(aut, localevents)
  initialset = set([aut.initial])
  initialset = find_local_reachable(initialset, succ_map)
  dictionary = set()
  dictionary.add(initialset)
  tovisit = [initialset]
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = find_local_reachable(targetstateset, succ_map)
          if targetstateset not in dictionary:
            dictionary.add(targetstateset)
            tovisit.append(targetstateset)
            #if (aut_new.get_num_states() >= aut.get_num_states()):
            #  return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
  extime += time()  
  always_with_dict = {}
  for state_set in dictionary:
    for state in state_set:
      if state not in always_with_dict:
        always_with_dict[state] = set(state_set)
        always_with_dict[state].remove(state)
      else:
        always_with_dict[state].intersection_update(state_set)
  merged = set()
  for state in always_with_dict:
    if state in merged:
      continue
    for merge_candidate in always_with_dict[state]:
      if merge_candidate in merged:
        continue
      if state in always_with_dict[merge_candidate]:
        merged.add(merge_candidate)
        for edge in merge_candidate.get_outgoing():
          succ = state if edge.succ == merge_candidate else edge.succ
          aut.add_edge_data(state, succ, edge.label)
        for edge in list(merge_candidate.get_incoming()):
          aut.remove_edge(edge)
        if merge_candidate.marked:
          state.marked = True
  print "equivalent: " + str(len(merged))
  aut.reduce(True, True)
  
def prune_tick_self(aut, tick):
  for state in aut.get_states():
    has_outgoing_tick = False
    for edge in state.get_outgoing(tick):
      if edge.succ != state and edge.label == tick:
        has_outgoing_tick = True
        break
    if has_outgoing_tick:
      for edge in list(state.get_outgoing(tick)):
        if edge.succ == state and edge.label == tick:
          aut.remove_edge(edge)
  
def subsetconstructionnotweighted_find_equiv_reverse(aut, localevents, depth = 0):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  pred_map = calculate_local_reachable_pred(aut, localevents)
  initialset = set([state for state in aut.get_states() if state.marked])
  initialset = find_local_reachable(initialset, pred_map)
  dictionary = set()
  dictionary.add(initialset)
  tovisit = [initialset]
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        if edge.label not in localevents:
          preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(preddictionary[event]) != 0):
          targetstateset = preddictionary[event]
          targetstateset = find_local_reachable(targetstateset, pred_map)
          if targetstateset not in dictionary:
            dictionary.add(targetstateset)
            tovisit.append(targetstateset)
            if len(dictionary) % 1000 == 0:
              print len(dictionary)
            #if (aut_new.get_num_states() >= aut.get_num_states()):
            #  return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
  extime += time()  
  always_with_dict = {}
  for state_set in dictionary:
    for state in state_set:
      if state not in always_with_dict:
        always_with_dict[state] = set(state_set)
        always_with_dict[state].remove(state)
      else:
        always_with_dict[state].intersection_update(state_set)
  merged = set()
  #for state in always_with_dict:
  #  if state in merged:
  #    continue
  #  for merge_candidate in always_with_dict[state]:
  #    if merge_candidate in merged:
  #      continue
  #    if state in always_with_dict[merge_candidate]:
  #      merged.add(merge_candidate)
  #      for edge in merge_candidate.get_incoming():
  #        pred = state if edge.pred == merge_candidate else edge.pred
  #        aut.add_edge_data(pred, state, edge.label)
  #      for edge in list(merge_candidate.get_incoming()):
  #        aut.remove_edge(edge)
  #      if merge_candidate == aut.initial:
  #        aut.initial = state
  predremoval = 0
  edgestoadd = set()
  for state in always_with_dict:
    if state in merged:
      continue
    for merge_candidate in always_with_dict[state]:
      if merge_candidate in merged:
        continue
      for event in aut.alphabet:
        orig_incom = list(state.get_incoming(event))
        super_incom = merge_candidate.get_incoming(event)
        for edge in super_incom:
          edgestoadd.add(data_structure.Edge(edge.pred, state, edge.label))
  aut.add_edges(edgestoadd)
  #print "equivalent: " + str(len(merged))
  print "predremoval: " + str(predremoval)
  aut.reduce(True, True)
  
def subsetconstructionnotweighted_more_conflicting(aut, localevents, depth):
  #if aut.get_num_states() > 20000:
   # return aut
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  succ_enabled_map = {}
  for state in aut.get_states():
    succ_enabled_map[state] = find_local_reachable_and_enabled(state, localevents)
  initialset = succ_enabled_map[aut.initial][0]
  marked = True
  for state in initialset:
    if not succ_enabled_map[state][2]:
      marked = False
      break
  initstate = aut_new.add_new_state(marked,aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    enabled = None
    allpos = set()
    for state in stateset:
      if enabled != None:
        enabled.intersection_update(succ_enabled_map[state][1])
      else:
        enabled = set(succ_enabled_map[state][1])
      allpos.update(succ_enabled_map[state][1])
    if not enabled:
      continue
    for event in enabled:
      succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label in enabled:
          succdictionary[edge.label].update(succ_enabled_map[edge.succ][0])
    if len(allpos) != len(enabled):
      observer = False
      print allpos.difference(enabled)
      print stateset
      #ai = iad
    for event in enabled:
      succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label in enabled:
          succdictionary[edge.label].update(succ_enabled_map[edge.succ][0])
    for event in enabled:
      if (len(succdictionary[event]) != 0):
        targetstateset = frozenset(succdictionary[event])
        if targetstateset not in dictionary:
          marked = True
          for state in targetstateset:
            if not succ_enabled_map[state][2]:
              marked = False
              break
          newstate = aut_new.add_new_state(marked, aut_new.get_num_states())
          dictionary[targetstateset] = newstate
          tovisit.append(targetstateset)
          if (aut_new.get_num_states() % 1000 == 0):
            print aut_new.get_num_states()
          #if (aut_new.get_num_states() >= aut.get_num_states()):
          #  return aut
        #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
        edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  aut_new.add_edges(edgestoadd)
  aut_new.reduce(True, True)
  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new
  
def remove_tick_selfloops(aut, tick):
  for state in aut.get_states():
    for edge in list(state.get_outgoing()):
      if edge.succ == state and edge.label == tick:
        aut.remove_edge(edge)

def add_tick_selfloop(aut, tick):
  for state in aut.get_states():
    aut.add_edge_data(state, state, tick)
  
def subsetconstructionnotweighted_more_conflicting_weighted(aut, localevents, depth):
  #if aut.get_num_states() > 20000:
   # return aut
  aut.save_as_dot("subbefore" + str(depth) + ".dot")
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = weighted_structure.WeightedAutomaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  succ_enabled_map = {}
  event_weight = {}
  for state in aut.get_states():
    succ_enabled_map[state] = find_local_reachable_and_enabled(state, localevents)
    for edge in state.get_outgoing():
      event_weight[edge.label] = edge.weight
  initialset = succ_enabled_map[aut.initial][0]
  marked = True
  for state in initialset:
    if not succ_enabled_map[state][2]:
      marked = False
      break
  initstate = aut_new.add_new_state(marked,aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  observer = True
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    enabled = None
    allpos = set()
    for state in stateset:
      if enabled != None:
        enabled.intersection_update(succ_enabled_map[state][1])
      else:
        enabled = set(succ_enabled_map[state][1])
      allpos.update(succ_enabled_map[state][1])
    if not enabled:
      continue
    for event in enabled:
      succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label in enabled:
          succdictionary[edge.label].update(succ_enabled_map[edge.succ][0])
    if len(allpos) != len(enabled):
      observer = False
      print allpos.difference(enabled)
      print stateset
      #ai = iad 
    for event in enabled:
      if (len(succdictionary[event]) != 0):
        targetstateset = frozenset(succdictionary[event])
        if targetstateset not in dictionary:
          marked = True
          for state in targetstateset:
            if not succ_enabled_map[state][2]:
              marked = False
              break
          newstate = aut_new.add_new_state(marked, aut_new.get_num_states())
          dictionary[targetstateset] = newstate
          tovisit.append(targetstateset)
          if (aut_new.get_num_states() % 1000 == 0):
            print aut_new.get_num_states()
          #if (aut_new.get_num_states() >= aut.get_num_states()):
          #  return aut
        #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
        edgestoadd.append(weighted_structure.WeightedEdge(dictionary[stateset], dictionary[targetstateset], event, event_weight[event]))
  aut_new.add_edges(edgestoadd)
  aut_new.save_as_dot("subafter" + str(depth) + "notreduce.dot")
  aut_new.reduce(True, True)
  aut_new.save_as_dot("subafter" + str(depth) + ".dot")
  return aut_new, observer
  
def prune_impossible_events_crane(aut, pick1, pick2, drop1, drop2):
  print "pick1: " + str(pick1) + " pick2: " + str(pick2) + " drop1: " + str(drop1) + " drop2: " + str(drop2)
  aut.save_as_dot("pruneimpbefore.dot")
  queue = [(aut.initial, False, False)]
  visited = set([aut.initial])
  toremove = []
  aut.save_as_dot("impossible.dot")
  while len(queue) != 0:
    state, disable1, disable2 = queue.pop()
    containsdrop1, containsdrop2 = False, False
    numremed = 0
    for edge in list(state.get_outgoing()):
      if disable1 and edge.label.name.startswith("C1") and edge.label != drop1 and "drop" in edge.label.name:
        #toremove.append(edge)
        aut.remove_edge(edge)
        continue
      if disable2 and edge.label.name.startswith("C2") and edge.label != drop2 and "drop" in edge.label.name:
        #toremove.append(edge)
        aut.remove_edge(edge)
        continue
      disable1prime = disable1
      disable2prime = disable2
      if edge.label == drop1:
        disable1prime = False
        containsdrop1 = True
      elif edge.label == drop2:
        disable2prime = False
        containsdrop2 = True
      elif edge.label == pick1:
        disable1prime = True
      elif edge.label == pick2:
        disable2prime = True
      if edge.succ not in visited:
        visited.add(edge.succ)
        queue.append((edge.succ, disable1prime, disable2prime))
    #if containsdrop1 or containsdrop2:
    #  for edge in list(state.get_outgoing()):
    #    if edge.label == drop1 and containsdrop1:
    #      continue
    #    if edge.label == drop2 and not containsdrop1:
    #      continue
    #    toremove.append(edge)
  print "removing: " + str(len(toremove))
  for edge in toremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  aut.save_as_dot("pruneimp.dot")

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
  print "aut is: " + str(aut)
  aut_copy = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  aut_copy.name = aut.name
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
    for edge in state.get_outgoing():
      if (first):
        state = edge.succ
        first = False
      else:
        edgestoremove.append(edge)
    for edge in edgestoremove:
      path.remove_edge(edge)
  path.reduce(True, True)
  return path
  
def maketausequal(aut, alphabet, eventdata):
  aut.save_as_dot("beforemakeequal.dot")
  dictionary = {}
  for event in aut.alphabet:
    if event in alphabet:
      continue
    if eventdata[event].matHat in dictionary:
      dictionary[eventdata[event].matHat].append(event)
    else:
      dictionary[eventdata[event].matHat] = [event]
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
  aut.save_as_dot("aftermakeequal.dot")
  return aut
  
def project_not_weighted(path, alphabet):
  #note this assumes a single path automaton
  #print path
  for state in path.get_states():
    path.state_names[state.number] = str(state.number)
  path.save_as_dot("project.dot")
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
        path.add_edge_data(prevedge.pred, state, prevedge.label)
      else:
        path.set_initial(edge.pred)
      prevedge = edge
    if (edge == None):
      break
    else:
      state = edge.succ
  path.reduce(True, True)
  path.save_as_dot("projectafter.dot")
  path.alphabet.intersection_update(alphabet)
  return path

def project(path, alphabet):
  #note this assumes a single path automaton
  print path
  path.save_as_dot("project.dot")
  state = path.initial
  prevedge = None
  while True:
    edge = None
    for stedge in state.get_outgoing():
      edge = stedge
    print edge
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
  path.save_as_dot("projectafter.dot")
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
  new_aut = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  new_aut.alphabet.add(tick)
  dictionary = {}
  init = new_aut.add_new_state(True, 0)
  dictionary[0] = init
  new_aut.initial = init
  new_aut.add_edge_data(init, init, tick)
  dealtwith = set()
  max_weight = 0
  for state in aut.get_states():
    for edge in state.get_outgoing():
      if edge.label not in dealtwith:
        dealtwith.add(edge.label)
        if edge.weight not in dictionary:
          weightstate = new_aut.add_new_state(False, edge.weight)
          dictionary[edge.weight] = weightstate
          max_weight = max(max_weight, edge.weight)
        weightstate = dictionary[edge.weight]
        new_aut.add_edge_data(init, weightstate, edge.label)
  for i in xrange(max_weight):
    if i+1 not in dictionary:
      weightstate = new_aut.add_new_state(False, i+1)
      dictionary[i+1] = weightstate
    source = dictionary[i+1]
    target = dictionary[i]
    new_aut.add_edge_data(source, target, tick)
  sync = synchronousproduct([aut, new_aut], 0)
  events = new_aut.collection.events
  tau = events["tau"] if "tau" in events else new_aut.collection.make_event("tau", False, False, False)
  has_tau = tau in sync.alphabet
  if not has_tau:
    sync.alphabet.add(tau)
  sync = abstraction.automaton_abstraction(sync)
  sync.name = aut.name
  return sync
  aut.save_as_dot("tick" + aut.name + "before.dot")
  new_aut = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  new_aut.name = aut.name
  new_aut.alphabet.add(tick)
  dictionary = {}
  for state in aut.get_states():
    newstate = new_aut.add_new_state(state.marked, new_aut.get_num_states())
    dictionary[state] = newstate
  for state in aut.get_states():
    new_aut.add_edge_data(dictionary[state], dictionary[state], tick)
    for edge in state.get_outgoing():
      events = new_aut.collection.events
      succstate = new_aut.add_new_state(False, new_aut.get_num_states())
      #succstate = new_aut.add_new_state(edge.succ.marked, new_aut.get_num_states())
      new_aut.add_edge_data(dictionary[edge.pred], succstate, edge.label)
      weight = edge.weight
      while weight > 1:
        nextstate = new_aut.add_new_state(False, new_aut.get_num_states())
        weight -= 1
        new_aut.add_edge_data(succstate, nextstate, tick)
        #new_aut.add_edge_data(succstate, succstate, tick)
        succstate = nextstate
      new_aut.add_edge_data(succstate, dictionary[edge.succ], tick)
  new_aut.set_initial(dictionary[aut.initial])
  events = new_aut.collection.events
  tau = events["tau"] if "tau" in events else new_aut.collection.make_event("tau", False, False, False)
  has_tau = tau in new_aut.alphabet
  if not has_tau:
    new_aut.alphabet.add(tau)
  new_aut = abstraction.automaton_abstraction(new_aut)
  if not has_tau:
    new_aut.alphabet.remove(tau)
  new_aut.name = aut.name
  new_aut.save_as_dot("tick" + aut.name + "after.dot")
  return new_aut
  
def convert_weighted_to_tick_end_event(aut, tick):
  #new_aut = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  #new_aut.alphabet.add(tick)
  #dictionary = {}
  #init = new_aut.add_new_state(True, 0)
  #dictionary[0] = init
  #new_aut.initial = init
  #new_aut.add_edge_data(init, init, tick)
  #dealtwith = set()
  #max_weight = 0
  #for state in aut.get_states():
  #  for edge in state.get_outgoing():
  #    if edge.label not in dealtwith:
  #      dealtwith.add(edge.label)
  #      if edge.weight not in dictionary:
  #        weightstate = new_aut.add_new_state(False, edge.weight)
  #        dictionary[edge.weight] = weightstate
  #        max_weight = max(max_weight, edge.weight)
  #      weightstate = dictionary[edge.weight]
  #      new_aut.add_edge_data(init, weightstate, edge.label)
  #for i in xrange(max_weight):
  #  if i+1 not in dictionary:
  #    weightstate = new_aut.add_new_state(False, i+1)
  #    dictionary[i+1] = weightstate
  #  source = dictionary[i+1]
  #  target = dictionary[i]
  #  new_aut.add_edge_data(source, target, tick)
  #sync = synchronousproduct([aut, new_aut], 0)
  #events = new_aut.collection.events
  #tau = events["tau"] if "tau" in events else new_aut.collection.make_event("tau", False, False, False)
  #has_tau = tau in sync.alphabet
  #if not has_tau:
  #  sync.alphabet.add(tau)
  #sync = abstraction.automaton_abstraction(sync)
  #return sync
  aut.save_as_dot("tick" + aut.name + "before.dot")
  new_aut = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  new_aut.name = aut.name
  new_aut.alphabet.add(tick)
  dictionary = {}
  for state in aut.get_states():
    newstate = new_aut.add_new_state(state.marked, new_aut.get_num_states())
    dictionary[state] = newstate
  for state in aut.get_states():
    new_aut.add_edge_data(dictionary[state], dictionary[state], tick)
    for edge in state.get_outgoing():
      events = new_aut.collection.events
      end = events[edge.label.name + "end"] if edge.label.name + "end" in events else new_aut.collection.make_event(edge.label.name + "end", False, False, False)
      new_aut.alphabet.add(end)
      succstate = new_aut.add_new_state(False, new_aut.get_num_states())
      #succstate = new_aut.add_new_state(edge.succ.marked, new_aut.get_num_states())
      new_aut.add_edge_data(dictionary[edge.pred], succstate, edge.label)
      weight = edge.weight
      while weight > 0:
        nextstate = new_aut.add_new_state(False, new_aut.get_num_states())
        weight -= 1
        new_aut.add_edge_data(succstate, nextstate, tick)
        #new_aut.add_edge_data(succstate, succstate, tick)
        succstate = nextstate
      new_aut.add_edge_data(succstate, succstate, tick)
      new_aut.add_edge_data(succstate, dictionary[edge.succ], end)
  new_aut.set_initial(dictionary[aut.initial])
  events = new_aut.collection.events
  tau = events["tau"] if "tau" in events else new_aut.collection.make_event("tau", False, False, False)
  has_tau = tau in new_aut.alphabet
  if not has_tau:
    new_aut.alphabet.add(tau)
  new_aut = abstraction.automaton_abstraction(new_aut)
  if not has_tau:
    new_aut.alphabet.remove(tau)
  new_aut.name = aut.name
  new_aut.save_as_dot("tick" + aut.name + "after.dot")
  return new_aut
  
def remove_weighted(aut):
  aut.save_as_dot("tick" + aut.name + "before.dot")
  new_aut = data_structure.Automaton(copy.copy(aut.alphabet), aut.collection)
  new_aut.name = aut.name
  dictionary = {}
  for state in aut.get_states():
    newstate = new_aut.add_new_state(state.marked, new_aut.get_num_states())
    dictionary[state] = newstate
  for state in aut.get_states():
    for edge in state.get_outgoing():
      #succstate = new_aut.add_new_state(edge.succ.marked, new_aut.get_num_states())
      new_aut.add_edge_data(dictionary[edge.pred], dictionary[edge.succ], edge.label)
  new_aut.set_initial(dictionary[aut.initial])
  return new_aut

def do_tau_abstraction(aut_list, selected_aut, eventdata, heap_len, evt_pairs):
    #local_alphabet = find_local_alphabet(aut_list, selected_aut, evt_pairs)
    local_alphabet = get_local_events(selected_aut, aut_list)
    
    # Find critical states
    critical_states, semi_critical_states = find_critical_states(selected_aut, local_alphabet)
    
    #combinations = len(critical_states)*len(critical_states.union(semi_critical_states))
    combinations = len(critical_states)*len(semi_critical_states)
    print combinations
    count = 0
    for end_state in critical_states:
        for start_state in semi_critical_states:
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
    
def ticks_to_init(aut, tick):
  distances = {}
  visited = set()
  queue = []
  tup = (0, 0, aut.initial)
  heapq.heappush(queue, tup)
  number = 1
  traceback = None
  while len(queue) != 0:
    distance, throwaway, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = distance
    for edge in state.get_outgoing():
      if edge.succ in visited:
        continue
      newdistance = distance
      if edge.label == tick:
        newdistance += 1
      number += 1
      heapq.heappush(queue, (newdistance,number,edge.succ))
  #TODO deal with the case where the marked state is unreachable
  return distances
  
def ticks_to_marked(aut, tick):
  distances = {}
  visited = set()
  queue = []
  number = 0
  for state in aut.get_states():
    if state.marked:
      tup = (0, number, state)
      heapq.heappush(queue, tup)
      number += 1
  while len(queue) != 0:
    distance, throwaway, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = distance
    for edge in state.get_incoming():
      if edge.pred in visited:
        continue
      newdistance = distance
      if edge.label == tick:
        newdistance += 1
      number += 1
      heapq.heappush(queue, (newdistance,number,edge.pred))
  #TODO deal with the case where the marked state is unreachable
  return distances
  
def ticks_to_marked_crane(aut, tick):
  dictionary = {}
  for state in aut.get_states():
    for edge in state.get_outgoing():
      if edge.label not in dictionary:
        dictionary[edge.label] = set()
      dictionary[edge.label].add(state)
  distances = {}
  for event in dictionary:
    distances[event] = ticks_to_marked_crane_define_marked(aut, tick, dictionary[event])
  return dictionary, distances
  
def ticks_to_marked_crane_define_marked(aut, tick, markedset):
  distances = {}
  visited = set()
  queue = []
  number = 0
  for state in markedset:
    tup = (0, number, state)
    heapq.heappush(queue, tup)
    number += 1
  while len(queue) != 0:
    distance, throwaway, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = distance
    for edge in state.get_incoming():
      if edge.pred in visited:
        continue
      newdistance = distance
      if edge.label == tick:
        newdistance += 1
      number += 1
      heapq.heappush(queue, (newdistance,number,edge.pred))
  #TODO deal with the case where the marked state is unreachable
  return distances
  
  
def astar_heur(distances, state_tuple):
  distance = distances[0][state_tuple[0]]
  for i in range(1, len(state_tuple)):
    newdistance = distances[i][state_tuple[i]]
    distance = newdistance if newdistance > distance else distance
    #distance = distance + newdistance
  return distance
  
def astar_heur_crane(dictionary, distances, state_tuple):
  guess = 0
  for i in range(3, len(state_tuple)):
    state = state_tuple[i]
    if state.marked:
      continue
    currguess = None
    for edge in state.get_outgoing():
      if edge.succ == state:
        continue
      if edge.label not in distances:
        continue
      tempguess = distances[edge.label][state_tuple[0]]
      fromstate = next(iter(dictionary[edge.label]))
      succ = edge.succ
      if not edge.succ.marked:
        for edge in succ.get_outgoing():
          if edge.succ == succ:
            continue
          tempguess += distances[edge.label][fromstate]
      if currguess == None or currguess > tempguess:
        currguess = tempguess
    guess += currguess
  return guess
  
def is_marked(state_tuple):
  for state in state_tuple:
    if not state.marked:
      return False
  return True
  
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
    
def generate_aut_from_path_events(path, alphabet, collection):
  aut = data_structure.Automaton(alphabet.copy(), collection)
  state = aut.add_new_state(len(path) == 0, aut.get_num_states())
  aut.initial = state
  for i in range(len(path)):
    nextstate = aut.add_new_state(i + 1 == len(path), aut.get_num_states())
    event = path[i]
    aut.add_edge_data(state, nextstate, event)
    state = nextstate
  return aut

def generate_aut_from_path_events_weighted(path, alphabet, collection):
  aut = weighted_structure.WeightedAutomaton(alphabet.copy(), collection)
  state = aut.add_new_state(len(path) == 0, aut.get_num_states())
  aut.initial = state
  for i in range(len(path)):
    nextstate = aut.add_new_state(i + 1 == len(path), aut.get_num_states())
    event, weight = path[i]
    aut.add_edge_data(state, nextstate, event, weight)
    state = nextstate
  return aut
  
def astar_search(auts, tick):
  distances_too_marked = []
  state_tuple = []
  visited = set()
  queue = []
  alphabet = set()
  for aut in auts:
    alphabet.update(aut.alphabet)
    distances_too_marked.append(ticks_to_marked(aut, tick))
    state_tuple.append(aut.initial)
  state_tuple = tuple(state_tuple)
  heur_dist = astar_heur(distances_too_marked, state_tuple)
  heapq.heappush(queue, (heur_dist, 0, 0, state_tuple, None))
  link = None
  count = 0
  number = 1
  while len(queue) != 0:
    astar_dist, dist, throw, state_tuple, link = heapq.heappop(queue)
    if (count % 1000 == 0):
      print "count: " + str(count)
      #print "visited: " + str(len(visited))
      #print "heap: " + str(len(queue))
      #print "dist:" + str(dist)
      print "astar_dist:" + str(astar_dist)
    count += 1
    if state_tuple in visited:
      continue
    visited.add(state_tuple)
    if is_marked(state_tuple):
      break
    trans = []
    for state in state_tuple:
      dic = {}
      trans.append(dic)
      for edge in state.get_outgoing():
        dic[edge.label] = edge.succ
    for evt in alphabet:
      succ_tuple = []
      for i in range(len(trans)):
        if evt in auts[i].alphabet:
          if evt in trans[i]:
            succ_tuple.append(trans[i][evt])
          else:
            succ_tuple = None
            break
        else:
          succ_tuple.append(state_tuple[i])
      if succ_tuple == None:
        continue
      newdist = dist
      if evt == tick:
        newdist += 1
      succ_tuple = tuple(succ_tuple)
      new_astar_dist = astar_heur(distances_too_marked, succ_tuple)
      heapq.heappush(queue, (new_astar_dist + newdist, newdist, number, succ_tuple, FrozenLink(link, evt)))
  path = []
  while link != None:
    path.append(link.mEvent)
    link = link.mParent
  path = list(reversed(path))
  pathaut = generate_aut_from_path_events(path, alphabet, auts[0].collection)
  testpath_not_weighted(auts, pathaut, tick)
  return pathaut
  
def astar_crane(auts, tick):
  distances_too_marked = []
  state_tuple = []
  visited = set()
  queue = []
  alphabet = set()
  dictionary, distances = ticks_to_marked_crane(auts[0], tick)
  for aut in auts:
    alphabet.update(aut.alphabet)
    state_tuple.append(aut.initial)
  state_tuple = tuple(state_tuple)
  print state_tuple
  print len(auts)
  heur_dist = astar_heur_crane(dictionary, distances, state_tuple)
  heapq.heappush(queue, (heur_dist, 0, 0, state_tuple, None))
  link = None
  count = 0
  number = 1
  while len(queue) != 0:
    astar_dist, dist, throw, state_tuple, link = heapq.heappop(queue)
    if (count % 1000 == 0):
      print "count: " + str(count)
      #print "visited: " + str(len(visited))
      #print "heap: " + str(len(queue))
      #print "dist:" + str(dist)
      print "astar_dist:" + str(astar_dist)
    count += 1
    if state_tuple in visited:
      continue
    visited.add(state_tuple)
    if is_marked(state_tuple):
      print "is marked"
      print state_tuple
      print count
      break
    trans = []
    for state in state_tuple:
      dic = {}
      trans.append(dic)
      for edge in state.get_outgoing():
        dic[edge.label] = edge.succ
    for evt in alphabet:
      succ_tuple = []
      for i in range(len(trans)):
        if evt in auts[i].alphabet:
          if evt in trans[i]:
            succ_tuple.append(trans[i][evt])
          else:
            succ_tuple = None
            break
        else:
          succ_tuple.append(state_tuple[i])
      if succ_tuple == None:
        continue
      newdist = dist
      if evt == tick:
        newdist += 1
      succ_tuple = tuple(succ_tuple)
      new_astar_dist = astar_heur_crane(dictionary, distances, succ_tuple)
      heapq.heappush(queue, (new_astar_dist + newdist, newdist, number, succ_tuple, FrozenLink(link, evt)))
  path = []
  while link != None:
    path.append(link.mEvent)
    link = link.mParent
  path = list(reversed(path))
  pathaut = generate_aut_from_path_events(path, alphabet, auts[0].collection)
  pathaut.save_as_dot("astarpath.dot")
  testpath_not_weighted(auts, pathaut, tick)
  return pathaut
    
def synchronousproduct(auts, depth):
  initstate = []
  newalphabet = set()
  transmap = []
  transweight = []
  enabled = []
  exectime = -time()
  print "begin transmap"
  for aut in auts:
    newalphabet.update(aut.alphabet)
  for i in range(len(auts)):
    aut = auts[i]
    initstate.append(aut.initial)
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    transweight.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
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
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
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
          if (len(dictionary) % 1000 == 0):
            print len(dictionary)
          tovisit.append(succtuple)
        edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print len(dictionary)
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

def synchronousproductstateweight(auts):
  def calctupleweight(statetuple):
    return sum(auts[i][1][statetuple[i]] for i in xrange(len(auts)))
  initstate = []
  newalphabet = set()
  transmap = []
  transweight = []
  enabled = []
  exectime = -time()
  n_state_weight = {}
  print "begin transmap"
  for aut,_ in auts:
    newalphabet.update(aut.alphabet)
  for i in range(len(auts)):
    print aut
    print aut.initial.marked
    aut, _ = auts[i]
    initstate.append(aut.initial)
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    transweight.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
        enabled[i][state].add(edge.label)
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i][0].alphabet)
    for state in auts[i][0].get_states():
      enabled[i][state].update(nonlocalevents)
  print "end transmap"
  exectime += time()
  print "time: " + str(exectime)
  inittuple = tuple(initstate)
  dictionary = {}
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
  print 'allmarked: ', allmarked(inittuple)
  initstate = aut_sync.add_new_state(allmarked(inittuple), aut_sync.get_num_states())
  n_state_weight[initstate] = calctupleweight(inittuple)
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
        if event not in auts[i][0].alphabet:
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
          n_state_weight[newstate] = calctupleweight(succtuple)
          dictionary[succtuple] = newstate
          if (len(dictionary) % 1000 == 0):
            print len(dictionary)
          tovisit.append(succtuple)
        edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print len(dictionary)
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
  return aut_sync, n_state_weight

def subsetconstructionnotweightedreversestateweight(aut, localevents, state_weight):
  def calcmaxweight(state_tuple):
    return max(map(lambda x: state_weight[x], state_tuple))
  extime = -time()
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  pred_map = calculate_local_reachable_pred(aut, localevents)
  n_state_map = {}
  initialset = set()
  for state in aut.get_states():
    if state.marked:
      initialset.add(state)
  initialset = find_local_reachable(initialset, pred_map)
  initstate = aut_new.add_new_state(aut.initial.marked)
  aut_new.initial = initstate
  n_state_map[initstate] = calcmaxweight(initialset)
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        if edge.label not in localevents:
          preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(preddictionary[event]) != 0):
          targetstateset = preddictionary[event]
          targetstateset = find_local_reachable(targetstateset, pred_map)
          if targetstateset not in dictionary:
            coninit = False
            for state in targetstateset:
              if aut.initial == state:
                coninit = True
                break
            newstate = aut_new.add_new_state(coninit, aut_new.get_num_states())
            n_state_map[newstate] = calcmaxweight(targetstateset)
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  aut_new.reduce(True, True)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new, n_state_map
  
def synchronousproduct_weighted(auts, depth):
  initstate = []
  newalphabet = set()
  transmap = []
  eventweight = {}
  enabled = []
  exectime = -time()
  print "begin transmap"
  for aut in auts:
    newalphabet.update(aut.alphabet)
  for i in range(len(auts)):
    aut = auts[i]
    initstate.append(aut.initial)
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        eventweight[edge.label] = edge.weight
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
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
        edgestoadd.append(weighted_structure.WeightedEdge(dictionary[statetuple], dictionary[succtuple], event, eventweight[event]))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
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
  
def synchronousproduct_supervisor(auts, requirements, depth):
  extime = -time()
  initstate = []
  newalphabet = set()
  transmap = []
  transweight = []
  enabled = []
  exectime = -time()
  temp = []
  for aut in auts:
    temp.append((aut, False))
  for aut in requirements:
    temp.append((aut, True))
  auts = temp
  print "begin transmap"
  for aut in auts:
    newalphabet.update(aut[0].alphabet)
  for i in range(len(auts)):
    aut = auts[i][0]
    initstate.append(aut.initial)
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    transweight.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
        enabled[i][state].add(edge.label)
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i][0].alphabet)
    for state in auts[i][0].get_states():
      enabled[i][state].update(nonlocalevents)
  print "end transmap"
  exectime += time()
  print "time: " + str(exectime)
  inittuple = tuple(initstate)
  dictionary = {}
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
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
  bad_states = []
  while len(tovisit) != 0:
    count += 1
    statetuple = tovisit.pop()
    calccurrenab -= time()
    currenabled = None
    compenabled = None
    requirementenabled = None
    for i in range(len(enabled)):
      if currenabled == None:
        currenabled = set(enabled[i][statetuple[i]])
      else:
        currenabled.intersection_update(enabled[i][statetuple[i]])
      if auts[i][1]:
        if requirementenabled == None:
          requirementenabled = set(enabled[i][statetuple[i]])
        else:
          requirementenabled.intersection_update(enabled[i][statetuple[i]])
      else:
        if compenabled == None:
          compenabled = set(enabled[i][statetuple[i]])
        else:
          compenabled.intersection_update(enabled[i][statetuple[i]])
    is_bad = False
    for evt in compenabled:
      if not evt.controllable and evt not in requirementenabled:
         bad_states.append(dictionary[state_tuple])
         is_bad = True
         dictionary[state_tuple].marked = False
         break
    if is_bad:
      continue
    calccurrenab += time()
    for event in currenabled:
      hassuccs = True
      successorlists = []
      indexs = []
      for i in range(len(transmap)):
        indexs.append(0)
        if event not in auts[i][0].alphabet:
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
        edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
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
  # Time to do coreachability search
  coreachable = set()
  bad_states = set(bad_states)
  not_done = []
  for state in aut_sync.get_states():
    if state.marked:
      coreachable.add(state)
      not_done.append(state)
  while not_done:
    state = not_done.pop()
    for edge in state.get_incoming():
      if edge.pred not in coreachable:
        coreachable.add(edge.pred)
        not_done.append(edge.pred)
  if len(coreachable) == aut_sync.get_num_states():
    extime += time()
    if handle:
      handle.write("supsynctime: " + str(extime) + "\t\tstates: " + str(aut_sync.get_num_states()) \
        + "\t\tedges: " + str(aut_sync.get_num_edges()) + "\n")
    return aut_sync, bad_states
  
  non_coreachable = set()
  for state in aut_sync.get_states():
    if state in coreachable:
      continue
    if state in bad_states:
      continue
      
    pred_coreachable = False
    for edge in state.get_incoming():
      if edge.pred in coreachable:
        pred_coreachable = True
        break
      if pred_coreachable:
        bad_states.add(state)
        state.marked = False
        #possibly optimize this later
        for edge in list(state.get_outgoing()):
          aut_sync.remove_edge(edge)
      else:
        non_coreachable.add(state)
        
  coreachable.clear()
  
  for state in non_coreachable:
    if state not in bad_states:
      aut_sync.remove_state(state)
  
  del non_coreachable
  
  illegal_states = set()
  uncontrollables = set([evt for evt in aut_sync.alphabet if not evt.controllable])
  pred_map = calculate_local_reachable_pred(aut_sync, uncontrollables)
  for state in bad_states:
    illegal_states.update(find_local_reachable([state], pred_map))
  if illegal_states == bad_states:
    extime += time()
    if handle:
      handle.write("supsynctime: " + str(extime) + "\t\tstates: " + str(aut_sync.get_num_states()) \
        + "\t\tedges: " + str(aut_sync.get_num_edges()) + "\n")
    return aut_sync, bad_states
  
  assert bad_states.issubset(illegal_states)
  
  bad_states = set()
  for state in illegal_states:
    found_good_state = False
    for edge in state.get_incoming():
      if edge.pred not in illegal_states:
        found_good_state = True
        break
        
      if found_good_state:
        bad_states.add(state)
        state.marked = False
        for edge in list(state.get_outgoing):
          aut_sync.removed_edge(edge)
      else:
        aut_sync.remove_state(state)
      
  illegal_states.clear()
  exectime += time()
  print "time: " + str(exectime)
  #if depth == 5:
    #auia = aieia
  extime += time()
  if handle:
    handle.write("supsynctime: " + str(extime) + "\t\tstates: " + str(aut_sync.get_num_states()) \
      + "\t\tedges: " + str(aut_sync.get_num_edges()) + "\n")
  return aut_sync, bad_states

def prune_long_path(aut, tick, weight):
  for state in aut.get_states():
    aut.state_names[state.number] = state.number
  distances = {}
  visited = set()
  queue = []
  tup = (0, 0, aut.initial)
  heapq.heappush(queue, tup)
  number = 1
  while len(queue) != 0:
    distance, throwaway, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = (distance)
    for edge in state.get_outgoing():
      newdistance = distance
      if edge.succ in visited:
        continue
      if edge.label == tick:
        newdistance += 1
      number += 1
      heapq.heappush(queue, (newdistance,number,edge.succ))
  #TODO deal with the case where the marked state is unreachable
  rev_distances = {}
  visited = set()
  queue = []
  for state in aut.get_states():
    if (state.marked):
      tup = (0, 0, state)
      heapq.heappush(queue, tup)
  number = 1
  while len(queue) != 0:
    distance, throwaway, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    rev_distances[state] = (distance)
    for edge in state.get_incoming():
      newdistance = distance
      if edge.pred in visited:
        continue
      if edge.label == tick:
        newdistance += 1
      number += 1
      heapq.heappush(queue, (newdistance,number,edge.pred))
  to_remove = []
  buckets = {}
  bestofbest = 100000
  for state in aut.get_states():
    bestposs = distances[state] + rev_distances[state]
    bestofbest = min(bestofbest, bestposs)
    #if (bestposs > weight):
    #  to_remove.append(state)
    bucket = bestposs# // 10
    if bucket not in buckets:
      buckets[bucket] = 0
    buckets[bucket] = buckets[bucket] + 1
  if (bestofbest > 100):
    for state in aut.get_states():
      if (distances[state] + rev_distances[state]) > bestofbest:
        to_remove.append(state)
  keys = list(buckets.keys())
  keys = sorted(keys)
  for i in keys:
    print str(i) + ":" + str(buckets[i])
  raw_input("press enter")
  for state in to_remove:
    aut.remove_state(state)
  aut.reduce(True, True)
  return aut

    
def tickdijkstrapath(aut, tick):
  print aut
  for state in aut.get_states():
    aut.state_names[state.number] = state.number
  aut.save_as_dot("anneal.dot")
  distances = {}
  visited = set()
  queue = []
  tup = (0, 0, None, aut.initial)
  heapq.heappush(queue, tup)
  number = 1
  traceback = None
  while len(queue) != 0:
    distance, throwaway, prededge, state = heapq.heappop(queue)
    if (state in visited):
      continue
    visited.add(state)
    distances[state] = (distance, prededge)
    if state.marked:
      traceback = state
      break
    for edge in state.get_outgoing():
      newdistance = distance
      if edge.succ in visited:
        continue
      if edge.label == tick:
        newdistance += 1
      number += 1
      heapq.heappush(queue, (newdistance,number,edge,edge.succ))
  #TODO deal with the case where the marked state is unreachable
  tokeep = []
  while traceback != aut.initial:
    distance, edge = distances[traceback]
    tokeep.append(edge)
    traceback = edge.pred
    print edge.label.name
  for state in aut.get_states():
    for edge in list(state.get_outgoing()):
      if edge not in tokeep:
        aut.remove_edge(edge)
  aut.reduce(True, True)
  return aut

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
        
def prochack(aut,local_alphabet):
  edgestoremove = []
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
    removenonpick = False
    for edge in state.get_outgoing():
      if edge.label in local_alphabet and "pick" in edge.label.name:
        removenonpick = True
    if removenonpick:
      for edge in state.get_outgoing():
        if edge.label not in local_alphabet or "pick" not in edge.label.name:
          edgestoremove.append(edge)
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  
def prochack2(aut,local_alphabet):
  edgestoremove = []
  for state in aut.get_states():
    removenonproc = False
    tokeep = None
    for edge in state.get_outgoing():
      if edge.label in local_alphabet:
        removenonproc = True
        tokeep = edge
    if tokeep != None:
      for edge in state.get_outgoing():
        #if edge != tokeep and edge.label not in local_alphabet:
        if edge.label not in local_alphabet:
          edgestoremove.append(edge)
      continue
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  
def prochacktick(aut, local_alphabet, tick):
  edgestoremove = []
  for state in aut.get_states():
    removenonproc = False
    tokeep = None
    for edge in state.get_outgoing():
      if edge.label in local_alphabet:
        removenonproc = True
        tokeep = edge
    if tokeep != None:
      for edge in state.get_outgoing():
        if edge == tick:
          edgestoremove.append(edge)
      continue
  for edge in edgestoremove:
    aut.remove_edge(edge)
  aut.reduce(True, True)
  
def neverempty(aut):
  if aut.initial.marked:
    new_state = aut.add_new_state(True, aut.get_num_states())
    for edge in list(aut.initial.get_incoming()):
      aut.remove_edge(edge)
      aut.add_edge_data(edge.pred, new_state, edge.label)
    aut.initial.marked = False
  for state in aut.get_states():
    if state.marked:
      print
      print
      print
      print
      print "is marked"
      print
      print
      print
      print
      toremove = []
      for edge in state.get_outgoing():
        print "removing edge"
        toremove.append(edge)
      for edge in toremove:
        aut.remove_edge(edge)

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
    unfolded.save_as_dot("unfolded.dot")

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


def get_greedy_time_optimal_sup(aut, eventdata, heap_len):

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_correctly(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False)
    wsup = weighted_supervisor.reduce_automaton_greedy_correctly(aut, weight_map, eventdata,
                                                heap_len, 300)
    return wsup
    
def get_greedy_time_optimal_sup_vector(aut, eventdata, heap_len):

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_weight.compute_state_vector_weights_vector(aut, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,300,False)
    wsup = weighted_supervisor.reduce_automaton_greedy_vector(aut, weight_map, eventdata,
                                                heap_len, 300)
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
    
class hashcachingtuple(tuple):
  
  def __init__(self, values):
    super(hashcachingtuple, self).__init__(values)
    self.hashcache = super(hashcachingtuple, self).__hash__()
    
  def __hash__(self):
    return self.hashcache
    
def synchronousproduct_crane(auts, depth, incoming_events, tick):
  initstate = []
  newalphabet = set()
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
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
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
    hasnonincoming = set()
    needwait = False
    incomingsuccs = {}
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
      if "move" in event.name and event not in incoming_events:
        hasnonincoming.add(event.name[1])
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
      if event in incoming_events:
        incomingsuccs[event] = successors
      else:
        for succtuple in successors:
          if event == tick and statetuple != succtuple:
            needwait = True
          if succtuple not in dictionary:
            newstate = aut_sync.add_new_state(allmarked(succtuple), aut_sync.get_num_states())
            dictionary[succtuple] = newstate
            tovisit.append(succtuple)
          edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
          #print aut_sync
        addstatetime += time()
    for event in incomingsuccs:
      if needwait or event.name[1] in hasnonincoming:
        #print "hasnon"
        continue
      successors = incomingsuccs[event]
      for succtuple in successors:
        if succtuple not in dictionary:
          newstate = aut_sync.add_new_state(allmarked(succtuple), aut_sync.get_num_states())
          dictionary[succtuple] = newstate
          tovisit.append(succtuple)
        edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
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
  #aut_sync.add_edges(edgestoadd)
  for edge in edgestoadd:
    aut_sync.add_edge(edge)
  print "end add edges"
  exectime += time()
  print "time: " + str(exectime)
  #if depth == 5:
    #auia = aieia      
  return aut_sync
  
def synchronousproduct_crane2(auts, depth, cranepositions, slots, tick):
  initstate = []
  newalphabet = set()
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
        enabled[i][state].add(edge.label)
  positions = set()
  for event in newalphabet:
    #print event
    if "move" in event.name:
      positions.add(int(event.name.split("-")[-2]))
  positions.add(99999999)
  positions = sorted(list(positions))
  segments = [0]
  j = 0
  k = 0
  for i in range(1, slots+1):
    segments.append(k)
    if positions[j] == i:
      if j + 1 < len(positions) and positions[j + 1] == positions[j] + 1:
        k += 1
      j += 1
  print segments
  for i, slot in enumerate(cranepositions):
    cranepositions[i] = segments[slot]
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i].alphabet)
    for state in auts[i].get_states():
      enabled[i][state].update(nonlocalevents)
  print "end transmap"
  exectime += time()
  print "time: " + str(exectime)
  inittuple = (tuple(initstate), tuple(cranepositions))
  dictionary = {}
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
  initstate = aut_sync.add_new_state(allmarked(inittuple[0]), aut_sync.get_num_states())
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
    stateandseg = tovisit.pop()
    statetuple, cranepositions = stateandseg
    calccurrenab -= time()
    currenabled = set(enabled[0][statetuple[0]])
    #print currenabled
    #for i in range(1,len(enabled)):
    #  currenabled.intersection_update(enabled[i][statetuple[i]])
    #print currenabled
    calccurrenab += time()
    hasnonincoming = set()
    needwait = False
    incomingsuccs = {}
    for event in newalphabet:
      if "move" in event.name:
        #print "checking: " + str(event.name)
        #print "at segment: " + str(statetosegment[statetuple])
        crane = int(event.name[1])-1
        seg = segments[int(event.name.split("-")[-2])]
        if cranepositions[crane] != seg:
          #print "removing: " + str(event.name)
          continue
      if "pick" in event.name or "drop" in event.name:
        #print "checking: " + str(event.name)
        #print "at segment: " + str(statetosegment[statetuple])
        crane = int(event.name[1])-1
        seg = segments[int(event.name.split("-")[-3])]
        if cranepositions[crane] != seg:
          #print "removing: " + str(event.name)
          continue
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
        #print "at segment: " + str(statetosegment[statetuple])
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
        if event == tick and statetuple != succtuple:
          needwait = True
        cranepositionsprime = None
        if "move" in event.name:
          cranepositionsprime = list(cranepositions)
          crane = int(event.name[1])-1
          cranepositionsprime[crane] = segments[int(event.name.split("-")[-1])]
          cranepositionsprime = tuple(cranepositionsprime)
          #print "event: " + str(event.name)
          #print "segment: " + str(cranepositions) + " to " + str(cranepositionsprime)
        else:
          cranepositionsprime = cranepositions
        succtuple = (succtuple, cranepositionsprime)
        if succtuple not in dictionary:
          newstate = aut_sync.add_new_state(allmarked(succtuple[0]), aut_sync.get_num_states())
          dictionary[succtuple] = newstate
          tovisit.append(succtuple)
        edgestoadd.append(data_structure.Edge(dictionary[stateandseg], dictionary[succtuple], event))
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
  #aut_sync.add_edges(edgestoadd)
  for edge in edgestoadd:
    aut_sync.add_edge(edge)
  print "end add edges"
  exectime += time()
  print "time: " + str(exectime)
  #if depth == 5:
    #auia = aieia      
  return aut_sync
  
def tau_abstracted_greedy_supervisor_recurse_crane(comp_list, evt_pairs, orig_alphabet, depth, compnums, tau, tick, nonprog, resultfile, subcon = False):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      comp_list[0].save_as_dot("lastaut.dot")
      return tickdijkstrapath(comp_list[0], tick)
    else:
      print comp_list[0]
      old_aut = get_automaton_copy_not_weighted(comp_list[0])#copy.deepcopy(comp_list[0])
      #if depth > 1:
        #prochack2(comp_list[0],get_local_events(comp_list[0], comp_list))
        #comp_list[0] = prune_wait(comp_list[0], tick, depth)
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = prune_wait_non_prog_full2(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))#get_local_events(comp_list[0], comp_list))
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      local = get_local_events(comp_list[0], comp_list)
      local.add(tau)
      local.difference_update(set([tick]))
      #prune_crane(comp_list[0])
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #comp_list[0] = prune_wait_local(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_local_memory(comp_list[0], local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
      print "before subcons"
      print comp_list[0]
      #if subcon:
       # comp_list[0] = subsetconstructionnotweighted(comp_list[0], local, depth)
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #print nonprog[depth]
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, get_prog(comp_list[0]))
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, nonprog[depth])
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))
      #comp_list[0] = prune_wait_number(comp_list[0], tick, depth, 2)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      if previousaut == comp_list[0]:
        print "didn't subset construct"
        comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
        #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
        comp_list[0].alphabet.add(tau)
        comp_list[0] = abstraction.model_conversion_language(comp_list[0], comp_list[0].alphabet.difference(local))
        comp_list[0].alphabet.add(tau)
        comp_list[0] = abstraction.automaton_abstraction_refined(comp_list[0])
        #comp_list[0] = abstraction.abstraction_refined(comp_list[0], comp_list[0].alphabet.difference(local))
        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      else:
        comp_list[0].save_as_dot("beforehopcroft" + str(depth) + ".dot")
        #comp_list[0] = hopcroft(comp_list[0])
        comp_list[0].alphabet.add(tau)
        comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
        comp_list[0].save_as_dot("afterhopcroft" + str(depth) + ".dot")
      #comp_list[0] = prunebadticks(comp_list[0], tick, tau, depth)
      #abstraction.automaton_abstraction(comp_list[0])
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      #reinsert_tick(comp_list[0], tick)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      comp_list[0].name = old_aut.name
      if False: #depth >= 1:
        path = astar_crane(comp_list, tick)
      else :
        tocompose = []
        incoming = set()
        for aut in comp_list:
          print aut.name
        if depth == 0:
          for aut in comp_list:
            if aut.name != None and aut.name.startswith("D"):
              tocompose.append(aut)
        #elif not comp_list[1].name.startswith("CS"):
          #tocompose.append(comp_list[0])
          #tocompose.append(comp_list[1])
        else:
          tocompose.append(comp_list[0])
          slot = int(comp_list[1].name[2:])
          nextaut = None
          for aut in comp_list[1:]:
            if not aut.name.startswith("SC"):
              continue
            alllocal = True
            for event in aut.alphabet:
              #print event.name
              #print event.name.split("-")
              if ("drop" in event.name or "pick" in event.name) and int(event.name.split("-")[-3]) >= slot:
                alllocal = False
                break
            if alllocal:
              nextaut = aut
              break
          if nextaut == None:
            tocompose.append(comp_list[1])
            if comp_list[2].name.startswith("CS"):
              print comp_list[1].name
              print comp_list[1].name[2:]
              for event in comp_list[1].alphabet:
                if "move" in event.name:                
                  slots = event.name.split("-")[-2:]
                  slots = [int(slots[0]), int(slots[1])]
                  print str(slots) + " " + str(slot)
                  if slots[1] == slot and slots[1] < slots[0]:
                    incoming.add(event)
              #for event in comp_list[0].alphabet:
              #  if ("drop" in event.name or "pick" in event.name) and int(event.name.split("-")[-3]) > slot:
              #    incoming.add(event)
          else:
            tocompose.append(nextaut)
          #for aut in comp_list[2:-1] :
          #  if aut.name != None and aut.name.startswith("SC") and len(aut.alphabet.intersection(comp_list[1].alphabet).difference(set([tau]))) != 0:
          #    print aut.alphabet.intersection(comp_list[0].alphabet).difference(set([tau]))
          #    tocompose.append(aut)
        print "tocompose"
        for aut in tocompose:
          print aut.name
        print incoming
        new_plant = synchronousproduct_crane2(tocompose, depth, [1,30], 30, tick)
        new_plant.save_as_dot("newplant" + str(depth) + ".dot")
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        if len(tocompose) > 1 and tocompose[1].name.startswith("SC"):
          state = tocompose[1].initial
          tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
          pick1, pick2, drop1, drop2 = None, None, None, None
          for edge in state.get_outgoing():
            if edge.succ != state:
              nextstate = edge.succ
              if edge.label.name.startswith("C1"):
                pick1 = edge.label
              else:
                pick2 = edge.label
          for state in aut.get_states():
            if state.marked:
              #for edge in state.get_incoming():
              #  if edge.succ != state:
              #    state = edge.pred
              #    break
              break
          for edge in state.get_incoming():
            if edge.pred != state:
              if edge.label.name.startswith("C1"):
                drop1 = edge.label
              else:
                drop2 = edge.label
          prune_impossible_events_crane(new_plant, pick1, pick2, drop1, drop2)
        #  nonprog = set()
        #  nonprog.add(pick1)
        #  nonprog.add(pick2)
        #  new_plant = prune_wait_non_prog_full2(new_plant, tick, depth, nonprog)#get_local_events(comp_list[0], comp_list))
        resultfile.write("comp size: " + str(new_plant.get_num_states()))
        resultfile.write("\n")
        #new_plant = synchronousproduct(comp_list[0:2], depth)
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        new_plant.name = str(depth)
        print "synchronous before reduce"
        print new_plant
        #neverempty(new_plant)
        new_plant.reduce(True, True)
        print "synchronous after reduce"
        print new_plant
        print "depth:" + str(depth)
        #print comp_list[0].alphabet
        #print comp_list[1].alphabet
        #comp_list.pop(0)
        #comp_list.pop(0)
        #comp_list = comp_list[compnums[depth]:len(comp_list)]
        for aut in tocompose:
          print "to be removed: " + str(aut.name)
          for i, oaut in enumerate(comp_list):
            if aut is oaut:
              print "removing"
              comp_list.pop(i)
              break
        print len(comp_list)
        comp_list.insert(0,new_plant)
        new_plant.save_as_dot("newplant" + str(depth) + ".dot")
        print "get new path"
        path = tau_abstracted_greedy_supervisor_recurse_crane(comp_list, evt_pairs, orig_alphabet, depth+1, compnums, tau, tick, nonprog, resultfile, tocompose[1].name.startswith("SC"))
      print "path returned"
      if path == None:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project_not_weighted(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
      old_aut.save_as_dot("G1" + str(depth) + ".dot")
      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      return (get_common_path(old_aut, path, resultfile))
      #patholdsync = product.n_ary_unweighted_product(tosync)
      #print "looks like: "
      #patholdsync.reduce(True, True)
      #print patholdsync
      #patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      #return restrictpath(patholdsync)
      
def convert_orders_to_auts(craneorders, eventmap, alphabets, collection):
  auts =[]
  for i, orders in enumerate(craneorders):
    events = []
    for name in orders:
      events.append(eventmap["C" + str(i + 1) + name])
    auts.append(generate_aut_from_path_events(events, alphabets[i], collection))
  return auts
      
def count_tick(path, tick):
  state = path.initial
  count = 0
  while not state.marked:
    for edge in state.get_outgoing():
      if edge.label == tick:
        count += 1
      state = edge.succ
  return count
      
def get_shortest_path(auts, tick, craneorders, eventmap, alphabets):
  print "craneorders"
  print craneorders
  orderings = convert_orders_to_auts(craneorders, eventmap, alphabets, auts[0].collection)
  tocompose = list(auts) + orderings
  for i, aut in enumerate(tocompose):
    aut.save_as_dot("aut" + str(i).zfill(2) + ".dot")
  sync = product.n_ary_unweighted_product(tocompose)
  for aut in orderings:
    aut.save_as_dot("order.dot")
    aut.clear()
  path = tickdijkstrapath(sync, tick)
  return path, count_tick(path, tick)
      
def simulated_anealling(auts, events, eventmap, cranes, tick):
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
      
def tau_abstracted_greedy_supervisor_recurse_crane2(comp_list, evt_pairs, orig_alphabet, depth, compnums, tau, tick, nonprog, resultfile, subcon = False):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      comp_list[0].save_as_dot("lastaut.dot")
      return tickdijkstrapath(comp_list[0], tick)
    else:
      print comp_list[0]
      old_aut = get_automaton_copy_not_weighted(comp_list[0])#copy.deepcopy(comp_list[0])
      #if depth > 1:
        #prochack2(comp_list[0],get_local_events(comp_list[0], comp_list))
        #comp_list[0] = prune_wait(comp_list[0], tick, depth)
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = prune_wait_non_prog_full2(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))#get_local_events(comp_list[0], comp_list))
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      local = get_local_events(comp_list[0], comp_list)
      local.add(tau)
      local.difference_update(set([tick]))
      #prune_crane(comp_list[0])
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #comp_list[0] = prune_wait_local(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
      print "before subcons"
      print comp_list[0]
      #if subcon:
      #comp_list[0] = subsetconstructionnotweighted(comp_list[0], local, depth)
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #print nonprog[depth]
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, get_prog(comp_list[0]))
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, nonprog[depth])
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))
      #comp_list[0] = prune_wait_number(comp_list[0], tick, depth, 2)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      if previousaut == comp_list[0]:
        print "didn't subset construct"
        comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
        #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
        comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(local))
        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      else:
        comp_list[0].save_as_dot("beforehopcroft" + str(depth) + ".dot")
        #comp_list[0] = hopcroft(comp_list[0])
        comp_list[0].alphabet.add(tau)
        comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
        comp_list[0].save_as_dot("afterhopcroft" + str(depth) + ".dot")
      #comp_list[0] = prunebadticks(comp_list[0], tick, tau, depth)
      #abstraction.automaton_abstraction(comp_list[0])
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      #reinsert_tick(comp_list[0], tick)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      comp_list[0].name = old_aut.name
      if False: #depth >= 1:
        path = astar_crane(comp_list, tick)
      else :
        tocompose = []
        incoming = set()
        for aut in comp_list:
          print aut.name
        if depth == 0:
          for aut in comp_list:
            if aut.name != None and aut.name.startswith("D"):
              tocompose.append(aut)
        else:
          tocompose.append(comp_list[0])
          bestlocal = -1
          bestaut = None
          for aut in comp_list[1:]:
            if aut.name.startswith("CS"):
              continue
            numlocal = len(get_local_events(aut, comp_list[1:]))
            if bestlocal < numlocal:
              bestaut, bestlocal = aut, numlocal
          if bestaut != None:
            tocompose.append(bestaut)
            for aut in comp_list[1:]:
              if not aut.name.startswith("CS"):
                continue
              if len(aut.alphabet.intersection(bestaut.alphabet).difference([tau])) != 0:
                tocompose.append(aut)
          else:
            tocompose.append(comp_list[0])
          for aut in tocompose:
            if aut.name.startswith("CS"):
              slot = int(aut.name[2:])
              for event in aut.alphabet:
                if "move" in event.name:
                  slots = event.name.split("-")[-2:]
                  slots = [int(slots[0]), int(slots[1])]
                  print event
                  print str(slots) + " " + str(slot)
                  if slots[1] == slot:
                    incoming.add(event)
          #for aut in comp_list[2:-1] :
          #  if aut.name != None and aut.name.startswith("SC") and len(aut.alphabet.intersection(comp_list[1].alphabet).difference(set([tau]))) != 0:
          #    print aut.alphabet.intersection(comp_list[0].alphabet).difference(set([tau]))
          #    tocompose.append(aut)
        print "tocompose"
        for aut in tocompose:
          print aut.name
        print incoming
        new_plant = synchronousproduct_crane2(tocompose, depth, [1], 30, tick)
        new_plant.save_as_dot("newplant" + str(depth) + ".dot")
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        if len(tocompose) > 1 and tocompose[1].name.startswith("SC"):
          state = tocompose[1].initial
          tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
          pick1, pick2, drop1, drop2 = None, None, None, None
          for edge in state.get_outgoing():
            if edge.succ != state:
              nextstate = edge.succ
              if edge.label.name.startswith("C1"):
                pick1 = edge.label
              else:
                pick2 = edge.label
          for state in aut.get_states():
            if state.marked:
              #for edge in state.get_incoming():
              #  if edge.succ != state:
              #    state = edge.pred
              #    break
              break
          for edge in state.get_incoming():
            if edge.pred != state:
              if edge.label.name.startswith("C1"):
                drop1 = edge.label
              else:
                drop2 = edge.label
          #prune_impossible_events_crane(new_plant, pick1, pick2, drop1, drop2)
          #nonprog = set()
          #nonprog.add(pick1)
          #nonprog.add(pick2)
          #new_plant = prune_wait_non_prog_full2(new_plant, tick, depth, nonprog)#get_local_events(comp_list[0], comp_list))
        resultfile.write("comp size: " + str(new_plant.get_num_states()))
        resultfile.write("\n")
        #new_plant = synchronousproduct(comp_list[0:2], depth)
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        new_plant.name = str(depth)
        print "synchronous before reduce"
        print new_plant
        #neverempty(new_plant)
        new_plant.reduce(True, True)
        print "synchronous after reduce"
        print new_plant
        print "depth:" + str(depth)
        #print comp_list[0].alphabet
        #print comp_list[1].alphabet
        #comp_list.pop(0)
        #comp_list.pop(0)
        #comp_list = comp_list[compnums[depth]:len(comp_list)]
        for aut in tocompose:
          print "to be removed: " + str(aut.name)
          for i, oaut in enumerate(comp_list):
            if aut is oaut:
              print "removing"
              comp_list.pop(i)
              break
        print len(comp_list)
        comp_list.insert(0,new_plant)
        new_plant.save_as_dot("newplantpath" + str(depth) + ".dot")
        print "get new path"
        path = tau_abstracted_greedy_supervisor_recurse_crane2(comp_list, evt_pairs, orig_alphabet, depth+1, compnums, tau, tick, nonprog, resultfile)
      print "path returned"
      if path == None:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project_not_weighted(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
      old_aut.save_as_dot("G1" + str(depth) + ".dot")
      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      return (get_common_path(old_aut, path, resultfile))
      #patholdsync = product.n_ary_unweighted_product(tosync)
      #print "looks like: "
      #patholdsync.reduce(True, True)
      #print patholdsync
      #patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      #return restrictpath(patholdsync)
      
def tau_abstracted_greedy_supervisor_recurse_crane3(comp_list, evt_pairs, orig_alphabet, depth, compnums, tau, tick, nonprog, resultfile, subcon = False):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      comp_list[0].save_as_dot("lastaut.dot")
      return tickdijkstrapath(comp_list[0], tick)
    else:
      print comp_list[0]
      old_aut = get_automaton_copy_not_weighted(comp_list[0])#copy.deepcopy(comp_list[0])
      #if depth > 1:
        #prochack2(comp_list[0],get_local_events(comp_list[0], comp_list))
        #comp_list[0] = prune_wait(comp_list[0], tick, depth)
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = prune_wait_non_prog_full2(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))#get_local_events(comp_list[0], comp_list))
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      local = get_local_events(comp_list[0], comp_list)
      local.add(tau)
      local.difference_update(set([tick]))
      #prune_crane(comp_list[0])
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #comp_list[0] = prune_wait_local(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
      print "before subcons"
      print comp_list[0]
      #if subcon:
      #comp_list[0] = subsetconstructionnotweighted(comp_list[0], local, depth)
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #print nonprog[depth]
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, get_prog(comp_list[0]))
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, nonprog[depth])
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))
      #comp_list[0] = prune_wait_number(comp_list[0], tick, depth, 2)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      if previousaut == comp_list[0]:
        print "didn't subset construct"
        comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
        #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
        comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(local))
        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      else:
        comp_list[0].save_as_dot("beforehopcroft" + str(depth) + ".dot")
        #comp_list[0] = hopcroft(comp_list[0])
        comp_list[0].alphabet.add(tau)
        comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
        comp_list[0].save_as_dot("afterhopcroft" + str(depth) + ".dot")
      #comp_list[0] = prunebadticks(comp_list[0], tick, tau, depth)
      #abstraction.automaton_abstraction(comp_list[0])
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      #reinsert_tick(comp_list[0], tick)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      comp_list[0].name = old_aut.name
      if comp_list[1].name.startswith("SC"):
        events = set()
        for aut in comp_list[1:]:
          for event in aut.alphabet:
            if "pick" in event.name:
              events.add(event.name[2:])
        events = list(events)
        print events
        simulated_anealling(comp_list, events, comp_list[0].collection.events, 2, tick)
      else :
        tocompose = []
        incoming = set()
        for aut in comp_list:
          print aut.name
        tocompose.append(comp_list[0])
        #for aut in comp_list[1:]:
        #  if not aut.name.startswith("SC"):
        #    tocompose.append(aut)
        tocompose.append(comp_list[1])
        #for aut in comp_list[2:-1] :
        #  if aut.name != None and aut.name.startswith("SC") and len(aut.alphabet.intersection(comp_list[1].alphabet).difference(set([tau]))) != 0:
        #    print aut.alphabet.intersection(comp_list[0].alphabet).difference(set([tau]))
        #    tocompose.append(aut)
        print "tocompose"
        for aut in tocompose:
          print aut.name
        print incoming
        #new_plant = product.n_ary_unweighted_product(tocompose)
        new_plant = synchronousproduct_crane2(tocompose, depth, [1,10], 10, tick)
        new_plant.save_as_dot("newplant" + str(depth) + ".dot")
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        if len(tocompose) > 1 and tocompose[1].name.startswith("SC"):
          state = tocompose[1].initial
          tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
          pick1, pick2, drop1, drop2 = None, None, None, None
          for edge in state.get_outgoing():
            if edge.succ != state:
              nextstate = edge.succ
              if edge.label.name.startswith("C1"):
                pick1 = edge.label
              else:
                pick2 = edge.label
          for state in aut.get_states():
            if state.marked:
              #for edge in state.get_incoming():
              #  if edge.succ != state:
              #    state = edge.pred
              #    break
              break
          for edge in state.get_incoming():
            if edge.pred != state:
              if edge.label.name.startswith("C1"):
                drop1 = edge.label
              else:
                drop2 = edge.label
          #prune_impossible_events_crane(new_plant, pick1, pick2, drop1, drop2)
          #nonprog = set()
          #nonprog.add(pick1)
          #nonprog.add(pick2)
          #new_plant = prune_wait_non_prog_full2(new_plant, tick, depth, nonprog)#get_local_events(comp_list[0], comp_list))
        resultfile.write("comp size: " + str(new_plant.get_num_states()))
        resultfile.write("\n")
        #new_plant = synchronousproduct(comp_list[0:2], depth)
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        new_plant.name = str(depth)
        print "synchronous before reduce"
        print new_plant
        #neverempty(new_plant)
        new_plant.reduce(True, True)
        print "synchronous after reduce"
        print new_plant
        print "depth:" + str(depth)
        #print comp_list[0].alphabet
        #print comp_list[1].alphabet
        #comp_list.pop(0)
        #comp_list.pop(0)
        #comp_list = comp_list[compnums[depth]:len(comp_list)]
        for aut in tocompose:
          print "to be removed: " + str(aut.name)
          for i, oaut in enumerate(comp_list):
            if aut is oaut:
              print "removing"
              comp_list.pop(i)
              break
        print len(comp_list)
        comp_list.insert(0,new_plant)
        new_plant.save_as_dot("newplantpath" + str(depth) + ".dot")
        print "get new path"
        #if not comp_list[1].name.startswith("SC"):
        path = tau_abstracted_greedy_supervisor_recurse_crane3(comp_list, evt_pairs, orig_alphabet, depth+1, compnums, tau, tick, nonprog, resultfile)
      print "path returned"
      if path == None:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project_not_weighted(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
      old_aut.save_as_dot("G1" + str(depth) + ".dot")
      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      return (get_common_path(old_aut, path, resultfile))
      #patholdsync = product.n_ary_unweighted_product(tosync)
      #print "looks like: "
      #patholdsync.reduce(True, True)
      #print patholdsync
      #patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      #return restrictpath(patholdsync)
      
def priority_heuristic(track, requirements, tick):
  print "priority_heuristic"
  unselected_requirements = []
  selected_requirements = []
  for i, req in enumerate(requirements):
    print req.name
    pick, drop = None, None
    for evt in req.alphabet:
      if "pick" in evt.name:
        pick = evt.name
      elif "drop" in evt.name:
        drop = evt.name
    dropslot = int(drop.split("-")[-3])
    pickslot = int(pick.split("-")[-3])
    distance = abs(pickslot - dropslot)
    heapq.heappush(unselected_requirements, (distance, i, req))
  path = []
  while unselected_requirements:
    throw1, throw2, req = heapq.heappop(unselected_requirements)
    selected_requirements.append(req)
    tocompose = [track]
    tocompose.extend(selected_requirements)
    if len(path) != 0:
      tocompose.append(generate_aut_from_path_events(path, set(path), track.collection))
    comp_aut = synchronousproduct(tocompose, 0)
    for aut in selected_requirements:
      if not aut.name.startswith("SC"):
        continue
      state = aut.initial
      #tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
      pick1, pick2, drop1, drop2 = None, None, None, None
      for edge in state.get_outgoing():
        if edge.succ != state:
          nextstate = edge.succ
          if edge.label.name.startswith("C1"):
            pick1 = edge.label
          else:
            pick2 = edge.label
      for state in aut.get_states():
        if state.marked:
          #for edge in state.get_incoming():
          #  if edge.succ != state:
          #    state = edge.pred
          #    break
          break
      for edge in state.get_incoming():
        if edge.pred != state:
          if edge.label.name.startswith("C1"):
            drop1 = edge.label
          else:
            drop2 = edge.label
      print (pick1, pick2, drop1, drop2)
      prune_impossible_events_crane(comp_aut, pick1, pick2, drop1, drop2)
    path_aut = tickdijkstrapath(comp_aut, tick)
    print "weight: " + str(count_tick(path_aut, tick))
    state = path_aut.initial
    path = []
    while not state.marked:
      for edge in state.get_outgoing():
        state = edge.succ
        if "pick" in edge.label.name:
          path.append(edge.label)
        continue
        
#def prune_drop(aut, events):
#  for state in aut.get_states():
#    has_event = False
#    for edge in state.get_outgoing():
#      if edge.label in events:
#        has_event = True
#        break
#    if has_event:
#      for edge in state.get_outgoing():
#        if edge.label not in events:
#          aut.remove_edge(edge)
def prune_drop(aut, events):
  for state in aut.get_states():
    cranes = []
    for edge in state.get_outgoing():
      if edge.label in events:
        cranes.append(edge.label.name[:2])
    if cranes:
      cranes = set(cranes)
      for edge in state.get_outgoing():
        if edge.label not in events and edge.label.name[:2] in cranes:
          aut.remove_edge(edge)
          
def prune_observer_proj(aut, events):
  dictionary = {}
  for state in aut.get_states():
    dictionary[state] = find_local_reachable_and_enabled(state, events)
  for state in aut.get_states():
    for edge in list(state.get_outgoing()):
      if edge.label in events:
        if dictionary[state][2] and not dictionary[edge.succ][2]:
          aut.remove_edge(edge)
        elif len(dictionary[edge.succ][1]) < len(dictionary[state][1]):
          aut.remove_edge(edge)

def tau_abstracted_greedy_supervisor_recurse_crane4(comp_list, evt_pairs, orig_alphabet, depth, compnums, tau, tick, nonprog, resultfile, subcon = False):
    if len(comp_list) == 1:
      print "last automaton"
      print comp_list[0]
      comp_list[0].save_as_dot("lastaut.dot")
      return tickdijkstrapath(comp_list[0], tick)
    else:
      print comp_list[0]
      old_aut = get_automaton_copy_not_weighted(comp_list[0])#copy.deepcopy(comp_list[0])
      #if depth > 1:
        #prochack2(comp_list[0],get_local_events(comp_list[0], comp_list))
        #comp_list[0] = prune_wait(comp_list[0], tick, depth)
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = prune_wait_non_prog_full2(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))#get_local_events(comp_list[0], comp_list))
      print "start abstraction"
      print comp_list[0]
      previousaut = comp_list[0]
      local = get_local_events(comp_list[0], comp_list)
      local.add(tau)
      local.difference_update(set([tick]))
      #prune_crane(comp_list[0])
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #comp_list[0] = prune_wait_local(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
      print "before subcons"
      print comp_list[0]
      #if subcon:
      #comp_list[0] = subsetconstructionnotweighted(comp_list[0], local, depth)
      #comp_list[0] = prune_wait(comp_list[0], tick, depth)
      #print nonprog[depth]
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, get_prog(comp_list[0]))
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, nonprog[depth])
      #comp_list[0] = prune_wait_non_prog_full(comp_list[0], tick, depth, comp_list[0].alphabet.difference(set([tick])))
      #comp_list[0] = prune_wait_number(comp_list[0], tick, depth, 2)
      #comp_list[0] = prune_wait_local_full(comp_list[0], tick, depth, local)
      #maketausequal(comp_list[0], orig_alphabet, eventdata)
      print comp_list[0]
      if previousaut == comp_list[0]:
        print "didn't subset construct"
        comp_list[0].save_as_dot("beforebisim" + str(depth) + ".dot")
        #comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(get_local_events(comp_list[0], comp_list)))
        comp_list[0] = abstraction.abstraction(comp_list[0], comp_list[0].alphabet.difference(local))
        comp_list[0].save_as_dot("afterbisim" + str(depth) + ".dot")
      else:
        comp_list[0].save_as_dot("beforehopcroft" + str(depth) + ".dot")
        #comp_list[0] = hopcroft(comp_list[0])
        comp_list[0].alphabet.add(tau)
        comp_list[0] = abstraction.automaton_abstraction(comp_list[0])
        #comp_list[0] = abstraction.automaton_abstraction(comp_list[0], get_local_events(comp_list[0], comp_list))
        comp_list[0].save_as_dot("afterhopcroft" + str(depth) + ".dot")
      #comp_list[0] = prunebadticks(comp_list[0], tick, tau, depth)
      #abstraction.automaton_abstraction(comp_list[0])
      print "before reduce"
      print comp_list[0]
      print "after reduce"
      comp_list[0].reduce(True, True)
      #reinsert_tick(comp_list[0], tick)
      print comp_list[0]
      print "end abstraction"
      print comp_list[1].name
      print len(comp_list)
      comp_list[0].name = old_aut.name
      if comp_list[1].name.startswith("SC"):
        events = set()
        for aut in comp_list[1:]:
          for event in aut.alphabet:
            if "pick" in event.name:
              events.add(event.name[2:])
        events = list(events)
        print events
        priority_heuristic(comp_list[0], comp_list[1:], tick)
      else :
        tocompose = []
        incoming = set()
        for aut in comp_list:
          print aut.name
        tocompose.append(comp_list[0])
        for aut in comp_list[1:]:
          if not aut.name.startswith("SC"):
            tocompose.append(aut)
        #tocompose.append(comp_list[1])
        #for aut in comp_list[2:-1] :
        #  if aut.name != None and aut.name.startswith("SC") and len(aut.alphabet.intersection(comp_list[1].alphabet).difference(set([tau]))) != 0:
        #    print aut.alphabet.intersection(comp_list[0].alphabet).difference(set([tau]))
        #    tocompose.append(aut)
        print "tocompose"
        for aut in tocompose:
          print aut.name
        print incoming
        new_plant = product.n_ary_unweighted_product(tocompose)
        #new_plant = synchronousproduct_crane2(tocompose, depth, [1,10], 10, tick)
        new_plant.save_as_dot("newplant" + str(depth) + ".dot")
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        if len(tocompose) > 1 and tocompose[1].name.startswith("SC"):
          state = tocompose[1].initial
          tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
          pick1, pick2, drop1, drop2 = None, None, None, None
          for edge in state.get_outgoing():
            if edge.succ != state:
              nextstate = edge.succ
              if edge.label.name.startswith("C1"):
                pick1 = edge.label
              else:
                pick2 = edge.label
          for state in aut.get_states():
            if state.marked:
              #for edge in state.get_incoming():
              #  if edge.succ != state:
              #    state = edge.pred
              #    break
              break
          for edge in state.get_incoming():
            if edge.pred != state:
              if edge.label.name.startswith("C1"):
                drop1 = edge.label
              else:
                drop2 = edge.label
          #prune_impossible_events_crane(new_plant, pick1, pick2, drop1, drop2)
          #nonprog = set()
          #nonprog.add(pick1)
          #nonprog.add(pick2)
          #new_plant = prune_wait_non_prog_full2(new_plant, tick, depth, nonprog)#get_local_events(comp_list[0], comp_list))
        resultfile.write("comp size: " + str(new_plant.get_num_states()))
        resultfile.write("\n")
        #new_plant = synchronousproduct(comp_list[0:2], depth)
        comp_list[1].save_as_dot("other" + str(depth) + ".dot")
        new_plant.name = str(depth)
        print "synchronous before reduce"
        print new_plant
        #neverempty(new_plant)
        new_plant.reduce(True, True)
        print "synchronous after reduce"
        print new_plant
        print "depth:" + str(depth)
        #print comp_list[0].alphabet
        #print comp_list[1].alphabet
        #comp_list.pop(0)
        #comp_list.pop(0)
        #comp_list = comp_list[compnums[depth]:len(comp_list)]
        for aut in tocompose:
          print "to be removed: " + str(aut.name)
          for i, oaut in enumerate(comp_list):
            if aut is oaut:
              print "removing"
              comp_list.pop(i)
              break
        print len(comp_list)
        comp_list.insert(0,new_plant)
        new_plant.save_as_dot("newplantpath" + str(depth) + ".dot")
        print "get new path"
        #if not comp_list[1].name.startswith("SC"):
        path = tau_abstracted_greedy_supervisor_recurse_crane4(comp_list, evt_pairs, orig_alphabet, depth+1, compnums, tau, tick, nonprog, resultfile)
      print "path returned"
      if path == None:
        return path
      path.save_as_dot("beforproj" + str(depth) + ".dot")
      path = project_not_weighted(path, orig_alphabet)
      #print "alphabet"
      #print path.alphabet
      tosync = [old_aut, path]
      old_aut.save_as_dot("G1" + str(depth) + ".dot")
      path.save_as_dot("G2" + str(depth) + ".dot")
      #old_aut.collection = tosync
      #path.collection = tosync
      return (get_common_path(old_aut, path, resultfile))
      #patholdsync = product.n_ary_unweighted_product(tosync)
      #print "looks like: "
      #patholdsync.reduce(True, True)
      #print patholdsync
      #patholdsync.save_as_dot("sync" + str(depth) + ".dot")
      #return restrictpath(patholdsync)
      
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
    
def calc_path_from_num(aut, num_paths, random_num):
  state = aut.initial
  path_events = []
  while True:
    if state.marked:
      if random_num == 1:
        break
      else:
        random_num -= 1
    found_edge = False
    for edge in state.get_outgoing():
      if random_num <= num_paths[edge.succ]:
        state = edge.succ
        path_events.append(edge.label)
        found_edge = True
        break
      random_num -= num_paths[edge.succ]
    assert found_edge
  return path_events
    
def uniform_polling(aut, eventdata, heap_len, resultfile):
  stack = [state for state in aut.get_states() if len(state.get_outgoing()) == 0]
  uncovered_transitions = {}
  for state in aut.get_states():
    uncovered_transitions[state] = len(state.get_outgoing())
  num_paths = {}
  best = None
  while stack:
    state = stack.pop()
    paths = 1 if state.marked else 0
    for edge in state.get_outgoing():
      paths += num_paths[edge.succ]
    num_paths[state] = paths
    for edge in state.get_incoming():
      uncovered_transitions[edge.pred] = uncovered_transitions[edge.pred] - 1
      if uncovered_transitions[edge.pred] == 0:
        stack.append(edge.pred)
  total_strings = num_paths[aut.initial]
  print "total_strings: " + str(total_strings)
  sys_random = random.SystemRandom()
  path = sys_random.randint(1, total_strings)
  path_events = calc_path_from_num(aut, num_paths, path)
  bestpath = path_events
  best = testpath([aut], generate_aut_from_path_events(path_events, aut.alphabet, aut.collection), eventdata, heap_len, resultfile)
  curr_span = best
  bit_length = total_strings.bit_length()
  #default_mut = float(bit_length) /4
  #for i in range(3):
  #  T = 1 / (i + 1)
  #  while T >= 0:
  #    dist = int(default_mut * T)
  #    mutant = 0
  #    for i in xrange(dist):
  #      bit = random.randint(0, bit_length-1)
  #      num = 1 << bit
  #      mutant = mutant | num
  #    new_path = (path ^ mutant) % total_strings
  #    #dist = .25 * T
  #    #dist = total_strings * dist
  #    #dist = sys_random.randint(-dist, dist)
  #    #new_path = (path + dist) % total_strings
  #    path_events = calc_path_from_num(aut, num_paths, new_path)
  #    span = testpath([aut], generate_aut_from_path_events(path_events, aut.alphabet, aut.collection), eventdata, heap_len, resultfile)
  #    if span < best:
  #      bestpath = path_events
  #      best = span
  #    if span < curr_span:
  #      path = new_path
  #      curr_span = span
  #    #elif sys_random.random() < T:
  #      #print "rand cross"
  #      #path = new_path
  #      #curr_span = span
  #    print "span: " + str(span) + " curr_span: " + str(curr_span) + " best: " + str(best)
  #    T -= 0.0001
  default_mut = float(bit_length) /4
  change = True
  #while change:
  #  change = False
  #  for i in xrange(bit_length):
  #    for j in xrange(1, 2):
  #      mutant = j << i
  #      new_path = (path ^ mutant)
  #      if new_path > total_strings:
  #        continue
  #      #dist = .25 * T
  #      #dist = total_strings * dist
  #      #dist = sys_random.randint(-dist, dist)
  #      #new_path = (path + dist) % total_strings
  #      path_events = calc_path_from_num(aut, num_paths, new_path)
  #      span = testpath([aut], generate_aut_from_path_events(path_events, aut.alphabet, aut.collection), eventdata, heap_len, resultfile)
  #      if span < best:
  #        bestpath = path_events
  #        best = span
  #      if span < curr_span:
  #        path = new_path
  #        curr_span = span
  #        change = True
  #      #elif sys_random.random() < T:
  #        #print "rand cross"
  #        #path = new_path
  #        #curr_span = span
  #      print "span: " + str(span) + " curr_span: " + str(curr_span) + " best: " + str(best)
  i = 0
  while True:
    i += 1
    random_num = sys_random.randint(1, total_strings)
    state = aut.initial
    path_events = []
    while True:
      if state.marked:
        if random_num == 1:
          break
        else:
          random_num -= 1
      found_edge = False
      for edge in state.get_outgoing():
        if random_num <= num_paths[edge.succ]:
          state = edge.succ
          path_events.append(edge.label)
          found_edge = True
          break
        random_num -= num_paths[edge.succ]
      assert found_edge
    print "i: " + str(i)
    span = testpath([aut], generate_aut_from_path_events(path_events, aut.alphabet, aut.collection), eventdata, heap_len, resultfile)
    if best == None or span < best:
      best = span
      resultfile.write(str(i) + ": " + str(best) + "\n")
      resultfile.flush()
  print "best: " + str(best)
  #genetic_alg(aut, total_strings, num_paths, eventdata, heap_len, resultfile)
  
def genetic_alg(aut, total_strings, num_paths, eventdata, heap_len, resultfile):
  pop_num = 100
  cull = int(pop_num * .5)
  pop = [random.randint(1, total_strings) for i in range(pop_num)]
  for i, val in enumerate(pop):
    path_events = calc_path_from_num(aut, num_paths, val)
    span = testpath([aut], generate_aut_from_path_events(path_events, aut.alphabet, aut.collection), eventdata, heap_len, resultfile)
    pop[i] = (span, val)
  best = None
  bit_length = total_strings.bit_length()
  while True:
    pop = sorted(pop)
    if best == None or pop[0][0] < best:
      best = pop[0][0]
    arena = range(1, pop_num + 1)
    m = sum(arena)
    remset = set()
    for i in xrange(cull):
      torem = random.randint(1, m)
      for j in xrange(len(arena) -1, -1, -1):
        if torem <= arena[j]:
          m -= arena[j]
          arena[j] = 0
          remset.add(j)
          break
        assert(j != 0)
        torem -= arena[j]
    print remset
    pop = [tup for i, tup in enumerate(pop) if i in remset]
    arena = list(reversed(range(1, len(pop) + 1)))
    m = sum(arena)
    new_pop = list(pop)
    for i in xrange(cull):
      breeder = random.randint(1, m)
      first = None
      for j in xrange(0, len(arena)):
        if breeder <= arena[j]:
          n = m - arena[j]
          first = j
          break
        assert(j != len(arena)-1)
        breeder -= arena[j]
      breeder = random.randint(1, n)
      second = None
      for j in xrange(0, len(arena)):
        if j == first:
          assert(j != len(arena)-1)
          continue
        if breeder <= arena[j]:
          second = j
          break
        assert(j != len(arena)-1)
        breeder -= arena[j]
      offspring = breed(pop[first][1], pop[second][1], bit_length)
      path_events = calc_path_from_num(aut, num_paths, offspring % total_strings)
      span = testpath([aut], generate_aut_from_path_events(path_events, aut.alphabet, aut.collection), eventdata, heap_len, resultfile)
      new_pop.append((span, offspring))
    assert len(new_pop) == pop_num
    pop = new_pop
    print best
    
def breed(father, mother, bit_length):
  breakpoint = random.randint(1, bit_length-2)
  mask = 1 << breakpoint
  mask -= 1
  bits = mask
  #bits = random.getrandbits(bit_length)
  father_part = bits & father
  bits = ~bits
  mother_part = bits & mother
  offspring = father_part | mother_part
  mutant = 0
  for i in range(bit_length/50):
    bit = random.randint(0, bit_length-1)
    num = 1 << bit
    mutant = mutant | num
  offspring = mutant ^ offspring
  #print bin(father)
  #print bin(mother)
  #print bin(offspring)
  return offspring
    
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
    
def deadlock_detection(state_tuple, auts):
  waiting_on = {}
  outgoing_events = {}
  blocked_by = {}
  for i in range(len(state_tuple)):
    state, aut = state_tuple[i], auts[i]
    outgoing_events[(i, state)] = set()
    waiting_on[(i, state)] = set()
    active = set()
    for edge in state.get_outgoing():
      active.add(edge.label)
      if edge.succ != state:
        outgoing_events[(i, state)].add(edge.label)
    for event in aut.alphabet.difference(active):
      if event not in blocked_by:
        blocked_by[event] = set()
      blocked_by[event].add(i)
  blocked = set()
  for i in range(len(state_tuple)):
    state, aut = state_tuple[i], auts[i]
    not_blocked = False
    for event in outgoing_events[(i, state)]:
      if event not in blocked_by:
        not_blocked = True
        break
    if not_blocked:
      continue
    blocked.add((i, state))
    
    
def random_walker_comp(auts, weighted = False):
  initstate = []
  newalphabet = set()
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
        transweight[i][state, edge.label] = edge.weight
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
  path = []
  currstate = inittuple
  while not allmarked(currstate):
    statetuple = currstate
    currenabled = set(enabled[0][statetuple[0]])
    for i in range(1,len(enabled)):
      currenabled.intersection_update(enabled[i][statetuple[i]])
    possible_edges = []
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
      for succtuple in successors:
        if weighted:
          weight = max(transweight[index][(state, event)] for i, state in enumerate(statetuple))
          possible_edges.append(((event, weight), succtuple))
        else:
          possible_edges.append((event, succtuple))
        #print aut_sync
    edge = random.sample(possible_edges, 1)[0]
    path.append(edge[0])
    path.append(edge[0])
    currstate = edge[1]
    #if count % 500 == 0:
    #  print "succcalctime" +str(succcalctime)
    #  print "addstatetime" +str(addstatetime)
    #  print "calccurrenab" +str(calccurrenab)
  if weighted:
    return generate_aut_from_path_events_weighted(path, newalphabet, auts[0].collection)
  else:
    return generate_aut_from_path_events(path, newalphabet, auts[0].collection)

def convert_automata_to_to_be_named(aut):
  aut = get_automaton_copy_not_weighted(aut)
  base_aut = data_structure.Automaton(aut.alphabet, aut.collection)
  base_aut.initial = base_aut.add_new_state(False)
  base_aut.initial.languages = set()
  base_aut.language_aut = aut
  for state in aut.get_states():
    base_aut.initial.languages.add(state)
  aut.initial = None
  return base_aut

def convert_automata_to_to_be_named_base(aut):
  aut = get_automaton_copy_not_weighted(aut)
  base_aut = data_structure.Automaton(aut.alphabet, aut.collection)
  base_aut.initial = base_aut.add_new_state(False)
  base_aut.initial.languages = frozenset([aut.initial])
  dictionary = {}
  dictionary[aut.initial] = base_aut.initial
  tovisit = [aut.initial]
  edges_to_add = []
  while len(tovisit) != 0:
    pred = tovisit.pop()
    for edge in pred.get_outgoing():
      succ = edge.succ
      if succ not in dictionary:
        tovisit.append(succ)
        newstate = base_aut.add_new_state(False)
        newstate.languages = frozenset([succ])
        dictionary[succ] = newstate
      edges_to_add.append(data_structure.Edge(dictionary[pred], dictionary[succ], edge.label))
  base_aut.language_aut = aut
  base_aut.add_edges(edges_to_add)
  base_aut.name = aut.name
  aut.initial = None
  return base_aut

def synchronousproduct_to_be_named(auts, init_tuples):
  newalphabet = set()
  transmap = []
  enabled = []
  exectime = -time()
  print "begin transmap"
  for aut in auts:
    newalphabet.update(aut.alphabet)
  for i in range(len(auts)):
    aut = auts[i]
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
        enabled[i][state].add(edge.label)
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i].alphabet)
    for state in auts[i].get_states():
      enabled[i][state].update(nonlocalevents)
  print "end transmap"
  exectime += time()
  print "time: " + str(exectime)
  dictionary = {}
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
  tovisit = []
  for tuple in init_tuples:
    state = aut_sync.add_new_state(allmarked(tuple))
    dictionary[tuple] = state
    tovisit.append(tuple)
  #initstate = aut_sync.add_new_state(allmarked(inittuple), aut_sync.get_num_states())
  aut_sync.initial = None
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
          if (len(dictionary) % 1000 == 0):
            print len(dictionary)
          tovisit.append(succtuple)
        edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print len(dictionary)
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
  return aut_sync, dictionary

def synchronousproduct_to_be_named_base(auts):
  newalphabet = set()
  transmap = []
  enabled = []
  exectime = -time()
  print "begin transmap"
  for aut in auts:
    newalphabet.update(aut.alphabet)
  for i in range(len(auts)):
    aut = auts[i]
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge.succ)
        enabled[i][state].add(edge.label)
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i].alphabet)
    for state in auts[i].get_states():
      enabled[i][state].update(nonlocalevents)
  print "end transmap"
  exectime += time()
  print "time: " + str(exectime)
  dictionary = {}
  aut_sync = data_structure.Automaton(newalphabet, aut.collection)
  inittuple = tuple([aut.initial for aut in auts])
  initstate = aut_sync.add_new_state(allmarked(inittuple), aut_sync.get_num_states())
  dictionary[inittuple] = initstate
  tovisit = [inittuple]
  aut_sync.initial = initstate
  transitions = 0
  edgestoadd = []
  exectime = -time()
  print "add edges"
  succcalctime = 0
  addstatetime = 0
  calccurrenab = 0
  count = 0
  def iterate_list(tup):
    while (tup != None):
      yield tup[0]
      tup = tup[1]
  def get_languages(state_tuple, num_states = len(auts), perms = [None]):
    if num_states == 0:
      return set([tuple(iterate_list(perm)) for perm in perms])
    num_states -= 1
    new_perms = []
    for lang in state_tuple[num_states].languages:
      for perm in perms:
        new_perms.append((lang, perm))
    return get_languages(state_tuple, num_states, new_perms)
  initstate.languages = get_languages(inittuple)
  languages = set(initstate.languages)
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
          if (len(dictionary) % 1000 == 0):
            print len(dictionary)
          tovisit.append(succtuple)
          newstate.languages = get_languages(succtuple)
          languages.update(newstate.languages)
        edgestoadd.append(data_structure.Edge(dictionary[statetuple], dictionary[succtuple], event))
        #print aut_sync
      addstatetime += time()
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print len(dictionary)
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
  aut_sync.language_aut, dictionary = synchronousproduct_to_be_named([aut.language_aut for aut in auts], languages)
  for state in aut_sync.get_states():
    state.languages = frozenset([dictionary[lang] for lang in state.languages])
  return aut_sync

def subsetconstruction_to_be_named(aut, localevents, initialstates):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  succ_map = calculate_local_reachable_succ(aut, localevents)
  dictionary = {}
  tovisit = []
  initstatemap = {}
  for init in initialstates:
    initset = set([init])
    initset = find_local_reachable(initset, succ_map)
    state = aut_new.add_new_state(containsmarked(initset))
    dictionary[initset] = state
    initstatemap[init] = state
    tovisit.append(initset)
  aut_new.initial = None
  edgestoadd = []
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = find_local_reachable(targetstateset, succ_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  aut_new.add_edges(edgestoadd)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new, initstatemap

def simplify_to_be_named(aut, local):
  print "state before subcons: " + str(aut.language_aut.get_num_states())
  #aut.language_aut,dictionary = subsetconstruction_to_be_named(aut.language_aut, local, aut.initial.languages)
  #aut.initial.languages = set(dictionary.values())
  revaut, dictionary = subsetconstructionnotweightedreverse_to_be_named(aut.language_aut, local,
                                                                        aut.initial.languages)
  print "state after subcons: " + str(aut.language_aut.get_num_states())
  #cProfile.runctx('hopcroft2(aut.language_aut)', globals(), locals())
  #aut.language_aut,dictionary = hopcroft2(aut.language_aut)
  #aut.initial.languages = set([dictionary[lang] for lang in aut.initial.languages])
  aut.language_aut, aut.initial.languages = subsetconstructionnotweightedreverse_to_be_named2(revaut, dictionary)
  print "state before subcons: " + str(aut.language_aut.get_num_states())

def simplify_to_be_named_base(aut, local):
  print "state before subcons: " + str(aut.language_aut.get_num_states())
  name = aut.name
  #aut.language_aut,dictionary = subsetconstruction_to_be_named(aut.language_aut, local, aut.initial.languages)
  #aut.initial.languages = set(dictionary.values())
  langstates = set()
  for state in aut.get_states():
    langstates.update(state.languages)
  revlangaut,dictionary =\
    subsetconstructionnotweightedreverse_to_be_named(aut.language_aut, local, langstates)
  langaut, dictionary = subsetconstructionnotweightedreverse_to_be_named2(revlangaut, dictionary)
  #langaut, dictionary = subsetconstruction_to_be_named(aut.language_aut, local, langstates)
  #langaut, dictionary2 = hopcroft2(langaut)
  for state in aut.get_states():
    state.languages = frozenset([dictionary[lang] for lang in state.languages])
    #state.languages = frozenset([dictionary2[dictionary[lang]] for lang in state.languages])
  aut = subsetconstructionnotweightedreverse_base_automaton(aut, local)
  aut = subsetconstructionnotweightedreverse_base_automaton2(aut, local)
  #aut = subsetconstruction_to_be_named_base(aut, local)
  #aut, _ = hopcroft2_to_be_named(aut)
  aut.language_aut = langaut
  aut.name = aut.name
  return aut


def subsetconstructionnotweightedreverse_to_be_named(aut, localevents, states_of_interest):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  pred_map = calculate_local_reachable_pred(aut, localevents)
  #succ_map = calculate_local_reachable_succ(aut, localevents)
  stateswithinterest = {}
  for state in states_of_interest:
    stateswithinterest[state] = set()
  initialset = set()
  for state in aut.get_states():
    if state.marked:
      initialset.add(state)
  initialset = find_local_reachable(initialset, pred_map)
  initstate = aut_new.add_new_state(False)
  for state in initialset:
    if state in stateswithinterest:
      stateswithinterest[state].add(initstate)
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        if edge.label not in localevents:
          preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(preddictionary[event]) != 0):
          targetstateset = preddictionary[event]
          targetstateset = find_local_reachable(targetstateset, pred_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(False)
            for state in targetstateset:
              if state in stateswithinterest:
                stateswithinterest[state].add(newstate)
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new, stateswithinterest

def subsetconstructionnotweightedreverse_to_be_named2(aut, stateswithinterest):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet, aut.collection)
  stateinterestdictionary = {}
  dictionary = {}
  tovisit = []

  statesets = set([frozenset(stateswithinterest[key]) for key in stateswithinterest])
  for stateset in statesets:
    new_state = aut_new.add_new_state(aut.initial in stateset)
    dictionary[stateset] = new_state
    tovisit.append(stateset)
  for state in stateswithinterest:
    stateinterestdictionary[state] = dictionary[frozenset(stateswithinterest[state])]
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if (len(preddictionary[event]) != 0):
        targetstateset = frozenset(preddictionary[event])
        if targetstateset not in dictionary:
          coninit = False
          for state in targetstateset:
            if aut.initial == state:
              coninit = True
              break
          newstate = aut_new.add_new_state(coninit)
          dictionary[targetstateset] = newstate
          tovisit.append(targetstateset)
          if (aut_new.get_num_states() % 1000 == 0):
            print aut_new.get_num_states()
          #if (aut_new.get_num_states() >= aut.get_num_states()):
           # return aut
        #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
        edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new, stateinterestdictionary

def subsetconstructionnotweightedreverse_base_automaton(aut, localevents):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  pred_map = calculate_local_reachable_pred(aut, localevents)
  #succ_map = calculate_local_reachable_succ(aut, localevents)
  stateswithlang = {}
  for state in aut.get_states():
    for lang in state.languages:
      if lang not in stateswithlang:
        stateswithlang[lang] = []
      stateswithlang[lang].append(state)
  dictionary = {}
  tovisit = []
  for lang, stateset in stateswithlang.iteritems():
    stateset = frozenset(stateset)
    if stateset not in dictionary:
      new_state = aut_new.add_new_state(aut.initial in stateset)
      dictionary[stateset] = new_state
      new_state.languages = set([lang])
      tovisit.append(stateset)
    else:
      dictionary[stateset].languages.add(lang)
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        if edge.label not in localevents:
          preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(preddictionary[event]) != 0):
          targetstateset = preddictionary[event]
          targetstateset = find_local_reachable(targetstateset, pred_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(aut.initial in targetstateset)
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new

def subsetconstructionnotweightedreverse_base_automaton2(aut, localevents):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  pred_map = calculate_local_reachable_pred(aut, localevents)
  #succ_map = calculate_local_reachable_succ(aut, localevents)
  initstateset = frozenset([state for state in aut.get_states() if state.marked])
  initstate = aut_new.add_new_state(False)
  aut_new.initial = initstate
  initstate.languages = set()
  for state in initstateset:
    if hasattr(state, 'languages'):
      initstate.languages.update(state.languages)
  dictionary = {}
  dictionary[initstateset] = initstate
  tovisit = [initstateset]
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    preddictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        preddictionary[event] = set()
    for state in stateset:
      for edge in state.get_incoming():
        if edge.label not in localevents:
          preddictionary[edge.label].add(edge.pred)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(preddictionary[event]) != 0):
          targetstateset = preddictionary[event]
          targetstateset = find_local_reachable(targetstateset, pred_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(False)
            newstate.languages = set()
            for state in targetstateset:
              if hasattr(state, 'languages'):
                newstate.languages.update(state.languages)
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new

def subsetconstruction_to_be_named_base(aut, localevents):
  extime = -time()
  #if aut.get_num_states() > 20000:
   # return aut
  coll = aut.collection
  #has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)
  #if (has_tau):
    #localevents.add(coll.events['tau'])
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  #for event in localevents:
    #aut_new.alphabet.remove(event)
  succ_map = calculate_local_reachable_succ(aut, localevents)
  initialset = set([aut.initial])
  initialset = find_local_reachable(initialset, succ_map)
  initstate = aut_new.add_new_state(containsmarked(initialset),aut_new.get_num_states())
  aut_new.initial = initstate
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = find_local_reachable(targetstateset, succ_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  aut_new.add_edges(edgestoadd)
  extime += time()
  for stateset, newstate in dictionary.iteritems():
    langs = set()
    for state in stateset:
      langs.update(state.languages)
    newstate.languages = frozenset(langs)
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new

def subsetconstructionnotweightedstateweight(aut, localevents, state_weight):
  def calcmaxweight(state_tuple):
    return max(map(lambda x: state_weight[x], state_tuple))
  extime = -time()
  aut_new = data_structure.Automaton(aut.alphabet.difference(localevents), aut.collection)
  succ_map = calculate_local_reachable_succ(aut, localevents)
  n_state_map = {}
  initialset = set([aut.initial])
  initialset = find_local_reachable(initialset, succ_map)
  initstate = aut_new.add_new_state(containsmarked(initialset))
  aut_new.initial = initstate
  n_state_map[initstate] = calcmaxweight(initialset)
  dictionary = {}
  dictionary[initialset] = initstate
  tovisit = [initialset]
  edgestoadd = []
  print"revsubstart"
  while len(tovisit) != 0:
    stateset = tovisit.pop()
    succdictionary = {}
    for event in aut.alphabet:
      if event not in localevents:
        succdictionary[event] = set()
    for state in stateset:
      for edge in state.get_outgoing():
        if edge.label not in localevents:
          succdictionary[edge.label].add(edge.succ)
    for event in aut.alphabet:
      if event not in localevents:
        if (len(succdictionary[event]) != 0):
          targetstateset = succdictionary[event]
          targetstateset = find_local_reachable(targetstateset, succ_map)
          if targetstateset not in dictionary:
            newstate = aut_new.add_new_state(containsmarked(targetstateset), aut_new.get_num_states())
            n_state_map[newstate] = calcmaxweight(targetstateset)
            dictionary[targetstateset] = newstate
            tovisit.append(targetstateset)
            if (aut_new.get_num_states() % 1000 == 0):
              print aut_new.get_num_states()
            #if (aut_new.get_num_states() >= aut.get_num_states()):
             # return aut
          #aut_new.add_edge_data(dictionary[stateset], dictionary[targetstateset], event)
          edgestoadd.append(data_structure.Edge(dictionary[stateset], dictionary[targetstateset], event))
  print"revsubend"
  aut_new.add_edges(edgestoadd)
  aut_new.reduce(True, True)
  extime += time()
  if handle:
    handle.write("subsettime: " + str(extime) + "\t\tstates: " + str(aut_new.get_num_states()) \
      + "\t\tedges: " + str(aut_new.get_num_edges()) + "\n")
  return aut_new, n_state_map

def calculate_longest_path(aut, state_weight, weight_function):
  print 'start longest'
  aut.reduce(True, True)
  state_incoming = {}
  state_best = collections.defaultdict(lambda : (-1, None))
  #visited = set()
  for state in aut.get_states():
    state_incoming[state] = len(state.get_incoming())
  state_best[aut.initial] = (state_weight[aut.initial], None)
  tovisit = [aut.initial]
  while tovisit:
    state = tovisit.pop()
    if state.marked:
      break
    w = state_best[state][0]
    for e in state.get_outgoing():
      bw, _ = state_best[e.succ]
      state_incoming[e.succ] -= 1
      if state_incoming[e.succ] == 0:
        tovisit.append(e.succ)
      nw = w + state_weight[e.succ]
      if bw < nw:
        state_best[e.succ] = (nw, e)
  if not state.marked:
    return None
  path = []
  while aut.initial != state:
    _, e = state_best[state]
    path.append((e.label, weight_function[e.label]))
    state = e.pred
  path.reverse()
  print 'end longest'
  return generate_aut_from_path_events_weighted(path, aut.alphabet, aut.collection)

def calculate_longest_path2(auts, weight_function):
  print 'start longest'
  visited = set()
  path = []
  prevstates = []
  new_alphabet = set()
  for aut,_ in auts:
    new_alphabet.update(aut.alphabet)
  state_incoming = {}
  statetuple = [aut.initial for aut, _ in auts]
  visited.add(tuple(statetuple))
  while not allmarked(statetuple):
    stateenabled = set()
    #print statetuple
    for s in statetuple:
      stateenabled.update([e.label for e in s.get_outgoing()])
    successors = {}
    for e in stateenabled:
      successors[e] = ([], 0)
    for i,s in enumerate(statetuple):
      covered = set()
      for e in s.get_outgoing():
        l, w = successors[e.label]
        l.append(e.succ)
        w += auts[i][1][e.succ]
        successors[e.label] = (l, w)
        covered.add(e.label)
      sce = stateenabled.difference(covered)
      #print sce
      for e in sce:
        if e not in auts[i][0].alphabet:
          l, w = successors[e]
          l.append(s)
          w += auts[i][1][s]
          successors[e] = (l, w)
    bestsuccessor, bestevent, bw = None, None, -1
    #print successors
    for e in successors:
      st, w = successors[e]
      if len(st) != len(auts) or tuple(st) in visited:
        continue
      if bw < w:
        bestsuccessor, bestevent, bw = st, e, w
    if bestsuccessor == None:
      statetuple = prevstates.pop()
      e, _ = path.pop()
      if e not in auts[0][0].alphabet:
        while path and path[-1][0] not in auts[0][0].alphabet:
          #print len(path)
          statetuple = prevstates.pop()
          e = path.pop()
      continue
    path.append((bestevent, weight_function[bestevent]))
    prevstates.append(statetuple)
    statetuple = bestsuccessor
    visited.add(tuple(bestsuccessor))
  print 'end longest'
  return generate_aut_from_path_events_weighted(path, new_alphabet, aut.collection), len(visited)

def calculate_longest_path2_process(auts, weight_function, process_event):
  print 'start longest'
  visited = set()
  path = []
  prevstates = []
  new_alphabet = set()
  for aut,_ in auts:
    new_alphabet.update(aut.alphabet)
  statetuple = [aut.initial for aut, _ in auts]
  visited.add((tuple(statetuple), False))
  progressed = False
  while not progressed or not allmarked(statetuple):
    stateenabled = set()
    #print statetuple
    for s in statetuple:
      stateenabled.update([e.label for e in s.get_outgoing()])
    successors = {}
    for e in stateenabled:
      successors[e] = ([], 0)
    for i,s in enumerate(statetuple):
      covered = set()
      for e in s.get_outgoing():
        l, w = successors[e.label]
        l.append(e.succ)
        w += auts[i][1][e.succ]
        successors[e.label] = (l, w)
        covered.add(e.label)
      sce = stateenabled.difference(covered)
      #print sce
      for e in sce:
        if e not in auts[i][0].alphabet:
          l, w = successors[e]
          l.append(s)
          w += auts[i][1][s]
          successors[e] = (l, w)
    bestsuccessor, bestevent, bw, bprogress = None, None, -1, progressed
    #print successors
    for e in successors:
      st, w = successors[e]
      if len(st) != len(auts) or (tuple(st), progressed or e == process_event) in visited:
        continue
      if bw < w:
        bestsuccessor, bestevent, bw, bprogress = st, e, w, progressed or e == process_event
    if bestsuccessor == None:
      statetuple, progressed = prevstates.pop()
      e, _ = path.pop()
      if e not in auts[0][0].alphabet:
        while path and path[-1][0] not in auts[0][0].alphabet:
          #print len(path)
          statetuple, progressed = prevstates.pop()
          e = path.pop()
      continue
    path.append((bestevent, weight_function[bestevent]))
    prevstates.append(statetuple, progressed)
    progressed = bprogress
    statetuple = bestsuccessor
    visited.add(tuple(bestsuccessor))
  print 'end longest'
  return generate_aut_from_path_events_weighted(path, new_alphabet, aut.collection), len(visited)

def hopcroftstateweight(aut, state_weight):
  m = collections.defaultdict(list)
  sToP = {}
  for s in aut.get_states():
    l = m[(s.marked, state_weight[s])]
    l.append(s)
  P = list(m.values())
  for i in xrange(len(P)):
    for s in P[i]:
      sToP[s] = i
  W = set(range(len(P)))
  while W:
    A = W.pop()
    for event in aut.alphabet:
      X = set()
      tobreak = set()
      for s in A:
        for e in s.get_incoming():
          if (e.label == event):
            X.add(e.pred)
            tobreak.add(sToP[e.pred])
      for i in tobreak:
        l = P[i]
        l1 = []
        l2 = []
        for s in l:
          if s in X:
            l1.append(s)
          else:
            l2.append(s)
            sToP[s] = len(P)
        if l2:
          P.append(l2)
          P[i] = l1
          if i in W:
            W.add(l2)
          else:
            if (len(l1)< len(l2)):
              W.add(i)
            else:
              W.add(len(P)-1)
  newaut = data_structure.Automaton(aut.alphabet, aut.collection)
  PtoNS = []
  newstateweight = {}
  for i in xrange(len(P)):
    state = newaut.add_new_state(P[i][0].marked)
    PtoNS.append(state)
    newstateweight[state] = state_weight[P[i][0]]
  newaut.initial = PtoNS[sToP[aut.initial]]
  for i in xrange(len(P)):
    s = P[i][0]
    for e in s.get_outgoing():
      newaut.add_edge_data(PtoNS[i], PtoNS[sToP[e.succ]], e.label)
  newaut.reduce(True, True)
  return newaut, state_weight

def hopcroftstateweight(aut, state_weight):
  m = collections.defaultdict(list)
  sToP = {}
  for s in aut.get_states():
    print s
    l = m[(s.marked, state_weight[s])]
    l.append(s)
  P = list(m.values())
  for i in xrange(len(P)):
    for s in P[i]:
      sToP[s] = i
  W = set(range(len(P)))
  while W:
    A = W.pop()
    print A
    for event in aut.alphabet:
      X = set()
      tobreak = set()
      for s in P[A]:
        for e in s.get_incoming():
          if (e.label == event):
            X.add(e.pred)
            tobreak.add(sToP[e.pred])
      for i in tobreak:
        l = P[i]
        l1 = []
        l2 = []
        for s in l:
          if s in X:
            l1.append(s)
          else:
            l2.append(s)
            sToP[s] = len(P)
        if l2:
          P.append(l2)
          P[i] = l1
          if i in W:
            W.add(i)
          else:
            if (len(l1)< len(l2)):
              W.add(i)
            else:
              W.add(len(P)-1)
  newaut = data_structure.Automaton(aut.alphabet, aut.collection)
  PtoNS = []
  newstateweight = {}
  for i in xrange(len(P)):
    state = newaut.add_new_state(P[i][0].marked)
    PtoNS.append(state)
    newstateweight[state] = state_weight[P[i][0]]
  newaut.initial = PtoNS[sToP[aut.initial]]
  for i in xrange(len(P)):
    s = P[i][0]
    for e in s.get_outgoing():
      newaut.add_edge_data(PtoNS[i], PtoNS[sToP[e.succ]], e.label)
  newaut.reduce(True, True)
  return newaut, state_weight
