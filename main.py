# coding=utf-8

import sys
# add the path for Graphviz
os.environ['PATH'] += "C:\\"+"Program Files\\Graphviz\\bin"
# add the path for SuSyNA
sys.path.insert(0, 'C:\\Users\\linliyong\\Desktop\\folder\\SuSyNA')
from automata import frontend
import os

# grid layout
grid_length = 2
vertex = list(range(1, grid_length * grid_length + 1))
neighbour = {}
for i in vertex:
    neighbour[i] = sorted([x for x in [i + 1, i + grid_length] if x >=1 and x <= grid_length * grid_length])
    if i % grid_length == 0:
        neighbour[i] = sorted(list(set(neighbour[i]).difference({i + 1})))
    if i % grid_length == 1:
        neighbour[i] = sorted(list(set(neighbour[i]).difference({i - 1})))

# each OD pair has vertex[1] as the start and vertex[-1] as the end
# we assume two AGVs
AGV_OD_list = [(vertex[1], vertex[-1]), (vertex[1], vertex[-1])]
number_of_AGVs = len(AGV_OD_list)

# sensor_delay dictionary for the example
# the size of the observation channel is too large in our construction
# we will work in the test mode where network delay is zero
TEST_MODE = 1
if not TEST_MODE:
    complete_neighbour = {}
    for i in vertex:
        complete_neighbour[i] = sorted([x for x in [i - 1, i + 1, i - grid_length, i + grid_length] if x >=1 and x <= grid_length * grid_length])
        if i % grid_length == 0:
            complete_neighbour[i] = sorted(list(set(complete_neighbour[i]).difference({i + 1})))
        if i % grid_length == 1:
            complete_neighbour[i] = sorted(list(set(complete_neighbour[i]).difference({i - 1})))
    sensor_delay = {}
    if grid_length % 2 == 0:
        sensor_delay[(grid_length / 2 - 1) * grid_length + grid_length / 2] = 1
        sensor_delay[(grid_length / 2 - 1) * grid_length + grid_length / 2 + 1] = 1
        sensor_delay[grid_length / 2 * grid_length + grid_length / 2] = 1
        sensor_delay[grid_length / 2 * grid_length + grid_length / 2 + 1] = 1
        explored_vertex = sorted(list(sensor_delay.keys()))
    if grid_length % 2 == 1:
        sensor_delay[grid_length / 2 * grid_length + grid_length / 2 + 1] = 0
        explored_vertex = sorted(list(sensor_delay.keys()))
    to_pop_vertex = explored_vertex[:]
    while to_pop_vertex:
        popped_vertex = to_pop_vertex.pop(0)
        to_assign_vertex = list(set(complete_neighbour[popped_vertex]).difference(set(explored_vertex)))
        to_pop_vertex = to_pop_vertex + to_assign_vertex
        for i in to_assign_vertex:
            sensor_delay[i] = sensor_delay[popped_vertex] + 1
        explored_vertex = explored_vertex + to_assign_vertex

# in test mode
if TEST_MODE:
    complete_neighbour = {}
    for i in vertex:
        complete_neighbour[i] = sorted([x for x in [i - 1, i + 1, i - grid_length, i + grid_length] if x >=1 and x <= grid_length * grid_length])
        if i % grid_length == 0:
            complete_neighbour[i] = sorted(list(set(complete_neighbour[i]).difference({i + 1})))
        if i % grid_length == 1:
            complete_neighbour[i] = sorted(list(set(complete_neighbour[i]).difference({i - 1})))
    sensor_delay = {}
    for i in range(1, grid_length * grid_length + 1):
        sensor_delay[i] = 0

# control delay dictionary for the example
control_delay = {}
for i in vertex:
    control_delay[i] = 0

# travel time dictionary for the example
travel_time = {}
for i in neighbour.keys():
    for j in neighbour[i]:
        for k in range(1, number_of_AGVs+1):
            # the travel time from vertex i to vertex j for agv k
            travel_time['e-' + str(i) + '-' + str(j) + '-' + str(k)] = 1


# generate the AGV movement automaton models
def generate_agv(agv):
    states = ['0', '1']
    alphabet = ['tau', 'mu', 'tick']
    controllable = ['mu']
    observable = ['tick']
    transitions = ['(0, 1, tau)', '(1, 1, mu)']
    initial_state = '0'
    marked_states = str(vertex[-1])
    for edge in [x for x in travel_time.keys() if x.split('-')[3] == str(agv)]:
        for time in range(travel_time[edge] + 1):
            states = states + [edge + '-' + str(time)]
    states = states + [str(i) for i in vertex[1:]]
    alphabet = alphabet + [x for x in list(travel_time.keys()) if x.split('-')[3] == str(agv)] + ['a-' + str(i) + '-' + str(agv) + '-in' for i in vertex[1:]]
    for i in vertex:
        transitions = transitions + ['({}, {}, tick)'.format(i, i)]
        for j in neighbour[i]:
            transitions = transitions + ['({}, e-{}-{}-{}-{}, e-{}-{}-{})'.format(i, i, j, agv, travel_time['e-' + str(i) + '-' + str(j) + '-' + str(agv)],  i, j, agv)]
            transitions = transitions + ['(e-{}-{}-{}-0, {}, a-{}-{}-in)'.format(i, j, agv, j, j, agv)]
            for k in range(1, travel_time['e-' + str(i) + '-' + str(j) + '-' + str(agv)] + 1):
                transitions = transitions + ['(e-{}-{}-{}-{}, e-{}-{}-{}-{}, tick)'.format(i, j, agv, k, i, j, agv, k-1)]
    with open('agv' + str(agv) + '.cfg', "w") as cfg_file:
        cfg_file.write("[automaton]\n")
        cfg_file.write("states = {}\n".format(", ".join(states)))
        cfg_file.write("alphabet = {}\n".format(", ".join(alphabet)))
        cfg_file.write("controllable = {}\n".format(", ".join(controllable)))
        cfg_file.write("observable = {}\n".format(", ".join(observable)))
        cfg_file.write("transitions = {}\n".format(", ".join(transitions)))
        cfg_file.write("initial-state = 0\n")
        cfg_file.write("marker-states = {}".format(marked_states))
    cfg_file.close()
    return states, alphabet, controllable, observable, transitions, initial_state, marked_states


# the assumption here is that the delay is zero in the control channel
def generate_control_channel():
    states = ['0', '1']
    alphabet = ['tau', 'mu', 'tick']
    controllable = ['mu']
    observable = ['tick']
    transitions = ['(0, 1, tau)', '(1, 1, mu)', '(1, 1, tick)']
    initial_state = '0'
    for i in vertex:
        for j in neighbour[i]:
            for k in range(1, number_of_AGVs+1):
                states = states + ['e-' + str(i) + '-' + str(j) + '-' + str(k)]
                transitions = transitions + ['(1, e-{}-{}-{}, e-{}-{}-{}-in)'.format(i, j, k, i, j, k)] + ['(e-{}-{}-{}, 1, e-{}-{}-{})'.format(i, j, k, i, j, k)]
                alphabet = alphabet + ['e-' + str(i) + '-' + str(j) + '-' + str(k) + '-in'] + ['e-' + str(i) + '-' + str(j) + '-' + str(k)]
                controllable = controllable + ['e-' + str(i) + '-' + str(j) + '-' + str(k) + '-in']
                observable = observable + ['e-' + str(i) + '-' + str(j) + '-' + str(k) + '-in']
    marked_states = states[1:]
    with open('control_channel.cfg', "w") as cfg_file:
        cfg_file.write("[automaton]\n")
        cfg_file.write("states = {}\n".format(", ".join(states)))
        cfg_file.write("alphabet = {}\n".format(", ".join(alphabet)))
        cfg_file.write("controllable = {}\n".format(", ".join(controllable)))
        cfg_file.write("observable = {}\n".format(", ".join(observable)))
        cfg_file.write("transitions = {}\n".format(", ".join(transitions)))
        cfg_file.write("initial-state = 0\n")
        cfg_file.write("marker-states = {}".format(", ".join(marked_states)))
    cfg_file.close()
    return states, alphabet, controllable, observable, transitions, initial_state, marked_states


def generate_observation_channel():
    states = ['0', '1']
    alphabet = ['tau', 'mu', 'tick']
    controllable = ['mu']
    observable = ['tick']
    initial_state = '0'
    transitions = ['(0, 1, tau)', '(1, 1, mu)']
    # specify the alphabet and the observable
    # nothing will be controllable
    for i in vertex[1:]:
        for j in range(1, number_of_AGVs + 1):
            alphabet = alphabet + ['a-' + str(i) + '-' + str(j) + '-in', 'a-' + str(i) + '-' + str(j) + '-out']
            observable = observable + ['a-' + str(i) + '-' + str(j) + '-out']
    # adding states and transitions with physical states
    # physical states correspond to agv state coupled with its own channel content
    to_explore = [('1', [], '1', [])]
    stored_states = to_explore[:]
    state_transitions = []
    while to_explore:
        #print(len(state_transitions))
        candidate = to_explore.pop(0)
        if candidate[0] != vertex[-1]:
            # one agv can move forward and send observation message into the channel, creating new states
            for j in neighbour[int(candidate[0])]:
                state_transitions = state_transitions + [(candidate, (str(j), candidate[1] + [('a-' + str(j) + '-1-in', sensor_delay[j])], candidate[2], candidate[3]), 'a-' + str(j) + '-1-in')]
                if [(str(j), candidate[1] + [('a-' + str(j) + '-1-in', sensor_delay[j])], candidate[2], candidate[3])] not in stored_states:
                    to_explore = to_explore + [(str(j), candidate[1] + [('a-' + str(j) + '-1-in', sensor_delay[j])], candidate[2], candidate[3])]
                    stored_states = stored_states + [(str(j), candidate[1] + [('a-' + str(j) + '-1-in', sensor_delay[j])], candidate[2], candidate[3])]
        #print(to_explore)
        if candidate[2] != vertex[-1]:
            # the other agv can move forward and send observation message into the channel
            for j in neighbour[int(candidate[2])]:
                state_transitions = state_transitions + [(candidate, (candidate[0], candidate[1], str(j), candidate[3] + [('a-' + str(j) + '-2-in', sensor_delay[j])]), 'a-'+ str(j) + '-2-in')]
                if [(candidate[0], candidate[1], str(j), candidate[3] + [('a-' + str(j) + '-2-in', sensor_delay[j])])] not in stored_states:
                    to_explore = to_explore + [(candidate[0], candidate[1], str(j), candidate[3] + [('a-' + str(j) + '-2-in', sensor_delay[j])])]
                    stored_states = stored_states + [(candidate[0], candidate[1], str(j), candidate[3] + [('a-' + str(j) + '-2-in', sensor_delay[j])])]
        # add tick transitions
        flag = 1
        for element in candidate[1] + candidate[3]:
            if element[1] == 0:
                flag = 0
                break
        if flag:
            post = (candidate[0], [(element[0], element[1]-1) for element in candidate[1]], candidate[2], [(element[0], element[1]-1) for element in candidate[3]])
            state_transitions = state_transitions + [(candidate, post, 'tick')]
            if post not in stored_states:
                to_explore = to_explore + [post]
                stored_states = stored_states + [post]
        # add message removal transitions
        if candidate[1]:
            for i in range(len(candidate[1])):
                event, time = candidate[1][i]
                post = (candidate[0], candidate[1][:i-1]+candidate[1][i+1:], candidate[2], candidate[3])
                state_transitions = state_transitions + [(candidate, post, "-".join(event.split('-')[:-1] + ['out']))]
                if post not in stored_states:
                    to_explore = to_explore + [post]
                    stored_states = stored_states + [post]
        if candidate[3]:
            for i in range(len(candidate[3])):
                event, time = candidate[3][i]
                post = (candidate[0], candidate[1], candidate[2], candidate[3][:i-1] + candidate[3][i + 1:])
                state_transitions = state_transitions + [(candidate, post, "-".join(event.split('-')[:-1] + ['out']))]
                if post not in stored_states:
                    to_explore = to_explore + [post]
                    stored_states = stored_states + [post]
    states = states + [str(x) for x in list(range(2, len(stored_states) + 1))]
    state_index = list(range(1, len(stored_states)+1))
    state_dict = dict(zip(state_index, stored_states))
    for transition in state_transitions:
        transitions = transitions + ['({}, {}, {})'.format(list(state_dict.keys())[list(state_dict.values()).index(transition[0])], list(state_dict.keys())[list(state_dict.values()).index(transition[1])], transition[2])]
    marked_states = states[1:]
    with open('observation_channel.cfg', "w") as cfg_file:
        cfg_file.write("[automaton]\n")
        cfg_file.write("states = {}\n".format(", ".join(states)))
        cfg_file.write("alphabet = {}\n".format(", ".join(alphabet)))
        cfg_file.write("controllable = {}\n".format(", ".join(controllable)))
        cfg_file.write("observable = {}\n".format(", ".join(observable)))
        cfg_file.write("transitions = {}\n".format(", ".join(transitions)))
        cfg_file.write("initial-state = 0\n")
        cfg_file.write("marker-states = {}".format(", ".join(marked_states)))
    cfg_file.close()
    return states, alphabet, controllable, observable, transitions, initial_state, marked_states


# generate early than specification
# given input as an order [[1, 2], 1] meaning that agv1 needs to arrive earlier, with a gap 1
def generate_early_spec(order):
    states = ['0', '1'] + [str(i) for i in list(range(2, 4 + order[1]))]
    alphabet = ['tau', 'mu', 'tick', 'a-' + str(vertex[-1]) + '-1-in', 'a-' + str(vertex[-1]) + '-2-in']
    controllable = ['mu']
    observable = ['tick']
    initial_state = '0'
    marked_states = states[-1]
    transitions = ['(0, 1, tau)', '(1, 1, mu)', '(1, 2, a-{}-{}-in)'.format(vertex[-1], order[0][0]), '({}, {}, a-{}-{}-in)'.format(states[-2], states[-1], vertex[-1], order[0][1])]
    for i in range(2, 2 + order[1]):
        transitions = transitions + ['({}, {}, tick)'.format(i, i + 1)]
    transitions = transitions + ['({}, {}, tick)'.format(vertex[-2], vertex[-2])]
    transitions = transitions + ['(1, 1, tick)']
    transitions = transitions + ['({}, {}, tick)'.format(vertex[-1], vertex[-1])]
    with open('early_spec.cfg', "w") as cfg_file:
        cfg_file.write("[automaton]\n")
        cfg_file.write("states = {}\n".format(", ".join(states)))
        cfg_file.write("alphabet = {}\n".format(", ".join(alphabet)))
        cfg_file.write("controllable = {}\n".format(", ".join(controllable)))
        cfg_file.write("observable = {}\n".format(", ".join(observable)))
        cfg_file.write("transitions = {}\n".format(", ".join(transitions)))
        cfg_file.write("initial-state = 0\n")
        cfg_file.write("marker-states = {}".format(marked_states))
    cfg_file.close()
    return states, alphabet, controllable, observable, transitions, initial_state, marked_states


# generate safety specification
def generate_safety_spec():
    pass

#print(travel_time)
# plant model generation
SYNTH_MODE = 1
if SYNTH_MODE:
    os.system('del *.dot')
    os.system('del *.png')
    os.system('del *.cfg')
    generate_agv(1)
    print('agv1 completed')
    generate_agv(2)
    print('agv2 completed')
    generate_control_channel()
    print('control channel completed')
    generate_observation_channel()
    print('observation channel completed')
    frontend.make_trim('observation_channel.cfg', 'observation_channel_trim.cfg')
    files = [x for x in os.listdir('C:\\Users\\linliyong\\Desktop\\folder\\') if x[-3:] == 'cfg']
    plant_string = ''
    for entry in files:
        plant_string = plant_string + entry + ', '
    frontend.make_product(plant_string[:-2], 'plant.cfg')
    print('plant model completed')
    order = [[1, 2], 1]
    generate_early_spec(order)
    for file in files:
        print(file[:-4])
        frontend.make_dot('C:\\Users\\linliyong\\Desktop\\folder\\' + file, file[:-4] + '.dot')
        frontend.make_dot('early_spec.cfg', 'early_spec.dot')
        os.system('dot -Tpng ' + file[:-4]+'.dot' + ' -o ' + file[:-4] + '.png')
        os.system('dot -Tpng early_spec.dot -o early_spec.png')
    frontend.make_supervisor('plant.cfg', 'early_spec.cfg', 'supervisor.cfg')
    frontend.make_dot('supervisor.cfg', 'supervisor.dot')
    os.system('dot -Tpng supervisor.dot -o supervisor.png')


