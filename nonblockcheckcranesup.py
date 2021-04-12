from automata import frontend

directory = "cranes\\unweighted\\"
string = ""
for i in range(61):
  if i != 0:
    string += ","
  string += directory + "sup" + str(i+1) + ".cfg"
frontend.make_nonconflicting_check(string, "False")