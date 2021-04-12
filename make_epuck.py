import random
import os

from automata.frontend import save_automaton
from automata.weighted_frontend import save_weighted_automaton
from automata.tau_abstraction import remove_always_disabled_events
from automata import weighted_structure, collection

def get_event(coll, name):
  if name in coll.events:
    return coll.events[name]
  else:
    return coll.make_event(name, True, True, False)
    
def epuck_slot(x, y, init, marked):
  for 