import automata
from automata import taskresource, maxplus, data_structure, collection, weighted_structure, \
                            compute_weight, conversion, weighted_product, algorithm

def tau_abstracted_greedy_supervisor(comp_list, req_list, comp_mut_ex, evt_pairs):
    if not comp_mut_ex == "type1" or comp_mut_ex == "type2":
        raise exceptions.InputError("Please use 'type1' or 'type2' for automaton type")
    result = taskresource.compute_custom_eventdata_extended(comp_list, evt_pairs, comp_mut_ex)
    if result is None:
        return None
    eventdata, cliques = result
    while len(comp_list) > 1:
        comp_list, eventdata = do_tau_abstraction(comp_list, comp_list[0], eventdata, cliques, evt_pairs)
        if len(comp_list) == 2:
            comp_list, eventdata = do_tau_abstraction(comp_list, comp_list[1], eventdata, cliques, evt_pairs)
        new_plant = weighted_product.n_ary_weighted_product(comp_list[0:2],
                                                 algorithm.EQUAL_WEIGHT_EDGES)
        comp_list.pop(0)
        comp_list.pop(0)
        comp_list.insert(0,new_plant)
    return comp_list[0]

def do_tau_abstraction(aut_list, selected_aut, eventdata, cliques, evt_pairs):
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
    
    # Find critical states
    critical_states, semi_critical_states = find_critical_states(selected_aut, local_alphabet)
    
    for end_state in critical_states:
        for start_state in critical_states.union(semi_critical_states):
            if start_state is not end_state: # We're not trying to create loops
                path = []
                # Find shortest path for each combination of critical states in each automaton
                local_aut = create_local_automaton(aut, local_alphabet, start_state, end_state)
                path = get_time_optimal_reduction(selected_aut, eventdata, len(cliques), local_alphabet, start_state, end_state)
                if path is not None:
                    # If a path is found, determine if it's worthy to create a tau transition
                    find_local_paths(selected_aut, eventdata, cliques, path, critical_states.union(semi_critical_states))
    
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
            
    return aut_list, eventdata

def searchDict(dict, searchFor, exeptItem):
    for item in dict:
        if item is not exeptItem:
            if searchFor in dict[item]:
                return item
    return None

def find_local_paths(aut, eventdata, cliques, path, critical_states):
    local_evt_path = []
    new_path = True
    for edge in path:
        if new_path:
            start_state = edge.pred
            new_path = False
        local_evt_path.append(edge.label)
        if edge.succ in critical_states:
            end_state = edge.succ
            add_abstracted_tau_paths(aut, eventdata, cliques, start_state, end_state, local_evt_path)
            local_evt_path = []
            new_path = True
            

def add_abstracted_tau_paths(aut, eventdata, cliques, start_state, end_state, evt_path):
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
    tau_evt_data = taskresource.ExtendedEventData(new_tau_evt, 0, set([frozenset(aut.alphabet)]))
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

# def dijkstras_local_hop(aut, eventdata, local_alphabet, start_state, end_state):
    # distances = {end_state: 0}
    # last_added = [end_state]
    # while len(last_added) > 0:
        # new_added = []
        # for state in last_added:
            # for edge in state.get_incoming():
                # if edge.label in local_alphabet:
                    # if edge.pred not in distances:
                        # distances[edge.pred] = edge.weight + distances[state]
                        # new_added.append(edge.pred)
                    # elif distances[edge.pred] > edge.weight + distances[state]:
                        # distances[edge.pred] = edge.weight + distances[state]
                        # new_added.append(edge.pred)
        # last_added = new_added
    # if start_state in distances:
        # path = []
        # while start_state != end_state:
            # for edge in start_state.get_outgoing():
                # if edge.succ in distances and distances[edge.succ] == distances[start_state] - edge.weight:
                    # path.append(edge)
                    # start_state = edge.succ
                    # break
        # return path
    # else:
        # return None

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

def get_time_optimal_reduction(aut, eventdata, heap_len):
    # # creating temporary automaton
    # temp_coll = collection.Collection()
    # temp_automaton = weighted_structure.WeightedAutomaton(local_alphabet, temp_coll)
    # for state in aut.get_states():
        # ns = temp_automaton.add_new_state(state == end_state, state.number)
    # for state in aut.get_states():
        # for edge in state.get_outgoing():
            # if edge.label in local_alphabet:
                # new_edge = edge.copy(temp_automaton.get_state(edge.pred.number),
                                     # temp_automaton.get_state(edge.succ.number))
                # temp_automaton.add_edge(new_edge)

    # temp_automaton.initial = temp_automaton.get_state(start_state.number)
    # temp_automaton.reduce(True, True)
    # if temp_automaton.get_num_states() == 0:
        # return None
    
    # # creating spek-en-bonen/useless requirement
    # random_evt = next(iter(local_alphabet))
    # temp_req = data_structure.Automaton(set([random_evt]),temp_coll)
    # ns = temp_req.add_new_state(True)
    # temp_req.initial = ns
    # temp_req.add_edge_data(ns, ns, random_evt)
    # # doing make_time_optimal
    # wsup = compute_weight.compute_weighted_supremal(temp_automaton, temp_req, False)
    # if wsup is None:
        # return None
    # temp_req.clear()
    # del temp_req
    
    marker_valfn = lambda state: 0
    weight_map = compute_weight.compute_state_weights(temp_automaton, marker_valfn)
    initial_weight = weight_map[temp_automaton.initial]
    if initial_weight is maxplus.INFINITE: # Infinite weight initial state.
        return None
    del weight_map
    # XXX Optimization: do heap computation while unfolding the automaton.
    unfolded = compute_weight.unfold_automaton_heaps(temp_automaton, initial_weight, eventdata, heap_len, False)

    wsup3 = compute_weight.compute_weighted_supremal(temp_automaton, unfolded, False)
    temp_automaton.clear()
    unfolded.clear()
    del temp_automaton
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
    initial_weight = weightmap[wunfolded2.initial]
    del weightmap
    wunfolded2.clear()
    del wunfolded2
    
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