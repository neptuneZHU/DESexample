

def create_supremal_controllable_nonbloking_co_marked(auts, requirements, depth = 0):
  extime = -time()
  initstate = []
  newalphabet = Set()
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
    compmarked = True
    requirementmarked = True
    for i in range(len(enabled)):
      if currenabled == None:
        currenabled = set(enabled[i][statetuple[i]])
      else:
        currenabled.intersection_update(enabled[i][statetuple[i]])
      if auts[i][1]:
        requirementmarked = requirementmarked and statetuple[i].marked
        if requirementenabled == None:
          requirementenabled = set(enabled[i][statetuple[i]])
        else:
          requirementenabled.intersection_update(enabled[i][statetuple[i]])
      else:
        compmarked = statemarked and statetuple[i].marked
        if compenabled == None:
          compenabled = set(enabled[i][statetuple[i]])
        else:
          compenabled.intersection_update(enabled[i][statetuple[i]])
    is_bad = False
    if compmarked and not requirementmarked:
      bad_states.append(dictionary[state_tuple])
      is_bad = True
      dictionary[state_tuple].marked = False
      break
    else:
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
  changed = True
  uncontrollable_events = set([evt for evt in aut_sync.alphabet if not evt.controllable])
  while changed:
    changed = False
    coreachable = set()
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
      return aut_sync
    non_coreachable = set()
    uncontrollable_states = set()
    for state in aut_sync.get_states():
      if state in coreachable:
        continue
      for edge in state.get_incoming():
        if edge.pred in coreachable:
          pred_coreachable = True
          if not edge.label.controllable:
            changed = True
            uncontrollable_states.add(edge.pred)
      aut_sync.remove_state(state)
    uncontrollable_states = aut_sync.coreachable_states_set(uncontrollable_states,\
                                                            uncontrollable_events)
    for state in uncontrollable_states:
      aut_sync.remove_state(state)
  return aut_sync
  
def language_inclusion(prop, auts):
  extime = -time()
  initstate = []
  newalphabet = Set()
  transmap = []
  transweight = []
  enabled = []
  exectime = -time()
  temp = []
  for aut in auts:
    temp.append((aut, False))
  temp.append((prop, True))
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
  dictionary = set()
  dictionary.add(inittuple)
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
    compmarked = True
    requirementmarked = True
    for i in range(len(enabled)):
      if currenabled == None:
        currenabled = set(enabled[i][statetuple[i]])
      else:
        currenabled.intersection_update(enabled[i][statetuple[i]])
      if auts[i][1]:
        requirementmarked = requirementmarked and statetuple[i].marked
        if requirementenabled == None:
          requirementenabled = set(enabled[i][statetuple[i]])
        else:
          requirementenabled.intersection_update(enabled[i][statetuple[i]])
      else:
        compmarked = statemarked and statetuple[i].marked
        if compenabled == None:
          compenabled = set(enabled[i][statetuple[i]])
        else:
          compenabled.intersection_update(enabled[i][statetuple[i]])
    if compmarked and not requirementmarked:
      return False
    else:
      for evt in compenabled:
        if not evt.controllable and evt not in requirementenabled:
          return False
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
          dictionary.add(succtuple)
          tovisit.append(succtuple)
        #print aut_sync
      addstatetime += time()
  return True