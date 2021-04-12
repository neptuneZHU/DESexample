__author__ = 'sware'

def walkthrough(auts):
  alphabet = set()
  for aut in auts:
    alphabet.update(aut.alphabet)
  path = []
  state_tuple = [aut.initial for aut in auts]
  succ_maps = []
  for i, aut in enumerate(auts):
    succ_map = {}
    succ_maps.append(succ_map)
    for state in aut.get_states():
      for edge in state.get_outgoing():
        succ_map[(state, edge.label)] = edge.succ
  while True:
    successors = []
    for event in alphabet:
      temp_succ = []
      for i, state in enumerate(state_tuple):
        if event not in auts[i].alphabet:
          temp_succ.append(state)
        elif (state, event) in succ_maps[i]:
          temp_succ.append(succ_maps[i][(state,event)])
        else:
          break
      if len(temp_succ) == len(state_tuple):
        successors.append((temp_succ, event))
    print "curr_state = " + str(state_tuple)
    for i, tuple in enumerate(successors):
      print str(i) + ": " + str(tuple[1])
    index = int(input("Choose Event"))
    tup = successors[index]
    path.append(tup[1])
    state_tuple = tup[0]
