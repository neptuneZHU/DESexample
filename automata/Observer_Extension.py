from automata import abstraction

def find_outgoing_nonobs(aut, state_to_partitions_map, non_obs_events):
  out_go_events = set()
  for state in aut.get_states():
    orig_part = state_to_partitions_map[state]
    for edge in state.get_outgoing():
      if edge.label not in non_obs_events:
        continue
      if (orig_part != state_to_partitions_map[edge.succ]):
        out_go_events.add(edge.label)
        print str(orig_part) + "->" + edge.label.name + "->" + str(state_to_partitions_map[edge.succ])
  return out_go_events

def split(state, event_set, observable_events, partition_to_state_map):
  for event in observable_events:
    if not nopath(state, event, event_set, partition_to_state_map):
      return False
  return True
  
def nopath(state, event, unobservable, partition_to_state_map):
  count_outgoing = 0
  for edge in state.get_outgoing():
    if edge.label == event:
      count_outgoing += 1
      if count_outgoing > 1:
        break
  if count_outgoing <= 1:
    return True
  exits = llambda(state, partition_to_state_map, event)
  for E in exits:
    for F in exits:
      if E is F:
        continue
      if can_reach(E, unobservable, F):
        return False
  return True
  
def can_reach(E, unobservable, F):
  if not E.intersection(F):
    return True
  stack = list(E)
  reached = set(E)
  while stack:
    state = stack.pop()
    for edge in state.get_outgoing:
      if edge.label in unobservable:
        if edge.succ in F:
          return True
        if edge.succ not in reached:
          reached.add(edge.succ)
          stack.append(edge.succ)
  return False
  
def llambda(state, partition_to_state_map, event):
  lookedat = set()
  exits = set()
  orig_part = partition_to_state_map[state]
  for edge in state.get_outgoing():
    if edge.label != event or edge.succ in lookedat:
      continue
    lookedat.add(edge.succ)
    possible = partition_to_state_map[edge.succ]
    exit = set()
    for poss in possible:
      for edge2 in poss.get_incoming():
        if edge2.label == event and edge2.pred in orig_part:
          exit.add(edge2.pred)
    if exit: 
      exits.add(frozenset(exit))
  return exits
  
def Event_Set_Extension(aut, observable, obs_aut, state_to_partitions_map,
                        partition_to_state_map):
  non_obs_events = aut.alphabet.difference(observable)
  B = find_outgoing_nonobs(aut, state_to_partitions_map, non_obs_events)
  N = set()
  for state in obs_aut.get_states():
    partition = partition_to_state_map[state]
    outparts = {}
    add_to_N = False
    for orig_state in partition: 
      for edge in orig_state.get_outgoing():
        succ_part = state_to_partitions_map[edge.succ]
        if edge.label in outparts and succ_part != outparts[edge.label]:
          add_to_N = True
          break
        outparts[edge.label] = succ_part
      if add_to_N:
        break
    if add_to_N:
      N.add(state)
  if len(N) == 0:
    return observable.union(B)
  TN = set()
  H = set()
  for state in N:
    partition = partition_to_state_map[state]
    for orig_state in partition:
      for edge in orig_state.get_outgoing():
        if edge.label in non_obs_events and edge.succ in partition:
          TN.add(edge)
          H.add(edge.label)
  SIGMAi1 = B.union(H).union(observable)
  go_through = H.difference(B)
  print "B"
  print B
  print "H"
  print go_through
  for event in go_through:
    T = SIGMAi1.difference(set([event]))
    new_unobs = aut.alphabet.difference(T)
    all_split = True
    for state in N:
      if not split(state, new_unobs, observable, partition_to_state_map):
        all_split = False
        break
    if all_split:
      print "removed from observable:" + str(event) 
      SIGMAi1 = T
  return SIGMAi1
  
def natural_observer_computation(aut, observable):
  observable = set(observable)
  while True:
    aut_abs, partition_map = abstraction.abstraction_refined_with_partitions(aut, observable)
    is_deterministic = True
    for state in aut_abs.get_states():
      used_events = set()
      for edge in state.get_outgoing():
        if edge.label in used_events:
          is_deterministic = False
          print "not determistic"
          break
        used_events.add(edge.label)
      if not is_deterministic:
        break
    if is_deterministic:
      return aut_abs, observable
    state_to_partitions_map = {}
    for abs_state in partition_map:
      partition = partition_map[abs_state]
      for orig_state in partition:
        state_to_partitions_map[orig_state] = abs_state
    #print str(len(observable)) + " bef"
    observable = Event_Set_Extension(aut, observable, aut_abs,
                                     state_to_partitions_map, partition_map)
    #print str(len(observable)) + " aft"
      
def create_test_automaton(aut, test_event):
  init = frozenset([aut.initial])
  stack = [init]
  state_set = set(stack)
  while stack:
    state_tuple = stack.pop()
    l = list(state_tuple)
    if len(state_tuple) == 1:
      state_tuple = (l[0], l[0])
    else:
      state_tuple = (l[0], l[1])
    succ_map1 = {}
    succ_map2 = {}
    for edge in state_tuple[0].get_outgoing():
      succ_map1[edge.label] = edge.succ
    for edge in state_tuple[1].get_outgoing():
      succ_map2[edge.label] = edge.succ
    for event in aut.alphabet:
      if event == test_event:
        if event in succ_map2:
          succ1 = frozenset([state_tuple[0], succ_map2[event]])
          if succ1 not in state_set:
            state_set.add(succ1)
            stack.append(succ1)
        if event in succ_map1:
          succ2 = frozenset([succ_map1[event], state_tuple[1]])        
          if succ2 not in state_set:
            state_set.add(succ2)
            stack.append(succ2)
      elif event in succ_map1 and event in succ_map2:
        succ = frozenset([succ_map1[event], succ_map2[event]])
        if succ not in state_set:
          state_set.add(succ)
          stack.append(succ)
  return state_set
    
def find_reachable(state, unobservable):
  stack = list([state])
  reached = set(stack)
  enabled = set()
  while stack:
    state = stack.pop()
    for edge in state.get_outgoing():
      if edge.label in unobservable:
        if edge.succ not in reached:
          reached.add(edge.succ)
          stack.append(edge.succ)
      else:
        enabled.add(edge.label)
    if state.marked:
      enabled.add(None)
  return enabled
  
def create_enabled_map(aut, unobservable):
  enabled_map = {}
  for state in aut.get_states():
    enabled_map[state] = find_reachable(state, unobservable)
  return enabled_map
  
def natural_observer_computation_def_rel(aut, observable):
  observable = set(observable)
  print observable
  test_aut_map = {}
  for event in aut.alphabet.difference(observable):
    test_aut_map[event] = create_test_automaton(aut, event)
  while True:
    aut_abs, partition_map = \
      abstraction.abstraction_refined_with_partitions(aut, observable)
    is_deterministic = True
    for state in aut_abs.get_states():
      used_events = set()
      for edge in state.get_outgoing():
        if edge.label in used_events:
          is_deterministic = False
          break
        used_events.add(edge.label)
      if not is_deterministic:
        break
    if is_deterministic:
      return aut_abs, observable
    def_rel_found = True
    enabled_map = create_enabled_map(aut, aut.alphabet.difference(observable))
    def_rel_pick_p42 = False
    while def_rel_found:
      def_rel_found = False
      for event in aut.alphabet.difference(observable):
        test_set = test_aut_map[event]
        #if "pick" in event.name:
         # print test_set
          #oi = dad
        found_counter = False
        for state_set in test_aut_map[event]:
          if len(state_set) == 1:
            continue
          tup = list(state_set)
          if tup[0].marked and None not in enabled_map[tup[1]] or\
             tup[1].marked and None not in enabled_map[tup[0]]:
            found_counter = True
            break
          for edge in tup[0].get_outgoing():
            if edge.label.name == "tau" or edge.label not in observable:
              continue
            if edge.label not in enabled_map[tup[1]]:
              print edge.label
              print tup
              found_counter = True
              break
          if found_counter:
            break
          for edge in tup[1].get_outgoing():
            if edge.label.name == "tau" or edge.label not in observable:
              continue
            if edge.label not in enabled_map[tup[0]]:
              print edge.label
              print tup
              found_counter = True
              break
        if found_counter:
          def_rel_found = True
          print "def rel found!"
          print "def rel found"
          print "def rel found" + str(event)
          print "def rel found"
          print "def rel found!"
          observable.add(event)
          if "pick-P52" in event.name:
            def_rel_pick_p42 = True
          enabled_map = create_enabled_map(aut, aut.alphabet.difference(observable))
    print "done def rel"
    aut_abs, partition_map = \
      abstraction.abstraction_refined_with_partitions(aut, observable)
    for state in aut_abs.get_states():
      aut_abs.state_names[state.number] = str(state.number)
    if def_rel_pick_p42:
      aut_abs.save_as_dot("check_def_rel.dot")
    is_deterministic = True
    for state in aut_abs.get_states():
      used_events = set()
      for edge in state.get_outgoing():
        if edge.label in used_events:
          is_deterministic = False
          break
        used_events.add(edge.label)
      if not is_deterministic:
        break
    if is_deterministic:
      return aut_abs, observable
    state_to_partitions_map = {}
    for abs_state in partition_map:
      partition = partition_map[abs_state]
      for orig_state in partition:
        state_to_partitions_map[orig_state] = abs_state
    observable = Event_Set_Extension(aut, observable, aut_abs,
                                     state_to_partitions_map, partition_map)