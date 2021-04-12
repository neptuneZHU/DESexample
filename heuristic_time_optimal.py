import automata
from automata import collection, common, tools, weighted_frontend, \
                     taskresource, weighted_product, algorithm, product, \
                     data_structure, maxplus, frontend

####### Settings #######
# Specify the number of components (no more than 6 at this time)
num_comp = 6

####### Initialize #######
comp_string = "EPUCK1"
for i in range(1, num_comp):
    comp_string = comp_string + " EPUCK" + str(i+1)
with open("EPUCK-mut_ex_" + str(num_comp) + "_plants.txt", "r") as mut_ex_list_file:
    mut_ex_list = mut_ex_list_file.read()
# comp_string = "plant1 plant2"
# mut_ex_list = "{}"

####### Program #######

# Generate component data
coll = collection.Collection()
common.print_line("Loading automata...")
comp_names = tools.convert(comp_string)
comp_list = weighted_frontend.load_weighted_automata(coll, comp_names, False, True)

common.print_line("Computing event data...")
evt_pairs = taskresource.process_event_pairs(coll, None, mut_ex_list)
eventdata, heap_len = taskresource.compute_custom_eventdata(comp_list, evt_pairs)

def find_distances_to_marker(comp_list):
    distances_structure = {}
    for comp in comp_list:
        distances_to_marker = {}
        
        # Find marker state
        # Maybe edit this part to work for automata with multiple marker states?
        end_state = None
        while end_state == None:
            for state in comp.get_states():
                if state.marked:
                    end_state = state
        distances_to_marker[end_state] = 0
        
        # 
        last_added = [end_state]
        while len(last_added) > 0:
            new_added = []
            for state in last_added:
                for edge in state.get_incoming():
                    if edge.pred not in distances_to_marker:
                        distances_to_marker[edge.pred] = edge.weight + distances_to_marker[state]
                        new_added.append(edge.pred)
                    elif distances_to_marker[edge.pred] > edge.weight + distances_to_marker[state]:
                        distances_to_marker[edge.pred] = edge.weight + distances_to_marker[state]
                        new_added.append(edge.pred)
            last_added = new_added
        
        # Add distances to total list
        distances_structure[comp] = distances_to_marker
    return distances_structure

def find_distances_to_initial(comp_list):
    distances_structure = {}
    for comp in comp_list:
        distances_to_initial = {}
        distances_to_initial[comp.initial] = 0
        
        # 
        last_added = [comp.initial]
        while len(last_added) > 0:
            new_added = []
            for state in last_added:
                for edge in state.get_outgoing():
                    if edge.succ not in distances_to_initial:
                        distances_to_initial[edge.succ] = edge.weight + distances_to_initial[state]
                        new_added.append(edge.succ)
                    elif distances_to_initial[edge.succ] > edge.weight + distances_to_initial[state]:
                        distances_to_initial[edge.succ] = edge.weight + distances_to_initial[state]
                        new_added.append(edge.succ)
            last_added = new_added
        
        # Add distances to total list
        distances_structure[comp] = distances_to_initial
    return distances_structure

def state_path_distance(comp_list, distances_from_start, distances_from_end):
    path_length_state = {}
    shortest_path = {}
    longest_path = {}
    for comp in comp_list:
        path_length_state[comp] = {}
        shortest_path[comp] = 999999999999999999999999999999999999999999999999
        longest_path[comp] = 0
        for state in comp.get_states():
            path_length_state[comp][state] = distances_from_start[comp][state] + distances_from_end[comp][state]
            if path_length_state[comp][state] > longest_path[comp]:
                longest_path[comp] = path_length_state[comp][state]
            if path_length_state[comp][state] < shortest_path[comp]:
                shortest_path[comp] = path_length_state[comp][state]
    return path_length_state, shortest_path, longest_path

common.print_line("Finding Distances per automaton...")
distances_to_marker = find_distances_to_marker(comp_list)
distances_from_start = find_distances_to_initial(comp_list)
path_length_state, shortest_path, longest_path = state_path_distance(comp_list, distances_from_start, distances_to_marker)

def trim_components(comp_list, path_length_state, shortest_path, allow_detour = False):
    shortest_path_max = 0
    for comp, path in shortest_path.items():
        if path > shortest_path_max:
            shortest_path_max = path
    
    for comp in comp_list:
        if allow_detour:
            for state, path_distance in path_length_state[comp].items():
                if path_distance > shortest_path_max:
                    comp.remove_state(state)
        else:
            for state, path_distance in path_length_state[comp].items():
                if path_distance > shortest_path[comp]:
                    comp.remove_state(state)
    return comp_list

common.print_line("Removing component states not in shortest path...")
comp_list = trim_components(comp_list, path_length_state, shortest_path)

def marker_calc(mapping):
    for state in mapping:
        if not state.marked:
            return False
    return True

def calc_resource_usage(aut_list, eventdata, heap_len):
    resource_usage = {}
    resource_num = {}
    basic_list = []
    for i in range(heap_len):
        basic_list.append(True)
    for aut in aut_list:
        resource_usage[aut] = basic_list
        for evt in aut.alphabet:
            resource_usage[aut] = [all(bools) for bools in zip(resource_usage[aut],eventdata[evt].used)]
        for i in range(heap_len):
            if resource_usage[aut][i] == True:
                resource_num[aut] = i
    return resource_num
        

def heap_unfold_product(aut_list, eventdata, heap_len, distances_to_marker, shortest_path):
    result_alphabet = set()
    for aut in aut_list:
        result_alphabet.update(aut.alphabet)
    plant = data_structure.Automaton(result_alphabet, aut_list[0].collection)
    mapping = {}
    heap_map = {}
    aut_resource_usage = calc_resource_usage(aut_list, eventdata, heap_len)
    initial_state_mapping = tuple(aut.initial for aut in aut_list)
    initial_state = plant.add_new_state(marker_calc(initial_state_mapping))
    plant.set_initial(initial_state)
    mapping[initial_state] = initial_state_mapping
    heap_map[initial_state] = maxplus.make_rowmat(0, heap_len)
    shortest_path_max = 0
    for comp, path in shortest_path.items():
        if path > shortest_path_max:
            shortest_path_max = path
    
    traverse(comp_list, plant, initial_state, mapping, heap_map, eventdata, aut_resource_usage, distances_to_marker, shortest_path_max)
    return plant

def calc_target(aut_list, start_mapping, evt):
    target_mapping = ()
    for aut, state in zip(aut_list, start_mapping):
        if evt in aut.alphabet:
            for edge in state.get_outgoing():
                if edge.label == evt:
                    target_state = edge.succ
            target_mapping = target_mapping + (target_state,)
        else:
            target_mapping = target_mapping + (state,)
    return target_mapping


def traverse(aut_list, plant, start_state, mapping, heap_map, eventdata, aut_resource_usage, distances_to_marker, shortest_path_max):
    global path_found
    if path_found:
        return
    if plant.get_num_states() % 1000 == 0:
        common.print_line("%d states traversed." % plant.get_num_states())
    edges = []
    disabled = set()
    for aut, state in zip(aut_list, mapping[start_state]):
        aut_edges = []
        aut_events = set()
        for edge in state.get_outgoing():
            aut_edges.append(edge)
            aut_events.add(edge.label)
        edges.append(aut_edges)
        disabled.update(aut.alphabet.difference(aut_events))
        
    for evt in plant.alphabet.difference(disabled):
        if path_found:
            return
        target_mapping = calc_target(aut_list, mapping[start_state], evt)
        
        # state collision part, make it nicer
        state_name_list = []
        for aut, state in zip(aut_list, target_mapping):
            for name in aut.state_names[state.number].split("_"):
                state_name_list.append(name)
        if len(state_name_list) > len(set(state_name_list)):
            continue
        
        target_heap = maxplus.otimes_mat_mat(heap_map[start_state], eventdata[evt].matHat)
        
        do_this_event = True
        if target_mapping in mapping.values():
            do_this_event = False
            for state, map in mapping.items():
                if map == target_mapping:
                    for heap_old, heap_new in zip(heap_map[state].data[0], target_heap.data[0]):
                        if heap_new < heap_old:
                            do_this_event = True
                            break
                if do_this_event == True:
                    break
        if do_this_event == False:
            continue
        do_this_event = False
        for aut, start, target in zip(aut_list, mapping[start_state], target_mapping):
            if distances_to_marker[aut][start] > distances_to_marker[aut][target]:
                do_this_event = True
                break
        if do_this_event == False:
            continue
        for aut, start, target in zip(aut_list, mapping[start_state], target_mapping):
            if target_heap.data[0][aut_resource_usage[aut]] + distances_to_marker[aut][target] > shortest_path_max:
                do_this_event = False
                break
        if do_this_event == False:
            continue
        if do_this_event:
            # add target state to plant
            target_state = plant.add_new_state(marker_calc(target_mapping))
            # add transition to plant
            new_edge = data_structure.Edge(start_state, target_state, evt)
            plant.add_edge(new_edge)
            # add mapping
            mapping[target_state] = target_mapping
            heap_map[target_state] = target_heap
            if marker_calc(target_mapping):
                path_found = True
                common.print_line("Path length:")
                print max(target_heap.data[0])
                break
            else:
                traverse(aut_list, plant, target_state, mapping, heap_map, eventdata, aut_resource_usage, distances_to_marker, shortest_path_max)

def extract_trace(path):
  eventlist = []
  pathstate = path.initial
  while not pathstate.marked:
    for edge in pathstate.get_outgoing():
      pathstate = edge.succ
      eventlist.append(edge.label)
  return eventlist

common.print_line("Calculating product...")
path_found = False
plant = heap_unfold_product(comp_list, eventdata, heap_len, distances_to_marker, shortest_path)
if path_found:
    plant.reduce(True, True)
    common.print_line("Path found, outputting to file...")
    plant.save_as_dot("test_plant_as_dot.dot")
    frontend.save_automaton(plant, "saving", "epuckpath.cfg")
    trace = extract_trace(plant)
    string = ""
    for (i, event) in enumerate(trace):
      if i != 0:
        string += ", "
      string += event.name 
    handle = file("epuckevents.txt", 'w')
    handle.write(string)
    handle.close()
else:
    common.print_line("No path could be found...")




























