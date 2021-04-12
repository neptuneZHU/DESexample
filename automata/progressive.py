import automata,copy, heapq, random
from automata import taskresource, maxplus, data_structure, collection, weighted_structure, \
                            compute_weight, conversion, weighted_product, algorithm, common, \
                            weighted_supervisor, abstraction, product
from sets import Set
from time import time

def calcstarttime(currentcontours, used):
  maxcont = 0
  for i in range(len(used)):
    if used[i]:
      maxcont = maxcont if currentcontours.data[i] < maxcont else currentcontours.data[i]
  return maxcont

def calcpath(aut, eventdata, heap_len, num):
  pathstate = aut.initial
  weight = maxplus.matrix_to_vector(maxplus.make_rowmat(0,heap_len))
  wavers = num
  #newwaver = aut.collection.events["R1-pick-C"]
  if "NewWaver" in aut.collection.events:
    newwaver = aut.collection.events["NewWaver"]
  else:
    newwaver = None
  procevent = aut.collection.events["R1-drop-C"]
  processed = 0
  #newwaver = None
  while not (pathstate.marked and wavers == 0):
    possibleedges = None
    beststart = None
    cannewwaver = None
    for edge in pathstate.get_outgoing():
      if edge.label == newwaver:
        cannewwaver = edge
        continue
      pathstate = edge.succ
      event = edge.label
      soonestfire = calcstarttime(weight, eventdata[event].used)
      if beststart == None or soonestfire < beststart:
        soonestfire = beststart
        possibleedges = [edge]
      elif beststart == soonestfire:
        possibleedges.append(edge)
    if wavers != 0 and cannewwaver != None and (beststart == None or beststart >= calcstarttime(weight, eventdata[newwaver].used)):
      wavers -= 1
      possibleedges = [cannewwaver]
    index = random.randrange(len(possibleedges))
    edge = possibleedges[index]
    event = edge.label
    #print event
    pathstate = edge.succ
    weight = maxplus.newtimes_vec_vec(weight, eventdata[event].matHat)
    if event == procevent:
      processed += 1
  print "weight: " + str(weight) + " processed: num"
  
def allmarked(statetuple):
  for state in statetuple:
    if not state.marked:
      return False
  return True
  
def calcpath_mult(auts, eventdata, heap_len):
  pathstatetup = [aut.initial for aut in auts]
  weight = maxplus.matrix_to_vector(maxplus.make_rowmat(0,heap_len))
  wavers = 0
  alphabet = set()
  for aut in auts:
    alphabet.update(aut.alphabet)
  newwaver = None
  #newwaver = aut.collection.events['NewWaver']
  while not (allmarked(pathstatetup) and wavers == 0):
    possibleedges = None
    beststart = None
    cannewwaver = None
    successors = []
    for state in pathstatetup:
      successors.append({edge.label : edge.succ for edge in state.get_outgoing()})
    act_successors = []
    for evt in alphabet:
      successor_tup = []
      for i, dictionary in enumerate(successors):
        if evt not in auts[i].alphabet:
          successor_tup.append(pathstatetup[i])
        elif evt not in dictionary:
          successor_tup = None
          break
        else:
          successor_tup.append(dictionary[evt])
      if successor_tup:
        act_successors.append((evt, successor_tup))
    for tup in act_successors:
      event, pathstate = tup
      if event == newwaver:
        cannewwaver = tup
        continue
      soonestfire = calcstarttime(weight, eventdata[event].used)
      if beststart == None or soonestfire < beststart:
        soonestfire = beststart
        possibleedges = [tup]
      elif beststart == soonestfire:
        possibleedges.append(tup)
    if wavers != 0 and cannewwaver != None and (beststart == None or beststart >= calcstarttime(weight, eventdata[newwaver].used)):
      wavers -= 1
      possibleedges = [cannewwaver]
    index = random.randrange(len(possibleedges))
    tup = possibleedges[index]
    event = tup[0]
    pathstatetup = tup[1]
    weight = maxplus.newtimes_vec_vec(weight, eventdata[event].matHat)
    print event
    print weight
  print "weight: " + str(weight)
  
def load_test(plant_list, supervisor, evt_pairs, comp_mut_ex):
  result = taskresource.compute_custom_eventdata_extended(plant_list, evt_pairs, comp_mut_ex)
  eventdata, cliques = result
  for event in eventdata:
      eventdata[event].matHat = maxplus.matrix_to_vector(eventdata[event].matHat)
  for i in range(1, 21):
    calcpath(supervisor, eventdata, len(cliques), i * 100)
  iio = oi
  
def load_test_mult_supervisors(plant_list, supervisors, evt_pairs, comp_mut_ex):
  coll = collection.Collection()
  plant_list = weighted_frontend.load_weighted_automata(coll,plant_list, False, True)
  events = coll.events
  C1_events = set([events[evt] for evt in events if evt.startswith("C1")])
  C2_events = set([events[evt] for evt in events if evt.startswith("C2")])
  C3_events = set([events[evt] for evt in events if evt.startswith("C3")]) 
  plant_list = []
  aut = weighted_structure.WeightedAutomaton(C1_events, coll)
  aut.initial = aut.add_new_state(True,0)
  for evt in C1_events:
    aut.add_edge_data(aut.initial, aut.initial, evt, 1)
  plant_list.append(aut)
  aut = weighted_structure.WeightedAutomaton(C2_events, coll)
  aut.initial = aut.add_new_state(True,0)
  for evt in C2_events:
    aut.add_edge_data(aut.initial, aut.initial, evt, 1)
  plant_list.append(aut)
  aut = weighted_structure.WeightedAutomaton(C3_events, coll)
  aut.initial = aut.add_new_state(True,0)
  for evt in C3_events:
    aut.add_edge_data(aut.initial, aut.initial, evt, 1)
  plant_list.append(aut)
  result = taskresource.compute_custom_eventdata_extended(plant_list, evt_pairs, comp_mut_ex)
  supervisors = frontend.load_automata(coll,supervisors, False, True)
  #tau_abstraction.testpath_not_weighted(plant_list, supervisors[0], None)
  eventdata, cliques = result
  for event in eventdata:
      eventdata[event].matHat = maxplus.matrix_to_vector(eventdata[event].matHat)
  calcpath_mult(supervisors, eventdata, len(cliques))