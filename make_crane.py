import random
import os

from automata.frontend import save_automaton
from automata.weighted_frontend import save_weighted_automaton
from automata.tau_abstraction import remove_always_disabled_events
from automata import weighted_structure, collection, tau_abstraction

def get_event(coll, name):
  if name in coll.events:
    return coll.events[name]
  else:
    return coll.make_event(name, True, True, False)
    
def make_move_order(SC_auts, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  aut.initial = aut.add_new_state(True, 1)
  picks = []
  for SC_aut in SC_auts:
    pick_events = [evt for evt in SC_aut.alphabet if "pick" in evt.name]
    aut.alphabet.update(pick_events)
    picks.append(pick_events)
  state = aut.initial
  while picks:
    pick_events = picks.pop(random.randint(0, len(picks)-1))
    pick_event = random.sample(pick_events, 1)[0]
    new_state = aut.add_new_state(True, aut.get_num_states() + 1)
    aut.add_edge_data(state, new_state, pick_event, 1)
    state = new_state
  return aut
  
def add_move_events_to_crane(crane, move_events):
  crane.alphabet.update(move_events)
  for state in crane.get_states():
    for evt in move_events:
      crane.add_edge_data(state, state, evt, 1)

def make_crane(index, slots, containers, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  state2 = aut.add_new_state(False, 2)
  aut.initial = state1
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  crane = "C" + str(index)
  for func in functions:
    eventlist[func] = []
    for i in range(1, slots + 1):
      for j in range(1, 3):
        for k in range(1, containers + 1):
          loc = str(i) + "-" + str(j) + "-" + str(k)
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
          eventlist[func].append(event)
  for func in functions:
    pred = None
    succ = None
    if "-pick-" == func:
      pred, succ = state1, state2
    else:
      pred, succ = state2, state1
    for event in eventlist[func]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
  return aut

def make_crane2(index, slots, containers, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  state2 = aut.add_new_state(False, 2)
  aut.initial = state1
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  crane = "C" + str(index)
  for func in functions:
    eventlist[func] = []
    for i in range(1, slots + 1):
      for j in range(1, 3):
        for k in range(1, containers + 1):
          loc = str(i) + "-" + str(j) + "-" + str(k)
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
          eventlist[func].append(event)
  for func in functions:
    pred = None
    succ = None
    if "-pick-" == func:
      pred, succ = state1, state2
    else:
      pred, succ = state2, state1
    for event in eventlist[func]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
  for slot in range(1, slots + 1):
    aut.alphabet.add(get_event(coll, crane + "-switch-" + str(slot)))
    aut.add_edge_data(state1, state1, get_event(coll, crane + "-switch-" + str(slot)), 1)
  return aut
  
def make_crane3(index, slots, containers, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  container_states = []
  for i in range(containers):
    container_states.append(aut.add_new_state(False, i + 2))
  aut.initial = state1
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  crane = "C" + str(index)
  for func in functions:
    eventlist[func] = []
    for i in range(1, slots + 1):
      for j in range(1, 3):
        for k in range(1, containers + 1):
          loc = str(i) + "-" + str(j) + "-" + str(k)
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
          eventlist[func].append(event)
  for func in functions:
    if "-pick-" == func:
      for event in eventlist[func]:
        pred, succ  = state1, container_states[int(event.split('-')[-1])-1]
        aut.add_edge_data(pred, succ, get_event(coll, event), 1)
    else:
      for event in eventlist[func]:
        pred, succ  = container_states[int(event.split('-')[-1])-1], state1
        aut.add_edge_data(pred, succ, get_event(coll, event), 1)
  for slot in range(1, slots + 1):
    aut.alphabet.add(get_event(coll, crane + "-switch-" + str(slot)))
    aut.add_edge_data(state1, state1, get_event(coll, crane + "-switch-" + str(slot)), 1)
  return aut

def make_crane_location(cranes, slot, containers, last, init, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  statedict = {}
  for i in range(2, cranes + 2):
    statedict[str(i)] = aut.add_new_state(True, i)
  print "init: " + str(init)
  print aut._states
  aut.initial = aut.get_state(int(init))
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  craneenter = []
  craneleave = []
  for l in range(1, cranes+1):
    crane = "C" + str(l)
    eventlist[crane] = []
    i = slot
    craneenter.append([])
    craneleave.append([])
    if slot != 1:
      event = crane + "-move-" + str(slot-1) + "-" + str(slot)
      craneenter[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
      event = crane + "-move-" + str(slot) + "-" + str(slot-1)
      craneleave[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
    if not last:
      event = crane + "-move-" + str(slot+1) + "-" + str(slot)
      craneenter[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
      event = crane + "-move-" + str(slot) + "-" + str(slot+1)
      craneleave[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
    for func in functions:
      for j in range(1, 3):
        for k in range(1, containers + 1):
          loc = str(i) + "-" + str(j) + "-" + str(k)
          first = False
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
          eventlist[crane].append(event)
  for i in range(2, cranes + 2):
    pred = statedict[str(i)]
    succ = statedict[str(i)]
    crane = "C" + str(i-1)
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
  for i in range(len(craneenter)):
    empty = state1
    full = statedict[str(i + 2)]
    for event in craneenter[i]:
      aut.add_edge_data(empty, full, get_event(coll, event), 1)
    for event in craneleave[i]:
      aut.add_edge_data(full, empty, get_event(coll, event), 1)
  return aut
  
def make_crane_location2(cranes, slot, containers, last, init, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  statedict = {}
  for i in range(2, cranes * 3, 3):
    statedict[str(i)] = aut.add_new_state(True, i)
    statedict[str(i+1)] = aut.add_new_state(True, i+1)
    statedict[str(i+2)] = aut.add_new_state(True, i+2)
  print "init: " + str(init)
  print aut._states
  if init == 1:
    aut.initial = aut.get_state(int(init))
  else:
    init = (init - 1)*3 + 1
    aut.initial = aut.get_state(int(init))
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  craneenter = []
  craneleave = []
  for l in range(1, cranes+1):
    crane = "C" + str(l)
    eventlist[crane] = []
    i = slot
    craneenter.append([])
    craneleave.append([])
    if slot != 1:
      event = crane + "-move-" + str(slot-1) + "-" + str(slot)
      craneenter[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
      event = crane + "-move-" + str(slot) + "-" + str(slot-1)
      craneleave[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
    if not last:
      event = crane + "-move-" + str(slot+1) + "-" + str(slot)
      craneenter[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
      event = crane + "-move-" + str(slot) + "-" + str(slot+1)
      craneleave[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
    for func in functions:
      for j in range(1, 3):
        for k in range(1, containers + 1):
          loc = str(i) + "-" + str(j) + "-" + str(k)
          first = False
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
          eventlist[crane].append(event)
  for i in range(2, cranes *3, 3):
    pred = statedict[str(i)]
    succ = statedict[str(i+2)]
    crane = "C" + str((i/3)+1)
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
    pred = statedict[str(i+1)]
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
    pred = statedict[str(i+2)]
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
  for i in range(len(craneenter)):
    empty = state1
    full1 = statedict[str((i*3) + 2)]
    full2 = statedict[str((i*3) + 3)]
    full3 = statedict[str((i*3) + 4)]
    for event in craneenter[i]:
      print event
      split = event.split("-")
      if int(split[-2]) < int(split[-1]): 
        aut.add_edge_data(empty, full1, get_event(coll, event), 1)
      else:
        aut.add_edge_data(empty, full2, get_event(coll, event), 1)
    for event in craneleave[i]:
      split = event.split("-")
      aut.add_edge_data(full3, empty, get_event(coll, event), 1)
      if int(split[-2]) < int(split[-1]):
        aut.add_edge_data(full1, empty, get_event(coll, event), 1)
      else:
        aut.add_edge_data(full2, empty, get_event(coll, event), 1)
  return aut
  
def make_crane_location3(cranes, slot, containers, last, init, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  statedict = {}
  for i in range(2, cranes * 3, 3):
    statedict[str(i)] = aut.add_new_state(True, i)
    statedict[str(i+1)] = aut.add_new_state(True, i+1)
    statedict[str(i+2)] = aut.add_new_state(True, i+2)
  print "init: " + str(init)
  print aut._states
  if init == 1:
    aut.initial = aut.get_state(int(init))
  else:
    init = (int(init) - 1)*3 + 1
    aut.initial = aut.get_state(int(init))
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  craneenter = []
  craneleave = []
  for l in range(1, cranes+1):
    crane = "C" + str(l)
    eventlist[crane] = []
    aut.alphabet.add(get_event(coll, crane + "-switch-" + str(slot)))
    i = slot
    craneenter.append([])
    craneleave.append([])
    if slot != 1:
      event = crane + "-move-" + str(slot-1) + "-" + str(slot)
      craneenter[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
      event = crane + "-move-" + str(slot) + "-" + str(slot-1)
      craneleave[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
    if not last:
      event = crane + "-move-" + str(slot+1) + "-" + str(slot)
      craneenter[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
      event = crane + "-move-" + str(slot) + "-" + str(slot+1)
      craneleave[l-1].append(event)
      aut.alphabet.add(get_event(coll, event))
    for func in functions:
      for j in range(1, 3):
        for k in range(1, containers + 1):
          loc = str(i) + "-" + str(j) + "-" + str(k)
          first = False
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
          eventlist[crane].append(event)
  for i in range(2, cranes *3, 3):
    pred = statedict[str(i)]
    succ = statedict[str(i+2)]
    crane = "C" + str((i/3)+1)
    aut.add_edge_data(pred, succ, get_event(coll, crane + "-switch-" + str(slot)), 1)
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
    pred = statedict[str(i+1)]
    aut.add_edge_data(pred, succ, get_event(coll, crane + "-switch-" + str(slot)), 1)
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
    pred = statedict[str(i+2)]
    for event in eventlist[crane]:
      aut.add_edge_data(pred, succ, get_event(coll, event), 1)
  for i in range(len(craneenter)):
    empty = state1
    full1 = statedict[str((i*3) + 2)]
    full2 = statedict[str((i*3) + 3)]
    full3 = statedict[str((i*3) + 4)]
    for event in craneenter[i]:
      print event
      split = event.split("-")
      if int(split[-2]) < int(split[-1]): 
        aut.add_edge_data(empty, full1, get_event(coll, event), 1)
      else:
        aut.add_edge_data(empty, full2, get_event(coll, event), 1)
    for event in craneleave[i]:
      split = event.split("-")
      aut.add_edge_data(full3, empty, get_event(coll, event), 1)
      if int(split[-2]) < int(split[-1]):
        aut.add_edge_data(full1, empty, get_event(coll, event), 1)
      else:
        aut.add_edge_data(full2, empty, get_event(coll, event), 1)
  return aut
  
def make_crane_restriction(crane, slot, init, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(True, 1)
  state2 = aut.add_new_state(True, 2)
  aut.initial = aut.get_state(int(init))
  event = crane + "-move-" + str(slot) + "-" + str(slot+1)
  aut.alphabet.add(get_event(coll, event))
  aut.add_edge_data(state1, state2, get_event(coll, event), 1)
  event = crane + "-move-" + str(slot+1) + "-" + str(slot)
  aut.alphabet.add(get_event(coll, event))
  aut.add_edge_data(state2, state1, get_event(coll, event), 1)
  return aut
  
def make_container(index, pick_up, drop_off, next, cranes, slots, coll, name):
  aut = weighted_structure.WeightedAutomaton(set(), coll)
  aut.name = name
  state1 = aut.add_new_state(False, 1)
  aut.initial = state1
  state2 = aut.add_new_state(True, 2)
  statedict = {}
  for i in range(3, 3 + cranes):
    statedict[str(i)] = aut.add_new_state(False, i)
  functions = ["-pick-", "-drop-"]
  picklist = []
  droplist = []
  nextlist = [] if next != None else None
  first = True
  for l in range(1, cranes + 1):
    crane = "C" + str(l)
    for func in functions:
      for i in range(1, slots + 1):
        for j in range(1, 3):        
          loc = str(i) + "-" + str(j) + "-" + str(index)
          event = crane + func + loc
          aut.alphabet.add(get_event(coll, event))
  for l in range(1, cranes + 1):
    crane = "C" + str(l)
    event = crane + "-pick-" + pick_up + str(index)
    aut.alphabet.add(get_event(coll, event))
    picklist.append(get_event(coll, event))
    event = crane + "-drop-" + drop_off + str(index)
    aut.alphabet.add(get_event(coll, event))
    droplist.append(get_event(coll, event))
    if nextlist != None:
      event = crane + "-pick-" + pick_up + str(next)
      aut.alphabet.add(get_event(coll, event))
      nextlist.append(get_event(coll, event))
  pred = state1
  succ = 3
  for (crane, event) in enumerate(picklist):
    aut.add_edge_data(pred, statedict[str(succ + crane)], event, 1)
  pred = 3
  succ = state2
  for (crane, event) in enumerate(droplist):
    aut.add_edge_data(statedict[str(pred + crane)], succ, event, 1)
  if nextlist != None:
    for event in nextlist:
      aut.add_edge_data(state2, state2, event, 1)
      for crane in range(cranes):
        crane = statedict[str(crane + 3)]
        aut.add_edge_data(crane, crane, event, 1)
  return aut
  
def generate_containers(num_incoming, num_outgoing, incomeslot, outgoslot, num_slots):
  occupied = set()
  insl, insi = incomeslot
  ousl, ousi = outgoslot
  pickup = str(insl) + "-" + str(insi) + "-"
  dropoff = str(ousl) + "-" + str(ousi) + "-"
  picks = {}
  picks[pickup] = []
  for i in range(1, num_incoming + 1):
    while True:
      dropslot = random.randint(1, num_slots)
      dropside = random.randint(1, 2)
      tup = (dropslot, dropside)
      if tup not in occupied and tup != incomeslot:
        if tup != outgoslot:
          occupied.add((dropslot, dropside))
        drop = str(dropslot) + "-" + str(dropside) + "-"
        picks[pickup].append(drop)
        break
  for i in range(1, num_outgoing + 1):
    while True:
      pickslot = random.randint(1, num_slots)
      pickside = random.randint(1, 2)
      tup = (pickslot, pickside)
      if tup not in occupied and tup != incomeslot and tup != outgoslot:
        occupied.add(tup)
        pick = str(pickslot) + "-" + str(pickside) + "-"
        picks[pick] = [dropoff]
        break
  return picks
  
def make_system(num_cranes, num_slots, init_crane, num_incoming, num_outgoing, incomeslot, outgoslot):
  filenames = []
  coll = collection.Collection()
  automata = []
  for i in range(1, num_cranes + 1):
    stnum = str(i)
    name = "D" + stnum
    filenames.append(name)
    automata.append(make_crane3(i, num_slots, num_outgoing + num_incoming, coll, name))
  defaultinit = "1"
  craneslot = {}
  inits = {}
  for (crane, slot) in init_crane:
    inits[slot] = str(crane + 1)
    craneslot[crane] = slot
  for i in range(1, num_slots + 1):
    stnum = str(i).zfill(3)
    name = "CS" + stnum
    filenames.append(name)
    init = defaultinit if i not in inits else inits[i]
    automata.append(make_crane_location3(num_cranes, i, num_outgoing + num_incoming, i == num_slots, init, coll, name))
  for i in range(1, num_slots):
    for c in range(1, num_cranes + 1):
      crane = "C" + str(c)
      name = "E" + str(c) + "_" + str(i).zfill(3)
      filenames.append(name)
      init = 1 if craneslot[c] <= i else 2
      automata.append(make_crane_restriction(crane, i, init, coll, name))
  picks = generate_containers(num_incoming, num_outgoing, incomeslot, outgoslot, num_slots)
  num = 0
  for pick in picks:
    drops = picks[pick]
    for i in range(len(drops)):
      drop = drops[i]
      num += 1
      stnum = str(num)
      name = "SC" + stnum
      filenames.append(name)
      automata.append(make_container(num, pick, drop, (num + 1) if (i + 1 < len(drops)) else None, num_cranes, num_slots, coll, name))
  process_system(automata, "cranes", True, num_cranes)

def generate_containers3(num_containers, num_slots):
  occupied = set()
  occupied.add((30, 1))
  occupied.add((90, 1))
  picks = {}
  for i in range(1, num_containers + 1):
    while True:
      pickslot = random.randint(2, num_slots-1)
      pickside = random.randint(1, 2)
      tup = (pickslot, pickside)
      if tup not in occupied:
        occupied.add(tup)
        if random.choice([True, False]):
          dropslot = 90
          dropside = 1
        else:
          dropslot = pickslot
          dropside = pickside
          pickslot = 30
          pickside = 1
        pick = str(pickslot) + "-" + str(pickside) + "-"
        drop = str(dropslot) + "-" + str(dropside) + "-"
        if pick not in picks:
          picks[pick] = [drop]
        else:
          picks[pick].append(drop)
        break
  return picks
  
def generate_containers4(num_containers, num_slots):
  pickups = [(44, 1), (79, 2), (42, 1), (97, 1), (15, 1), (3, 1), (11, 1), \
           (12, 1), (51, 2), (29, 2), (30, 1), (30, 1), (30, 1), (30, 1), \
           (30, 1), (30, 1), (30, 1), (30, 1), (30, 1), (30, 1)]
  dropoff = [(90, 1), (90, 1), (90, 1), (90, 1), (90, 1), (90, 1), (90, 1), \
           (90, 1), (90, 1), (90, 1), (32, 2), (61, 1), (87, 1), (44, 2), \
           (52, 2), (51, 1), (110, 2), (13, 1), (106, 1), (36, 2)]
  picks = {}
  for i in range(len(pickups)):
    pickslot, pickside = pickups[i]
    dropslot, dropside = dropoff[i]
    pick = str(pickslot) + "-" + str(pickside) + "-"
    drop = str(dropslot) + "-" + str(dropside) + "-"
    if pick not in picks:
      picks[pick] = [(drop, i)]
    else:
      picks[pick].append((drop, i))
  return picks
  
def generate_containers2(num_containers, num_slots):
  occupied = set()
  picks = {}
  for i in range(1, num_containers + 1):
    while True:
      pickslot = random.randint(2, num_slots-1)
      pickside = random.randint(1, 2)
      tup = (pickslot, pickside)
      if tup not in occupied:
        occupied.add(tup)
        while True:
          dropslot = random.randint(2, num_slots-1)
          dropside = random.randint(1, 2)
          tup = (dropslot, dropside)
          if tup not in occupied:
            occupied.add(tup)
            pick = str(pickslot) + "-" + str(pickside) + "-"
            drop = str(dropslot) + "-" + str(dropside) + "-"
            picks[pick] = [drop]
            break
        break
  return picks
  
def make_system2(num_cranes, num_slots, init_crane, num_containers):
  filenames = []
  coll = collection.Collection()
  automata = []
  for i in range(1, num_cranes + 1):
    stnum = str(i)
    name = "D" + stnum
    filenames.append(name)
    automata.append(make_crane(i, num_slots, num_containers, coll, name))
  defaultinit = "1"
  craneslot = {}
  inits = {}
  for (crane, slot) in init_crane:
    inits[slot] = str(crane + 1)
    craneslot[crane] = slot
  for i in range(1, num_slots + 1):
    stnum = str(i).zfill(3)
    name = "CS" + stnum
    filenames.append(name)
    init = defaultinit if i not in inits else inits[i]
    automata.append(make_crane_location(num_cranes, i, num_containers, i == num_slots, init, coll, name))
  for i in range(1, num_slots):
    for c in range(1, num_cranes + 1):
      crane = "C" + str(c)
      name = "E" + str(c) + "_" + str(i).zfill(3)
      filenames.append(name)
      init = 1 if craneslot[c] <= i else 2
      automata.append(make_crane_restriction(crane, i, init, coll, name))
  picks = generate_containers4(num_containers, num_slots)
  num = 0
  for pick in picks:
    drops = picks[pick]
    for i in range(len(drops)):
      drop, num = drops[i]
      num += 1
      stnum = str(num)
      name = "SC" + stnum
      filenames.append(name)
      automata.append(make_container(num, pick, drop, None, num_cranes, num_slots, coll, name))
  process_system(automata, "cranes", True, num_cranes)
  
def explicitly_disable_events(aut, cranes, slot):
  #crane_dis = {}
  #for i in (1, cranes+1):
    #crane_dis[i] = set()
  for evt in aut.collection.events:
    evt = aut.collection.events[evt]
    if "mov" in evt.name and evt not in aut.alphabet and int(evt.name.split("-")[-2]) > slot:
      aut.alphabet.add(evt)
      #crane_dis[int(evt.name[1])].add(evt)
      state = aut.get_state(1)
      aut.add_edge_data(state, state, evt, 1)
      c = int(evt.name[1])
      for i in range(2, cranes + 2):
        if c+1 == i:
          continue
        state = aut.get_state(i)
        aut.add_edge_data(state, state, evt, 1)
        
def explicitly_disable_events2(aut, cranes, events):
  slot = int(aut.name[-3:])
  for evt in events:
    if evt in aut.alphabet or int(evt.name.split("-")[-3]) < slot:
      continue
    crane = int(evt.name[1])
    aut.alphabet.add(evt)
    state = aut.get_state(1)
    aut.add_edge_data(state, state, evt, 1)
    for c in range(cranes):
      if c + 1 == crane:
        continue
      for i in range(3):
        state = aut.get_state(i + c*3 + 2)
        aut.add_edge_data(state, state, evt, 1)
      
def explicitly_disable_events_container(aut, cranes, containers_after):
  for after_aut in containers_after:
    for evt in after_aut.alphabet:
      if "drop" in evt.name and evt not in aut.alphabet:
        aut.alphabet.add(evt)
        state = aut.get_state(1)
        aut.add_edge_data(state, state, evt, 1)
        state = aut.get_state(2)
        aut.add_edge_data(state, state, evt, 1)
        c = int(evt.name[1])
        for i in range(3, cranes + 3):
          if c+2 == i:
            continue
          state = aut.get_state(i)
          aut.add_edge_data(state, state, evt, 1)
        
def output_crane_order(auts, output_dir):
  CS_auts = [aut for aut in auts if aut.name.startswith("CS")]
  D_auts = [aut for aut in auts if aut.name.startswith("D")]
  E_auts = [aut for aut in auts if aut.name.startswith("E")]
  SC_auts = [aut for aut in auts if aut.name.startswith("SC")]
  SC_order =[]
  first_comp = D_auts[0].name
  first_comp += "".join("," + aut.name for aut in D_auts[1:])
  spec_comp = ""
  handle = file(output_dir + "\\unweighted\\steps", 'w')
  handle.write(first_comp + " " + spec_comp + " sup1 abs1\n")
  handle2 = file(output_dir + "\\unweightedtau\\steps", 'w')
  handle2.write(first_comp + " " + spec_comp + " sup1 abs1\n")
  count = 2
  for i, CS_aut in enumerate(CS_auts):
    SC_to_add = []
    E_to_add = []
    slot = int(CS_aut.name[-3:]) 
    for SC_aut in SC_auts:
      tokeep = True
      for event in SC_aut.alphabet:
        #if ("drop" in event.name) and int(event.name.split("-")[-3]) > (i+1):
        if ("pick" in event.name or "drop" in event.name) and int(event.name.split("-")[-3]) > (i+1):
          tokeep = False
          break
      if tokeep:
        SC_to_add.append(SC_aut)
        SC_order.append(SC_aut)
    for E_aut in E_auts:
      if int(E_aut.name[-3:]) == slot:
        E_to_add.append(E_aut)
    SC_auts = [aut for aut in SC_auts if aut not in SC_to_add]
    E_auts = [aut for aut in E_auts if aut not in E_to_add]
    comp = "abs" + str(count-1) + "," + CS_aut.name
    comp += "".join("," + aut.name for aut in E_to_add)
    #comp += "".join("," + aut.name for aut in SC_to_add)
    handle.write(comp + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
    handle2.write(comp + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
    count += 1
    for aut in SC_to_add:
      handle.write("abs" + str(count - 1) + "," + aut.name + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
      handle2.write("abs" + str(count - 1) + "," + aut.name + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
      count += 1
  print str(SC_auts)
  handle.close()
  handle2.close()
  return SC_order
  
def output_crane_order_track_first(auts, output_dir):
  CS_auts = [aut for aut in auts if aut.name.startswith("CS")]
  D_auts = [aut for aut in auts if aut.name.startswith("D")]
  E_auts = [aut for aut in auts if aut.name.startswith("E")]
  SC_auts = [aut for aut in auts if aut.name.startswith("SC")]
  SC_order =[]
  first_comp = D_auts[0].name
  first_comp += "".join("," + aut.name for aut in D_auts[1:])
  spec_comp = ""
  handle = file(output_dir + "\\unweighted\\steps", 'w')
  handle.write(first_comp + " " + spec_comp + " sup1 abs1\n")
  handle2 = file(output_dir + "\\unweightedtau\\steps", 'w')
  handle2.write(first_comp + " " + spec_comp + " sup1 abs1\n")
  count = 2
  for i, CS_aut in enumerate(CS_auts):
    SC_to_add = []
    E_to_add = []
    slot = int(CS_aut.name[-3:]) 
    for E_aut in E_auts:
      if int(E_aut.name[-3:]) == slot:
        E_to_add.append(E_aut)
    SC_auts = [aut for aut in SC_auts if aut not in SC_to_add]
    E_auts = [aut for aut in E_auts if aut not in E_to_add]
    comp = "abs" + str(count-1) + "," + CS_aut.name
    comp += "".join("," + aut.name for aut in E_to_add)
    #comp += "".join("," + aut.name for aut in SC_to_add)
    handle.write(comp + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
    handle2.write(comp + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
    count += 1
  for SC_aut in SC_auts:
    SC_order.append(SC_aut)
    handle.write("abs" + str(count - 1) + "," + SC_aut.name + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
    handle2.write("abs" + str(count - 1) + "," + SC_aut.name + "  " + "sup" + str(count) + " abs" + str(count) + "\n")
    count += 1
  print str(SC_auts)
  handle.close()
  handle2.close()
  return SC_order
  
def output_crane_order_compose_segments(auts, output_dir):
  CS_auts = [aut for aut in auts if aut.name.startswith("CS")]
  D_auts = [aut for aut in auts if aut.name.startswith("D")]
  SC_auts = [aut for aut in auts if aut.name.startswith("SC")]
  first_comp = D_auts[0].name
  first_comp += "".join("," + aut.name for aut in D_auts[1:])
  spec_comp = ""
  handle = file(output_dir + "\\unweighted\\steps_segments", 'w')
  handle.write(first_comp + " " + spec_comp + " sup1 abs1\n") 
  for i, CS_aut in enumerate(CS_auts):
    comp = "abs" + str(i + 1) + "," + CS_aut.name
    handle.write(comp + "  " + "sup" + str(i + 2) + " abs" + str(i + 2) + "\n")
  print str(SC_auts)
  handle.close()
  
def output_crane_order_compose_full_track(auts, output_dir):
  CS_auts = [aut for aut in auts if aut.name.startswith("CS")]
  D_auts = [aut for aut in auts if aut.name.startswith("D")]
  SC_auts = [aut for aut in auts if aut.name.startswith("SC")]
  first_comp = D_auts[0].name
  first_comp += "".join("," + aut.name for aut in D_auts[1:])
  spec_comp = ""
  handle = file(output_dir + "\\unweighted\\steps_full_track", 'w')
  handle.write(first_comp + " " + spec_comp + " sup1 abs1\n")
  second_comp = "abs1"
  second_comp += "".join("," + aut.name for aut in CS_auts)
  handle.write(second_comp + " " + spec_comp + " sup2 abs2\n")
  for i, SC_aut in enumerate(SC_auts):
    comp = "abs" + str(i + 2) + "," + SC_aut.name
    handle.write(comp + "  " + "sup" + str(i + 3) + " abs" + str(i + 3) + "\n")
  print str(SC_auts)
  handle.close()
  
def process_system(automata, output_dir, explicitly_disable, cranes):
  #explicitly_disable = False
  if not os.path.exists(output_dir + "\\before_removal\\"):
    os.makedirs(output_dir + "\\before_removal\\")
  for aut in automata:
    aut.save_as_dot(output_dir + "\\before_removal\\" + aut.name + ".dot")
  remove_always_disabled_events(automata)
  if not os.path.exists(output_dir + "\\after_removal\\"):
    os.makedirs(output_dir + "\\after_removal\\")
  for aut in automata:
    print aut.name
    aut.save_as_dot(output_dir + "\\after_removal\\" + aut.name + ".dot")
  tick = automata[0].collection.make_event("tick", True, True, False)
  tau = automata[0].collection.make_event("tau", False, False, False)
  #automata.append(make_move_order([aut for aut in automata if aut.name.startswith("SC")], \
  #                                automata[0].collection, "move_order"))
  #remove_always_disabled_events(automata)
  #for i, aut in enumerate(automata):
  #  if aut.name.startswith("D"):
  #    move_events = [aut.collection.events[evt] for evt in aut.collection.events if "mov" in evt and evt[1] == aut.name[1]]
  #    add_move_events_to_crane(aut, move_events)
  #    aut.alphabet.add(tau)
  #    automata[i] = tau_abstraction.convert_weighted_to_tick(aut, tick)
  #if explicitly_disable:
  #  for aut in automata:
  #    if aut.name.startswith("CS"):
  #      explicitly_disable_events(aut, cranes, int(aut.name[2:]))
  #if explicitly_disable:
  #  evts = set()
  #  for aut in automata:
  #    if aut.name.startswith("SC"):
  #      evts.update(aut.alphabet) 
  #  for aut in list(automata):
  #    if aut.name.startswith("CS"):
  #      explicitly_disable_events2(aut, cranes, evts)
  #for i, aut in enumerate(automata):
  #  if aut.name.startswith("CS"):
  #    aut.alphabet.add(tau)
  #    automata[i] = tau_abstraction.convert_weighted_to_tick(aut, tick)
  sc_order = output_crane_order(automata, output_dir)
  #sc_order = output_crane_order_track_first(automata, output_dir)
  if explicitly_disable:
    for i, aut in enumerate(sc_order):
      print aut.name
      explicitly_disable_events_container(aut, cranes, sc_order[i+1:])
  if not os.path.exists(output_dir + "\\after_disable\\"):
    os.makedirs(output_dir + "\\after_disable\\")
  for aut in automata:
    aut.save_as_dot(output_dir + "\\after_disable\\" + aut.name + ".dot")
  if not os.path.exists(output_dir + "\\weighted\\"):
    os.makedirs(output_dir + "\\weighted\\")
  if not os.path.exists(output_dir + "\\unweighted\\"):
    os.makedirs(output_dir + "\\unweighted\\")
  if not os.path.exists(output_dir + "\\unweightedtau\\"):
    os.makedirs(output_dir + "\\unweightedtau\\")
  for aut in automata:
    save_weighted_automaton(aut, "", output_dir + "\\weighted\\" + aut.name + ".cfg")
    save_automaton(aut, "", output_dir + "\\unweighted\\" + aut.name + ".cfg")
    new_init = aut.add_new_state(False)
    aut.alphabet.add(tau)
    aut.add_edge_data(new_init, aut.initial, tau, 1)
    aut.initial = new_init
    save_automaton(aut, "", output_dir + "\\unweightedtau\\" + aut.name + ".cfg")
  string_unweighted = "\"C:\Users\sware\swareaug12\\aug5\Latest version2\Latest version\make_aggregated_supervisor.py\" -d "
  string_weighted = "\"C:\Users\sware\swareaug12\\aug5\Latest version2\Latest version\make_tau_abstracted_supervisor.py\" -d "
  for i, aut in enumerate(automata):
    if i != 0:
      string_unweighted += ","
      string_weighted += ","
    string_unweighted += aut.name + ".cfg"
    string_weighted += aut.name + ".cfg"
  string_unweighted += " req.cfg "
  string_weighted += " req.cfg {} sup.cfg"
  handle = file(output_dir + "\\unweighted\\cranetau.bat", 'w')
  handle.write(string_unweighted + " steps")
  handle.close()
  handle = file(output_dir + "\\unweightedtau\\cranetau.bat", 'w')
  handle.write(string_unweighted + " steps")
  handle.close()
  handle = file(output_dir + "\\unweighted\\cranetau_full_track.bat", 'w')
  handle.write(string_unweighted + " steps_full_track")
  handle.close()
  handle = file(output_dir + "\\unweighted\\cranetau_segments.bat", 'w')
  handle.write(string_unweighted + " steps_segments")
  handle.close()
  handle = file(output_dir + "\\weighted\\cranetau.bat", 'w')
  handle.write(string_unweighted)
  handle.close()
  #output_crane_order(automata, output_dir)
  output_crane_order_compose_segments(automata, output_dir)
  output_crane_order_compose_full_track(automata, output_dir)

if __name__ == '__main__':
    import sys
    num_cranes = int(sys.argv[1])
    num_slots = int(sys.argv[2])
    init_crane = sys.argv[3]
    init_crane = init_crane.split(":")
    for i, crane in enumerate(init_crane):
      slot, side = crane.split(",")
      init_crane[i] = (int(slot), int(side))
    #num_containers = int(sys.argv[4])
    #make_system2(num_cranes, num_slots, init_crane, num_containers)
    num_incoming = int(sys.argv[4])
    num_outgoing = int(sys.argv[5])
    incomeslot = sys.argv[6]
    slot, side = incomeslot.split(",")
    incomeslot = (int(slot), int(side))
    outgoslot = sys.argv[7]
    slot, side = outgoslot.split(",")
    outgoslot = (int(slot), int(side))
    make_system(num_cranes, num_slots, init_crane, num_incoming, num_outgoing, incomeslot, outgoslot)