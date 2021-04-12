
def find_observable_sub_language(aut, localevents, depth):
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
    for state in stateset:
      if enabled != None:
        enabled.intersection_update(succ_enabled_map[state][1])
      else:
        enabled = set(succ_enabled_map[state][1])
    if not enabled:
      continue
    for event in enabled:
      succdictionary[event] = Set()
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
  
def find_definitely_relevant_events(aut, rel_events):
  non_relevant = aut.alphabet.difference(rel_events)
  def_relevant = set()
  succ_enabled_map = {}
  for state in aut.get_states():
    succ_enabled_map[state] = find_local_reachable_and_enabled(state, non_relevant)
  for evt in non_relevant:
    evt_enabled_map = {}
    for state in aut.get_states():
      evt_enabled_map[state] = list(find_local_reachable_and_enabled(state, set([evt])))
      evt_enabled_map[state][1] = evt_enabled_map[state][1].difference(non_relevant)
      for reachable in evt_enabled_map[state][0]:
        if evt_enabled_map[state][2] and not succ_enabled_map[reachable][2]:
          print evt
          print "marked"
          def_relevant.add(evt)
          break
        elif not evt_enabled_map[state][1].issubset(succ_enabled_map[reachable][1]):
          print evt
          print evt_enabled_map[state][1].difference(succ_enabled_map[reachable][1])
          def_relevant.add(evt)
          break
      if evt in def_relevant:
        break
    if evt in def_relevant:
      continue
  return def_relevant
      
      
      
    