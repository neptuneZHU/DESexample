from automata import data_structure, baseobjects, path, collection, frontend
import os, exceptions, sys, collections

class IntervalEdge(baseobjects.EqualityObject):
    """
    Classs representing an edge between two states.

    @ivar pred: Predecessor state.
    @type pred: L{State} or L{WeightedState}

    @ivar succ: Successor state.
    @type succ: L{State} or L{WeightedState}

    @ivar label: Event label associated with the edge.
    @type label: L{Event}
    """
    __slots__ = ['pred', 'succ', 'label', 'l', 'r']

    def __init__(self, pred, succ, label, l, r):
        self.pred = pred
        self.succ = succ
        self.label = label
        self.l= l
        self.r = r

    def __repr__(self):
        return "Edge(%r, %r, %r, %r, %r)" % (self.pred, self.succ, self.label, self.l, self.r)

    def _equals(self, other):
        return self.pred is other.pred and \
               self.succ is other.succ and \
               self.label is other.label and \
               self.l == other.l and \
               self.r == other.r

    def __hash__(self):
      return (self.pred, self.succ, self.label, self.l, self.r).__hash__()

    def copy(self, new_pred, new_succ):
        """
        Make a copy of the edge, and place it between the given new states.

        @param new_pred: New predecessor state.
        @type  new_pred: L{State}

        @param new_succ: New successor state.
        @type  new_succ: L{State}
        """
        return IntervalEdge(new_pred, new_succ, self.label, self.l, self.r)

    def clear(self):
        self.pred = None
        self.succ = None
        self.label = None
        self.l = None
        self.r = None

class IntervalAutomaton(data_structure.BaseAutomaton):

    def __init__(self, alphabet, coll):
        super(IntervalAutomaton, self).__init__(alphabet, coll, data_structure.State, IntervalEdge)

    def _make_automaton(self, alphabet):
        return IntervalAutomaton(alphabet, self.collection)

    def add_edge_data(self, pred, succ, label, l, r):
        """
        Add an edge from its values.

        @param pred: Source state.
        @type  pred: L{State}

        @param succ: Destination state.
        @param succ: L{State}

        @param label: Event label.
        @type  label: L{Event}

        @todo: Eliminate me.
        """
        self.add_edge(IntervalEdge(pred, succ, label, l, r))

    # {{{ def get_path(self, state):
    def get_path(self, state):
        """
        Compute a path from initial state to the given state.

        @param state: Target state of the path.
        @type  state: L{State}

        @return: C{None} if path cannot be found, or a sequence of
                 (state, outgoing event) pairs that leads from the initial
                 state to the given state.
        @rtype:  C{None} or a C{list} of (L{State}, L{collection.Event})

        @note: L{state} is not in the returned path.
        """
        return path.get_path(self.initial, state)

    def to_dot(self, plot_marker_events = False):
        """
        Generate a Graphviz DOT representation of the automaton

        @return: String containing the automaton in DOT format
        @rtype:  C{string}
        """
        self.make_state_names_complete()
        marker_evt = self.collection.marker_event

        text = ["digraph Automaton {"]
        for state in self.get_states():
            if state is self.initial:
                if marker_evt is not None and state.marked:
                    style = 'doubleoctagon' # initial state with marker event
                else:
                    style = 'octagon'  # initial state without marker event

            elif marker_evt is not None and state.marked:
                style = 'doublecircle'
            else:
                style = 'circle'
            name = 's%d [label="%s", shape=%s];' \
                        % (state.number, self.state_names[state.number], style)
            text.append(name)
            for edge in state.get_outgoing():
                # Do not plot marker events unless explicitly asked
                if not plot_marker_events and edge.label is marker_evt:
                    continue

                text.append("s%s -> s%d [label=\"%s,%s,%s\"];"
                            % (state.number, edge.succ.number, edge.label.name, edge.l, edge.r))

        text.append('}')
        return '\n'.join(text)

    def save_as_dot(self, fname, plot_marker_events = False):
        """ Save the automaton to file as 'fname' """
        handle = open(fname, 'w')
        handle.write(self.to_dot(plot_marker_events))
        handle.write('\n')
        handle.close()

class IntervalAutomatonLoader(collection.BaseAutomatonLoader):
    """
    @ivar state_map: Mapping of state name to State.
    @type state_map: C{dict} of C{str} to L{State}
    """
    def __init__(self, coll):
        super(IntervalAutomatonLoader, self).__init__(coll)
        self.state_map = {}


    def make_new_automaton(self, alphabet):
        return IntervalAutomaton(alphabet, self.collection)

    def process_states(self):
        statename_map = self.order_states() #: Mapping of number to name
        self.state_map = {} #: Mapping of name to L{State}
        for num, name in statename_map.iteritems():
            state = self.automaton.add_new_state(name in self.marker_states,
                                                 num = num)
            self.automaton.set_state_name(state, name)
            self.state_map[name] = state

        self.automaton.set_initial(self.state_map[self.initial_state])

    def process_single_edge(self, edge_data):
        if len(edge_data) != 5:
            return "Edge %r should have five fields." % repr(edge_data)

        if not self.is_numeric(edge_data[3]):
            return "Edge l %r should should be a integer number." % \
                                                            repr(edge_data[3])

        if not self.is_numeric(edge_data[4]) and not edge_data[4] == 'inf':
            return "Edge r %r should should be a integer number." % \
                                                            repr(edge_data[4])

        src = self.state_map[edge_data[0]]
        dst = self.state_map[edge_data[1]]
        evt = self.collection.get_event(edge_data[2])
        l = int(edge_data[3], 10)
        r = float('inf') if edge_data[4] == 'inf' else int(edge_data[4], 10)
        self.automaton.add_edge_data(src, dst, evt, l, r)
        return None

    def get_sectname(self):
        return "interval-automaton"

class IntervalAutomatonSaver(collection.BaseAutomatonSaver):
    def check_aut_type(self, aut):
        #return type(aut) is Automaton
        return True

    def get_sectname(self):
        return "interval-automaton"

    def convert_single_edge(self, aut, edge):
        return "(%s, %s, %s, %s, %s)" % (aut.state_names[edge.pred.number],
                                 aut.state_names[edge.succ.number],
                                 edge.label.name, edge.l, edge.r)

    def save_automaton(aut, fname, make_backup = True):
        """
        Convenience function for saving an unweighted automaton.

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @param aut: Automaton to save.
        @type  aut: L{Automaton}

        @param make_backup: Make a backup file.
        @type  make_backup: C{bool}
        """
        saver = AutomatonSaver()
        saver.save(aut, fname, make_backup)


def IntervalSynchronousProduct(auts, collection):
  initstate = []
  newalphabet = set()
  transmap = []
  stablevalue = []
  enabled = []
  infinity = float('inf')
  zeroclocktuple = tuple([0 for i in range(len(auts))])
  for aut in auts:
    newalphabet.update(aut.alphabet)
  for i in range(len(auts)):
    aut = auts[i]
    initstate.append(aut.initial)
    #newalphabet.update(aut.alphabet)
    transmap.append({})
    stablevalue.append({})
    enabled.append({})
    for state in aut.get_states():
      enabled[i][state] = set()
      stabvalue = 0
      for edge in state.get_outgoing():
        if (state,edge.label) not in transmap[i]:
          transmap[i][state,edge.label] = []
        transmap[i][state,edge.label].append(edge)
        enabled[i][state].add(edge.label)
        if (edge.r == infinity):
            stabvalue = max(stabvalue, edge.l)
        else:
            stabvalue = max(stabvalue, edge.r + 1)
      stablevalue[i][state] = stabvalue
  for i in range(len(auts)):
    nonlocalevents = newalphabet.difference(auts[i].alphabet)
    for state in auts[i].get_states():
      enabled[i][state].update(nonlocalevents)
  inittuple = tuple(initstate)
  dictionary = {}
  aut_sync = IntervalAutomaton(newalphabet, aut.collection)
  def allmarked(statetuple):
      for state in statetuple:
          if not state.marked:
              return False
      return True
  initstate = aut_sync.add_new_state(allmarked(inittuple))
  aut_sync.initial = initstate
  dictionary[(inittuple, zeroclocktuple)] = initstate
  tovisit = [(inittuple, zeroclocktuple)]
  edgestoadd = []
  print "add edges"
  succcalctime = 0
  addstatetime = 0
  calccurrenab = 0
  count = 0
  while len(tovisit) != 0:
    count += 1
    statetuple, clocktuple = tovisit.pop()
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
          successorlists.append([None])
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
        successors.append(succtuple)
        if needtoincrement:
          break
      for succtuple in successors:
        edgel, edger, stable = 0, infinity, 0
        newstatetuple = []
        print (statetuple, clocktuple)
        print succtuple
        for i, edge in enumerate(succtuple):
            if edge == None:
                stable = max(stable, stablevalue[i][statetuple[i]])
                newstatetuple.append(statetuple[i])
                continue
            edgel, edger = max(edgel, edge.l-clocktuple[i]), min(edger, edge.r-clocktuple[i])
            newstatetuple.append(edge.succ)
        print edgel, edger
        if edgel > edger:
            break
        # If the nonlocal states stabilize after edger then iterate up to edger
        newstatetuple = tuple(newstatetuple)
        print stable
        stable = min(stable, edger + 1)
        print stable
        for time in range(edgel, stable):
            newclocktuple = tuple([min(c + time, stablevalue[i][statetuple[i]]) if succtuple[i] == None else 0
                                   for i, c in enumerate(clocktuple)])
            if (newstatetuple, newclocktuple) not in dictionary:
              newstate = aut_sync.add_new_state(allmarked(newstatetuple))
              dictionary[(newstatetuple, newclocktuple)] = newstate
              tovisit.append((newstatetuple, newclocktuple))
            edgestoadd.append(IntervalEdge(dictionary[(statetuple, clocktuple)],
                                                      dictionary[(newstatetuple, newclocktuple)], event, time, time))
        # If the nonlocal states stabilize after edger then add a final edge from stable to edger
        stable = max(stable, edgel)
        if stable <= edger:
            newclocktuple = tuple([min(stable, stablevalue[i][statetuple[i]]) if succtuple[i] == None else 0
                                   for i in range(len(auts))])
            if (newstatetuple, newclocktuple) not in dictionary:
              newstate = aut_sync.add_new_state(allmarked(newstatetuple))
              dictionary[(newstatetuple, newclocktuple)] = newstate
              tovisit.append((newstatetuple, newclocktuple))
            edgestoadd.append(IntervalEdge(dictionary[(statetuple, clocktuple)],
                                                      dictionary[(newstatetuple, newclocktuple)], event, stable, edger))
        #print aut_sync
    #if count % 500 == 0:
      #print "succcalctime" +str(succcalctime)
      #print "addstatetime" +str(addstatetime)
      #print "calccurrenab" +str(calccurrenab)
  print len(dictionary)
  print "end add edges"
  print succcalctime
  print addstatetime
  print calccurrenab
  print "added edges"
  aut_sync.add_edges(edgestoadd)
  print "end add edges"
  aut_sync.save_as_dot("intsync.dot")
  #if depth == 5:
    #auia = aieia
  return aut_sync

def IntervalToTick(aut):
    tickaut = data_structure.Automaton(aut.alphabet, aut.collection)
    dictionary = {}
    tickaut.initial = tickaut.add_new_state(aut.initial.marked)
    dictionary[aut.initial] = tickaut.initial
    tovisit = [aut.initial]
    if 'tick' not in aut.collection.events:
        aut.collection.make_event('tick', False, True, False)
    tick = aut.collection.events['tick']
    infinity = float('inf')
    edgestoadd = []
    while len(tovisit) != 0:
        intstate = tovisit.pop()
        tickstate = dictionary[intstate]
        maxticks = max([edge.l if edge.r == infinity else edge.r + 1 for edge in intstate.get_outgoing()])
        tickstates = [tickstate] + [tickaut.add_new_state(tickstate.marked) for i in range(maxticks)]
        edgestoadd.extend([data_structure.Edge(tickstate[i], tickstate[i+1], tick) for i in range(maxticks)])
        edgestoadd.append(data_structure.Edge(tickstate[maxticks+1], tickstate[maxticks+1], tick))
        for edge in intstate.get_outgoing():
            if edge.succ not in dictionary:
                newstate = tickaut.add_new_state(edge.succ.marked)
                dictionary[edge.succ] = newstate
                tovisit.append(newstate)
            succstate = dictionary[edge.succ]
            l,r = edge.l, min(maxticks, edge.r)+1
            for i in range(l,r):
                edgestoadd.append(data_structure.Edge(tickstates[i], succstate, edge.label))
    tickaut.add_edges(edgestoadd)
    return tickaut

def load_interval_automaton(collect, fname, test_standardized, needs_marker_states):
    """
    Load an automaton file.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automaton.
    @rtype:  L{Automaton}
    """
    flags = 0
    if test_standardized:
        flags = flags | frontend.TEST_STANDARDIZED
    if needs_marker_states:
        flags = flags | frontend.MUST_HAVE_MARKER_STATE

    return frontend.load_automaton_file(collect, fname, IntervalAutomatonLoader,
                                        flags)

# }}}
# {{{ def load_automata(collect, fnames, test_standardized, needs_marker_states)
def load_interval_automata(collect, fnames, test_standardized, needs_marker_states):
    """
    Load many automata files.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fnames: Comma-seperated list of automata filenames.
    @type  fnames: C{str}

    @param test_standardized: Check and report whether the loaded automaton is
                              standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automata.
    @rtype:  A C{list} of L{Automaton}
    """
    aut_list = []
    for fname in fnames.split(','):
        if len(fname) > 0:
            aut_list.append(load_interval_automaton(collect, fname,
                                       test_standardized, needs_marker_states))

    return aut_list

def make_interval_product(aut_names, productname):
    coll = collection.Collection()
    auts = load_interval_automata(collection.Collection(), aut_names, False, True)
    product = IntervalSynchronousProduct(auts, coll)
    saver = IntervalAutomatonSaver()
    product.save_as_dot("C.dot")
    saver.save(product, productname)

def tick_to_interval(aut, tick):
    intaut = IntervalAutomaton(aut.alphabet, aut.collection)

def interval_plantify(aut):
    intaut = IntervalAutomaton(aut.alphabet, aut.collection)
    uncontrollable = [event for event in aut.alphabet if not event.controllable]
    smap = {}
    for state in aut.get_states():
        nstate = intaut.add_new_state(state.marked)
        smap[state] = nstate
    dump = intaut.add_new_state(False)
    for state in aut.get_states():
        uncontrollableint = collections.defaultdict(list)
        for edge in state.get_outgoing():
            intaut.add_edge_data(smap[edge.pred], smap[edge.succ], edge.label, edge.l, edge.r)
            if not edge.label.controllable:
                uncontrollableint[edge.label].append((edge.l,edge.r))
        for uncontevent, tups in uncontrollableint.iteritems():
            tups.sort()
            bottom = -1
            for tup in tups:
                assert(bottom < tup[0])
                if bottom + 1 < tup[0]:
                    intaut.add_edge_data(smap[state], dump, uncontevent, bottom + 1, tups[0]-1)
                bottom = tup[1]
            if bottom != float('inf'):
                intaut.add_edge_data(smap[state], dump uncontevent, bottom + 1, float('inf'))
    return intaut

def supervisor_interval(aut, forcible_events):
    forbidden_states = set()
    forbidden_trans = set()
    marked_states = [state for state in aut.get_states() if state.marked]
    changed = True
    while changed:
        changed = False
        reachable = set(marked_states)
        to_expand = list(marked_states)
        while len(to_expand) != 0:
            state = to_expand.pop()
            for edge in state.get_incoming():
                if edge not in forbidden_trans and \
                    edge.pred not in reachable and edge.pred not in forbidden_states:
                    reachable.add(edge.pred)
                    to_expand.append(edge.pred)
        num_bef = len(forbidden_states)
        forbidden_states.update([state for state in aut.get_states if state not in reachable])
        changed = changed or num_bef < len(forbidden_states)
        for state in aut.get_states():
            max_uncont_time = float('inf')
            for edge in state.get_outgoing():
                if edge not in forbidden_trans:
                    if edge.succ in forbidden_states:
                        forbidden_trans.add(edge)
                        changed = True
            max_force_time = -1
            for edge in state.get_outgoing():
                if edge in forbidden_trans:
                    if not edge.label.controllable:
                        max_uncont_time = min(max_uncont_time, edge.l-1)
                else:
                    if edge.r == float('inf'):
                        max_force_time = float('inf')
                    elif edge.label in forcible_events:
                        max_force_time = max(max_force_time, edge.r)
            max_time = min(max_force_time, max_uncont_time)
            if max_time < 0:
                forbidden_states.add(state)
                continue
            elif max_time == float('inf'):
                continue
            for edge in state.get_outgoing():
                if edge not in forbidden_trans:
                    if edge.l >= max_time:
                        changed = True
                        forbidden_trans.add(edge)
                    elif edge.r >= max_time:
                        edge.r = max_time - 1
                        changed = True
    for state in forbidden_states:
        aut.remove_state(state)
    for edge in forbidden_trans:
        aut.remove(edge)
    return aut