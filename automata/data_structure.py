#
# $Id: data_structure.py 768 2011-03-24 12:46:46Z hat $
#
"""
Data structures for expressing discrete automata without data.
"""

from automata import baseobjects, path, collection

# {{{ class Edge(baseobjects.EqualityObject):
class Edge(baseobjects.EqualityObject):
    """
    Classs representing an edge between two states.

    @ivar pred: Predecessor state.
    @type pred: L{State} or L{WeightedState}

    @ivar succ: Successor state.
    @type succ: L{State} or L{WeightedState}

    @ivar label: Event label associated with the edge.
    @type label: L{Event}
    """
    __slots__ = ['pred', 'succ', 'label']

    def __init__(self, pred, succ, label):
        self.pred = pred
        self.succ = succ
        self.label = label

    def __repr__(self):
        return "Edge(%r, %r, %r)" % (self.pred, self.succ, self.label)

    def _equals(self, other):
        return self.pred is other.pred and \
               self.succ is other.succ and \
               self.label is other.label
               
    def __hash__(self):
      return (self.pred, self.succ, self.label).__hash__()

    def copy(self, new_pred, new_succ):
        """
        Make a copy of the edge, and place it between the given new states.

        @param new_pred: New predecessor state.
        @type  new_pred: L{State}

        @param new_succ: New successor state.
        @type  new_succ: L{State}
        """
        return Edge(new_pred, new_succ, self.label)

    def clear(self):
        self.pred = None
        self.succ = None
        self.label = None

# }}}

# {{{ class BaseState(baseobjects.EqualityObject):
class BaseState(baseobjects.EqualityObject):
    """
    Base class representing a state in an automaton.

    @ivar number: Unique number of the state (within the automaton).
    @type number: C{int}

    @ivar marked: Boolean indicating this state is a marker state.
    @type marked: C{bool}

    @ivar out_edges: Outgoing edges.
    @type out_edges: C{list} of L{Edge}

    @ivar in_edges: Outgoing edges.
    @type in_edges: C{list} of L{Edge}
    """
    __slots__ = ['number', 'marked', 'out_edges', 'in_edges']

    def __init__(self, number, marked):
        super(BaseState, self).__init__()
        self.number = number
        self.marked = marked
        self.in_edges  = []
        self.out_edges = []

    def _equals(self, other):
        return self.number == other.number

    def __hash__(self):
        return self.number

    def __repr__(self):
        if self.marked:
            return "<%s (number = %d, marked)>" % \
                                        (self.__class__.__name__, self.number)
        else:
            return "<%s (number = %d)>" % (self.__class__.__name__, self.number)

    def set_marked(self, marked):
        """
        Set the L{self.marked} property of the state.

        @param marked: Boolean indicating the state should be considered a
                       marked state.
        @type  marked: C{bool}
        """
        self.marked = marked

    def __lt__(self, other):
        if self is other:
            return False
        if type(self) is not type(other):
            raise NotImplementedError('Cannot compare a %s with something '
                                      'else' % self.__class__.__name__)

        return self.number < other.number

    def clear(self):
        """
        Prepare the state for removal by the garbage collector.
        In particular, remove links to other data.
        """
        for edge in self.out_edges:
            edge.clear()
        self.in_edges  = []
        self.out_edges = []
        self.number = None

    # {{{ def get_outgoing(self, evt = None):
    def get_outgoing(self, evt = None):
        """
        Return an iterable for the outgoing edges. If L{evt} is specified,
        only return edges that have event L{evt}.

        @param evt: If specified, only return edges with this event.
        @type  evt: L{Event}, or C{None} if not specified.

        @return: Iterable over edges.
        @rtype:  C{iterable} over L{Edge}
        """
        if evt is None:
            return self.out_edges
        else:
            return (edge for edge in self.out_edges if edge.label is evt)

    # }}}
    # {{{ def get_incoming(self, evt = None):
    def get_incoming(self, evt = None):
        """
        Return an iterable for the incoming edges. If L{evt} is specified,
        only return edges that have event L{evt}.

        @param evt: If specified, only return edges with this event.
        @type  evt: L{Event}, or C{None} if not specified.

        @return: Iterable over edges.
        @rtype:  C{iterable} over L{Edge}
        """
        if evt is None:
            return self.in_edges
        else:
            return (edge for edge in self.in_edges if edge.label is evt)

    # }}}
    # {{{ def remove_incoming_edge(self, edge):
    def remove_incoming_edge(self, edge):
        """
        Remove an incoming edge from the state.

        @param edge: Incoming edge to remove.
        @type  edge: L{Edge}
        """
        for idx, inedge in enumerate(self.in_edges):
            if inedge is edge:
                if idx < len(self.in_edges) - 1:
                    self.in_edges[idx] = self.in_edges[-1]
                del self.in_edges[-1]
                return

        msg = "Trying to remove a non-existing incoming edge " \
              "%r from state %r" % (edge, self)
        raise ValueError(msg)

    # }}}
    # {{{ def remove_outgoing_edge(self, edge):
    def remove_outgoing_edge(self, edge):
        """
        Remove an outgoing edge from the state.

        @param edge: Outgoing edge to remove.
        @type  edge: L{Edge}
        """
        for idx, outedge in enumerate(self.out_edges):
            if outedge is edge:
                if idx < len(self.out_edges) - 1:
                    self.out_edges[idx] = self.out_edges[-1]
                del self.out_edges[-1]
                return

        msg = "Trying to remove a non-existing outgoing edge " \
              "%r from state %r" % (edge, self)
        raise ValueError(msg)

    # }}}

# }}}
# {{{ class BaseAutomaton(baseobjects.EqualityObject):
class BaseAutomaton(baseobjects.EqualityObject):
    """
    Baseclass for an automaton.

    @ivar name: Name of the automaton (optional).
    @type name: C{str} or C{None}

    @ivar initial: Initial state if it exists.
    @type initial: L{BaseState} or C{None}

    @ivar _states: Mapping of state number to the state information.
    @type _states: C{dict} of C{int} to L{BaseState}

    @ivar state_names: Names of states. May be incomplete.
    @type state_names: C{dict} of C{int} to C{str}

    @ivar state_class: Class used for states in the automaton.
    @type state_class: L{BaseState}

    @ivar edge_class: Class used for edges in the automaton.
    @type edge_class: L{Edge}

    @ivar aut_kind: Kind of automaton. Currently known values: C{'plant'},
                    C{'requirement'}, C{'supervisor'}, and C{'unknown'}.
    @type aut_kind: C{str}

    @ivar alphabet: Alphabet of the automaton.
    @type alphabet: C{set} of L{collection.Event},
                    must be a sub-set of C{self.collection.events}

    @ivar collection: Automata collection (contains shared set of events)
                      that this automaton is part of.
    @type collection: L{Collection}

    @ivar free_number: Cache containing (probably) first free state number.
    @type free_number: C{int}

    @todo: Merge L{_states} and L{state_names} in a way that does not conflict
           with moving to Cython or C.
    """
    def __init__(self, alphabet, coll, state_class, edge_class):
        super(BaseAutomaton, self).__init__()
        self.name = None
        self.initial = None
        self._states = {}
        self.state_names = {}
        self.state_class = state_class
        self.edge_class  = edge_class
        self.aut_kind = 'unknown'
        self.alphabet = alphabet
        self.collection = coll
        self.free_number = 0

    def _equals(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    # {{{ def __str__(self):
    def __str__(self):
        lines = ['Number of states: %d' % self.get_num_states(),
                 'Number of transitions: %d' % self.get_num_edges()]
        return "\n".join(lines)

    # }}}

    # {{{ ABSTRACT: def _make_automaton(self, alphabet):
    def _make_automaton(self, alphabet):
        """
        Construct an empty automaton object of L{self}.

        @param alphabet: Alphabet of the new automaton.
        @type  alphabet: C{Set} of L{Event}

        @return: Empty automaton.
        @rtype:  L{BaseAutomaton}
        """
        raise NotImplementedError("Implement me in %r" % type(self))

    # }}}
    # {{{ def clear(self):
    def clear(self):
        """
        Prepare the automaton for removal by the garbage collector.
        """
        for state in self.get_states():
            state.clear()

        self.name = None
        self.initial = None
        self._states = {}
        self.state_names = {}
        self.alphabet = set()
        self.collection = None
        self.free_number = 0

    # }}}
    # {{{ def add_event_set(self, evtset):
    def add_event_set(self, evtset):
        """
        Add set of events L{evtset} to the alphabet of the automaton."
        """
        self.alphabet = self.alphabet.union(evtset)

    # }}}
    # {{{ def get_alphabet_text(self):
    def get_alphabet_text(self):
        """
        Return a human-readable dump of the alphabet.
        """
        lines = []
        line = 'Alphabet:'
        for evt in self.alphabet:
            if len(line) + 1 + len(evt.name) > 79:
                lines.append(line)
                line = "    " + evt.name
            else:
                line = line + " " + evt.name

        lines.append(line)
        return "\n".join(lines)

    # }}}
    # {{{ def copy(self, add_marker_events = False):
    def copy(self, add_marker_events = False):
        """
        Copy the automaton.

        @param add_marker_events: Add self-loops with the marker event for all
                                  marker states.
        @type  add_marker_events: C{bool}

        @return: A copy of L{self}.
        @rtype: L{Automaton}
        """
        marker_event = self.collection.marker_event

        if add_marker_events and marker_event not in self.alphabet:
            alphabet = self.alphabet.union(set([marker_event]))
        else:
            alphabet = self.alphabet

        new_aut = self._make_automaton(alphabet)
        new_aut.set_kind(self.aut_kind)
        new_aut.name = self.name
        for state in self.get_states():
            ns = new_aut.add_new_state(state.marked, state.number)
            if add_marker_events and state.marked:
                new_edge = new_aut.edge_class(ns, ns, marker_event)
                new_aut.add_edge(new_edge)

        for state in self.get_states():
            for edge in state.get_outgoing():
                new_edge = edge.copy(new_aut.get_state(edge.pred.number),
                                     new_aut.get_state(edge.succ.number))
                new_aut.add_edge(new_edge)

        if self.initial is None:
            new_aut.initial = None
        else:
            new_aut.initial = new_aut.get_state(self.initial.number)

        return new_aut
        
    def copy_optimized(self, add_marker_events = False):
        """
        Copy the automaton.

        @param add_marker_events: Add self-loops with the marker event for all
                                  marker states.
        @type  add_marker_events: C{bool}

        @return: A copy of L{self}.
        @rtype: L{Automaton}
        """
        marker_event = self.collection.marker_event

        if add_marker_events and marker_event not in self.alphabet:
            alphabet = self.alphabet.union(set([marker_event]))
        else:
            alphabet = self.alphabet

        new_aut = self._make_automaton(alphabet)
        new_aut.set_kind(self.aut_kind)
        new_aut.name = self.name
        edgestoadd = []
        for state in self.get_states():
            ns = new_aut.add_new_state(state.marked, state.number)
            if add_marker_events and state.marked:
                new_edge = new_aut.edge_class(ns, ns, marker_event)
                edgestoadd.append(new_edge)
                #new_aut.add_edge(new_edge)
                
        for state in self.get_states():
            for edge in state.get_outgoing():
                new_edge = edge.copy(new_aut.get_state(edge.pred.number),
                                     new_aut.get_state(edge.succ.number))
                edgestoadd.append(new_edge)
                #new_aut.add_edge(new_edge)

        new_aut.add_edges(edgestoadd)
        if self.initial is None:
            new_aut.initial = None
        else:
            new_aut.initial = new_aut.get_state(self.initial.number)

        return new_aut

    # }}}

    # {{{ def set_name(self, name):
    def set_name(self, name):
        """
        Set the name of the automaton.

        @param name: Name of the automaton.
        @type  name: C{str}
        """
        self.name = name
    # }}}
    # {{{ def get_states(self):
    def get_states(self):
        """
        Get an iterable for iterating over the states of the automaton.

        @note: The state set should not be modified while using the iterable.

        @return: Iterable for iterating over the states of the automaton.
        @rtype:  C{iter} over L{BaseState}
        """
        return self._states.itervalues()
    # }}}
    # {{{ def get_state(self, number):
    def get_state(self, number):
        """
        Get state by number.

        @param number: Number of the state to retrieve.
        @type  number: C{int}

        @return: State with the specified number.
        @rtype:  C{BaseState}
        """
        return self._states[number]
    # }}}
    # {{{ def has_state(self, number):
    def has_state(self, number):
        """
        Check whether the state L{number} exists in the automaton.

        @param number: Number of the state to look for.
        @type  number: C{int}

        @return: Indication whether the state exists.
        @rtype:  C{bool}
        """
        return number in self._states
    # }}}
    # {{{ def get_num_states(self):
    def get_num_states(self):
        """
        @return: Number of states in the weighted automaton.
        @rtype:  C{int}
        """
        return len(self._states)
    # }}}
    # {{{ def set_initial(self, state):
    def set_initial(self, state):
        """
        Set initial state of the automaton.

        @param state: New initial state.
        @type  state: L{BaseState}
        """
        assert state is self._states[state.number]
        self.initial = state
    # }}}

    # {{{ def add_new_state(self, marked, num = None):
    def _find_free_number(self):
        """
        Find a free number to use as a state number.

        @return: Free state number.
        @rtype:  C{int}
        """
        while self.free_number in self._states:
            self.free_number = self.free_number + 1

        num = self.free_number
        self.free_number = self.free_number + 1
        return num

    def add_new_state(self, marked, num = None):
        """
        Add a state to the automaton.

        @param marked: State should be considered a marker state.
        @type  marked: C{bool}

        @param num: State number to add.
        @type num:  C{int}

        @return: Added state.
        @rtype:  L{BaseState}
        """
        if num is None:
            num = self._find_free_number()
        else:
            assert num not in self._states

        state = self.state_class(num, marked)
        self._states[num] = state
        return state

    # }}}
    # {{{ def remove_state(self, state):
    def remove_state(self, state):
        """
        Remove L{state} from the automaton.

        @param state: State to remove.
        @type  state: L{BaseState}
        """
        assert self.get_state(state.number) is state

        for edge in state.get_outgoing():
            if edge.succ is not state: # Not a self-loop.
                edge.succ.remove_incoming_edge(edge)
        for edge in state.get_incoming():
            if edge.pred is not state: # Not a self-loop.
                edge.pred.remove_outgoing_edge(edge)

        state.out_edges = []
        state.in_edges  = []

        del self._states[state.number]
        if state.number in self.state_names:
            del self.state_names[state.number]

        # If state is initial state, remove that as well.
        if state is self.initial:
            self.initial = None

    # }}}
    # {{{ def add_edge(self, edge):
    
    def add_edges(self, edges):
      """
      Add edge to the automaton.

      @param edge: Edge to add.
      @type  edge: L{Edge}
      """
      for edge in edges:
        assert edge.label in self.alphabet
        assert edge.pred is self.get_state(edge.pred.number)
        assert edge.succ is self.get_state(edge.succ.number)
        assert type(edge) is self.edge_class
      
      presentedges = set()
      for state in self.get_states():
        for edge in state.get_outgoing():
          presentedges.add(edge)
      for edge in edges:
        if edge not in presentedges:
          presentedges.add(edge)
          edge.pred.out_edges.append(edge)
          edge.succ.in_edges.append(edge)
    
    def add_edge(self, edge):
        """
        Add edge to the automaton.

        @param edge: Edge to add.
        @type  edge: L{Edge}
        """
        assert edge.label in self.alphabet
        assert edge.pred is self.get_state(edge.pred.number)
        assert edge.succ is self.get_state(edge.succ.number)
        assert type(edge) is self.edge_class

        # Check whether such an edge exists.
        for exist_edge in edge.pred.get_outgoing():#edge.label): # edited since the label search doesn't work for weighted edges
            if exist_edge.label == edge.label and exist_edge.pred == edge.pred and exist_edge.succ == edge.succ:
            # if exist_edge == edge: # Same thing as 2 lines up.
                return
        
        # Edge not present yet, add it.
        edge.pred.out_edges.append(edge)
        edge.succ.in_edges.append(edge)

    # }}}
    # {{{ def remove_edge(self, edge):
    def remove_edge(self, edge):
        """
        Remove an edge from the automaton.

        @param edge: Edge to remove.
        @type  edge: L{Edge}
        """
        edge.pred.remove_outgoing_edge(edge)
        edge.succ.remove_incoming_edge(edge)

    # }}}
    # {{{ def set_state_name(self, state, name):
    def set_state_name(self, state, name):
        """
        Set the name of a state.

        @param state: State to add name to.
        @type  state: L{BaseState}

        @param name: Name to use.
        @type  name: C{str}

        @todo: Code does not check for name conflicts.
        """
        self.state_names[state.number] = name
    # }}}
    # {{{ def make_state_names_complete(self):
    def make_state_names_complete(self):
        """
        Ensure that for all states in the automaton, a L{self.state_names}
        entry exists.
        """
        number = len(self.state_names)
        name_set = None
        for state in self.get_states():
            if state.number not in self.state_names:
                # The first time, initialize the name_set with the existing
                # state names.
                if name_set is None:
                    name_set = set(self.state_names.itervalues())
                    assert len(name_set) == len(self.state_names)
                # Find a fresh state name.
                while True:
                    newname = "state%d" % number
                    number = number + 1
                    if newname not in name_set:
                        break

                self.set_state_name(state, newname)
                name_set.add(newname)
    # }}}
    # {{{ def set_kind(self, kind):
    def set_kind(self, kind):
        """
        Set the automaton kind of the automaton.

        @param kind: New kind of the automaton.
        @type  kind: C{str}
        """
        self.aut_kind = kind
    # }}}

    # {{{ def get_num_edges(self):
    def get_num_edges(self):
        """
        @return: Number of edges in the automaton.
        @rtype:  C{int}
        """
        return sum(1 for state in self.get_states()
                     for edge in state.get_outgoing())
    # }}}

    # {{{ def is_standardized(self):
    def is_standardized(self):
        """
        Is the automaton standardized (single tau event from initial state)?

        @return: I am a standardized automation.
        @rtype: C{bool}
        """
        if self.initial is None:
            return False # Not even a valid automaton.

        count = sum(1 for edge in self.initial.get_outgoing())
        if count == 0:
            return False # Not a single transition from initial state.

        tau_evt = self.collection.events.get('tau', None)
        if tau_evt is None:
            return False    # 'tau' doesn't exist at all.
        if tau_evt not in self.alphabet:
            return False    # No 'tau' in the alphabet.

        # Only 'tau' from initial state.
        for edge in self.initial.get_outgoing():
            if edge.label is not tau_evt:
                return False

        return True
    # }}}

    # {{{ def reachable_states(self, start_state, allowed_events):
    def reachable_states(self, start_state, allowed_events):
        """
        Collect and return all reachable states from L{start_state} using only
        transitions with an event in L{allowed_events}.

        @param start_state: Start state to compute reachable set from.
        @type  start_state: L{BaseState}

        @param allowed_events: Set of events that may be traversed
                               (C{None} means all events are allowed).
        @type  allowed_events: Either C{set} of C{collection.Event} or C{None}

        @return: Set of reachable states.
        @rtype: C{set} of L{BaseState}
        """

        if start_state is None:
            return set()

        reachable = set([start_state])
        to_examine = set([start_state])
        while len(to_examine) > 0:
            state = to_examine.pop()
            for edge in state.get_outgoing():
                if allowed_events is None or edge.label in allowed_events:
                    if edge.succ not in reachable:
                        reachable.add(edge.succ)
                        to_examine.add(edge.succ)
        return reachable

    # }}}
    # {{{ def coreachable_states(self, start_state, allowed_events):
    def coreachable_states(self, start_state, allowed_events):
        """
        Collect and return all coreachable states from L{start_state} using only
        transitions with an event in L{allowed_events}.

        @param start_state: Start state to compute coreachable set from.
        @type  start_state: L{BaseState}

        @param allowed_events: Set of events that may be traversed
                               (C{None} means all events are allowed).
        @type  allowed_events: Either C{set} of C{collection.Event} or C{None}

        @return: Set of coreachable states.
        @rtype:  C{set} of L{BaseState}

        @todo: Move uses to coreachable_states_set() if possible.
        """
        if start_state is None:
            return set()

        return self.coreachable_states_set(set([start_state]), allowed_events)

    # }}}
    # {{{ def coreachable_states_set(self, start_set, allowed_events):
    def coreachable_states_set(self, start_set, allowed_events):
        """
        Collect and return all coreachable states from L{start_set} using only
        transitions with an event in L{allowed_events}.

        @param start_set: Set of start states to compute coreachable set from,
                          if C{None}, use all marker states as starting points.
        @type  start_set: C{set} of L{BaseState} or C{None}

        @param allowed_events: Set of events that may be traversed
                               (C{None} means all events are allowed).
        @type  allowed_events: Either C{set} of C{collection.Event} or C{None}

        @return: Set of coreachable states.
        @rtype:  C{set} of L{BaseState}
        """
        if start_set is None:
            start_set = set(state for state in self.get_states()
                            if state.marked)

        coreachable = start_set.copy()
        to_examine = start_set.copy()
        while len(to_examine) > 0:
            state = to_examine.pop()
            for edge in state.get_incoming():
                if allowed_events is None or edge.label in allowed_events:
                    if edge.pred not in coreachable:
                        coreachable.add(edge.pred)
                        to_examine.add(edge.pred)
        return coreachable

    # }}}
    # {{{ def reduce(self, reachability = False, coreachability = False):
    def reduce(self, reachability = False, coreachability = False):
        """
        Reduce states of L{self} based on reachability and/or co-reachability
        properties (throw out states that violate the required property).

        @param reachability: Reduce automaton on reachability.
        @type  reachability: C{bool}

        @param coreachability: Reduce automaton on co-reachability.
        @type  coreachability: C{bool}

        @return: Indication whether the reduced automaton is good (non-empty).
        @rtype:  C{bool}
        """
        good_states = set(self.get_states())

        if reachability:
            reachables = self.reachable_states(self.initial, None)
            good_states.intersection_update(reachables)

        if coreachability:
            coreachables = set()
            for state in good_states:
                if state.marked and state not in coreachables:
                    coreachables.update(self.coreachable_states(state, None))
            good_states.intersection_update(coreachables)

        for state in list(self.get_states()):
            if state not in good_states:
                self.remove_state(state)

        return self.initial is not None

    # }}}

# }}}

    

State = BaseState #: State in an automaton. @todo: Remove me.

# {{{ class Automaton
class Automaton(BaseAutomaton):
    """
    Automaton with states.
    """
    def __init__(self, alphabet, coll):
        super(Automaton, self).__init__(alphabet, coll, State, Edge)

    def _make_automaton(self, alphabet):
        return Automaton(alphabet, self.collection)

    def add_edge_data(self, pred, succ, label):
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
        self.add_edge(Edge(pred, succ, label))

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

    # }}}

    # {{{ def to_dot(self, plot_marker_events = False):
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

                text.append("s%s -> s%d [label=\"%s\"];"
                            % (state.number, edge.succ.number, edge.label.name))

        text.append('}')
        return '\n'.join(text)

    # }}}
    # {{{ def save_as_dot(self, fname, plot_marker_events = False):
    def save_as_dot(self, fname, plot_marker_events = False):
        """ Save the automaton to file as 'fname' """
        handle = open(fname, 'w')
        handle.write(self.to_dot(plot_marker_events))
        handle.write('\n')
        handle.close()

    # }}}

# }}}

# {{{ Load
class AutomatonLoader(collection.BaseAutomatonLoader):
    """
    @ivar state_map: Mapping of state name to State.
    @type state_map: C{dict} of C{str} to L{State}
    """
    def __init__(self, coll):
        super(AutomatonLoader, self).__init__(coll)
        self.state_map = {}


    def make_new_automaton(self, alphabet):
        return Automaton(alphabet, self.collection)

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
        if len(edge_data) != 3:
            return "Edge %r should have only three fields." % repr(edge_data)

        src = self.state_map[edge_data[0]]
        dst = self.state_map[edge_data[1]]
        evt = self.collection.get_event(edge_data[2])
        self.automaton.add_edge_data(src, dst, evt)
        return None

    def get_sectname(self):
        return "automaton"


def load_automaton(coll, fname):
    """
    Convenience function for loading an unweighted automaton.

    @param fname: Name of the file to load.
    @type  fname: C{str}

    @return: Loaded automaton if no errors were found.
    @rtype:  L{Automaton}, C{None} if errors were found
    """
    loader = AutomatonLoader(coll)
    aut = loader.load(fname)
    return aut
# }}}
# {{{ Save
class AutomatonSaver(collection.BaseAutomatonSaver):
    def check_aut_type(self, aut):
        #return type(aut) is Automaton
        return True

    def get_sectname(self):
        return "automaton"

    def convert_single_edge(self, aut, edge):
        return "(%s, %s, %s)" % (aut.state_names[edge.pred.number],
                                 aut.state_names[edge.succ.number],
                                 edge.label.name)

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

# }}}
