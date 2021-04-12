from automata import collection, weighted_structure, weighted_frontend, data_structure


def dothis(local_alphabet):
    print local_alphabet.pop()

coll = collection.Collection()
comp_list = weighted_frontend.load_weighted_automata(coll, "plant1.cfg", False, True)
local_alphabet = comp_list[0].alphabet
print local_alphabet
dothis(local_alphabet)
print local_alphabet
temp_coll = collection.Collection()
temp_automaton = weighted_structure.WeightedAutomaton(local_alphabet, temp_coll)
# temp_automaton.add_new_state(False, comp_list[0].initial.number)
for state in comp_list[0].get_states():
    ns = temp_automaton.add_new_state(state.marked, state.number)

for state in comp_list[0].get_states():
    for edge in state.get_outgoing():
        if edge.label in local_alphabet:
            print "this happends"
            new_edge = edge.copy(temp_automaton.get_state(edge.pred.number),
                                 temp_automaton.get_state(edge.succ.number))
            temp_automaton.add_edge(new_edge)

temp_automaton.initial = temp_automaton.get_state(comp_list[0].initial.number)
temp_automaton.reduce(True, True)
temp_req = data_structure.Automaton(set([next(iter(local_alphabet))]),temp_coll)
print temp_automaton.initial.get_outgoing().pop()