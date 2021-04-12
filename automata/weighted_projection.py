#
# $Id: weighted_projection.py 727 2010-04-08 10:41:14Z hat $
#
"""
Weighted abstraction functions.
"""
from automata import weighted_structure, maxplus

def new_state(waut, state, new_waut):
    """
    Return the equivalent state L{state} of L{waut} in L{new_waut}.

    @param waut: Existing weighted automaton.
    @type  waut: L{WeightedAutomaton}

    @param state: Existing state in L{waut}.
    @type  state: L{WeightedState}

    @param new_waut: 'New' weighted automaton, possibly without an equivalent
                     of state L{state}.
    @type  new_waut: L{WeightedAutomaton}

    @postcond: Equivalent state L{state} exists in L{new_waut},
               L{WeightedAutomaton.initial} in L{new_waut} is setup to the
               initial state if it exists.

    @return: Equivalent state of L{state} in L{new_waut}
    @rtype:  L{WeightedState}

    @todo: Looks like it belongs in an Algorithm instance.
    """
    if new_waut.has_state(state.number):
        return new_waut.get_state(state.number)

    ns = new_waut.add_new_state(state.marked, state.number)
    if waut.initial is state:
        new_waut.set_initial(ns)

    return ns


def weighted_projection(waut, preserved_events):
    """
    Perform abstraction of weighted automaton L{waut} over the subset
    L{preserved_events} of the automaton events.

    @param waut: Weighed automaton.
    @type  waut: L{WeightedAutomaton}

    @param preserved_events: Events to preserve.
    @type  preserved_events: C{set} of L{collection.Event}

    @return: Abstracted automaton.
    @rtype:  L{WeightedAutomaton}
    """
    coll = waut.collection
    new_waut = weighted_structure.WeightedAutomaton(preserved_events, coll)
    new_waut.set_kind(waut.aut_kind)

    non_sub = waut.alphabet.difference(preserved_events)
    for evt in preserved_events:
        maxpair_weight = compute_statepairs(waut, evt, non_sub)
        for (ws1, ws2), wght in maxpair_weight.iteritems():
            nws1 = new_state(waut, ws1, new_waut)
            nws2 = new_state(waut, ws2, new_waut)
            new_waut.add_edge_data(nws1, nws2, evt, wght)

    assert new_waut.initial is not None
    return new_waut


def compute_statepairs(waut, evt, non_sub):
    """
    Compute maximum weight between pairs of states in L{waut} that are
    connected through the longest path that contains 1 edge with event L{evt},
    and zero or more edges with an event from L{non_sub}.

    @param waut: Weighed automaton.
    @type  waut: L{WeightedAutomaton}

    @param evt: Event that must happen exactly once on the longest path between
                each pair of states returned.
    @type  evt: L{collection.Event}

    @param non_sub: Events not to preserve, must be used at other transitions
                    of the longest path.
    @type  non_sub: C{set} of L{collection.Event}

    @return: Mapping of pairs of states in L{waut} to their maximal weight.
    @rtype:  C{dict} of (L{WeightedState}, L{WeightedState}) to (C{int} or
             C{None}) where C{None} means 'inifinite weight.
    """
    maxpair_weights = {}
    for state in waut.get_states():
        succs = list(state.get_outgoing(evt))
        if len(succs) == 0:
            continue

        pred_paths = calc_preds_path(waut, state, non_sub)
        for edge in succs:
            succ_paths = calc_succs_path(waut, edge.succ, non_sub)
            for ws1, wght1 in pred_paths.iteritems():
                for ws2, wght3 in succ_paths.iteritems():
                    pair = (ws1, ws2)
                    bestfound = maxpair_weights.get(pair, -1)
                    if bestfound is None:
                        continue  # Already infinite.

                    if wght1 is None or wght3 is None:
                        maxpair_weights[pair] = None
                    else:
                        total = wght1 + edge.weight + wght3
                        if total > bestfound:
                            maxpair_weights[pair] = total

    return maxpair_weights


def calc_succs_path(waut, state, non_sub):
    """
    Compute the longest path for all reachable states from L{state} while only
    traversing L{non_sub} edges.

    States reachable only without visiting a cycle will get a finite weight
    (namely the weight of the longest path to that state). States reachable
    after visiting one or more cycles get infinite weight, even if the sum of
    the weights at the edges of the cycle is 0. States that are part of a cycle
    also get infinite weight (ie the longest path to a state may visit that
    state several times).

    @param waut: Weighed automaton.
    @type  waut: L{WeightedAutomaton}

    @param state: Start state.
    @type  state: L{WeightedState}

    @param non_sub: Events of edges that may be traversed.
    @type  non_sub: C{set} of L{collection.Event}

    @return: Mapping of reachable states to the distance. Infinite distance
             is represented as C{None}
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None})
    """
    #: Set states reachable that have no longest path.
    reachables = waut.reachable_states(state, non_sub)

    distances = {}  #: Longest distance of each state.
    distance_states = set() #: set(distances.keys()) for 2.3 compability.
    #: Collection of direct neighbours (tuples (state, pred_neighbours)).
    neighbours = {state : get_pred_neighbours(state, reachables, non_sub)}

    while len(reachables) > len(distances): # Not all states done.
        assert len(neighbours) > 0
        to_remove = [] #: Collection of neighbours to remove
        for nstate, nstate_succs in neighbours.iteritems():
            if nstate_succs.issubset(distance_states):
                # All successor neighbours of nstate are in distances.
                dist = 0 #: Longest path to nstate.
                for edge in nstate.get_incoming():
                    if edge.label in non_sub and edge.pred in reachables:
                        # Max computation works since distances does
                        # not contain C{None} values at this time.
                        dist = max(dist, distances[edge.pred] + edge.weight)
                distances[nstate] = dist
                distance_states.add(nstate)
                to_remove.append(nstate)

        if len(to_remove) == 0:
            # No progress made ==> We have a cycle.
            break

        # Update neighbours.
        for tr in to_remove:
            del neighbours[tr]
            # And add new neighbours.
            for new_neigh in get_succ_neighbours(tr, reachables, non_sub):
                if new_neigh not in neighbours:
                    neighbours[new_neigh] = get_pred_neighbours(new_neigh,
                                                                reachables,
                                                                non_sub)

    if len(reachables) > len(distances):
        # Not all states done ==> we have a cycle, make all remaining states
        # have infinite longest path.
        for st in reachables.difference(distance_states):
            distances[st] = None

    return distances


# {{{ def calc_preds_path(waut, state, non_sub):
def calc_preds_path(waut, state, non_sub):
    """
    Compute the longest path for all co-reachable states from L{state} while
    only traversing L{non_sub} edges.

    States coreachable only without visiting a cycle will get a finite weight
    (namely the weight of the longest path to that state). States coreachable
    after visiting one or more cycles get infinite weight, even if the sum of
    the weights at the edges of the cycle is 0. States that are part of a cycle
    also get infinite weight (ie the longest path to a state may visit that
    state several times).

    @param waut: Weighed automaton.
    @type  waut: L{WeightedAutomaton}

    @param state: Start state.
    @type  state: L{WeightedState}

    @param non_sub: Events of edges that may be traversed.
    @type  non_sub: C{set} of L{collection.Event}

    @return: Mapping of coreachable states to the distance. Infinite distance
             is represented as C{None}
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None})
    """
    #: Set states coreachable that have no longest path.
    coreachables = waut.coreachable_states(state, non_sub)

    distances = {}  #: Longest distance of each state.
    distance_states = set() #: set(distances.keys()) for 2.3 compability.
    #: Collection of direct neighbours (tuples (state, succ_neighbours)).
    neighbours = {state : get_succ_neighbours(state, coreachables, non_sub)}

    while len(coreachables) > len(distances): # Not all states done.
        assert len(neighbours) > 0
        to_remove = [] #: Collection of neighbours to remove
        for nstate, nstate_succs in neighbours.iteritems():
            if nstate_succs.issubset(distance_states):
                # All successor neighbours of nstate are in distances.
                dist = 0 #: Longest path to nstate.
                for edge in nstate.get_outgoing():
                    if edge.label in non_sub and edge.succ in coreachables:
                        # Max computation works since distances does
                        # not contain C{None} values at this time.
                        dist = max(dist, distances[edge.succ] + edge.weight)
                distances[nstate] = dist
                distance_states.add(nstate)
                to_remove.append(nstate)

        if len(to_remove) == 0:
            # No progress made ==> We have a cycle.
            break

        # Update neighbours.
        for tr in to_remove:
            del neighbours[tr]
            # And add new neighbours.
            for new_neigh in get_pred_neighbours(tr, coreachables, non_sub):
                if new_neigh not in neighbours:
                    neighbours[new_neigh] = get_succ_neighbours(new_neigh,
                                                                coreachables,
                                                                non_sub)

    if len(coreachables) > len(distances):
        # Not all states done ==> we have a cycle, make all remaining states
        # have infinite longest path.
        for st in coreachables.difference(distance_states):
            distances[st] = None

    return distances

# }}}

# {{{ def get_pred_neighbours(state, stateset, evtset):
def get_pred_neighbours(state, stateset, evtset):
    """
    Get all predecessor neighbours of L{state} that are in L{stateset} and
    are connected through an event in L{evtset}.

    @param state: Originating state.
    @type  state: L{WeightedState}

    @param stateset: Collection of allowed neighbours.
    @type  stateset: C{set} of L{WeightedState}

    @param evtset: Collection allowed events.
    @type  evtset: C{set} of L{Event}

    @return: Collection of predecessor neighbours.
    @rtype:  C{set} of L{WeightedState}
    """
    pred_neighbours = set()
    for edge in state.get_incoming():
        if edge.label in evtset and edge.pred in stateset:
            pred_neighbours.add(edge.pred)
    return pred_neighbours

# }}}
# {{{ def get_succ_neighbours(state, stateset, evtset):
def get_succ_neighbours(state, stateset, evtset):
    """
    Get all sucessor neighbours of L{state} that are in L{stateset} and
    are connected through an event in L{evtset}.

    @param state: Originating state.
    @type  state: L{WeightedState}

    @param stateset: Collection of allowed neighbours.
    @type  stateset: C{set} of L{WeightedState}

    @param evtset: Collection allowed events.
    @type  evtset: C{set} of L{Event}

    @return: Collection of sucessor neighbours.
    @rtype:  C{set} of L{WeightedState}

    @todo: This is a method in automaton.
    """
    succ_neighbours = set()
    for edge in state.get_outgoing():
        if edge.label in evtset and edge.succ in stateset:
            succ_neighbours.add(edge.succ)
    return succ_neighbours

# }}}
