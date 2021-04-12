import heapq

def add_tup_to_heap(tup, heap_num, crane, heap):
  time = int(tup[0])
  if tup[1] != "MoveStart":
    time -= 1
  heapq.heappush(heap, (time, heap_num, crane, tup[1:]))

with open('result.txt', 'r') as handle:
  pick = [(44, 1), (79, 2), (42, 1), (97, 1), (15, 1), (3, 1), (11, 1), \
           (12, 1), (51, 2), (29, 2), (30, 1), (30, 1), (30, 1), (30, 1), \
           (30, 1), (30, 1), (30, 1), (30, 1), (30, 1), (30, 1)]
  drop = [(90, 1), (90, 1), (90, 1), (90, 1), (90, 1), (90, 1), (90, 1), \
           (90, 1), (90, 1), (90, 1), (32, 2), (61, 1), (87, 1), (44, 2), \
           (52, 2), (51, 1), (110, 2), (13, 1), (106, 1), (36, 2)] 
  content = handle.readlines()
  crane_orders = [[],[],[]]
  crane = None
  for line in content:
    if line.startswith("Crane:"):
      crane = int(line[6])
      continue
    if crane == None:
      continue
    if line.startswith("Time"):
      continue
    if len(line.split()) != 4:
      continue
    crane_orders[crane].append(line.split())
  timeheap = []
  crane_pick_up = [True, True, True]
  heapcount = 0
  
  output_handle = file("chong_path.cfg", 'w')
  output_handle.write("[automaton]\n")
  alphabet = []
  for c in range(1, 4):
    for s in range(1, 121):      
      if s != 1:
        event = "C" + str(c) + "-move-" + str(s) + "-" + str(s-1)
        alphabet.append(event)
      if s != 120:
        event = "C" + str(c) + "-move-" + str(s) + "-" + str(s+1)
        alphabet.append(event)
    for r in range(len(pick)):
      req = str(r+1)
      sl, si = pick[r]
      event = "C" + str(c) + "-pick-" + str(sl) + "-" + str(si) + "-" + req
      alphabet.append(event)
      sl, si = drop[r]
      event = "C" + str(c) + "-drop-" + str(sl) + "-" + str(si) + "-" + req
      alphabet.append(event)
  output_handle.write("alphabet = ")
  for i, evt in enumerate(alphabet):
    if i != 0:
      output_handle.write(", ")
    output_handle.write(evt)
  output_handle.write("\n")
  output_handle.write("controllable = ")
  for i, evt in enumerate(alphabet):
    if i != 0:
      output_handle.write(", ")
    output_handle.write(evt)
  output_handle.write("\n")
  output_handle.write("observable = ")
  for i, evt in enumerate(alphabet):
    if i != 0:
      output_handle.write(", ")
    output_handle.write(evt)
  output_handle.write("\n")
  heap_num = 0
  crane_order = []
  for crane, tuplist in enumerate(crane_orders):
    add_tup_to_heap(tuplist[0], heap_num, crane, timeheap)
    heap_num += 1
    crane_order.append(tuplist[0][1])
    tuplist.pop(0)
  crane_location = [1, 60, 120]
  time = -1
  state = 1
  transitions = []
  while timeheap:
    tup = heapq.heappop(timeheap)
    time, throw, crane, command = tup
    tuplist = crane_orders[crane]
    if command[0] == "MoveStart":      
      target_location = int(tuplist[0][3])
      direction = target_location - int(command[2])
      if direction == 0:
        print tup
        tuplist.pop(0)
        if tuplist:
          add_tup_to_heap(tuplist[0], heap_num, crane, timeheap)
          crane_order[crane] = (tuplist[0][1])
          heap_num += 1
          tuplist.pop(0)
      elif direction < 0:
        if int(command[2])-1 not in crane_location:
          heapq.heappush(timeheap, (time + 1, heap_num, crane, (command[0], command[1], str(int(command[2]) - 1))))
          heap_num += 1
          event = "C" + str(crane+1) + "-move-" + command[2] + "-" + str(int(command[2])-1)
          crane_location[crane] = int(command[2])-1
          transitions.append("(" + str(state) + ", " + str(state+1) + ", " + event + ")")
          state += 1
        else:
          print tup
          target_location = int(command[2])-1
          for i in range(len(crane_location)):
            if target_location == crane_location[i]:
              break
          if crane_order[i] != "MoveStart":
            time += 1
          heapq.heappush(timeheap, (time, heap_num, crane, command))
          heap_num += 1
      else:
        if int(command[2])+1 not in crane_location:
          heapq.heappush(timeheap, (time + 1, heap_num, crane, (command[0], command[1], str(int(command[2]) + 1))))
          heap_num += 1
          event = "C" + str(crane+1) + "-move-" + command[2] + "-" + str(int(command[2])+1)
          crane_location[crane] = int(command[2])+1
          transitions.append("(" + str(state) + ", " + str(state+1) + ", " + event + ")")
          state += 1
        else:
          print tup
          target_location = int(command[2])+1
          for i in range(len(crane_location)):
            if target_location == crane_location[i]:
              break
          if crane_order[i] != "MoveStart":
            time += 1
          heapq.heappush(timeheap, (time, heap_num, crane, command))
          heap_num += 1
    elif command[0] == "MoveStop":
      print "shouldn't happen"
      assert(False)
    elif command[0] == "LoadEnd":
      if tuplist:
        add_tup_to_heap(tuplist[0], heap_num, crane, timeheap)
        crane_order[crane] = (tuplist[0][1])
        heap_num += 1
        tuplist.pop(0)
      order = int(command[1])
      slot, side = pick[order-1]
      event = "C" + str(crane+1) + "-pick-" + str(slot) + "-" + str(side) + "-" + str(order)
      transitions.append("(" + str(state) + ", " + str(state+1) + ", " + event + ")")
      state += 1
    elif command[0] == "UnloadEnd":
      if tuplist:
        add_tup_to_heap(tuplist[0], heap_num, crane, timeheap)
        crane_order[crane] = (tuplist[0][1])
        heap_num += 1
        tuplist.pop(0)
      order = int(command[1])
      slot, side = drop[order-1]
      event = "C" + str(crane+1) + "-drop-" + str(slot) + "-" + str(side) + "-" + str(order)
      transitions.append("(" + str(state) + ", " + str(state+1) + ", " + event + ")")
      state += 1
  output_handle.write("states = ")
  for s in range(1, state + 1):
    if s != 1:
      output_handle.write(", ")
    output_handle.write(str(s))
  output_handle.write("\ninitial-state = 1\n")
  output_handle.write("marker-states = " + str(state) + "\n")
  output_handle.write("transitions = ")
  for t, transition in enumerate(transitions):
    if t != 0:
      output_handle.write(", ")
    output_handle.write(transition)
  output_handle.close()
