from automata import frontend, weighted_frontend, collection, tau_abstraction

def make_robot(index, last):
  string = "[weighted-automaton]\n"
  string += "states = 1, 2\n"
  functions = ["-pick-", "-drop-"]
  eventlist = {}
  locations = ["P" + str(index) + "1", "P" + str(index) + "2"]
  alphabet = ""
  if index == 1:
    locations.append("C")
  else:
    locations.append("B" + str(index - 1))
  if last:
    locations.append("P" + str(index) + "3")
  else:
    locations.append("B" + str(index))
  first = True
  robot = "R" + str(index)
  for func in functions:
    eventlist[func] = []
    for loc in locations:
      if not first:
        alphabet += ","
      first = False
      event = robot + func + loc
      alphabet += event
      eventlist[func].append(event)
  string += "alphabet = " + alphabet + "\n"
  string += "controllable = " + alphabet + "\n"
  string += "observable = " + alphabet + "\n"
  transitions = ""
  first = True
  for func in functions:
    pred = None
    succ = None
    if "-pick-" == func:
      pred, succ = "1", "2"
    else:
      pred, succ = "2", "1"
    for event in eventlist[func]:
      if not first:
        transitions += ","
      first = False
      transitions += "("+ pred + ", " + succ + ", " + event + ",1)"
  string += "transitions = " + transitions + "\n"
  string += "marker-states = 1\n"
  string += "initial-state = 1\n"
  return string
  
def make_buffer(index):
  string = "[weighted-automaton]\n"
  string += "states = 1, 2, 3, 4\n"
  functions = ["-pick-", "-drop-"]
  robots = ["R" + str(index), "R" + str(index + 1)]
  eventlist = {}
  buf = "B" + str(index)
  alphabet = ""
  first = True
  robot = "R" + str(index)
  for func in functions:
    eventlist[func] = []
    for rob in robots:
      if not first:
        alphabet += ","
      first = False
      event = rob + func + buf
      alphabet += event
      eventlist[func].append(event)
  string += "alphabet = " + alphabet + "\n"
  string += "controllable = " + alphabet + "\n"
  string += "observable = " + alphabet + "\n"
  transitions = ""
  first = True
  for func in functions:
    pred = None
    succ = None
    if "-pick-" == func:
      pred, succ = "2", "1"
    else:
      pred, succ = "1", "2"
    for event in eventlist[func]:
      if "pick" in event and ("R" + str(index)) in event:
        pred, succ = "3", "1"
      elif "drop" in event and ("R" + str(index)) in event:
        pred, succ = "1", "2"
      elif "pick" in event and ("R" + str(index+1)) in event:
        pred, succ = "2", "1"
      elif "drop" in event and ("R" + str(index+1)) in event:
        pred, succ = "1", "3"
      if not first:
        transitions += ","
      first = False
      transitions += "("+ pred + ", " + succ + ", " + event + ",1)"
  string += "transitions = " + transitions + "\n"
  string += "marker-states = 1\n"
  string += "initial-state = 1\n"
  return string
  
def make_proc(index, procnum):
  string = "[weighted-automaton]\n"
  string += "states = 1, 2, 3\n"
  rob = "R" + str(index)
  proc = "P" + str(index) + str(procnum)
  pick = rob + "-pick-" + proc
  drop = rob + "-drop-" + proc
  process = "Proc" + str(index) + str(procnum)
  alphabet = drop +  ", " + process + ", " + pick
  string += "alphabet = " + alphabet + "\n"
  string += "controllable = " + alphabet + "\n"
  string += "observable = " + alphabet + "\n"
  transitions = "(1, 2, " + drop + ",1), (2, 3, " + process + ",4), (3, 1, " + pick + ",1)"
  string += "transitions = " + transitions + "\n"
  string += "marker-states = 1\n"
  string += "initial-state = 1\n"
  return string
  
def make_H(pick, drop):
  string = "[weighted-automaton]\n"
  string += "states = 1, 2\n"
  alphabet = drop +  ", " + pick
  string += "alphabet = " + alphabet + "\n"
  string += "controllable = " + alphabet + "\n"
  string += "observable = " + alphabet + "\n"
  transitions = "(1, 2, " + pick + ",1), (2, 1, " + drop + ",1)"
  string += "transitions = " + transitions + "\n"
  string += "marker-states = 1\n"
  string += "initial-state = 1\n"
  return string
  
def make_job(num):
  string = "[weighted-automaton]\n"
  states = "1"
  for i in range(2, num + 2):
    states += ", " + str(i)
  states += "\n"
  string += "states = " + states
  event = "R1-pick-C"
  string += "alphabet = " + event + "\n"
  string += "controllable = " + event + "\n"
  string += "observable = " + event + "\n"
  transitions = ""
  first = True
  for i in range(1, num + 1):
    if not first:
      transitions += ", "
    first = False
    transitions += "(" + str(i) + ", " + str(i + 1) + ", " + event + ",1)" 
  string += "transitions = " + transitions + "\n"
  string += "marker-states = " + str(num + 1) + "\n"
  string += "initial-state = 1\n"
  return string

def make_clusters(number):
  directory = "clustertool_weighted\\"
  if not os.path.exists(directory):
    os.makedirs(directory)
  filenames = []
  steps = []
  for i in range(1, number + 1):
    composition = ""
    stnum = str(i)
    name = "TR" + stnum + ".cfg"
    handle = file(directory + name, 'w')
    filenames.append(name)
    composition += name[:-4]
    handle.write(make_robot(i, i == number))
    handle.close()
    name = "TProc" + stnum + "1.cfg"
    handle = file(directory + name, 'w')
    filenames.append(name)
    composition += "," + name[:-4]
    handle.write(make_proc(i, 1))
    handle.close()
    name = "TProc" + stnum + "2.cfg"
    handle = file(directory + name, 'w')
    filenames.append(name)
    composition += "," + name[:-4]
    
    handle.write(make_proc(i, 2))
    handle.close()
    if i == number:
      name = "TProc" + stnum + "3.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_proc(i, 3))
      handle.close()
    else:
      name = "TB" + stnum + ".cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_buffer(i))
      handle.close()
    if i == 1:
      name = "H" + stnum + "1.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R1-pick-C", "R1-drop-P11"))
      handle.close()
      name = "H" + stnum + "4.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R1-pick-P12", "R1-drop-C"))
      handle.close()
    else:
      name = "H" + stnum + "1.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R"+stnum + "-pick-B" + str(i-1), "R" + stnum + "-drop-P" + stnum + "1"))
      handle.close()
      suffix = "2" if i != number else "3"
      name = "H" + stnum + "4.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R"+stnum + "-pick-P" + stnum + suffix, "R" + stnum + "-drop-B" + str(i-1)))
      handle.close()
    if i == number:
      name = "H" + stnum + "2.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R" + stnum + "-pick-P" + stnum + "1", "R" + stnum + "-drop-P" + stnum + "2"))
      handle.close()
      name = "H" + stnum + "3.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R" + stnum + "-pick-P" + stnum + "2", "R" + stnum + "-drop-P" + stnum + "3"))
      handle.close()
    else:
      name = "H" + stnum + "2.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R"+stnum + "-pick-P" + stnum + "1", "R" + stnum + "-drop-B" + stnum))
      handle.close()   
      name = "H" + stnum + "3.cfg"
      handle = file(directory + name, 'w')
      filenames.append(name)
      composition += "," + name[:-4]
      handle.write(make_H("R"+stnum + "-pick-B" + stnum, "R" + stnum + "-drop-P" + stnum + "2"))
      handle.close()
    composition += "  sup" + stnum
    composition += " abs" + stnum + " True "
    if i == 1:
      composition += "R1-pick-C,R2-drop-B1"
    elif i == number:
      composition += "R" + stnum + "-pick-B" + str(i-1)
    else:
      composition += "R" + stnum + "-pick-B" + str(i-1) + ",R" + str(i+1) + "-drop-B" + stnum
    steps.append(composition)
  composition = "abs1,abs2  sup" + str(number + 1) + " abs" + str(number + 1) + " False "
  steps.append(composition)
  for i in range(3, number + 1):
    composition = "abs" + str(i) + ",abs" + str(number + i - 2) + "  sup" + str(i + number - 1) + " abs" + str(i + number - 1) + " False "
    steps.append(composition)
  string = "\"C:\Users\sware\swareaug12\\aug5\Latest version2\Latest version\make_aggregated_time_optimal_supervisor.py\" -d "
  string += name
  for name in filenames:
    string += "," + name
  string += " steps"
  handle = file(directory + "clustertau.bat", 'w')
  handle.write(string)
  handle.close()
  #handle = file(directory + "steps", 'w')
  #for line in steps:
  #  handle.write(line + "\n")
  #handle.close()

if __name__ == '__main__':
    import sys, os
    make_clusters(int(sys.argv[1]))
    #for i in range(4, 5):
    #  for j in range(1, 41, 1):
    #    make_clusters(i, j)
    #    os.system("clustertau.bat ")