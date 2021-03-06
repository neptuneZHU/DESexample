#
# $Id: compute_weight.py 717 2010-04-06 13:57:19Z hat $
#
"""
Routines for computing with weighted automata.
"""

DBG_TIME_OPTIMAL_SUP = False

from automata import weighted_product, conversion, maxplus, \
                     common, data_structure, weighted_structure, \
                     taskresource, product, path, algorithm#, supervisor

from automata import baseobjects

MARKER_STATE = 0   #: Marker state computation (weight = 0)
CONTROLLABLE = 1   #: State has only controllable edges (min of weights)
UNCONTROLLABLE = 2 #: State has uncontrollable edges (max of weights)

# {{{ def make_state_info_mapping(waut):
def make_state_info_mapping(waut):
    """
    Construct state information about each state for use in the next state
    weights computation.

    @param waut: Weighted automaton.
    @type  waut: L{WeightedAutomaton}

    @return: State information for all states in L{waut}.
    @rtype:  Depending on the kind of state, one of the following values is
             computed for it:
              - Marker state: C{(MARKER_STATE,)},
              - Non-marker state with only controllable outgoing edges:
                tuple (C{CONTROLLABLE}, [edge]), and
              - Non-marker state with uncontrollable edges:
                tuple (C{UNCONTROLLABLE}, [edge])
              where 'edge' is (evt, [(weight, dest_state)])
    """
    computation = {}

    for state in waut.get_states():
        if state.marked:
            computation[state] = (MARKER_STATE,)
            continue

        # Non-marked states
        edges = []  #: Edges collected so far
        controllable = True #: Collect controllable edges

        # Collect successor states from 'state' by event.
        evt_dests = {} #: event to list (weight, dest-state).
        controllable = True #: State has only edges with controllable events.
        for edge in state.get_outgoing():
            weight_dests = evt_dests.get(edge.label)
            if weight_dests is None:
                weight_dests = []
                evt_dests[edge.label] = weight_dests

                controllable = (controllable and edge.label.controllable)

            weight_dests.append((edge.weight, edge.succ))

        if controllable:
            # Keep all edges (all have controllable event label).
            edges = list(evt_dests.iteritems())
            assert len(edges) > 0 # Otherwise cannot compute min or max.
            computation[state] = (CONTROLLABLE, edges)
        else:
            # Only keep edges with uncontrollable event labels.
            edges = [(evt, dests) for evt, dests in evt_dests.iteritems()
                                       if not evt.controllable]
            assert len(edges) > 0 # Otherwise cannot compute min or max.
            computation[state] = (UNCONTROLLABLE, edges)

    return computation

# }}}

# {{{ def compute_state_weights(aut, marker_valfn):
def compute_state_weights(aut, marker_valfn):
    """
    Compute weighted controllable language.

    Attach a weight to each state, and iteratively update these weights until a
    stable situation is found.
     - Initial setup:
        - Marker states have weight 'marker_valfn(state)'.
        - Other states have weight $\infty$.
     - Update rules:
        - Marker states are never updated.
        - Non-marker states *with* outgoing uncontrollable events get weight
          max(edge_weight(i) + dest_state(i) for all uncontrollable edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
        - Non-marker states *without* outgoing uncontrollable events get
          weight min(edge_weight(i) + dest_state(i) for all (controllable)
          edges i with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
    Update until all weights are stable.

    If initial state has finite weight, make a new weighted automaton with
    reachable states such that the costs do not increase.

    @param aut: Weighted automaton.
    @type  aut: L{WeightedAutomaton}

    @param marker_valfn: Weight function of marker states to their weight.
    @type  marker_valfn: C{func} of L{WeightedState} to C{int}

    @return: Dictionary of states to their weights.
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

    @todo: Make this a class.
    """
    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    weights = {} #: Map of states to weights.
    for state, comp in computation.iteritems():
        if comp[0] == MARKER_STATE:
            weights[state] = marker_valfn(state)
            assert weights[state] is not None
        else:
            weights[state] = maxplus.INFINITE

    #count = 0

    # 3. Iteratively update the weights with new ones until stable.
    while True:
        if DBG_TIME_OPTIMAL_SUP:
            dump_map(weights)
        #print_weights(weights, "iterating (%d)" % count)
        #count = count + 1
        # Compute new weights
        new_weights = {}
        changed = False
        for state, comp in computation.iteritems():
            if comp[0] == MARKER_STATE:
                if DBG_TIME_OPTIMAL_SUP:
                    print "State %d (marker)" % state.number
                # Marker states do not change
                new_weights[state] = weights[state]

            elif comp[0] == CONTROLLABLE:
                if DBG_TIME_OPTIMAL_SUP:
                    print ("State %d (controllable)" % state.number),
                best = maxplus.INFINITE #: Minimal found solution so far
                #print "\ncontrollable from state", state
                #for evt, weightdests in comp[1]:
                #    print "\t", evt, weightdests
                for _evt, weightdests in comp[1]:
                    biggest = 0
                    for edge_weight, dest in weightdests:
                        if weights[dest] is maxplus.INFINITE:
                            biggest = maxplus.INFINITE
                            break
                        else:
                            val = edge_weight + weights[dest]
                            if val > biggest:
                                biggest = val
                    if biggest is maxplus.INFINITE:
                        continue
                    elif best is maxplus.INFINITE or best > biggest:
                        best = biggest
                        #print "best is set to", best, "for evt", evt

                if DBG_TIME_OPTIMAL_SUP:
                    print "->", best

                new_weights[state] = best
                if not changed and \
                        not maxplus.equal(weights[state], new_weights[state]):
                    changed = True

            elif comp[0] == UNCONTROLLABLE:
                if DBG_TIME_OPTIMAL_SUP:
                    print ("State %d (uncontrollable)" % state.number),
                best = 0 #: best maximal value so far
                for evt, weightdests in comp[1]:
                    for edge_weight, dest in weightdests:
                        if weights[dest] is maxplus.INFINITE:
                            best = maxplus.INFINITE
                            break
                        else:
                            val = edge_weight + weights[dest]
                            if val > best:
                                best = val
                    if best is maxplus.INFINITE:
                        break

                if DBG_TIME_OPTIMAL_SUP:
                    print "->", best

                new_weights[state] = best
                if not changed and \
                        not maxplus.equal(weights[state], new_weights[state]):
                    changed = True

            else:
                raise ValueError("Unknown computation type")

        weights = new_weights
        if not changed:
            break

        # Weights are different, let's try again.

    return weights

# }}}

# {{{ def pred_states(state):
def pred_states(state):
    """
    Compute the set of predecessor states of state L{state}.

    @return: Set of predecessor states.
    @rtype:  C{set} of L{State}
    """
    predset = set(edge.pred for edge in state.get_incoming())
    return predset

# }}}
# {{{ def is_neginf_matrix(mat):
def is_neginf_matrix(mat):
    """
    Is L{mat} a matrix containing all negative infinite values?

    @param mat: Matrix to examine.
    @type  mat: L{maxplus.Vector}

    @return: All values are -infinite.
    @rtype:  C{bool}
    """
    for row in mat.data:
        for val in row:
            if val is not maxplus.EPSILON:
                return False

    return True

# }}}
# {{{ def dump_map(weights):
def dump_map(weights):
    """
    Dump the state map in the iterative weight computation.

    @param weights: The map to output, maps states to column matrices.
    @type  weights: C{dict} of L{State} to L{maxplus.Matrix}
    """
    print
    print "State weight:"
    for state, wght in weights.iteritems():
        print "state %d -> %s" % (state.number, wght)
    print

# }}}
# {{{ def compute_state_vector_weights(aut, marker_valfn, ...
def compute_state_vector_weights(aut, marker_valfn, nonmarker_valfn, num_res,
                                 eventdata,L):
    """
    Compute weighted controllable language.

    Attach a weight to each state, and iteratively update these weights until a
    stable situation is found.
     - Initial setup:
        - Marker states have weight 'marker_valfn(state)'.
        - Other states have weight 'nonmarker_valfn(state)'
     - Update rules:
        - Marker states are never updated.
        - Non-marker states *with* outgoing uncontrollable events get weight
          max(edge_weight(i) + dest_state(i) for all uncontrollable edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
        - Non-marker states *without* outgoing uncontrollable events get weight
          min(edge_weight(i) + dest_state(i) for all (controllable) edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
    Update until all weights are stable.

    If initial state has finite weight, make a new weighted automaton with
    reachable states such that the costs do not increase.

    @param aut: Weighted automaton.
    @type  aut: L{WeightedAutomaton}

    @param marker_valfn: Weight function of marker states to their weight.
    @type  marker_valfn: C{func} of L{WeightedState} to C{int}

    @return: Dictionary of states to their weights.
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

    @todo: THIS CODE LOOKS LIKE A DUPLICATE
    """
    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    weights = {} #: Map of states to a set of column vectors.
    need_to_update = set()
    for state, comp in computation.iteritems():
        if comp[0] == MARKER_STATE:
            weights[state] = marker_valfn(state)
            assert weights[state] is not None
            need_to_update.update(pred_states(state))
        else:
            weights[state] = nonmarker_valfn(state)
            assert weights[state] is not None
            need_to_update.update(pred_states(state))

    count = 0

    # 3. Iteratively update the weights with new ones until stable.
    while True:
        if DBG_TIME_OPTIMAL_SUP:
            dump_map(weights)

        count = count + 1
        common.print_line("#states=%d, count=%d (%d states need to be updated)"
                                % (len(weights), count, len(need_to_update)))
        # Compute new weights
        new_weights = {}
        new_need_to_update = set()
        for state, comp in computation.iteritems():
            if state not in need_to_update:
                new_weights[state] = weights[state]
                continue

            if comp[0] == MARKER_STATE:
                # Marker states do not change
                new_weights[state] = weights[state]
                #new_weights[state] = marker_valfn(state)

            elif comp[0] == CONTROLLABLE:
                best = None # None means 'not assigned'
                evt_result = {} #: Mapping of event -> weight
                for evt, weightdests in comp[1]:

                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for _edge_weight, dest in weightdests:
                        # Skip -inf destinations.
                        if is_neginf_matrix(weights[dest]):
                            continue

                        biggest = maxplus.oplus_mat_mat(biggest, weights[dest])
                        assert biggest is not maxplus.EPSILON

                    # Skip events that always lead to states with -inf weight.
                    if is_neginf_matrix(biggest):
                        continue

                    evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        biggest)
                    #common.print_line("result0[%d][%d], evt_result[evt].data[0], evt_result[evt].data[1])"


                    #zeroes = maxplus.make_rowmat(0, num_res)
                    #result = maxplus.otimes_mat_mat(zeroes, evt_result[evt])
                    ##if best is None or \
                    #        maxplus.biggerthan(best[1], result.get_scalar()):
                    #    best = (evt, result.get_scalar())
                    #elif maxplus.equal(best[1], result.get_scalar()) \
                    #                            and evt.name < best[0].name:
                    #    best = (evt, result.get_scalar())

                    #result = maxplus.otimes_mat_mat(zeroes, evt_result[evt])
                    beta = 0

                    sum_val = 0;
                    max_val = evt_result[evt].data[0][0];
                    for rnum in range(evt_result[evt].num_row):
                       for cnum in range(evt_result[evt].num_col):
                           sum_val = sum_val + evt_result[evt].data[rnum][cnum]
                           if max_val < evt_result[evt].data[rnum][cnum]:
                                max_val = evt_result[evt].data[rnum][cnum]
                    beta = max_val + (sum_val - max_val)/L

                    if best is None or \
                    maxplus.biggerthan(best[1], beta):
                        best = (evt, beta)
                    elif maxplus.equal(best[1], beta) \
                                                and evt.name < best[0].name:
                        best = (evt, beta)


                if best is None:
                    # Everything leads to -infinite, apparently.
                    new_weights[state] = weights[state]

                else:
                    # Compute new weight
                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for evt, weightdests in comp[1]:
                        if evt is best[0]:
                            # XXX Does this make sense?
                            biggest = maxplus.oplus_mat_mat(biggest,
                                                            evt_result[evt])
                            break

                    new_weights[state] = biggest

                # Did the weight change?
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            elif comp[0] == UNCONTROLLABLE:
                # Compute new weight
                best = maxplus.make_colmat(maxplus.EPSILON, num_res)
                found_neg_inf = False #: Found an uncontrollable edge to -inf ?
                for evt, weightdests in comp[1]:
                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for _edge_weight, dest in weightdests:
                        if is_neginf_matrix(weights[dest]):
                            best = maxplus.make_colmat(maxplus.EPSILON,
                                                       num_res)
                            found_neg_inf = True
                            break

                        biggest = maxplus.oplus_mat_mat(biggest, weights[dest])

                    if found_neg_inf:
                        break

                    result = maxplus.otimes_mat_mat(eventdata[evt].matHat,
                                                    biggest)
                    best = maxplus.oplus_mat_mat(best, result)

                new_weights[state] = best
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            else:
                raise ValueError("Unknown computation type")

        weights = new_weights

        if len(new_need_to_update) == 0:
            break

        need_to_update = new_need_to_update
        # Weights are different, let's try again.

    return weights


def compute_state_vector_weights_correctly(aut, marker_valfn, nonmarker_valfn, num_res,
                                 eventdata,L, verbose = True):
    """
    Compute weighted controllable language.

    Attach a weight to each state, and iteratively update these weights until a
    stable situation is found.
     - Initial setup:
        - Marker states have weight 'marker_valfn(state)'.
        - Other states have weight 'nonmarker_valfn(state)'
     - Update rules:
        - Marker states are never updated.
        - Non-marker states *with* outgoing uncontrollable events get weight
          max(edge_weight(i) + dest_state(i) for all uncontrollable edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
        - Non-marker states *without* outgoing uncontrollable events get weight
          min(edge_weight(i) + dest_state(i) for all (controllable) edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
    Update until all weights are stable.

    If initial state has finite weight, make a new weighted automaton with
    reachable states such that the costs do not increase.

    @param aut: Weighted automaton.
    @type  aut: L{WeightedAutomaton}

    @param marker_valfn: Weight function of marker states to their weight.
    @type  marker_valfn: C{func} of L{WeightedState} to C{int}

    @return: Dictionary of states to their weights.
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

    @todo: THIS CODE LOOKS LIKE A DUPLICATE
    """
    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    weights = {} #: Map of states to a set of column vectors.
    need_to_update = set()
    for state, comp in computation.iteritems():
        if comp[0] == MARKER_STATE:
            weights[state] = marker_valfn(state)
        else:
            weights[state] = nonmarker_valfn(state)
        assert weights[state] is not None
        need_to_update.update(pred_states(state))

    count = 0

    # 3. Iteratively update the weights with new ones until stable.
    while True:
        if DBG_TIME_OPTIMAL_SUP:
            dump_map(weights)

        count = count + 1
        if verbose:
            common.print_line("#states=%d, count=%d (%d states need to be updated)"
                                    % (len(weights), count, len(need_to_update)))
        # Compute new weights
        new_weights = {}
        new_need_to_update = set()
        for state, comp in computation.iteritems():
            if state not in need_to_update:
                new_weights[state] = weights[state]
                continue

            if comp[0] == MARKER_STATE:
                # Marker states do not change
                new_weights[state] = weights[state]
                #new_weights[state] = marker_valfn(state)

            elif comp[0] == CONTROLLABLE:
                best = None # None means 'not assigned'
                evt_result = {} #: Mapping of event -> weight
                for evt, weightdests in comp[1]:

                    targetQ = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    _edge_weight = weightdests[0][0]
                    dest = weightdests[0][1]
                    # Skip -inf destinations.
                    if is_neginf_matrix(weights[dest]):
                        continue

                    targetQ = maxplus.oplus_mat_mat(targetQ, weights[dest])
                    assert targetQ is not maxplus.EPSILON

                    # Skip events that always lead to states with -inf weight.
                    if is_neginf_matrix(targetQ):
                        continue

                    evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        targetQ)
                    
                    norm = compute_norm(evt_result[evt], L)

                    if best is None or maxplus.biggerthan(best[1], norm):
                        best = (evt, norm)

                if best is None:
                    # Everything leads to -infinite, apparently.
                    # Or no outgoing events
                    new_weights[state] = weights[state]

                else:
                    for evt, weightdests in comp[1]:
                        if evt is best[0]:
                            if not is_neginf_matrix(weights[state]):
                                if best[1] < compute_norm(weights[state], L):
                                    new_weights[state] = evt_result[evt]
                                    break
                                else:
                                    new_weights[state] = weights[state]
                                    break
                            else:
                                new_weights[state] = evt_result[evt]
                                break

                # Did the weight change?
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            elif comp[0] == UNCONTROLLABLE:
                # Compute new weight
                worst = None
                evt_result = {} #: Mapping of event -> weight
                for evt, weightdests in comp[1]:
                    if not evt.controllable:
                        targetQ = maxplus.make_colmat(maxplus.EPSILON, num_res)
                        _edge_weight = weightdests[0][0]
                        dest = weightdests[0][1]
                        if is_neginf_matrix(weights[dest]):
                            worst = maxplus.make_colmat(maxplus.EPSILON,
                                                       num_res)
                            break
                        else:
                            targetQ = maxplus.oplus_mat_mat(targetQ, weights[dest])
                            evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        targetQ)
                        
                        norm = compute_norm(evt_result[evt], L)
                        if worst is None or maxplus.biggerthan(norm, worst[1]):
                            worst = (evt, norm)
                        
                new_weights[state] = worst
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            else:
                raise ValueError("Unknown computation type")

        weights = new_weights

        if len(new_need_to_update) == 0:
            break

        need_to_update = new_need_to_update
        # Weights are different, let's try again.

    return weights

def compute_norm(matrix, L):
    sum_val = 0;
    max_val = matrix.data[0][0];
    for rnum in range(matrix.num_row):
       for cnum in range(matrix.num_col):
           sum_val = sum_val + matrix.data[rnum][cnum]
           max_val = max(max_val, matrix.data[rnum][cnum])
    norm = max_val + (sum_val - max_val)/float(L)
    return norm

def compute_state_vector_weights_row_vectors(aut, marker_valfn, nonmarker_valfn, num_res,
                                 eventdata, row_vectors):
    """
    Compute weighted controllable language.

    Attach a weight to each state, and iteratively update these weights until a
    stable situation is found.
     - Initial setup:
        - Marker states have weight 'marker_valfn(state)'.
        - Other states have weight 'nonmarker_valfn(state)'
     - Update rules:
        - Marker states are never updated.
        - Non-marker states *with* outgoing uncontrollable events get weight
          max(edge_weight(i) + dest_state(i) for all uncontrollable edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
        - Non-marker states *without* outgoing uncontrollable events get weight
          min(edge_weight(i) + dest_state(i) for all (controllable) edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
    Update until all weights are stable.

    If initial state has finite weight, make a new weighted automaton with
    reachable states such that the costs do not increase.

    @param aut: Weighted automaton.
    @type  aut: L{WeightedAutomaton}

    @param marker_valfn: Weight function of marker states to their weight.
    @type  marker_valfn: C{func} of L{WeightedState} to C{int}

    @return: Dictionary of states to their weights.
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

    @todo: THIS CODE LOOKS LIKE A DUPLICATE
    """
    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    weights = {} #: Map of states to a set of column vectors.
    need_to_update = set()
    for state, comp in computation.iteritems():
        if comp[0] == MARKER_STATE:
            weights[state] = marker_valfn(state)
            assert weights[state] is not None
            need_to_update.update(pred_states(state))
        else:
            weights[state] = nonmarker_valfn(state)
            assert weights[state] is not None
            need_to_update.update(pred_states(state))

    count = 0

    # 3. Iteratively update the weights with new ones until stable.
    while True:
        if DBG_TIME_OPTIMAL_SUP:
            dump_map(weights)

        count = count + 1
        common.print_line("#states=%d, count=%d (%d states need to be updated)"
                                % (len(weights), count, len(need_to_update)))
        # Compute new weights
        new_weights = {}
        new_need_to_update = set()
        for state, comp in computation.iteritems():
            if state not in need_to_update:
                new_weights[state] = weights[state]
                continue

            if comp[0] == MARKER_STATE:
                # Marker states do not change
                new_weights[state] = weights[state]
                #new_weights[state] = marker_valfn(state)

            elif comp[0] == CONTROLLABLE:
                best = None # None means 'not assigned'
                evt_result = {} #: Mapping of event -> weight
                for evt, weightdests in comp[1]:

                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for _edge_weight, dest in weightdests:
                        # Skip -inf destinations.
                        if is_neginf_matrix(weights[dest]):
                            continue

                        biggest = maxplus.oplus_mat_mat(biggest, weights[dest])
                        assert biggest is not maxplus.EPSILON

                    # Skip events that always lead to states with -inf weight.
                    if is_neginf_matrix(biggest):
                        continue

                    evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        biggest)

                    #zeroes = maxplus.make_rowmat(0, num_res)
                    rvec =  row_vectors[state]
                    result = maxplus.otimes_mat_mat(rvec, evt_result[evt])

                    if best is None or \
                            maxplus.biggerthan(best[1], result.get_scalar()):
                        best = (evt, result.get_scalar())
                    elif maxplus.equal(best[1], result.get_scalar()) \
                                                and evt.name < best[0].name:
                        best = (evt, result.get_scalar())


                if best is None:
                    # Everything leads to -infinite, apparently.
                    new_weights[state] = weights[state]

                else:
                    # Compute new weight
                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for evt, weightdests in comp[1]:
                        if evt is best[0]:
                            # XXX Does this make sense?
                            biggest = maxplus.oplus_mat_mat(biggest,
                                                            evt_result[evt])

                    new_weights[state] = biggest

                # Did the weight change?
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            elif comp[0] == UNCONTROLLABLE:
                # Compute new weight
                best = maxplus.make_colmat(maxplus.EPSILON, num_res)
                found_neg_inf = False #: Found an uncontrollable edge to -inf ?
                for evt, weightdests in comp[1]:
                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for _edge_weight, dest in weightdests:
                        if is_neginf_matrix(weights[dest]):
                            best = maxplus.make_colmat(maxplus.EPSILON,
                                                       num_res)
                            found_neg_inf = True
                            break

                        biggest = maxplus.oplus_mat_mat(biggest, weights[dest])

                    if found_neg_inf:
                        break

                    result = maxplus.otimes_mat_mat(eventdata[evt].matHat,
                                                    biggest)
                    best = maxplus.oplus_mat_mat(best, result)

                new_weights[state] = best
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            else:
                raise ValueError("Unknown computation type")

        weights = new_weights

        if len(new_need_to_update) == 0:
            break

        need_to_update = new_need_to_update
        # Weights are different, let's try again.

    for state, comp in computation.iteritems():
      M = weights[state]

    return weights


# }}}
# {{{ def print_weights(weights, text = None):
def print_weights(weights, text = None):
    if text is None:
        print
    else:
        print text
    for state, weight in weights.iteritems():
        print state, [w.dump() for w in weight]
    print

# }}}
# {{{ def minimal_weight_deterministic_controllable(waut):
def minimal_weight_deterministic_controllable(waut):
    """
    Compute deterministic minimal weight controller.

    @param waut: Weighted automaton (not minimally weighted).
    @type  waut: L{WeightedAutomaton}

    @return: C{None} if there is no deterministic minimal weight controller,
             else a new deterministic automaton.
    @rtype:  Either C{None} or a L{Automaton}
    """
    result = minimal_weight_controllable(waut)
    if result is None:
        return None
    aut, initial_weight = result
    return aut, initial_weight

# }}}
# {{{ def unfold_automaton(waut, max_weight):
def unfold_automaton(waut, max_weight):
    """
    Unfold a weighted automaton up to some max number.

    @param waut: Weighted automaton to unfold.
    @type  waut: L{WeightedAutomaton}

    @param max_weight: Max weight to unfold to.
    @type  max_weight: C{int} or C{float}

    @return: Unweighted unfolded automaton.
    @rtype:  L{Automaton}
    """
    unfolded, unfolded_map = unfold_automaton_map(waut, max_weight)
    unfolded_map.clear()
    return unfolded

def unfold_automaton_map(waut, max_weight):
    """
    Unfold a weighted automaton up to some max number.

    @param waut: Weighted automaton to unfold.
    @type  waut: L{WeightedAutomaton}

    @param max_weight: Max weight to unfold to.
    @type  max_weight: C{int} or C{float}

    @return: Unweighted unfolded automaton, mapping of states to their
             accumulated weight.
    @rtype:  L{Automaton}, C{dict} of L{State} to C{float}

    @todo Extend to checking that no cycle with summed weight 0
          exists to prevent infinite unfolding.
    """
    # print max_weight
    assert type(max_weight) in (int, float)

    unfold = data_structure.Automaton(waut.alphabet, waut.collection)
    weight_map = {} #: Mapping of states to their accumulated weight.

    st = waut.initial
    ust = unfold.add_new_state(st.marked)
    unfold.set_initial(ust)
    weight_map[ust] = 0
    notdone = [(st, ust)]

    common.print_line("Unfolding to weight = %d" % max_weight)
    count = 0
    while len(notdone) > 0:
        fold_state, unfold_state = notdone.pop()
        fold_weight = weight_map[unfold_state]
        for edge in fold_state.get_outgoing():
            new_weight = fold_weight + edge.weight
            if new_weight <= max_weight:
                ust = unfold.add_new_state(edge.succ.marked)
                count = count + 1
                if count >= 100000:
                    common.print_line("#states done: %d" % count)
                    count = 0
                # XXX Extend to checking that no cycle with summed weight 0
                # exists to prevent infinite unfolding.
                unfold.add_edge_data(unfold_state, ust, edge.label)
                weight_map[ust] = new_weight
                notdone.append((edge.succ, ust))

    return unfold, weight_map

# }}}

def unfold_automaton_heaps(waut, max_weight, eventdata, heap_len, verbose = True):
    """
    Unfold a weighted automaton up to some max number.

    @param waut: Weighted automaton to unfold.
    @type  waut: L{WeightedAutomaton}

    @param max_weight: Max weight to unfold to.
    @type  max_weight: C{int} or C{float}
    
    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @return: Unweighted unfolded automaton
    @rtype:  L{Automaton}

    @todo Extend to checking that no cycle with summed weight 0
          exists to prevent infinite unfolding.
    """
    # print max_weight
    assert type(max_weight) in (int, float)

    unfold = data_structure.Automaton(waut.alphabet, waut.collection)
    weight_map = {} #: Mapping of states to their accumulated weight.

    st = waut.initial
    ust = unfold.add_new_state(st.marked)
    unfold.set_initial(ust)
    weight_map[ust] = maxplus.make_rowmat(0,heap_len)
    notdone = [(st, ust)]

    if verbose:
        common.print_line("Unfolding to weight = %d" % max_weight)
    count = 0
    while len(notdone) > 0:
        fold_state, unfold_state = notdone.pop()
        fold_weight = weight_map[unfold_state]
        for edge in fold_state.get_outgoing():
            new_weight = maxplus.otimes_mat_mat(fold_weight,eventdata[edge.label].matHat)
            if max(max(new_weight.data)) <= max_weight:
                ust = unfold.add_new_state(edge.succ.marked)
                count = count + 1
                if count >= 100000:
                    common.print_line("#states done: %d" % count)
                    count = 0
                # XXX Extend to checking that no cycle with summed weight 0
                # exists to prevent infinite unfolding.
                unfold.add_edge_data(unfold_state, ust, edge.label)
                weight_map[ust] = new_weight
                notdone.append((edge.succ, ust))
    weight_map.clear()
    del weight_map
    return unfold

# {{{ def minimal_weight_controllable(aut):
def minimal_weight_controllable(aut):
    """
    Compute minimal weight controller.

    @param aut: Weighted automaton (not minimally weighted).
    @type  aut: L{WeightedAutomaton}

    @return: C{None} if there is no minimal weight controller, else
             a new automaton.
    @rtype:  Either C{None} or a (L{Automaton}, initial-state weight) tuple.
    """
    weights = compute_state_weights(aut, marker_valfn = lambda s: 0)
    #print_weights(weights, "after compute_state_weights()")

    # 4. Make a new automaton if possible.
    if weights[aut.initial] is None:
        return None # No controllable language available.

    unfolded_aut = unfold_automaton(aut, weights[aut.initial])

    unw_plant = conversion.remove_weights(aut)

    sup_aut = supervisor.make_supervisor([unw_plant], [unfolded_aut])
    if sup_aut is None:
        return None
    return (sup_aut, weights[aut.initial])

# }}}
# {{{ def make_weighted_copy(uaut, state_map, w_orig):
def make_weighted_copy(uaut, state_map, w_orig):
    """
    Make a weighted copy of unweighted automaton L{uaut}.

    @param uaut: Unweighted automaton to copy.
    @type  uaut: L{Automaton}

    @param state_map: Map from L{uaut} states to state numbers in L{w_orig}.
    @type  state_map: C{dict} of L{State} to C{int}

    @param w_orig: Weighted automaton to copy edge weights from.
    @type  w_orig: L{WeightedAutomaton}

    @return: Weighted version of L{uaut}.
    @rtype:  L{WeightedAutomaton}
    """
    # Paranoia check: values of state_map should be unique
    assert len(set(state_map.values())) == len(state_map)

    # Construct weighted automaton
    waut = weighted_structure.WeightedAutomaton(uaut.alphabet, uaut.collection)
    waut.set_kind(uaut.aut_kind)

    # Copy states
    for ust in uaut.get_states():
        waut.add_new_state(ust.marked, num=state_map[ust])
    waut.set_initial(waut.get_state(state_map[uaut.initial]))

    # Copy edges
    for ust in uaut.get_states():
        w_src = waut.get_state(state_map[ust])
        for edge in ust.get_outgoing():
            w_dest = waut.get_state(state_map[edge.succ])
            # Find weight belong to the edge
            edge_weights = find_edge_weights(
                                        w_orig.get_state(state_map[edge.succ]),
                                        w_orig.get_state(state_map[ust]),
                                        edge.label)
            assert len(edge_weights) == 1
            waut.add_edge_data(w_src, w_dest, edge.label, edge_weights[0])

    return waut

# }}}
# {{{ def find_edge_weights(src, dest, evt):
def find_edge_weights(src, dest, evt):
    """
    Find the weight of all edges from L{src} state to L{dest} state labeled
    with L{evt}.

    @param src: Source state.
    @type  src: L{WeightedState}

    @param dest: Destination state.
    @type  dest: L{WeightedState}

    @param evt: Event label.
    @type  evt: L{Event}

    @return: Weights of the selected edges.
    @rtype:  C{list} of C{float}
    """
    return [edge.weight for edge in src.get_outgoing(evt) if edge.succ is dest]


# }}}
# {{{ def get_maxweight_strings(aut, aut_weights):
def get_maxweight_strings(aut, aut_weights):
    """
    From weighted automaton with given state weights, find all strings with
    maximal weight. Put these in an unweighted automaton.

    @param aut: Weighted automaton used for searching strings with max weight.
    @type  aut: L{WeightedAutomaton}

    @param aut_weights: Weights of each state in L{aut}.
    @type  aut_weights: C{dict} of L{WeightedState} to C{int}

    @return: Unweighted automaton containing the strings with maximal weight.
    @rtype:  L{Automaton}

    @todo: Deal with the weighted/non-weighted problem in a different way.
           Current approach is too broken.
    """
    max_states = [] #: List of states with max weight
    best = None
    for state, weight in aut_weights.iteritems():
        if best is None or best < weight:
            max_states = [state]
            best = weight
        elif best == weight:
            max_states.append(state)

    #print "max_states=", [s.number for s in max_states]
    #print "aut_weights=", [(s.number, w) for s,w in aut_weights.iteritems()]

    # Crawl forward from 'max_states' to find the path with exactly the weight
    max_aut = data_structure.Automaton(aut.alphabet, aut.collection)
    notdone_list = max_states
    while len(notdone_list) > 0:
        state = notdone_list.pop()
        #print "Doing state %d %r" % (state.number, state)
        max_state = get_state(max_aut, state)
        max_state_weight = aut_weights[state]
        for edge in state.get_outgoing():
            if aut_weights[edge.succ] + edge.weight == max_state_weight:
                # At critical path
                if not max_aut.has_state(edge.succ.number):
                    notdone_list.append(edge.succ)
                    max_succ = max_aut.add_new_state(edge.succ.marked,
                                                     num=edge.succ.number)
                else:
                    max_succ = max_aut.get_state(edge.succ.number)
                    # max_pred is the equivalent state already

                max_aut.add_edge_data(max_state, max_succ, edge.label)

    initial = max_aut.get_state(aut.initial.number)
    max_aut.set_initial(initial)

    return max_aut


# }}}
# {{{ def get_weighted_state(aut, old_state):
def get_weighted_state(aut, old_state):
    """
    Check whether an equivalent state as L{old_state} is in the automaton.
    If so, return it. If not, create one and return the created new state.

    @param aut: Automaton.
    @type  aut: L{WeightedAutomaton}

    @param old_state: State in another automaton.
    @type  old_state: L{WeightedState}

    @return: Equivalent state in the L{aut} automaton.
    @rtype:  L{WeightedState}

    @todo: This should be part of an Algorithm instance.
    """
    if aut.has_state(old_state.number):
        return aut.get_state(old_state.number)
    return aut.add_new_state(old_state.marked, num=old_state.number)

# }}}
# {{{ def get_state(aut, old_state):
def get_state(aut, old_state):
    """
    Check whether an equivalent state as L{old_state} is in the automaton.
    If so, return it. If not, create one and return the created new state.

    @param aut: Automaton.
    @type  aut: L{Automaton}

    @param old_state: State in another automaton.
    @type  old_state: L{State}

    @return: Equivalent state in the L{aut} automaton.
    @rtype:  L{State}

    @todo: This should be part of an Algorithm instance.
    """
    if aut.has_state(old_state.number):
        return aut.get_state(old_state.number)
    return aut.add_new_state(old_state.marked, num=old_state.number)

# }}}
# {{{ def compute_weighted_supremal(plant_aut, spec_aut):
def compute_weighted_supremal(plant_aut, spec_aut, verbose = True):
    """
    Compute (non-minimal) weighted supremal controllable sub-language.

    @param plant_aut: Weighted plant model.
    @type  plant_aut: L{WeightedAutomaton}

    @param spec_aut: Unweighted specification model.
    @type  spec_aut: L{Automaton}

    @return: Resulting weighted supremal controllable sub-language
             or C{None} if it does not exist.
    @rtype:  L{WeightedAutomaton} or C{None}

    @todo: Eliminate me.
    """
    assert plant_aut is not None
    assert spec_aut is not None

    unw_plant = conversion.remove_weights(plant_aut)

    sup_aut = supervisor.make_supervisor([unw_plant], [spec_aut], verbose)
    if sup_aut is None:
        return None

    weighted_sup = conversion.add_weights(sup_aut)
    return weighted_product.n_ary_weighted_product([plant_aut, weighted_sup],
                                                   algorithm.SUM_EDGE_WEIGHTS)

# }}}

def compute_unweighted_supremal(plant_aut, spec_aut):
    """
    Compute (non-minimal) weighted supremal controllable sub-language.

    @param plant_aut: Uneeighted plant model.
    @type  plant_aut: L{UnweightedAutomaton}

    @param spec_aut: Unweighted specification model.
    @type  spec_aut: L{Automaton}

    @return: Resulting Unweighted supremal controllable sub-language
             or C{None} if it does not exist.
    @rtype:  L{UnweightedAutomaton} or C{None}

    @todo: Eliminate me.
    """
    assert plant_aut is not None
    assert spec_aut is not None

    unw_plant = conversion.remove_weights(plant_aut)

    sup_aut = supervisor.make_supervisor([unw_plant], [spec_aut])
    if sup_aut is None:
        return None

    #weighted_sup = conversion.add_weights(sup_aut)
    return product.n_ary_unweighted_product(sup_aut,
                                                   False,False,True)

# }}}



# {{{ Greedy time optimal
def compute_greedy_time_optimal_supervisor(comp_list, req_list, eventdata,
                                           heap_len, row_vectors, operator,L):
    """
    Computate time-optimal supervisor in a greedy way (ie locally optimal).

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata to compute supervisor for.
    @type  req_list: C{list} of L{Automaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param heap_len: Number of resources.
    @type  heap_len: C{int}

    @return: Computed supervisor and a weight-map if they exist.
    @rtype:  C{None} or
             (L{WeightedAutomaton}, C{dict} of L{State} to L{maxplus.Matrix})
    """
    # Compute synchronous products.
    plant = weighted_product.n_ary_weighted_product(comp_list,
                                                algorithm.EQUAL_WEIGHT_EDGES)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed plant')
    requirement = product.n_ary_unweighted_product(req_list)
    assert requirement is not None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed requirements')

    for comp in comp_list:
        comp.clear()
    del comp_list

    wsup = compute_weighted_supremal(plant, requirement)
    if wsup is None:
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed wsup')

    requirement.clear()
    del requirement

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    if (operator != 0):
                       weight_map = compute_state_vector_weights_row_vectors(wsup, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata, row_vectors)
    else:
                       weight_map = compute_state_vector_weights(wsup, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,L)
    return wsup, weight_map

# }}} Greedy time optimal

def compute_greedy_time_optimal_supervisor_correctly(comp_list, req_list, eventdata,
                                           heap_len, L):
    """
    Computate time-optimal supervisor in a greedy way (ie locally optimal).

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata to compute supervisor for.
    @type  req_list: C{list} of L{Automaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param heap_len: Number of resources.
    @type  heap_len: C{int}

    @return: Computed supervisor and a weight-map if they exist.
    @rtype:  C{None} or
             (L{WeightedAutomaton}, C{dict} of L{State} to L{maxplus.Matrix})
    """
    # Compute synchronous products.
    plant = weighted_product.n_ary_weighted_product(comp_list,
                                                algorithm.EQUAL_WEIGHT_EDGES)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed plant')
    requirement = product.n_ary_unweighted_product(req_list)
    assert requirement is not None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed requirements')

    for comp in comp_list:
        comp.clear()
    del comp_list

    wsup = compute_weighted_supremal(plant, requirement)
    if wsup is None:
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed wsup')

    requirement.clear()
    del requirement

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = compute_state_vector_weights_correctly(wsup, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata,L)
    return wsup, weight_map

# {{{ Time optimal supervisor
def compute_time_optimal_supervisor(comp_list, req_list, evt_pairs):
    """
    Computate time-optimal supervisor (globally optimal).

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata to compute supervisor for.
    @type  req_list: C{list} of L{Automaton}

    @param evt_pairs: Coupled events.
    @type  evt_pairs: C{set} of C{tuple} of L{Event}

    @return: Computed supervisor if there exists one, else C{None}.
    @rtype:  Either L{Automaton} or C{None}
    """
    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        return None

    eventdata, heap_len = result



    # Compute synchronous products.
    plant = weighted_product.n_ary_weighted_product(comp_list,
                                                 algorithm.EQUAL_WEIGHT_EDGES)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed plant')
    requirement = product.n_ary_unweighted_product(req_list)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed requirements')

    for comp in comp_list:
        comp.clear()
    del comp_list

    wsup = compute_weighted_supremal(plant, requirement)
    if wsup is None:
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed wsup')

    requirement.clear()
    del requirement

    marker_valfn = lambda state: 0
    weight_map = compute_state_weights(wsup, marker_valfn)
    initial_weight = weight_map[wsup.initial]
    assert initial_weight is not None # Temp paranoia check.
    if initial_weight is maxplus.INFINITE: # Infinite weight initial state.
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed state weights')

    # wsup2 = taskresource.reduce_sup(wsup, weight_map)
    del weight_map
    # wsup.clear()
    # del wsup

    # XXX Optimization: do heap computation while unfolding the automaton.
    unfolded = unfold_automaton_heaps(wsup, initial_weight, eventdata, heap_len)
    # unfolded = unfold_automaton_heaps(wsup2, initial_weight, eventdata, heap_len)
    # wsup2.clear()
    # del wsup2
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed unfolding (%d states)'
                                                % unfolded.get_num_states())

    wsup3 = compute_weighted_supremal(plant, unfolded)
    plant.clear()
    unfolded.clear()
    del plant
    del unfolded

    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed supremal')

    unfolded2 = unfold_automaton_heaps(wsup3, initial_weight, eventdata, heap_len)
    wsup3.clear()
    del wsup3
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed unfolding2 (%d states)'
                                                % unfolded2.get_num_states())

    heap_info = taskresource.compute_heap_states(unfolded2, eventdata, heap_len)
    del eventdata

    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed heap_info')

    # Convert unfolded2 to weighted unfolded automaton with 0 at the edges.
    wunfolded2 = conversion.add_weights(unfolded2, edge_weight = 0)
    wunfolded2_info = {}
    for state, wght in heap_info.iteritems():
        wunfolded2_info[wunfolded2.get_state(state.number)] = wght
    unfolded2.clear()
    del unfolded2
    # Compute weight of initial state.
    m_valfn = lambda s: taskresource.compute_heap_height(wunfolded2_info[s])
    weightmap = compute_state_weights(wunfolded2, m_valfn)
    m_valfn = None
    wunfolded2_info = None

    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed heap weights')

    pruned = taskresource.prune_tree_automaton(wunfolded2, weightmap)
    initial_weight = weightmap[wunfolded2.initial]
    del weightmap
    wunfolded2.clear()
    del wunfolded2

    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed pruning')

    return pruned, initial_weight
# }}}

# {{{ def compute_optimistic_hop_estimate(aut, eventdata, num_res):
def compute_optimistic_hop_estimate(aut, eventdata, num_res):
    """
    Compute an estimated distance from each state to the marker state which is
    optimistic (ie not bigger than the real optimal distance) for the heaps of
    pieces calculation.

    @param aut: Automaton (either weighted or unweighted).
    @type  aut: L{BaseAutomaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @return: Mapping of states of the automaton to optimistic hop distance.
    @rtype:  C{dict} of L{BaseState} to L{maxplus.Vector}

    @note: The estimate seems to return a lot of 0 values for the resources,
           thus giving little guidance to the A* search.
    """
    common.print_line('Computing optimistic estimates for A*')

    mgr = algorithm.IterativeNodeValueComputation('backward')

    empty = maxplus.make_vector(0, num_res)
    for state in aut.get_states():
        if state.marked:
            mgr.update_value(state, empty)
            mgr.propagate_change(state)

    while mgr.next_cycle():
        for state in mgr.get_nodes():
            if state.marked:
                # Keep marked states at an empty heap.
                empty = maxplus.make_vector(0, num_res)
                mgr.update_value(state, empty)
                continue

            smallest = None
            for edge in state.get_outgoing():
                succ_value = mgr.values.get(edge.succ, None)
                if succ_value is None:
                    continue

                piece = eventdata[edge.label].q_tilde
                succ_val = maxplus.otimes_vec_vec(succ_value, piece)
                if smallest is None:
                    smallest = succ_val
                else:
                    vals = [maxplus.minimum(mv, sv)
                            for mv, sv in zip(smallest.data, succ_val.data)]
                    smallest = maxplus.Vector(vals)

            assert smallest is not None
            mgr.update_value(state, smallest)

    return mgr.values

# }}}
# {{{ def compute_optimistic_hop_estimate2(aut, eventdata, num_res):
def compute_optimistic_hop_estimate2(aut, eventdata, num_res):
    """
    Compute an estimated distance from each state to the marker state which is
    optimistic (ie not bigger than the real optimal distance) for the heaps of
    pieces calculation.

    @param aut: Automaton (either weighted or unweighted).
    @type  aut: L{BaseAutomaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @return: Mapping of states of the automaton to optimistic hop distance.
    @rtype:  C{dict} of L{BaseState} to L{Vector}
    """
    common.print_line('Computing optimistic estimates for A* (second version)')

    mgr = algorithm.IterativeNodeValueComputation('backward')

    empty_set = set([maxplus.make_vector(0, num_res)])
    for state in aut.get_states():
        if state.marked:
            mgr.update_value(state, empty_set)
            mgr.propagate_change(state)

    while mgr.next_cycle():
        for state in mgr.get_nodes():
            if state.marked:
                # Keep marked states at an empty heap.
                mgr.update_value(state, empty_set)
                continue

            smallest = set() #: New value associated with the state.
            for edge in state.get_outgoing():
                succ_values = mgr.values.get(edge.succ, None)
                if succ_values is None:
                    # if succ_values is None, there is no estimate for it
                    # -> skip.
                    continue

                for sval in succ_values:
                    # Compute distance of 'state' to end-point.
                    sval = maxplus.vec_to_colmat(sval)
                    dist = maxplus.otimes_mat_mat(
                                        eventdata[edge.label].matHat, sval)
                    dist = maxplus.colmat_to_vec(dist)
                    smallest = taskresource.smallest_add_heap(smallest, dist)

            assert len(smallest) > 0
            mgr.update_value(state, smallest)

    return mgr.values

# }}}

def compute_unweight_time_optimal_supervisor(comp_list, req_list, evt_pairs):
    """
    Computate unweight time-optimal supervisor (globally optimal).

    @param comp_list: Noweighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata to compute supervisor for.
    @type  req_list: C{list} of L{Automaton}

    @param evt_pairs: Coupled events.
    @type  evt_pairs: C{set} of C{tuple} of L{Event}

    @return: Computed supervisor if there exists one, else C{None}.
    @rtype:  Either L{Automaton} or C{None}
    """
    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        return None

    eventdata, heap_len = result

    # Compute synchronous products.
    plant = product.n_ary_unweighted_product(comp_list,
                                                 False,False,True)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed plant')
    requirement = product.n_ary_unweighted_product(req_list)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed requirements')

    for comp in comp_list:
        comp.clear()
    del comp_list

    wsup = compute_unweighted_supremal(plant, requirement)
    if wsup is None:
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed wsup')

    requirement.clear()
    del requirement

    #marker_valfn = lambda state: 0
    #weight_map = compute_state_weights(wsup, marker_valfn)
    #initial_weight = weight_map[wsup.initial]
    #assert initial_weight is not None # Temp paranoia check.
    #if initial_weight is maxplus.INFINITE: # Infinite weight initial state.
    #    return None
    #if DBG_TIME_OPTIMAL_SUP:
    #    common.print_line('Computed state weights')

    #wsup2 = taskresource.reduce_sup(wsup, weight_map)
    #del weight_map
    #wsup.clear()
    #del wsup

    # XXX Optimization: do heap computation while unfolding the automaton.
    #unfolded = unfold_automaton(wsup2, initial_weight)
    #wsup2.clear()
    #del wsup2
    #if DBG_TIME_OPTIMAL_SUP:
    #    common.print_line('Computed unfolding (%d states)'
    #                                            % unfolded.get_num_states())

    #wsup3 = compute_unweight_time_optimal_supervisorn(plant, unfolded)
    #plant.clear()
    #unfolded.clear()
    #del plant
    #del unfolded

    #if DBG_TIME_OPTIMAL_SUP:
    #    common.print_line('Computed supremal')

    #unfolded2 = unfold_automaton(wsup3, initial_weight)
    #wsup3.clear()
    #del wsup3
    #if DBG_TIME_OPTIMAL_SUP:
    #    common.print_line('Computed unfolding2 (%d states)'
    #                                            % unfolded2.get_num_states())

    #heap_info = taskresource.compute_heap_states(unfolded2, eventdata, heap_len)
    #del eventdata

    #if DBG_TIME_OPTIMAL_SUP:
    #    common.print_line('Computed heap_info')

    # Convert unfolded2 to weighted unfolded automaton with 0 at the edges.
    #wunfolded2 = conversion.add_weights(unfolded2, edge_weight = 0)
    #wunfolded2_info = {}
    #for state, wght in heap_info.iteritems():
    #    wunfolded2_info[wunfolded2.get_state(state.number)] = wght
    #unfolded2.clear()
    #del unfolded2
    # Compute weight of initial state.
    #m_valfn = lambda s: taskresource.compute_heap_height(wunfolded2_info[s])
    #weightmap = compute_state_weights(wunfolded2, m_valfn)
    #m_valfn = None
    #wunfolded2_info = None

    #if DBG_TIME_OPTIMAL_SUP:
    #    common.print_line('Computed heap weights')

    #pruned = taskresource.prune_tree_automaton(wunfolded2, weightmap)
    #initial_weight = weightmap[wunfolded2.initial]
    #del weightmap
    #wunfolded2.clear()
    #del wunfolded2

    #if DBG_TIME_OPTIMAL_SUP:
     #   common.print_line('Computed pruning')

    #return pruned, initial_weight
    return wsup
# }}}

# {{{ def get_path_text(aut, path_seq):
def get_path_text(aut, path_seq):
    """
    Get the path in text form.

    @param aut: Automaton being traversed (for printing the state names).
    @type  aut: L{BaseAutomaton}

    @param path_seq: Path to return in text form.
    @type  path_seq: C{list} of (L{BaseState}, C{int}, L{Event} or C{None})

    @return: Text representation of the path.
    @rtype:  C{str}
    """
    aut.make_state_names_complete()
    text = []
    for node, cost, evt in path_seq:
        text.append("%s(cost %d)" % (aut.state_names[node.number], cost))
        if evt is not None:
            text.append(' --(%s)-> ' % evt.name)

    return ''.join(text)

# }}}
# {{{ def convert_cost(path_seq):
def convert_cost(path_seq):
    """
    Convert the cost part of the path.

    @param path_seq: Path to return in text form.
    @type  path_seq: C{list} of (L{BaseState}, max+ cost-vecot)

    @return: Path sequence with human-readable costs.
    @rtype:  C{list} of (L{BaseState}, C{int}, L{Event})
    """
    return [(node, taskresource.compute_heap_height(cost), evt)
            for node, cost, evt in path_seq]

# }}}
# {{{ class AStar(object):
class AStar(object):
    """
    Administration class for computing A*.

    @ivar paths: Paths that need further exploring.
    @type paths: C{dict} of total cost to C{list} of L{path.Path}

    @ivar smallest: Smallest total cost in L{paths} keys.
    @type smallest: Cost, or C{None} if smallest cost is not available or known.

    @invariant: If not C{None}, L{smallest} should not decrease, since optimal
                path is computed.
    """
    def __init__(self):
        self.paths = {}
        self.smallest = None

    def add_path(self, path_node, total):
        """
        Add a new path_node.

        @param path_node: Path to add.
        @type  path_node: L{path.Path}

        @param total: Total cost of the path (path_node.cost + estimate).
        @type  total: Cost
        """
        assert total is not None

        curlist = self.paths.get(total, None)
        if curlist is not None:
            curlist.append(path_node)
            return

        self.paths[total] = [path_node]
        assert self.smallest is None or self.smallest <= total

    def get_path(self):
        """
        Get a path to explore further.

        @return: Path to explore further if it exists.
        @rtype:  L{path.Path} or C{None}
        """
        if self.smallest is None:
            # self.smallest not yet initialized
            if len(self.paths) == 0:
                return None  # No entries available.

            for total in self.paths.iterkeys():
                if self.smallest is None or self.smallest > total:
                    self.smallest = total

        curlist = self.paths.get(self.smallest)
        if curlist is None:
            if len(self.paths) == 0:
                return None

            # self.smallest may be less than the smallest item in the dict.
            # XXX This is potentially expensive if you make large increments in
            # total costs.
            while curlist is None:
                self.smallest = self.smallest + 1
                curlist = self.paths.get(self.smallest)

        path_node = curlist.pop()
        if len(curlist) > 0:
            return path_node

        del self.paths[self.smallest]

        # self.smallest is now smaller than the smallest entry in self.paths
        # We do not increment self.smallest now, since the other code may
        # re-add the path node we are about to return with the same
        # (self.smallest) cost.
        # Instead, incrementing is done when detecting that
        # self.paths[self.smallest] does not exist (at the next time this
        # function is called).

        return path_node

# }}}
# {{{ def compute_optimal_hop_path(aut, eventdata, num_res):
def compute_optimal_hop_path(aut, eventdata, num_res):
    """
    Compute a path with optimal use of resources in L{aut} from initial state
    to a marker state using heaps of pieces.

    @param aut: Automaton.
    @type  aut: L{BaseAutomaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @return: Optimal hop path from a marker state back to the initial state
             if it exists.
    @rtype:  L{path.Path} or C{None}
    """
    estimates = compute_optimistic_hop_estimate2(aut, eventdata, num_res)

    def get_total(path_node):
        """
        Return the total cost of the path_node.
        """
        if path_node.cost is None: # Not traveled yet
            total = min([taskresource.compute_heap_height(dist)
                         for dist in estimates[path_node.node]])
        else:
            total = min([taskresource.compute_heap_height(
                                maxplus.otimes_vec_vec(path_node.cost, dist))
                         for dist in estimates[path_node.node]])

        return total

    print "Weight of the shortest path:", \
                min([taskresource.compute_heap_height(h)
                                          for h in estimates[aut.initial]])

    initial_heap = None
    initial_path = path.Path(aut.initial, initial_heap, None, None)

    common.print_line('Starting A* algortithm')

    astar = AStar()  # Does the A* algorithm administration.
    astar.add_path(initial_path, get_total(initial_path))

    count = 0 # Count number of explored states.
    while True:
        count = count + 1
        path_node = astar.get_path()
        if path_node is None or path_node.node.marked:
            break # Finished

        for edge in path_node.node.get_outgoing():
            if edge.succ not in estimates:
                # Successor node has no estimate. That happens when the node
                # is not co-reachable. Such nodes do not give a result anyway,
                # and can safely be skipped.
                continue

            nc = taskresource.stack_single_piece(path_node.cost, edge.label,
                                                 eventdata, num_res)
            np = path.Path(edge.succ, nc, path_node, edge.label)
            astar.add_path(np, get_total(np))

    common.print_line('A* algorithm finished, did %d explorations '
                      '(over %d states)' % (count, aut.get_num_states()))
    return path_node

# }}}
# {{{ def compute_shortest_path(comp_list, req_list, use_reqs):
def compute_shortest_path(comp_list, req_list, evt_pairs):
    """
    Compute shortest path to a marker state with A* algortihm.

    @param comp_list: Weighted automata containing the plant.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata containing the requirements,
                     may be empty.
    @type  req_list: (C{list} of L{Automaton})

    @param evt_pairs: Coupled events.
    @type  evt_pairs: C{set} of C{tuple} of L{Event}
    """
    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        return None

    eventdata, heap_len = result

    comp_list = [conversion.remove_weights(comp) for comp in comp_list]
    plant = product.n_ary_unweighted_product(comp_list + req_list, False, True)

    opt_path = compute_optimal_hop_path(plant, eventdata, heap_len)
    if opt_path is None:
        common.print_line("No path found.")
        return opt_path

    opt_path = path.get_path_list(opt_path)
    opt_path = convert_cost(opt_path)
    common.print_line("Path: %s" % get_path_text(plant, opt_path))
    return opt_path

# }}}
# {{{ def generate_task_resource_use(comp_list, req_list, plots, text_path):
def generate_task_resource_use(comp_list, req_list, plots, text_path):
    """
    Generate information about task/resource use.

    @param comp_list: Weighted automata containing the plant.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata containing the requirements,
                     may be empty.
    @type  req_list: (C{list} of L{Automaton})

    @param plots: (Optional) automata collection that should be plotted.
    @type  plots: C{None} or C{set} of L{BaseAutomaton}

    @param text_path: Sequence of events on the path (a sequence of event
                      names, comma or white-space seperated).
    @type  text_path: C{string}

    @return: Resource uses, collection of (resource, start, end, taskname).
    @rtype:  C{list} of C{tuple} (C{str}, C{float}, C{float}, C{str})

    @invariant: Automata provided in L{plots} should also be in L{comp_list}
                or L{req_list}.

    @note: The L{comp_list} and L{req_list} are only used to compute the shape
           of the pieces at the heap. Therefore, for type 1 requirements (where
           the requirements automata are not used in that calculation),
           L{req_list} should be left empty.
    """
    # For type1 requirements, req_list should be left empty.
    eventdata = taskresource.compute_greedy_eventdata(comp_list, req_list)
    heap_len = len(comp_list) + len(req_list)

    names = [] #: Name of each automaton, C{None} if not to plot.
    all_alphabets = set() #: Merge all alphabets, to convert the path to events.
    for aut in comp_list + req_list:
        all_alphabets.update(aut.alphabet)
        if plots is None or aut in plots:
            # This automaton should be plotted, add its name or create one.
            name = aut.name
            if not name:
                name = '_aut_%d' % len(names)
            names.append(name)
        else:
            # This automaton does not need plotting.
            names.append(None)

    res_uses = []
    heap = None  # Empty heap
    for evt in path.convert_string_to_event_sequence(text_path, all_alphabets):
        edata = eventdata[evt]
        used_resources = [num for num, val in enumerate(edata.used) if val]

        heap = taskresource.stack_single_piece(heap, evt, eventdata, heap_len)
        end = heap.get(used_resources[0]) # piece ends at this height.

        for res in used_resources:
            name = names[res]
            if name is None: # Do not plot this resource.
                continue

            res_uses.append((name, end - edata.duration, end, evt.name))

    return res_uses

# }}}


# {{{ Greedy time optimal
def LBE_compute_greedy_time_optimal_supervisor(comp_list, req_list, eventdata,
                                           heap_len):
    """
    Computate time-optimal supervisor in a greedy way (ie locally optimal).

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata to compute supervisor for.
    @type  req_list: C{list} of L{Automaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param heap_len: Number of resources.
    @type  heap_len: C{int}

    @return: Computed supervisor and a weight-map if they exist.
    @rtype:  C{None} or
             (L{WeightedAutomaton}, C{dict} of L{State} to L{maxplus.Matrix})
    """
    # Compute synchronous products.
    plant = weighted_product.n_ary_weighted_product(comp_list,
                                                algorithm.EQUAL_WEIGHT_EDGES)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed plant')
    requirement = product.n_ary_unweighted_product(req_list)
    assert requirement is not None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed requirements')

    for comp in comp_list:
        comp.clear()
    del comp_list

    wsup = compute_weighted_supremal(plant, requirement)
    if wsup is None:
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed wsup')

    requirement.clear()
    del requirement

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    weight_map = LBE_compute_state_vector_weights(wsup, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata)
    return wsup, weight_map

# }}} Greedy time optimal


def LBE_compute_state_vector_weights(aut, marker_valfn, nonmarker_valfn, num_res,
                                 eventdata):
    """
    Compute weighted controllable language.

    Attach a weight to each state, and iteratively update these weights until a
    stable situation is found.
     - Initial setup:
        - Marker states have weight 'marker_valfn(state)'.
        - Other states have weight 'nonmarker_valfn(state)'
     - Update rules:
        - Marker states are never updated.
        - Non-marker states *with* outgoing uncontrollable events get weight
          max(edge_weight(i) + dest_state(i) for all uncontrollable edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
        - Non-marker states *without* outgoing uncontrollable events get weight
          min(edge_weight(i) + dest_state(i) for all (controllable) edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
    Update until all weights are stable.

    If initial state has finite weight, make a new weighted automaton with
    reachable states such that the costs do not increase.

    @param aut: Weighted automaton.
    @type  aut: L{WeightedAutomaton}

    @param marker_valfn: Weight function of marker states to their weight.
    @type  marker_valfn: C{func} of L{WeightedState} to C{int}

    @return: Dictionary of states to their weights.
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

    @todo: THIS CODE LOOKS LIKE A DUPLICATE
    """
    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    weights = {} #: Map of states to a set of column vectors.
    need_to_update = set()
    for state, comp in computation.iteritems():
        if comp[0] == MARKER_STATE:
            weights[state] = marker_valfn(state)
            assert weights[state] is not None
            need_to_update.update(pred_states(state))
        else:
            weights[state] = nonmarker_valfn(state)
            assert weights[state] is not None
            need_to_update.update(pred_states(state))

    count = 0

    # 3. Iteratively update the weights with new ones until stable.
    while True:
        if DBG_TIME_OPTIMAL_SUP:
            dump_map(weights)

        count = count + 1
        common.print_line("#states=%d, count=%d (%d states need to be updated)"
                                % (len(weights), count, len(need_to_update)))
        # Compute new weights
        new_weights = {}
        new_need_to_update = set()
        for state, comp in computation.iteritems():
            if state not in need_to_update:
                new_weights[state] = weights[state]
                continue

            if comp[0] == MARKER_STATE:
                # Marker states do not change
                new_weights[state] = weights[state]
                #new_weights[state] = marker_valfn(state)

            elif comp[0] == CONTROLLABLE:
                best = None     # None means 'not assigned'
                evt_result = {} #: Mapping of event -> weight
                uncontrollable_flag = False
                uncontrollable_smallest = maxplus.make_colmat(maxplus.INFINITE, num_res)
                controllable_smallest   = maxplus.make_colmat(maxplus.INFINITE, num_res)
                update = False
                for evt, weightdests in comp[1]:
                    if evt.controllable is False :
                       uncontrollable_flag = True

                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for _edge_weight, dest in weightdests:
                        # Skip -inf destinations.
                        if is_neginf_matrix(weights[dest]):
                            continue

                        biggest = maxplus.oplus_mat_mat(biggest, weights[dest])
                        assert biggest is not maxplus.EPSILON

                    # Skip events that always lead to states with -inf weight.
                    if is_neginf_matrix(biggest):
                        continue

                    evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        biggest)
                    update = True
                    if evt.controllable is False:
                            uncontrollable_smallest = maxplus.smaller_mat_mat(evt_result[evt],uncontrollable_smallest)
                    else:
                            controllable_smallest   = maxplus.smaller_mat_mat(evt_result[evt],controllable_smallest)

                if update is False:
                          new_weights[state] = weights[state]
                elif uncontrollable_flag is True:
                          new_weights[state] = uncontrollable_smallest
                elif uncontrollable_flag is False:
                          new_weights[state] = controllable_smallest

                # Did the weight change?
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            elif comp[0] == UNCONTROLLABLE:
                # Compute new weight
                best = maxplus.make_colmat(maxplus.EPSILON, num_res)
                found_neg_inf = False #: Found an uncontrollable edge to -inf ?
                for evt, weightdests in comp[1]:
                    biggest = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    for _edge_weight, dest in weightdests:
                        if is_neginf_matrix(weights[dest]):
                            best = maxplus.make_colmat(maxplus.EPSILON,
                                                       num_res)
                            found_neg_inf = True
                            break

                        biggest = maxplus.oplus_mat_mat(biggest, weights[dest])

                    if found_neg_inf:
                        break

                    result = maxplus.otimes_mat_mat(eventdata[evt].matHat,
                                                    biggest)
                    best = maxplus.oplus_mat_mat(best, result)

                new_weights[state] = best
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            else:
                raise ValueError("Unknown computation type")

        weights = new_weights

        if len(new_need_to_update) == 0:
            break

        need_to_update = new_need_to_update
        # Weights are different, let's try again.

    return weights


def FK_row_vector(comp_list, req_list, eventdata,heap_len):
    """
    Computate time-optimal supervisor in a greedy way (ie locally optimal).

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param req_list: Unweighted automata to compute supervisor for.
    @type  req_list: C{list} of L{Automaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param heap_len: Number of resources.
    @type  heap_len: C{int}

    @return: Computed supervisor and a weight-map if they exist.
    @rtype:  C{None} or
             (L{WeightedAutomaton}, C{dict} of L{State} to L{maxplus.Matrix})
    """
    # Compute synchronous products.
    plant = weighted_product.n_ary_weighted_product(comp_list,
                                                algorithm.EQUAL_WEIGHT_EDGES)
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed plant')
    requirement = product.n_ary_unweighted_product(req_list)
    assert requirement is not None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed requirements')

    for comp in comp_list:
        comp.clear()
    del comp_list

    wsup = compute_weighted_supremal(plant, requirement)
    if wsup is None:
        return None
    if DBG_TIME_OPTIMAL_SUP:
        common.print_line('Computed wsup')

    requirement.clear()
    del requirement

    col_zero_mat = maxplus.make_colmat(0, heap_len)
    col_epsilon_mat = maxplus.make_colmat(maxplus.EPSILON, heap_len)

    marker_valfn = lambda state: col_zero_mat
    nonmarker_valfn = lambda state: col_epsilon_mat
    FK = FK_compute_state_row_vector(wsup, marker_valfn,
                                              nonmarker_valfn,
                                              heap_len, eventdata)
    return wsup, FK



def FK_compute_state_row_vector(aut, marker_valfn, nonmarker_valfn, num_res,
                                 eventdata):

    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    FK = {} #: Map of states to a set of row vectors.

    count = 0;
    for state, comp in computation.iteritems():
        if (count ==0):
            FK[state] = maxplus.make_rowmat(0, num_res)
            assert FK[state] is not None
            count = count + 1
        else:
            FK[state] = maxplus.make_rowmat(maxplus.EPSILON, num_res)
            assert FK[state] is not None

    new_FK = {};
    for state, comp in computation.iteritems():
          if (comp[0] != MARKER_STATE):
             for evt, weightdests in comp[1]:
                rst = maxplus.otimes_mat_mat(FK[state], eventdata[evt].matHat)
                for _edge_weight, dest in weightdests:
                    p1 =  maxplus.oplus_mat_mat(FK[dest],rst)
                    FK[dest] = p1

    for state, comp in computation.iteritems():
         t = FK[state].data[0]
         common.print_line("#states=%d   row_vector:[%d %d]"
                                % (state.number, t[0], t[1]))
    return FK












def compute_state_vector_weights_progressive2(aut, marker_valfn, nonmarker_valfn, num_res,
                                              eventdata,L, verbose = True, non_progressive_events = set()):
    """
    Compute weighted controllable language.

    Attach a weight to each state, and iteratively update these weights until a
    stable situation is found.
     - Initial setup:
        - Marker states have weight 'marker_valfn(state)'.
        - Other states have weight 'nonmarker_valfn(state)'
     - Update rules:
        - Marker states are never updated.
        - Non-marker states *with* outgoing uncontrollable events get weight
          max(edge_weight(i) + dest_state(i) for all uncontrollable edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
        - Non-marker states *without* outgoing uncontrollable events get weight
          min(edge_weight(i) + dest_state(i) for all (controllable) edges i
          with edge weight 'edge_weight(i)' to destination state
          'dest_state(i)'.
    Update until all weights are stable.

    If initial state has finite weight, make a new weighted automaton with
    reachable states such that the costs do not increase.

    @param aut: Weighted automaton.
    @type  aut: L{WeightedAutomaton}

    @param marker_valfn: Weight function of marker states to their weight.
    @type  marker_valfn: C{func} of L{WeightedState} to C{int}

    @return: Dictionary of states to their weights.
    @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

    @todo: THIS CODE LOOKS LIKE A DUPLICATE
    """
    # 1. Compute state information for each state.
    computation = make_state_info_mapping(aut)

    # 2. Initialize weights.
    weights = {} #: Map of states to a set of column vectors.
    need_to_update = set()
    for state, comp in computation.iteritems():
        if comp[0] == MARKER_STATE:
            weights[state] = marker_valfn(state)
        else:
            weights[state] = nonmarker_valfn(state)
        assert weights[state] is not None
        need_to_update.update(pred_states(state))

    count = 0

    # 3. Iteratively update the weights with new ones until stable.
    while True:
        while True:
            if DBG_TIME_OPTIMAL_SUP:
                dump_map(weights)
    
            count = count + 1
            if verbose:
                common.print_line("#states=%d, count=%d (%d states need to be updated)"
                                        % (len(weights), count, len(need_to_update)))
            # Compute new weights
            new_weights = {}
            new_need_to_update = set()
            for state, comp in computation.iteritems():
                if state not in need_to_update:
                    new_weights[state] = weights[state]
                    continue
    
                if comp[0] == MARKER_STATE:
                    # Marker states do not change
                    new_weights[state] = weights[state]
                    #new_weights[state] = marker_valfn(state)
    
                elif comp[0] == CONTROLLABLE:
                    best = None # None means 'not assigned'
                    evt_result = {} #: Mapping of event -> weight
                    for evt, weightdests in comp[1]:
                        if evt in non_progressive_events:
                          continue
                        targetQ = maxplus.make_colmat(maxplus.EPSILON, num_res)
                        _edge_weight = weightdests[0][0]
                        dest = weightdests[0][1]
                        # Skip -inf destinations.
                        if is_neginf_matrix(weights[dest]):
                            continue
    
                        targetQ = maxplus.oplus_mat_mat(targetQ, weights[dest])
                        assert targetQ is not maxplus.EPSILON
    
                        # Skip events that always lead to states with -inf weight.
                        if is_neginf_matrix(targetQ):
                            continue
    
                        evt_result[evt] = maxplus.otimes_mat_mat(
                                                            eventdata[evt].matHat,
                                                            targetQ)
                        
                        norm = compute_norm(evt_result[evt], L)
    
                        if best is None or maxplus.biggerthan(best[1], norm):
                            best = (evt, norm)
    
                    if best is None:
                        # Everything leads to -infinite, apparently.
                        # Or no outgoing events
                        new_weights[state] = weights[state]
    
                    else:
                        for evt, weightdests in comp[1]:
                            if evt is best[0]:
                                if not is_neginf_matrix(weights[state]):
                                    if best[1] < compute_norm(weights[state], L):
                                        new_weights[state] = evt_result[evt]
                                        break
                                    else:
                                        new_weights[state] = weights[state]
                                        break
                                else:
                                    new_weights[state] = evt_result[evt]
                                    break
    
                    # Did the weight change?
                    if weights[state] != new_weights[state]:
                        new_need_to_update.update(pred_states(state))
    
                elif comp[0] == UNCONTROLLABLE:
                    # Compute new weight
                    worst = None
                    evt_result = {} #: Mapping of event -> weight
                    for evt, weightdests in comp[1]:
                        if not evt.controllable:
                            targetQ = maxplus.make_colmat(maxplus.EPSILON, num_res)
                            _edge_weight = weightdests[0][0]
                            dest = weightdests[0][1]
                            if is_neginf_matrix(weights[dest]):
                                worst = maxplus.make_colmat(maxplus.EPSILON,
                                                           num_res)
                                break
                            else:
                                targetQ = maxplus.oplus_mat_mat(targetQ, weights[dest])
                                evt_result[evt] = maxplus.otimes_mat_mat(
                                                            eventdata[evt].matHat,
                                                            targetQ)
                            
                            norm = compute_norm(evt_result[evt], L)
                            if worst is None or maxplus.biggerthan(norm, worst[1]):
                                worst = (evt, norm)
                            
                    new_weights[state] = worst
                    if weights[state] != new_weights[state]:
                        new_need_to_update.update(pred_states(state))
    
                else:
                    raise ValueError("Unknown computation type")
    
            weights = new_weights
    
            if len(new_need_to_update) == 0:
                break
    
            need_to_update = new_need_to_update
            # Weights are different, let's try again.
        new_weights = {}
        new_need_to_update = set()
        for state, comp in computation.iteritems():
            if comp[0] == MARKER_STATE:
                # Marker states do not change
                new_weights[state] = weights[state]
                #new_weights[state] = marker_valfn(state)
            elif not is_neginf_matrix(weights[state]):
                new_weights[state] = weights[state]
            elif comp[0] == CONTROLLABLE:
                best = None # None means 'not assigned'
                evt_result = {} #: Mapping of event -> weight
                for evt, weightdests in comp[1]:
                    if evt not in non_progressive_events:
                      continue
                    targetQ = maxplus.make_colmat(maxplus.EPSILON, num_res)
                    _edge_weight = weightdests[0][0]
                    dest = weightdests[0][1]
                    # Skip -inf destinations.
                    if is_neginf_matrix(weights[dest]):
                        continue

                    targetQ = maxplus.oplus_mat_mat(targetQ, weights[dest])
                    assert targetQ is not maxplus.EPSILON

                    # Skip events that always lead to states with -inf weight.
                    if is_neginf_matrix(targetQ):
                        continue

                    evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        targetQ)
                    
                    norm = compute_norm(evt_result[evt], L)

                    if best is None or maxplus.biggerthan(best[1], norm):
                        best = (evt, norm)

                if best is None:
                    # Everything leads to -infinite, apparently.
                    # Or no outgoing events
                    new_weights[state] = weights[state]

                else:
                    for evt, weightdests in comp[1]:
                        if evt is best[0]:
                            if not is_neginf_matrix(weights[state]):
                                if best[1] < compute_norm(weights[state], L):
                                    new_weights[state] = evt_result[evt]
                                    break
                                else:
                                    new_weights[state] = weights[state]
                                    break
                            else:
                                new_weights[state] = evt_result[evt]
                                break

                # Did the weight change?
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            elif comp[0] == UNCONTROLLABLE:
                # Compute new weight
                worst = None
                evt_result = {} #: Mapping of event -> weight
                for evt, weightdests in comp[1]:
                    if not evt.controllable:
                        targetQ = maxplus.make_colmat(maxplus.EPSILON, num_res)
                        _edge_weight = weightdests[0][0]
                        dest = weightdests[0][1]
                        if is_neginf_matrix(weights[dest]):
                            worst = maxplus.make_colmat(maxplus.EPSILON,
                                                       num_res)
                            break
                        else:
                            targetQ = maxplus.oplus_mat_mat(targetQ, weights[dest])
                            evt_result[evt] = maxplus.otimes_mat_mat(
                                                        eventdata[evt].matHat,
                                                        targetQ)
                        
                        norm = compute_norm(evt_result[evt], L)
                        if worst is None or maxplus.biggerthan(norm, worst[1]):
                            worst = (evt, norm)
                        
                new_weights[state] = worst
                if weights[state] != new_weights[state]:
                    new_need_to_update.update(pred_states(state))

            else:
                raise ValueError("Unknown computation type")

        weights = new_weights

        if len(new_need_to_update) == 0:
            break

        need_to_update = new_need_to_update
        
        
    print "init weight: " + str(weights[aut.initial])
    return weights