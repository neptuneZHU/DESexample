import automata
from automata import taskresource, maxplus

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
    local_alphabet = {}
    for aut in aut_list:
        local_alphabet[aut] = set()
        for evt in total_alphabet[aut]:
            if evt in mut_ex_evt_list:
                continue
            evt_is_local = True
            for comp in aut_list:
                if comp is not aut:
                    if evt in total_alphabet[comp]:
                        evt_is_local = False
                        break
            if evt_is_local:
                local_alphabet[aut].add(evt)
    
    # Find critical states
    critical_states, semi_critical_states = find_critical_states(aut_list, local_alphabet)
    
    for aut in aut_list:
        for end_state in critical_states[aut]:
            for start_state in critical_states[aut].union(semi_critical_states[aut]):
                if start_state is not end_state: # We're not trying to create loops
                    path = []
                    # Find shortest path for each combination of critical states in each automaton
                    path = dijkstras_local(aut, local_alphabet[aut], start_state, end_state)
                    if path is not None:
                        # If a path is found, determine if it's worthy to create a tau transition
                        print "path found"
                        find_local_paths(aut, eventdata, cliques, path, critical_states[aut].union(semi_critical_states[aut]))
    
    # Remove all non-critical states and local transitions from each automaton
    non_critical_states = {}
    for aut in aut_list:
        non_critical_states[aut] = []
        for state in aut.get_states():
            if state not in critical_states[aut].union(semi_critical_states[aut]):
                non_critical_states[aut].append(state)
        for state in non_critical_states[aut]:
            aut.remove_state(state)
        removable_edges = []
        for state in aut.get_states():
            for edge in state.get_outgoing():
                if edge.label in local_alphabet[aut]:
                    removable_edges.append(edge)
        for edge in removable_edges:
            aut.remove_edge(edge)
            
    return aut_list

def searchDict(dict, searchFor, exeptItem):
    for item in dict:
        if item is not exeptItem:
            if searchFor in dict[item]:
                return item
    return None

def find_local_paths(aut, eventdata, cliques, path, critical_states):
    local_evt_path = []
    local_path_weight = 0
    new_path = True
    for edge in path:
        if new_path:
            start_state = edge.pred
            new_path = False
        local_evt_path.append(edge.label)
        local_path_weight += edge.weight
        if edge.succ in critical_states:
            end_state = edge.succ
            add_abstracted_tau_paths(aut, eventdata, cliques, start_state, end_state, local_evt_path, local_path_weight)
            local_evt_path = []
            local_path_weight = 0
            new_path = True
            

def add_abstracted_tau_paths(aut, eventdata, cliques, start_state, end_state, evt_path, path_weight):
    new_tau_evt_name = "tau"
    for evt in evt_path:
        new_tau_evt_name = new_tau_evt_name + "-" + evt.name
        # print eventdata[evt]
    new_tau_evt = aut.collection.make_event(new_tau_evt_name, True, True, False)
    if not new_tau_evt in aut.alphabet:
        aut.alphabet.add(new_tau_evt)
    aut.add_edge_data(start_state, end_state, new_tau_evt, path_weight)
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
    # print tau_evt_data


def dijkstras_local(aut, local_alphabet, start_state, end_state):
    distances = {end_state: 0}
    last_added = [end_state]
    while len(last_added) > 0:
        new_added = []
        for state in last_added:
            for edge in state.get_incoming():
                if edge.label in local_alphabet:
                    if edge.pred not in distances:
                        distances[edge.pred] = edge.weight + distances[state]
                        new_added.append(edge.pred)
                    elif distances[edge.pred] > edge.weight + distances[state]:
                        distances[edge.pred] = edge.weight + distances[state]
                        new_added.append(edge.pred)
        last_added = new_added
    if start_state in distances:
        path = []
        while start_state != end_state:
            for edge in start_state.get_outgoing():
                if edge.succ in distances and distances[edge.succ] == distances[start_state] - edge.weight:
                    path.append(edge)
                    start_state = edge.succ
                    break
        return path
    else:
        return None


def find_critical_states(aut_list, local_alphabet):
    critical_states = {}
    semi_critical_states = {}
    for aut in aut_list:
        critical_states[aut] = set()
        semi_critical_states[aut] = set()
        for state in aut.get_states():
            if state.marked: # If a state is marked, it's critical
                critical_states[aut].add(state)
                continue
            for edge in state.get_outgoing():
                if edge.label not in local_alphabet[aut]: # If a state has a global event on an outgoing edge, it's critical
                    critical_states[aut].add(state)
                    break
            if state not in critical_states[aut]:
                for edge in state.get_incoming():
                    if edge.label not in local_alphabet[aut]: # If a state has a global event on an incoming edge, it's semi-critical
                        semi_critical_states[aut].add(state)
                        break
        if aut.initial not in critical_states[aut]: # If the initial state isn't in the critical state set yet, add it
            semi_critical_states[aut].add(aut.initial)
    return critical_states, semi_critical_states