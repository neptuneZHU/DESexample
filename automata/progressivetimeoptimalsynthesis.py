import automata
import collections
from automata import data_structure, weighted_structure
from time import time

class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval

def make_prog_supervisor_all_controllable(automata, progressive_events, resources = None):
  if resources == None:
    temp = []
    for aut in automata:
      temp.append(frozenset(aut.alphabet))
    resources = temp
  aut = synchronousproduct_weighted(automata, 0)
  aut.reduce(True, True)
  print aut
  print len(resources)
  #return aut
  return progressive_synthesis(aut, resources, progressive_events)

def make_greedy_prog_supervisor_all_controllable(automata, progressive_events, resources = None):
  temp = []
  if resources == None:
    for aut in automata:
      temp.append(frozenset(aut.alphabet))
    resources = temp
  tim = -time()
  aut = synchronousproduct_weighted(automata, 0)
  aut.reduce(True, True)
  #return aut
  print "fin start"
  aut.save_as_dot("beforerestrict.dot")
  automaton = finite_makespan_restricted(aut, progressive_events)
  automaton.save_as_dot("afterrestrict.dot")
  print "triple start"
  triples, weight = compute_triples(automaton, resources, progressive_events, 40)
  print "sup start"
  sup = construct_greedy_progressive_supervisor(automaton, resources, progressive_events, triples, 40)
  tim += time()
  print "time: " + str(tim)
  return sup, weight

def make_greedy_prog_supervisor_all_controllable_epuck(automaton, progressive_events, resources = None):
  tim = -time()
  #return aut
  print "triple start"
  triples, weight = compute_triples(automaton, resources, progressive_events, 40)
  print "sup start"
  sup = construct_greedy_progressive_supervisor_epuck(automaton, resources, progressive_events, triples, 40)
  tim += time()
  print "time: " + str(tim)
  return sup, weight

def earliest_fire(contour, event):
  early = 0
  for r in contour:
    if event in r:
      early = max(contour[r], early)
  return early

def earliest_fire_default(contour, event, resources):
  return max([contour[r] for r in resources])

def rev_earliest_fire(contour, event, weight):
  early = 0
  for r in contour:
    if event in r:
      early = max(contour[r] + weight, early)
    else:
      early = max(contour[r], early)
  return early

def rev_earliest_fire_default(contour, event, weight, resources):
  list = [contour.get(r, 0) + weight for r in resources]
  list += [contour[r] for r in contour]
  return max(list)

def rev_earliest_fire_drop(contour, event, weight, state_resources):
  early = 0
  for r in contour:
    if event in r:
      if r in state_resources:
        early = max(contour[r], early)
      else:
        early = max(contour[r] + weight, early)
  return early

def res_plus(contour, edge):
  event = edge.label
  early = earliest_fire(contour, event)
  new_contour = frozendict()
  for r in contour:
    if event in r:
      new_contour[r] = early + edge.weight
    else:
      new_contour[r] = max(early, contour[r])
  return new_contour

def res_plus_default(contour, edge, resources):
  event = edge.label
  early = earliest_fire_default(contour, event, resources)
  new_contour = collections.defaultdict(lambda: early)
  for r in contour:
    if r not in resources and contour[r] > early:
      new_contour[r] = contour[r]
  for r in resources:
    new_contour[r] = early + edge.weight
  return new_contour

def res_plus_drop(contour, edge, state_resources):
  event = edge.label
  early = earliest_fire(contour, event)
  new_contour = frozendict()
  for r in contour:
    if event in r:
      if r in state_resources:
        new_contour[r] = early
      else:
        new_contour[r] = early + edge.weight
    else:
      new_contour[r] = contour[r]
  return new_contour

def rev_res_plus(contour, edge):
  event = edge.label
  early = rev_earliest_fire(contour, event, edge.weight)
  new_contour = frozendict()
  list = []
  for r in contour:
    if event in r:
      new_contour[r] = early
    else:
      new_contour[r] = contour[r]#max(early, contour[r])
    list.append(new_contour[r])
  #print list
  return new_contour

def rev_res_plus_default(contour, edge, resources):
  event = edge.label
  early = rev_earliest_fire_default(contour, event, edge.weight, resources)
  new_contour = {}
  for r in contour:
    if r not in resources:
      new_contour[r] = contour[r]
  for r in resources:
    new_contour[r] = early
  return new_contour

def rev_res_plus_drop(contour, edge, state_resources):
  event = edge.label
  early = rev_earliest_fire_drop(contour, event, edge.weight, state_resources)
  new_contour = frozendict()
  list = []
  for r in contour:
    if event in r:
      new_contour[r] = early
    else:
      new_contour[r] = contour[r]#max(early, contour[r])
    list.append(new_contour[r])
  #print list
  return new_contour

def floor(contour):
  f = None
  for v in contour.values():
    if f == None:
      f = v
    else:
      f = min(f, v)
  return f

def ground(contour):
  f = floor(contour)
  new_contour = frozendict()
  for r in contour:
    new_contour[r] = contour[r] - f
  return new_contour

def ceil(contour):
  c = None
  for v in contour.values():
    if c == None:
      c = v
    else:
      c = max(c, v)
  return c

def progressive_synthesis(automaton, resources, progressive_events):
  #print progressive_events
  tim = -time()
  automaton = finite_makespan_restricted(automaton, progressive_events)
  supervisor = data_structure.Automaton(set(automaton.alphabet), automaton.collection)
  zero_contour = frozendict()
  for r in resources:
    zero_contour[r] = 0
  init = supervisor.add_new_state(automaton.initial.marked)
  init.x = automaton.initial
  init.x_f = zero_contour
  dictionary = {}
  dictionary[(init.x, init.x_f)] = init
  supervisor.initial = init
  to_process = [init]
  Q = {}
  num_uncont = {}
  covered_uncont = {}
  Q_process = set()
  while to_process:
    state = to_process.pop()
    x, x_f = state.x, state.x_f
    uncont = 0
    for edge in state.x.get_outgoing():
      if edge.label in progressive_events and not edge.label.controllable:
        uncont = uncont + 1
      y, y_f = edge.succ, ground(res_plus(x_f, edge))
      if (y, y_f) not in dictionary:
        new_state = supervisor.add_new_state(y.marked)
        dictionary[(y, y_f)] = new_state
        new_state.x = y
        new_state.x_f = y_f
        to_process.append(new_state)
      succ_state = dictionary[(y, y_f)]
      new_edge = data_structure.Edge(state, succ_state, edge.label)
      new_edge.weight = edge.weight
      supervisor.add_edge(new_edge)
      #supervisor.add_edge_data(state, succ_state, edge.label)
    if not state.marked or uncont != 0:
      Q[state] = None
    else:
      Q[state] = ceil(x_f)
      Q_process.add(state)
    num_uncont[state] = uncont
    covered_uncont[state] = 0
  print "states: " + str(supervisor.get_num_states())
  print supervisor
  while Q_process:
    print len(Q_process)
    Q_processnew = set()
    for state in Q_process:
      if num_uncont[state] > 0:
        m = None
        for edge in state.get_outgoing():
          if edge.label in progressive_events and not edge.label.controllable:
            temp = floor(res_plus(state.x_f, edge)) + Q[edge.succ]
            if (m == None):
              m = temp
            else:
              m = max(m, temp)
        if (Q[state] == m):
          continue
        Q[state] = m
      for edge in state.get_incoming():
        if edge.label in progressive_events:
          if edge.label.controllable and num_uncont[edge.pred] == 0:
            temp = floor(res_plus(edge.pred.x_f, edge)) + Q[state]
            if Q[edge.pred] == None:
              Q[edge.pred] = temp
              Q_processnew.add(edge.pred)
              for edge2 in edge.pred.get_incoming():
                if edge2.label in progressive_events and not edge2.label.controllable:
                  covered_uncont[edge2.pred] = covered_uncont[edge2.pred] + 1
            elif (temp < Q[edge.pred]):
              Q[edge.pred] = temp
              if edge.pred not in Q_processnew:
                Q_processnew.add(edge.pred)
          elif not edge.label.controllable and num_uncont[edge.pred] == covered_uncont[edge.pred]:
            temp = floor(res_plus(edge.pred.x_f, edge)) + Q[state]
            if (Q[edge.pred] == None):
              for edge2 in edge.pred.get_incoming():
                if edge2.label in progressive_events and not edge2.label.controllable:
                  covered_uncont[edge2.pred] = covered_uncont[edge2.pred] + 1
            if (Q[edge.pred] == None or temp < Q[edge.pred]):
              Q_processnew.add(edge.pred)
    if (len(Q_processnew) == 0):
      break
    else:
      Q_process = Q_processnew
  edgestoremove = []
  for state in supervisor.get_states():
    for edge in state.get_outgoing():
      if edge.label in progressive_events:
        temp = floor(res_plus(edge.pred.x_f, edge)) + Q[edge.succ]
        if Q[state] < temp:
          edgestoremove.append(edge)
  for edge in edgestoremove:
    supervisor.remove_edge(edge)
  supervisor.reduce(True, True)
  print supervisor
  tim = tim + time()
  print tim
  return supervisor, Q[automaton.initial]

def finite_makespan_restricted(automaton, progressive_events):
  automaton = automaton.copy_optimized()
  changed = True
  while changed:
    fin_makespan = has_prog_fin_makespan(automaton, progressive_events)
    no_fin_makespan = set(automaton.get_states()).difference(fin_makespan)
    to_process = list(no_fin_makespan)
    while to_process:
      state = to_process.pop()
      for edge in state.get_incoming():
        if edge.label not in progressive_events and not edge.label.controllable:
          if edge.pred not in no_fin_makespan:
            no_fin_makespan.add(edge.pred)
            to_process.append(edge.pred)
    for state in no_fin_makespan:
      automaton.remove_state(state)
    automaton.reduce(True, True)
    changed = len(no_fin_makespan)!= 0
  return automaton

def has_prog_fin_makespan(automaton, progressive_events):
  num_uncont = {}
  fin_makespan = set();
  to_process = []
  for state in automaton.get_states():
    uncont = 0
    for edge in state.get_outgoing():
      if edge.label in progressive_events and not edge.label.controllable:
        uncont += 1
    num_uncont[state] = uncont
    if not uncont and state.marked:
      to_process.append(state)
      fin_makespan.add(state)
  while to_process:
    state = to_process.pop()
    for edge in state.get_incoming():
      if edge.label in progressive_events:
        if not edge.label.controllable:
          uncont = num_uncont[edge.pred]
          uncont = uncont - 1
          num_uncont[edge.pred] = uncont
          if uncont == 0 and edge.pred not in fin_makespan:
            fin_makespan.append(edge.pred)
            to_process.append(edge.pred)
        else:
          if num_uncont[edge.pred] == 0 and edge.pred not in fin_makespan:
            fin_makespan.add(edge.pred)
            to_process.append(edge.pred)
  return fin_makespan

def allmarked(statetuple):
  for state in statetuple:
    if not state.marked:
      return False
  return True

def synchronousproduct_weighted(auts, depth):
  initstate = []
  newalphabet = set()
  transmap = []
  eventweight = {}
  enabled = []
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
  inittuple = tuple(initstate)
  dictionary = {}
  aut_sync = weighted_structure.WeightedAutomaton(newalphabet, aut.collection)
  initstate = aut_sync.add_new_state(allmarked(inittuple), aut_sync.get_num_states())
  aut_sync.initial = initstate
  dictionary[inittuple] = initstate
  tovisit = [inittuple]
  transitions = 0
  edgestoadd = []
  print "add edges"
  succcalctime = 0
  addstatetime = 0
  calccurrenab = 0
  count = 0
  while len(tovisit) != 0:
    count += 1
    statetuple = tovisit.pop()
    currenabled = set(enabled[0][statetuple[0]])
    for i in range(1,len(enabled)):
      currenabled.intersection_update(enabled[i][statetuple[i]])
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
        if succtuple not in dictionary:
          newstate = aut_sync.add_new_state(allmarked(succtuple), aut_sync.get_num_states())
          dictionary[succtuple] = newstate
          tovisit.append(succtuple)
        edgestoadd.append(weighted_structure.WeightedEdge(dictionary[statetuple], dictionary[succtuple], event, eventweight[event]))
        #print aut_sync
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print "end add edges"
  print "added edges"
  aut_sync.add_edges(edgestoadd)
  print "end add edges"
  #if depth == 5:
    #auia = aieia
  return aut_sync

def synchronousproduct_weighted_epucks(auts, depth):
  initstate = []
  newalphabet = set()
  transmap = []
  eventweight = {}
  enabled = []
  print "begin transmap"
  for aut in auts:
    newalphabet.update(aut.alphabet)
  collissions = set()
  num_colls = 0
  for i in range(len(auts)):
    aut = auts[i]
    initstate.append(aut.initial)
    collissions.update(aut.initial.collisions)
    num_colls += len(aut.initial.collisions)
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
  inittuple = tuple(initstate)
  dictionary = {}
  aut_sync = weighted_structure.WeightedAutomaton(newalphabet, aut.collection)
  initstate = aut_sync.add_new_state(allmarked(inittuple), aut_sync.get_num_states())
  assert(len(collissions) == num_colls)
  initstate.collisions = collissions
  aut_sync.initial = initstate
  dictionary[inittuple] = initstate
  tovisit = [inittuple]
  transitions = 0
  edgestoadd = []
  print "add edges"
  succcalctime = 0
  addstatetime = 0
  calccurrenab = 0
  count = 0
  while len(tovisit) != 0:
    count += 1
    statetuple = tovisit.pop()
    currenabled = set(enabled[0][statetuple[0]])
    for i in range(1,len(enabled)):
      currenabled.intersection_update(enabled[i][statetuple[i]])
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
        collissions = set()
        num_colls = 0
        for state in succtuple:
          collissions.update(state.collisions)
          num_colls += len(state.collisions)
        if num_colls != len(collissions):
          continue
        if succtuple not in dictionary:
          newstate = aut_sync.add_new_state(allmarked(succtuple), aut_sync.get_num_states())
          dictionary[succtuple] = newstate
          tovisit.append(succtuple)
          newstate.collisions = collissions
        edgestoadd.append(weighted_structure.WeightedEdge(dictionary[statetuple], dictionary[succtuple], event, eventweight[event]))
        #print aut_sync
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print "end add edges"
  print "added edges"
  aut_sync.add_edges(edgestoadd)
  print "end add edges"
  #if depth == 5:
    #auia = aieia
  return aut_sync

class hashcachingtuple(tuple):

  def __init__(self, values):
    super(hashcachingtuple, self).__init__(values)
    self.hashcache = super(hashcachingtuple, self).__hash__()

  def __hash__(self):
    return self.hashcache

def calculate_norm(contour, l):
  sum = 0
  maxv = 0
  for x in contour.values():
    sum += x
    maxv = max(maxv, x)
  maxv *= l
  return float(sum + maxv)/float(l)

def compute_triples(aut, resources, progressive_events, L):
  triples, last = [{}], {}
  zero_contour = frozendict()
  has_progressive_uncont = set()
  to_check = set()
  for r in resources:
    zero_contour[r] = 0
  for state in aut.get_states():
    contmarked = state.marked
    for edge in state.get_outgoing():
      if (not edge.label.controllable and edge.label in progressive_events):
        has_progressive_uncont.add(state)
        contmarked = False
        break
    if contmarked:
      triples[0][state] = (0, zero_contour, 0)
      last[state] = 0
      for edge in state.get_incoming():
        if (edge.label in progressive_events):
          to_check.add(edge.pred)
    else:
      last[state] = -1
  k = 0
  while len(to_check) != 0:
    k += 1
    next_to_check = set()
    triples.append({})
    update_last = []
    for state in to_check:
      chosen_norm = None
      if (state in has_progressive_uncont):
        max_norm = (0, None)
        for edge in state.get_outgoing():
          if (not edge.label.controllable and edge.label in progressive_events):
            if (last[edge.succ] == -1):
              max_norm = (None, None)
              break
            _, Q, _ = triples[last[edge.succ]][edge.succ]
            contour = rev_res_plus(Q, edge)
            norm = calculate_norm(contour, L)
            if (norm > max_norm[0]):
              max_norm = (norm, contour)
        chosen_norm = max_norm
      elif (state.marked):
        continue
      else:
        min_norm = (None, None)
        for edge in state.get_outgoing():
          if (edge.label in progressive_events):
            if (last[edge.succ] == -1):
              continue
            _, Q, _ = triples[last[edge.succ]][edge.succ]
            contour = rev_res_plus(Q, edge)
            norm = calculate_norm(contour, L)
            if (min_norm[0] == None or norm < min_norm[0]):
              min_norm = (norm, contour)
        chosen_norm = min_norm
      li = last[state]
      if (chosen_norm[0] == None):
        continue
      elif (li == -1 or chosen_norm[0] < triples[li][state][0]):
        triples[k][state] = (chosen_norm[0], chosen_norm[1], k)
        update_last.append(state)
        for edge in state.get_incoming():
          if (edge.label in progressive_events):
            next_to_check.add(edge.pred)
    for state in update_last:
      last[state] = k
    to_check = next_to_check
  #print "theta, Q" + str(triples[last[aut.initial]][aut.initial])
  return triples, calculate_norm(triples[last[aut.initial]][aut.initial][1], 10000)

def find_index(triples, state, k):
  while True:
    if k == -1:
      return k
    if state in triples[k]:
      print "k: " + str(k)
      return k
    else:
      k -= 1

def construct_greedy_progressive_supervisor(aut, resources, progressive_events, triples, L):
  sup = data_structure.Automaton(set(aut.alphabet), aut.collection)
  dict = {}
  to_process = []
  f_index = find_index(triples, aut.initial, len(triples)-1)
  init_index = f_index
  sup.initial = sup.add_new_state(aut.initial.marked)
  dict[(aut.initial, f_index)] = sup.initial
  to_process.append((aut.initial, f_index))
  while (to_process):
    state, k = to_process.pop(0)
    sup_source = dict[(state, k)]
    theta, _, _ = triples[k][state]
    for edge in state.get_outgoing():
      if edge.label not in progressive_events:
        f_index = find_index(triples, edge.succ, len(triples)-1)
        if (edge.succ, f_index) not in dict:
          dict[(edge.succ, f_index)] = sup.add_new_state(edge.succ.marked)
          to_process.append((edge.succ, f_index))
        sup_target = dict[(edge.succ, f_index)]
        sup.add_edge_data(sup_source, sup_target, edge.label)
      else:
        f_index = find_index(triples, edge.succ, k-1)
        if f_index == -1:
          continue
        _, Q, _ = triples[f_index][edge.succ]
        contour = rev_res_plus(Q, edge)
        norm = calculate_norm(contour, L)
        print str(norm) + " " + str(theta) + " " + str(f_index) + " " + str(k)
        if (norm <= theta):
          if (edge.succ, f_index) not in dict:
            dict[(edge.succ, f_index)] = sup.add_new_state(edge.succ.marked)
            to_process.append((edge.succ, f_index))
          sup_target = dict[(edge.succ, f_index)]
          sup.add_edge_data(sup_source, sup_target, edge.label)
  return sup

def construct_greedy_progressive_supervisor_epuck(aut, resources, progressive_events, triples, L):
  sup = data_structure.Automaton(set(aut.alphabet), aut.collection)
  dict = {}
  to_process = []
  f_index = find_index(triples, aut.initial, len(triples)-1)
  sup.initial = sup.add_new_state(aut.initial.marked)
  sup.initial.collisions = aut.initial.collisions
  dict[(aut.initial, f_index)] = sup.initial
  to_process.append((aut.initial, f_index))
  while (to_process):
    state, k = to_process.pop(0)
    sup_source = dict[(state, k)]
    theta, _, _ = triples[k][state]
    for edge in state.get_outgoing():
      if edge.label not in progressive_events:
        f_index = find_index(triples, edge.succ, len(triples)-1)
        if (edge.succ, f_index) not in dict:
          dict[(edge.succ, f_index)] = sup.add_new_state(edge.succ.marked)
          to_process.append((edge.succ, f_index))
        sup_target = dict[(edge.succ, f_index)]
        sup.add_edge_data(sup_source, sup_target, edge.label)
      else:
        f_index = find_index(triples, edge.succ, k-1)
        if f_index == -1:
          continue
        _, Q, _ = triples[f_index][edge.succ]
        contour = rev_res_plus(Q, edge)
        norm = calculate_norm(contour, L)
        print str(norm) + " " + str(theta) + " " + str(f_index) + " " + str(k)
        if (norm <= theta):
          if (edge.succ, f_index) not in dict:
            dict[(edge.succ, f_index)] = sup.add_new_state(edge.succ.marked)
            to_process.append((edge.succ, f_index))
            dict[(edge.succ, f_index)].collisions = edge.succ.collisions
          sup_target = dict[(edge.succ, f_index)]
          sup.add_edge_data(sup_source, sup_target, edge.label)
  for state in sup.get_states():
    for edge in state.get_outgoing():
      edge.weight = 1
  return sup