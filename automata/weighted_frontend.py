#
# $Id: weighted_frontend.py 726 2010-04-08 10:40:22Z hat $
#
"""
Frontend functions of weighted automata commands.

File format of weighted automata::

    [weighted-automaton]
    initial-state = 0
    states = 0, 1, 2, 3, 4
    alphabet = a, b, c, d
    controllable = a, b
    marker-states = 3, 4
    transitions = (0,1,a,1), (1,2,b,2), (2,0,d,1), (2,3,c,1), (1,4,d,6)

The differences compared to an unweighted automaton are the use of a different
section header, and the addition of a fourth value to each transition, the
weight.

"""
import automata, collections
from automata import abstraction, algorithm, collection, common, \
                     compute_weight, conversion, frontend, product, \
                     supervisor, taskresource, weighted_projection, \
                     weighted_equality, weighted_product, maxplus, \
                     weighted_structure, weighted_supervisor, tau_abstraction, \
                     tau_abstraction2, observer_property, walkthrough
from SimonStuff import compresstrace #incrementalimprovement
from collections import defaultdict
from time import time


# {{{ def load_weighted_automaton(collect, fname, test_std, needs_m-states):
def load_weighted_automaton(collect, fname, test_standardized,
                            needs_marker_states):
    """
    Load a weighted automaton file.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the weighted automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded weighted automaton.
    @rtype:  L{Weighted Automaton}
    """
    flags = 0
    if test_standardized:
        flags = flags | frontend.TEST_STANDARDIZED
    if needs_marker_states:
        flags = flags | frontend.MUST_HAVE_MARKER_STATE

    return frontend.load_automaton_file(collect, fname,
                            weighted_structure.WeightedAutomatonLoader, flags)

# }}}
# {{{ def load_weighted_automata(collect, fnames):
def load_weighted_automata(collect, fnames, test_standardized,
                           needs_marker_states):
    """
    Load many automata files.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fnames: Comma-seperated list of automata filenames.
    @type  fnames: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automata.
    @rtype:  A C{list} of L{WeightedAutomaton}
    """
    aut_list = []
    for fname in fnames.split(','):
        if len(fname) > 0:
            aut_list.append(load_weighted_automaton(collect, fname,
                                        test_standardized, needs_marker_states))

    return aut_list

# }}}
# {{{ def save_weighted_automaton(aut, title, fname):
def save_weighted_automaton(aut, title, fname):
    """
    Save weighted automaton L{aut} in file L{fname}.

    @param aut: Automaton to save.
    @type  aut: L{WeightedAutomaton}

    @param title: If existing, an additional text to output. If it contains
                  C{%s}, string formatting is used to insert the filename at
                  that point in the text.
    @type  title: Either a C{str} or C{None}

    @param fname: Filename to write the automaton to.
    @type  fname: C{str}
    """
    assert isinstance(aut, weighted_structure.WeightedAutomaton)

    frontend.make_backup_file(fname)
    weighted_structure.save_automaton(aut, fname, make_backup = False)

    if title is not None:
        if title.find("%s") >= 0:
            common.print_line(title % (fname,))
        else:
            common.print_line(title)
# }}}
# {{{ def make_weighted_dot(aut_fname, dot_fname)
def make_weighted_dot(aut_fname, dot_fname):
    """
    Convert automaton to Graphviz format.

    @param aut_fname: Filename of the automaton to convert.
    @type  aut_fname: C{str}

    @param dot_fname: Output filename for the Graphviz data.
    @type  dot_fname: C{str}
    """
    coll = collection.Collection()
    aut = load_weighted_automaton(coll, aut_fname, False, False)

    frontend.make_backup_file(dot_fname)

    dot_handle = open(dot_fname, 'w')
    dot_handle.write(aut.to_dot())
    dot_handle.close()

# }}}
# {{{ def make_get_weighted_size(aut_fname)
def make_get_weighted_size(aut_fname):
    """
    Display size of the weighted automaton.

    @param aut_fname: Filename of the weighted automaton.
    @type  aut_fname: C{str}
    """
    common.print_line("Started calculating size (version %s)"
                        % automata.version)
    coll = collection.Collection()
    aut = load_weighted_automaton(coll, aut_fname, False, False)

    print str(aut)

# }}}
# {{{ def make_weighted_product(aut_fnames, result_fname):
def make_weighted_product(aut_fnames, result_fname):
    """
    Multiply the weighthed automata in the L{aut_fnames} list, and write the
    result to L{result_fname}.

    @param aut_fnames: Comma-seperated list of weighted automata filenames.
    @type  aut_fnames: C{str}

    @param result_fname: Filename for writing the resulting weighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started weighted product computations (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut_list = load_weighted_automata(coll, aut_fnames, False, False)
    result = weighted_product.n_ary_weighted_product(aut_list,
                                                 algorithm.SUM_EDGE_WEIGHTS,
                                                 True, True)

    frontend.dump_stats("Computed product", result)
    save_weighted_automaton(result, "Product is saved in %s\n", result_fname)

# }}}
# {{{ def check_weighted_equality(aut_fname1, aut_fname2):
def check_weighted_equality(aut_fname1, aut_fname2):
    """
    Compare both weighted automata, and return whether they are the same.

    @param aut_fname1: First weighted automaton file to use.
    @type  aut_fname1: C{str}

    @param aut_fname2: Second weighted automaton file to use.
    @type  aut_fname2: C{str}
    """
    common.print_line("Started weigthed equality test (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut1 = load_weighted_automaton(coll, aut_fname1, False, False)
    aut2 = load_weighted_automaton(coll, aut_fname2, False, False)
    result = weighted_equality.check_weighted_equality(aut1, aut2)

    if result:
        print "weighted equality check: HOLDS"
    else:
        print "weighted equality check: CONFLICT FOUND"

    return result

# }}}
# {{{ def make_remove_weighted(aut_fname, result_fname):
def make_remove_weighted(waut_fname, result_fname):
    """
    Remove the weights of weighted automaton L{waut_fname}, and write the
    result to L{result_fname}.

    @param waut_fname: Filename of weighted automaton to load.
    @type  waut_fname: C{str}

    @param result_fname: Filename of the resulting unweighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started removing weights (version %s)"
                        % automata.version)
    coll = collection.Collection()

    waut = load_weighted_automaton(coll, waut_fname, False, False)
    aut = conversion.remove_weights(waut)

    frontend.save_automaton(aut, "Result is saved in %s\n", result_fname)

# }}}
# {{{ def make_weighted_projection(aut_name, evt_names, result_fname):
def make_weighted_projection(aut_name, evt_names, result_fname):
    """
    Perform projection over a weighted automaton.

    @param aut_name: Filename of the automaton to project.
    @type  aut_name: L{WeightedAutomaton}

    @param evt_names: Comma seperated list of event names to preserve.
    @type  evt_names: C{str}

    @param result_fname: Filename for writing the resulting weighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started weighted projection computation (version %s)"
                        % automata.version)
    coll = collection.Collection()

    waut = load_weighted_automaton(coll, aut_name, False, False)
    events = frontend.get_events(coll, evt_names)

    waut2 = weighted_projection.weighted_projection(waut, events)

    frontend.dump_stats("Computed weighted projection", waut2)
    save_weighted_automaton(waut2, "Projected automaton is saved in %s",
                            result_fname)

# }}} def make_weighted_projection(aut_name, evt_names, result_fname):
# {{{ def make_reset_weighted(aut_fname, result_fname):
def make_reset_weighted(aut_fname, result_fname):
    """
    Reset the weights in weighted automaton L{aut_fname} to 0, and write the
    result to L{result_fname}.

    @param aut_fname: Filename of weighted automaton to load.
    @type  aut_fname: C{str}

    @param result_fname: Filename for writing the resulting weighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started resetting weights (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut = load_weighted_automaton(coll, aut_fname, False, False)
    aut.reset_weight(0)

    save_weighted_automaton(aut, "Result is saved in %s\n", result_fname)

# }}}

# {{{ make_time_optimal_supervisor(comp_names, req_names, evt_pairs, sup_name)
def make_time_optimal_supervisor(comp_names, req_names, evt_pairs, sup_name):
    """
    Compute a time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of C{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{List} of C{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of resulting supervisor (unweighted automaton).
    @type  sup_name: C{str}
    """
    common.print_line("Started time optimal supervisor computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
    result = compute_weight.compute_time_optimal_supervisor(comp_list,
                                                        req_list, evt_pairs)

    if result is None:
        common.print_line("Time optimal supervisor cannot be computed.")
        return
    else:
        sup, min_weight = result
        common.print_line("Minimum makespan is %d" % min_weight)
        frontend.dump_stats("Computed time optimal supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)

# }}}

def make_heuristic_time_optimal_supervisor(plant_fnames, durations, evt_pairs, comp_mut_ex, steps):
    """
    Perform aggregated sythesis abstraction.

    @param steps: A list of tuples representing the steps of aggregated synthesis.
                  A tuple is comprised of a comma seperated list of automata names
                  to be composed, and a name
                  for the intermediate abstraction result
                  (None if no abstraction result is required).
    @type  aut_fnames: Tuple

    """
    sttime = time()
    common.print_line("Started aggregated synthesis abstraction computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()

    model_plants = load_weighted_automata(coll, plant_fnames, True, False)
    result = taskresource.compute_custom_eventdata_extended_ware(comp_list, durations, evt_pairs, comp_mut_ex)
    handle = file("profiling", 'w')
    original_auts = []
    for count, (plant_names, abs_name) in enumerate(steps):
      handle.write(str(count) + ":\n")
      plant_set = set()
      spec_set = set()
      for name in plant_names.split(","):
        plant_set.add(name.strip())
      to_compose_plants = [plant for plant in model_plants if plant.name in plant_set]
      model_plants = [plant for plant in model_plants if plant.name not in plant_set]
      print "num auts:"
      print len(model_plants)
      print "to_compose_plants:" + str(to_compose_plants)
      to_compose_plants[0].alphabet.add(tau)
      temp = to_compose_plants
      synctime = -time()
      composition = [tau_abstraction.synchronousproduct(to_compose_plants,0)]
      synctime += time()
      original_auts.append(composition.copy())
      handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(composition.get_num_states()) + "\n")      
      synctime = -time()
      to_compose_plants[0].save_as_dot("currentcomp" + str(count) + ".dot")
      composition.trim(True, True)
      synctime += time()
      handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(sup.get_num_states()) + "\n")
      global_alphabet = set()
      global_alphabet.update(*[aut.alphabet for aut in model_plants])
      to_keep = composition.alphabet.intersection(global_alphabet)
      for aut in model_plants:
        print aut.name 
      print "to_keep: " + str(to_keep)
      #for event in sup.alphabet:
      #  if event.name == "tau":
      #    to_keep.add(event)
      abstime = -time()
      abstracted = \
        tau_abstraction.subsetconstruction(composition, composition.alphabet.difference(to_keep), 0)
      abstracted = abstraction.abstraction_refined(sup, to_keep)
      #abstracted = abstraction.abstraction(sup, to_keep)
      abstracted.name = abs_name
      abstime += time()
      handle.write("abstime: " + str(abstime) + "\t\tstates: " + str(abstracted.get_num_states()) + "\n")
      model_plants.append(abstracted)
      print str(time() - sttime)
      
    while True:
      return restrictpath(get_greedy_time_optimal_sup_vector(comp_list[0], eventdata, len(cliques)))
      path = model_plants[0]

def make_tau_abstracted_greedy_supervisor(comp_names, req_names, comp_mut_ex, evt_pairs, sup_name):
    
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)
    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
    result = tau_abstraction.tau_abstracted_greedy_supervisor_not_weighted(comp_list, req_list,
                                                               comp_mut_ex, evt_pairs, sup_name + "res")
    if result is None:
        common.print_line("Tau abstracted greedy supervisor cannot be computed.")
        return
    else:
        sup = result
        sup.save_as_dot("tau_supervisor.dot")
        frontend.dump_stats("Computed tau abstracted greedy supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)
    

# def make_tau_abstraction(comp_names, req_names, evt_pairs):
    # common.print_line("Started making tau abstractions")
    
    # coll = collection.Collection()
    # comp_list = load_weighted_automata(coll, comp_names, False, True)
    # req_list  = frontend.load_automata(coll, req_names, False, True)
    # evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
    
    # result = tau_abstraction.do_tau_abstraction(comp_list, req_list, evt_pairs)
    # if result == None:
        # common.print_line("Something went wrong. No result")
    # for comp in result:
        # comp.save_as_dot("tau_abstracted_" + comp.name + ".dot")
        # save_weighted_automaton(comp, "Modified automaton saved in: %s", "tau_abstracted_" + comp.name + ".cfg")
    
# {{{ def make_optimal_weighted_supervisor(comp_name, req_name, sup_name):
def make_optimal_weighted_supervisor(comp_name, req_name, sup_name):
    """
    Compute a optimal weighted supervisor.

    @param comp_name: Available component (weighted automaton).
    @type  comp_name: C{str}

    @param req_name: Available requirement (unweighted automaton).
    @type  req_name: C{str}

    @param sup_name: Name of resulting supervisor (unweighted automaton).
    @type  sup_name: C{str}
    """
    common.print_line("Started optimal weighted supervisor computation "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp = load_weighted_automaton(coll, comp_name, False, True)
    req  = frontend.load_automaton(coll, req_name,  False, True)

    sup = weighted_supervisor.compute_optimal_weighted_supervisor(comp, req)
    if sup is None:
        common.print_line("Optimal weighted supervisor cannot be computed.")
        return
    else:
        frontend.dump_stats("Computed optimal weighted supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)

# }}}
# {{{ def make_weighted_supervisor(comp_name, req_name, sup_name):
def make_weighted_supervisor(comp_name, req_name, sup_name):
    """
    Compute a weighted supervisor.

    @param comp_name: Available component (weighted automaton).
    @type  comp_name: C{str}

    @param req_name: Available requirement (unweighted automaton).
    @type  req_name: C{str}

    @param sup_name: Name of resulting supervisor (unweighted automaton).
    @type  sup_name: C{str}
    """
    common.print_line("Started weighted supervisor computation "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp = load_weighted_automaton(coll, comp_name, False, True)
    req  = frontend.load_automaton(coll, req_name,  False, True)

    sup = weighted_supervisor.compute_weighted_supervisor(comp, req)
    if sup is None:
        common.print_line("Weighted supervisor cannot be computed.")
        return
    else:
        frontend.dump_stats("Computed weighted supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)

# }}}

# {{{ make_greedy_time_optimal_supervisor(comp_names, req_names, evt_pairs):
def make_greedy_time_optimal_supervisor(comp_names, req_names, evt_pairs,
                                        sup_name,L):
    """
    Compute a greedy time optimal supervisor. - MARIJN FIXED THIS

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.compute_greedy_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        eventdata, heap_len, 0, 0,L)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Sub-optimal makespan is %s" % biggest)

    wsup = weighted_supervisor.reduce_automaton(wsup, wmap, eventdata,
                                                heap_len)

    frontend.dump_stats("Computed weighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)

# }}}
def make_greedy_time_optimal_supervisor_correctly(comp_names, req_names, evt_pairs,
                                        sup_name,L):
    """
    Compute a greedy time optimal supervisor. - MARIJN FIXED THIS

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.compute_greedy_time_optimal_supervisor_correctly(
                                                        comp_list, req_list,
                                                        eventdata, heap_len, L)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Sub-optimal makespan is %s" % biggest)

    wsup = weighted_supervisor.reduce_automaton_greedy_correctly(wsup, wmap, eventdata,
                                                heap_len, L)

    frontend.dump_stats("Computed weighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)
    wsup.save_as_dot("GREEDY_DOT.dot")


def make_greedy_time_optimal_supervisor_row_vectors(comp_names, req_names, evt_pairs,
                                        sup_name, row_vectors, operator):
    """
    Compute a greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.compute_greedy_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        eventdata, heap_len, row_vectors, operator)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Sub-optimal makespan is %s" % biggest)

    wsup = weighted_supervisor.reduce_automaton_row_vecors(wsup, wmap, eventdata,
                                                heap_len, row_vectors)

    frontend.dump_stats("Computed weighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)

# }}}


def compute_shortest_path(comp_names, req_names, evt_pairs):
    """
    Compute shortest path with A* algorithm and type 1 requirements.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Name of the requirement automata (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}
    """
    common.print_line('Started shortest path type 1 computation (version %s)'
                      % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
    compute_weight.compute_shortest_path(comp_list, req_list, evt_pairs)


# {{{ def make_minimal_weighted_supervisor(plant, req, new_fname):
def make_minimal_weighted_supervisor(plant, req, new_fname):
    """
    Compute deterministic weighted supervisor for non-deterministic plant and
    deterministic requirements.

    @param plant: Filename of the non-deterministic weighted (but not
                  minimally) automaton.
    @type  plant: C{str}

    @param req: Filename of the requirements as deterministic non-weighted
                automaton.
    @type  req: C{str}

    @param new_fname: Filename of the created deterministic controller.
    @type  new_fname: C{str}
    """
    common.print_line("Started minimal weighted supervisor computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()

    plant_waut = load_weighted_automaton(coll, plant, False, True)
    req_aut = frontend.load_automaton(coll, req, False, True)
    wsup = compute_weight.compute_weighted_supremal(plant_waut, req_aut)
    if wsup is None:
        new_aut = None
    else:
        observables = set([evt for evt in plant.events.itervalues()
                           if evt.observable])
        check_marking_aware(wsup, observables)
        wsup2 = weighted_projection.weighted_projection(wsup, observables)
        new_aut = compute_weight.minimal_weight_deterministic_controllable(
                                wsup2)
    if new_aut is None:
        common.print_line("No minimal weight controller found!")

    else:
        unw_plant = conversion.remove_weights(plant_waut)
        prod = product.n_ary_unweighted_product([unw_plant, new_aut[0]])
        result = supervisor.unweighted_determinization(prod)

        common.print_line("Minimum weight is %s" % new_aut[1])
        frontend.save_automaton(result,
                            "Saving minimal weight controller in %s", new_fname)

def check_marking_aware(waut, events):
    """
    Verify that all incoming edges to marker states use events from the
    L{events} set.

    @param waut: Weighted automaton.
    @type  waut: L{WeightedAutomaton}

    @param events: Events that must be used at incoming edges of marker states.
    @type  events: A C{set} of L{Event}
    """
    common.print_line("Started marking aware computations (version %s)"
                        % automata.version)
    warnings = []
    for state in waut.get_states():
        if state.marked:
            labels = set(edge.label for edge in state.get_incoming())
            for evt in labels:
                if evt not in events:
                    warnings.append("\tevent %s to state %d is not observable"
                                    % (evt.name, state.number))
    if len(warnings) > 0:
        common.print_line(["Warning: Plant is not marking aware"])
        common.print_line(warnings)

# }}}

def generate_task_resource_use(comp_names, req_names, text_path, plots,
                               usefname):
    """
    Generate a task/resource usage picture for path L{text_path} with
    components L{comp_names} and requirements L{req_names}. Output data in
    L{usefname}.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param text_path: Sequence of events on the path (a sequence of event
                      names, comma or white-space seperated).
    @type  text_path: C{string}

    @param plots: Names of automata to plot, if specified.
    @type  plots: C{str}

    @param usefname: Filename for writing task/resource use to.
    @type  usefname: C{str}

    @note: The L{comp_names} and L{req_names} are only used to compute the
           shape of the pieces at the heap. Therefore, for type 1 requirements
           (where the requirements automata are not used in that calculation),
           L{req_names} should be left empty.

    """
    common.print_line('Started generation of task/resource use (version %s)'
                      % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    plots = set(plots.replace(',', ' ').split())
    if plots: # Non-empty set.
        plot_auts = set(aut
                        for aut in comp_list + req_list if aut.name in plots)
    else:
        plot_auts = None # All automata should be plotted.

    uses = compute_weight.generate_task_resource_use(comp_list, req_list,
                                                     plot_auts, text_path)

    if usefname:
        handle = open(usefname, 'w')
        for use in uses:
            handle.write('%s\t%s\t%s\t%s\n' % use)
        handle.close()
    else:
        for use in uses:
            print '%s\t%s\t%s\t%s' % use

def load_unweight_automaton(collect, fname, test_standardized,
                            needs_marker_states):
    """
    Load a weighted automaton file.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the weighted automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded weighted automaton.
    @rtype:  L{Weighted Automaton}
    """
    flags = 0
    if test_standardized:
        flags = flags | frontend.TEST_STANDARDIZED
    if needs_marker_states:
        flags = flags | frontend.MUST_HAVE_MARKER_STATE

    return frontend.load_automaton_file(collect, fname,
                            weighted_structure.WeightedAutomatonLoader, flags)
# }}}

def make_unweight_time_optimal_supervisor(comp_names, req_names, evt_pairs,
                                        sup_name):
    """
    Compute a non weighted time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started time unweight optimal supervisor computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_unweight_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)
    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = compute_weight.compute_unweight_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        evt_pairs)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup = result
    #one = maxplus.make_rowmat(0, heap_len)
    #one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    #biggest = one.get_scalar()
    #common.print_line("Sub-optimal makespan is %s" % biggest)

    #wsup = weighted_supervisor.reduce_automaton(wsup, wmap, eventdata,
    #                                            heap_len)

    frontend.dump_stats("Computed unweighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)

# }}}

def load_unweight_automata(collect, fnames, test_standardized,
                           needs_marker_states):
    """
    Load many automata files.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fnames: Comma-seperated list of automata filenames.
    @type  fnames: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automata.
    @rtype:  A C{list} of L{WeightedAutomaton}
    """
    aut_list = []
    for fname in fnames.split(','):
        if len(fname) > 0:
            aut_list.append(load_unweight_automaton(collect, fname,
                                        test_standardized, needs_marker_states))

    return aut_list

# }}}


def LBE_make_greedy_time_optimal_supervisor(comp_names, req_names, evt_pairs):
    """
    Compute a LBE greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.LBE_compute_greedy_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        eventdata, heap_len)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Low boundary estimate is %s" % biggest)

# }}}

def load_LBE(LBE_names):

    for fname in LBE_names.split(','):
        if len(fname) > 0:
            header = ''
            linenum = 0
            vocal_states = {}
            trans = []
            name = None
            lbef = 0
            lbes_list = []

            handle = open(fname, 'r')
            for rawline in handle.readlines():
               line = rawline.strip()

               if len(line) > 0:
                   if lbef == 1:
                       lbes_list.append(line)
                   elif line.find("states")!=-1:
                       line   = line.replace('states','')
                       line   = line.replace('=','')
                       states = line.split(',')
                   elif line.find('LBE') !=-1:
                       line        = line.replace('LBE','')
                       line        = line.replace('=','')
                       lbes_list.append(line)
                       lbef        = 1
                   elif line.find('alphabet') != -1:
                       line   = line.replace('alphabet','')
                       line   = line.replace('=','')
                       events = line.split(',')

    if len(states)   <= 0:
          raise exceptions.ModelError('LBE file is not right')
    elif len(lbes_list)  <= 0:
          raise exceptions.ModelError('LBE file is not right')
    elif len(events) <= 0:
          raise exceptions.ModelError('LBE file is not right')

    lbes = []
    for lbe_items in lbes_list:
         lbe_items_list = lbe_items.split('(')
         for lbe_items_tmp in lbe_items_list:
              index = lbe_items_tmp.find(')')
              if index != -1:
                   lbeins = lbe_items_tmp[0:index]
                   lbes.append(lbeins.strip())

    return lbes



def FK_row_vector(comp_names, req_names, evt_pairs):
    """
    Compute a LBE greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.FK_row_vector(comp_list, req_list, eventdata, heap_len)
    if result is None:
        common.print_line('Could not compute the row vector')
        return

def make_time_optimal_string(plant_fnames, spec_fnames, steps_fname):
  with open(steps_fname) as handle:
    content = handle.readlines()
    steps = [tuple(line.rstrip().split(" ")) for line in content]
    order = [tup[0] for tup in steps]
    coll = collection.Collection()
    model_plants = load_weighted_automata(coll, plant_fnames, True, False)
    #evt_pairs = taskresource.process_event_pairs(coll, [], '')
    tau_abstraction2.tau_abstracted_greedy_supervisor_cranes(model_plants, [], [], "sup.cfg", order)
    #make_aggregate_synthesis_abstraction(plant_fnames, spec_fnames, steps)

def make_aggregate_synthesis_weighted_abstraction(plant_fnames, spec_fnames, steps):
    """
    Perform aggregated sythesis abstraction.

    @param steps: A list of tuples representing the steps of aggregated synthesis.
                  A tuple is comprised of a comma seperated list of automata names
                  to be composed. A comma seperated list of event names. 
                  A name for the intermediate supervisor. And a name
                  for the intermediate abstraction result
                  (None if no abstraction result is required).
    @type  aut_fnames: Tuple

    """
    sttime = time()
    common.print_line("Started aggregated synthesis abstraction computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()

    model_plants = load_weighted_automata(coll, plant_fnames, True, False)
    model_specs = frontend.load_automata(coll, spec_fnames, True, False)
    model_specs = []
    # A dummy specification to use when no specification is needed
    tau = coll.make_event("tau", False, False, False)
    tau = coll.events['tau']
    tau_abstraction.handle = file("profiling", 'w')
    handle = tau_abstraction.handle
    result = taskresource.compute_custom_eventdata_extended(model_plants, set(), "type2")
    eventdata, cliques = result
    steps = [list(step) for step in steps]
    for step in steps:
      while len(step) < 6:
        step.append("")
    for count, (plant_names, spec_names, sup_name, abs_name, time_optimal, non_progressive_events) in enumerate(steps):
      handle.write(str(count) + ":\n")
      time_optimal = time_optimal == "True"
      plant_set = set()
      spec_set = set()
      for name in plant_names.split(","):
        plant_set.add(name.strip())
      for name in spec_names.split(","):
        if name.strip() == "":
          continue
        spec_set.add(name.strip())
      to_compose_plants = [plant for plant in model_plants if plant.name in plant_set]
      model_plants = [plant for plant in model_plants if plant.name not in plant_set]
      heap_len = len(cliques)
      non_progressive_events = \
        set([coll.events[evt] for evt in non_progressive_events.split(",")]) if \
        non_progressive_events != "" else set()
      print "num auts:"
      print len(model_plants)
      if len(spec_set) != 0:
        to_compose_specs = [spec for spec in model_specs if spec.name in spec_set]
        model_specs = [spec for spec in model_specs if spec.name not in spec_set]
      else :
        to_compose_specs = []
      print "to_compose_plants:" + str(to_compose_plants)
      print "to_compose_specs:" + str(to_compose_specs)
      to_compose_plants[0]
      temp = to_compose_plants
      synctime = -time()    
      temp = to_compose_plants
      if len(to_compose_plants) > 1:
        #to_compose_plants = [product.n_ary_unweighted_product(to_compose_plants)]
        to_compose_plants = [tau_abstraction.synchronousproduct_weighted(to_compose_plants,0)]
        for aut in temp:
          aut.save_as_dot("comp_" + aut.name + ".dot")
          aut.clear()
      synctime += time()
      handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(to_compose_plants[0].get_num_states())\
        + "\tedges: " + str(to_compose_plants[0].get_num_edges()) + "\n")      
      synctime = -time()
      #to_compose_plants = [tau_abstraction.synchronousproduct_crane2(to_compose_plants,0,[1,30],30,None)]
      to_compose_plants[0].save_as_dot("currentcomp" + str(count) + ".dot")
      #sup = supervisor.make_supervisor(to_compose_plants, to_compose_specs)
      #sup = supervisor.make_supervisor_optimized(to_compose_plants, to_compose_specs)
      sup = to_compose_plants[0]
      sup.reduce(True, True)
      if time_optimal:
        sup = tau_abstraction.get_greedy_time_optimal_sup_progressive2(sup, eventdata,
                                                                      heap_len,
                                                                      non_progressive_events)
      synctime += time()
      handle.write("suptime: " + str(synctime) + "\t\tstates: " + str(sup.get_num_states()) \
        + "\t\tedges: " + str(sup.get_num_edges()) + "\n")
      sup.name = sup_name
      #for aut in temp:
      #    if aut.name.startswith("SC"):            
      #      state = aut.initial
      #      #tocompose[1].save_as_dot("getting" + str(depth) + ".dot")
      #      pick1, pick2, drop1, drop2 = None, None, None, None
      #      for edge in state.get_outgoing():
      #        if edge.succ != state:
      #          nextstate = edge.succ
      #          if edge.label.name.startswith("C1"):
      #            pick1 = edge.label
      #          else:
      #            pick2 = edge.label
      #      for state in aut.get_states():
      #        if state.marked:
      #          #for edge in state.get_incoming():
      #          #  if edge.succ != state:
      #          #    state = edge.pred
      #          #    break
      #          break
      #      for edge in state.get_incoming():
      #        if edge.pred != state:
      #          if edge.label.name.startswith("C1"):
      #            drop1 = edge.label
      #          else:
      #            drop2 = edge.label
      #      print (pick1, pick2, drop1, drop2)
      #      tau_abstraction.prune_impossible_events_crane(sup, pick1, pick2, drop1, drop2)
      #    #elif False: #aut.name.startswith("CS"):
      global_alphabet = set()
      global_alphabet.update(*[aut.alphabet for aut in model_plants])
      global_alphabet.update(*[aut.alphabet for aut in model_specs])
      to_keep = sup.alphabet.intersection(global_alphabet)      
      frontend.save_automaton(sup, "supervisor saved in %s", sup_name + ".cfg")
      for aut in model_plants:
        print aut.name 
      print "to_keep: " + str(to_keep)
      sup.save_as_dot("currentsup" + str(count) + ".dot")
      print ""
      print count
      print ""
      for state in sup.get_states():
        sup.state_names[state.number] = str(state.number)
      sup.save_as_dot(sup.name + ".dot")
      #abstracted = product.n_ary_unweighted_product(to_compose_plants + [sup])
      synctime = -time()
      abstracted = sup
      #abstracted = tau_abstraction.synchronousproduct(to_compose_plants + [sup], 0)
      synctime += time()
      handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(abstracted.get_num_states()) \
        + "\t\tedges: " + str(abstracted.get_num_edges()) + "\n")
      abstracted.save_as_dot("absbefabs" + str(count) + ".dot")
      abstime = -time()
      if False: #abs_name == "abs60":
        abstracted = sup
      else:          
        #to_keep.update(def_relevant)
        #abstracted, observer = tau_abstraction.subsetconstructionnotweighted_more_conflicting_weighted(sup, sup.alphabet.difference(to_keep), count)
        #abstracted, observer = tau_abstraction.subsetconstruction(sup, sup.alphabet.difference(to_keep), 0), True
        #if not observer:
        #  print "not observer"
        #  sup = tau_abstraction.synchronousproduct([sup, abstracted], 0)
        #  sup.reduce(True, True)
        #  sup.alphabet.add(tau)
        #  sup = abstraction.automaton_abstraction(sup)
        #  sup.alphabet.add(tau)
        #  frontend.save_automaton(sup, "supervisor saved in %s", sup_name + ".cfg")
        #  sup.save_as_dot(sup_name + "_pruned.dot")
        #abstracted = tau_abstraction.subsetconstructionnotweighted(sup, sup.alphabet.difference(to_keep), 0)
        #if count == len(steps)-1:
        #abstracted.alphabet.add(tau)
        abstracted.save_as_dot("abs" + str(count).zfill(3) + "bef.dot")
        #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
        abstracted.alphabet.add(tau)
        abstracted = abstraction.automaton_abstraction_weighted(abstracted)
        abstracted.alphabet.remove(tau)
        abstracted.save_as_dot("abs" + str(count).zfill(3) + "after.dot")
        #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
        #abstracted.save_as_dot("abs" + str(count).zfill(3) + "revsubmerg.dot")
        #tau_abstraction.subsetconstructionnotweighted_find_equiv(abstracted, set())
        #abstracted.save_as_dot("abs" + str(count).zfill(3) + "submerg.dot")
        #abstracted = abstraction.abstraction(abstracted, to_keep)
        #sup.clear()
        #to_compose_plants[0].clear()
      abstracted.name = abs_name
      abstime += time()
      handle.write("abstime: " + str(abstime) + "\t\tstates: " + str(abstracted.get_num_states()) \
        + "\t\tedges: " + str(abstracted.get_num_edges()) + "\n")
      handle.flush()
      frontend.save_automaton(abstracted, "abstracted saved in %s", abs_name + ".cfg")
      abstracted.save_as_dot(abstracted.name + ".dot")
      model_plants.append(abstracted)
      model_names = set([aut.name for aut in model_plants])
      print str(time() - sttime)

def make_to_be_named(plants, resources, steps, weight_function):
    """
    Perform aggregated sythesis abstraction.

    @param steps: A list of tuples representing the steps of aggregated synthesis.
                  A tuple is comprised of a comma seperated list of automata names
                  to be composed. A comma seperated list of event names.
                  A name for the intermediate supervisor. And a name
                  for the intermediate abstraction result
                  (None if no abstraction result is required).
    @type  aut_fnames: Tuple

    """
    print 'to be named'
    sttime = time()
    common.print_line("Started aggregated synthesis abstraction computations "
                      "(version %s)" % automata.version)
    coll = plants[0].collection
    model_plants = plants
    for aut in model_plants:
        print aut.name
    tau_abstraction.handle = file("profiling", 'w')
    handle = tau_abstraction.handle
    orig = []
    tau = coll.make_event("tau", False, False, False)
    for count, step in enumerate(steps):
      plant_names, abs_name = step[0], step[1]
      handle.write(str(count) + ":\n")
      plant_set = set()
      for name in plant_names.split(","):
        plant_set.add(name.strip())
      to_compose_plants = [plant for plant in model_plants if plant.name in plant_set]
      model_plants = [plant for plant in model_plants if plant.name not in plant_set]
      print step
      print "to_compose_plants:"
      for aut in to_compose_plants:
        print aut.name
      print "model_plants:"
      for aut in model_plants:
        print aut.name
      print plant_set
      assert len(to_compose_plants) == len(plant_set)
      print "num auts:"
      print len(model_plants)
      print "to_compose_plants:" + str(to_compose_plants)
      to_compose_plants[0]
      temp = to_compose_plants
      synctime = -time()
      temp = to_compose_plants
      if len(to_compose_plants) > 1:
        to_compose_plants[0] = tau_abstraction.synchronousproduct(to_compose_plants, 0)
      synctime += time()
      handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(to_compose_plants[0].get_num_states())\
        + "\tedges: " + str(to_compose_plants[0].get_num_edges()) + "\n")
      synctime = -time()
      to_compose_plants[0].save_as_dot("currentcomp" + str(count) + ".dot")
      composition = to_compose_plants[0]
      if not model_plants:
        model_plants.append(composition)
        break
      orig.append(composition)
      synctime += time()
      handle.write("suptime: " + str(synctime) + "\t\tstates: " + str(composition.get_num_states()) \
        + "\t\tedges: " + str(composition.get_num_edges()) + "\n")
      global_alphabet = set()
      global_alphabet.update(*[aut.alphabet for aut in model_plants])
      to_keep = composition.alphabet.intersection(global_alphabet)
      for aut in model_plants:
        print aut.name
      print "to_keep: " + str(to_keep)
      print ""
      print count
      print ""
      abstime = -time()
      abstracted = composition
      #abstracted = tau_abstraction.get_automaton_copy_not_weighted(composition)
      #abstracted = abstraction.model_conversion_language(composition, to_keep)
      #if count == len(steps)-1:
      #abstracted.alphabet.add(tau)
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "bef.dot")
      #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted = tau_abstraction.subsetconstructionnotweighted(abstracted, set(), 0)
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      abstracted.save_as_dot('subsetconbef.dot')
      abstracted = tau_abstraction.subsetconstructionnotweightedreverse(abstracted, abstracted.alphabet.difference(to_keep), 0)
      abstracted.save_as_dot('subsetconbef2.dot')
      abstracted = tau_abstraction.subsetconstructionnotweightedreverse(abstracted, abstracted.alphabet.difference(to_keep), 0)
      abstracted.save_as_dot('subsetconbef3.dot')
      #if (len(step) > 2):
      #    abstracted = tau_abstraction.convert_automata_to_to_be_named(abstracted)
      #if hasattr(abstracted, "language_aut"):
      #abstracted = tau_abstraction.simplify_to_be_named_base(abstracted, abstracted.alphabet.difference(to_keep))
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "after.dot")
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "revsubmerg.dot")
      #tau_abstraction.subsetconstructionnotweighted_find_equiv(abstracted, set())
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "submerg.dot")
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #abstracted = abstraction.abstraction(abstracted, to_keep)
      #sup.clear()
      #to_compose_plants[0].clear()
      abstracted.name = abs_name
      abstime += time()
      handle.write("abstime: " + str(abstime) + "\t\tstates: " + str(abstracted.get_num_states()) \
        + "\t\tedges: " + str(abstracted.get_num_edges()) + "\n")
      handle.flush()
      #save_automaton(abstracted, "abstracted saved in %s", abs_name + ".cfg")
      abstracted.save_as_dot(abstracted.name + ".dot")
      model_plants.append(abstracted)
      print str(time() - sttime)
    assert len(model_plants) == 1
    event_resource_map = defaultdict(list)
    event_state_resource_map = defaultdict(list)
    curr_alphabet = set(model_plants[0].alphabet)
    model_plants[0].save_as_dot('last.dot')
    for i,r in enumerate(resources):
        for e in r:
            event_resource_map[e].append(i)
            #event_state_resource_map[e].append(r)
    for e in model_plants[0].alphabet:
        event_resource_map[e].append(len(resources))
    paths = [tau_abstraction.random_walker_comp([model_plants[0]],
                                                weight_function, True) for _ in xrange(100)]
    #print paths
    #print event_resource_map
    paths2 = [compresstrace.compress_path_better(path, event_resource_map, event_state_resource_map)
              for path in paths]
    paths = [tau_abstraction.generate_aut_from_path_events([e.label for e in path],
                                                           curr_alphabet, coll) for path, w in paths2]
    for e in model_plants[0].alphabet:
        event_resource_map[e].pop()
    #path = tau_abstraction.tickdijkstrapath(model_plants[0], tick)
    #if not path.initial:
    #  print "No Trace"
    #  return
    mweight = min([w for _,w in paths2])
    c = 0
    while orig:
      print 'len orig', len(orig)
      origaut = orig.pop()
      curr_alphabet.update(origaut.alphabet)
      #paths = [tau_abstraction.synchronousproduct([path, origaut], 0) for path in paths]
      #paths[0].save_as_dot('check{}.dot'.format(c))
      c+=1
      #for path in paths:
      #    path.reduce(True, True)
      #paths = [tau_abstraction.random_walker_comp([path],
      #                                            weight_function, len(orig) == 0) for path in paths]
      for e in origaut.alphabet:
          event_state_resource_map[e].append(len(resources))
      paths = [tau_abstraction.random_walker_comp([path, origaut],
                                                  weight_function, True) for path in paths]
      paths2 = [compresstrace.compress_path_better(path, event_resource_map, event_state_resource_map)
                for path in paths]
      paths = [tau_abstraction.generate_aut_from_path_events([e.label for e in path],
                                                             curr_alphabet, coll) for path, w in paths2]
      mweight = min([w for _,w in paths2])
      for e in origaut.alphabet:
          event_state_resource_map[e].pop()
      #path = tau_abstraction.get_common_path(orig.pop(), path, handle)
    #tau_abstraction.testpath_not_weighted(model_orig, path, tick, handle)
    #save_automaton(path, "supervisor saved in %s", "sup.cfg")
    #paths2 = [incrementalimprovement.compress_path_better(path, event_resource_map, event_state_resource_map)
    #          for path in paths]
    #mweight = min([w for _,w in paths2])
    print mweight

def make_parralel_trace(plants, resources, steps, weight_function):
    """
    Perform aggregated sythesis abstraction.

    @param steps: A list of tuples representing the steps of aggregated synthesis.
                  A tuple is comprised of a comma seperated list of automata names
                  to be composed. A comma seperated list of event names.
                  A name for the intermediate supervisor. And a name
                  for the intermediate abstraction result
                  (None if no abstraction result is required).
    @type  aut_fnames: Tuple

    """
    print 'to be named'
    handle = file('profilingpar', 'a')
    sttime = time()
    common.print_line("Started aggregated synthesis abstraction computations "
                      "(version %s)" % automata.version)
    coll = plants[0][0].collection
    model_plants = plants
    for aut, _ in model_plants:
        print aut.name
    #tau_abstraction.handle = file("profiling", 'w')
    #handle = tau_abstraction.handle
    orig = []
    tau = coll.make_event("tau", False, False, False)
    maxcompup = 0
    for count, step in enumerate(steps):
      plant_names, abs_name = step[0], step[1]
      #handle.write(str(count) + ":\n")
      plant_set = set()
      for name in plant_names.split(","):
        plant_set.add(name.strip())
      to_compose_plants = [plant for plant in model_plants if plant[0].name in plant_set]
      model_plants = [plant for plant in model_plants if plant[0].name not in plant_set]
      print step
      print "to_compose_plants:"
      for aut,_ in to_compose_plants:
        print aut.name
      print "model_plants:"
      for aut,_ in model_plants:
        print aut.name
      print plant_set
      assert len(to_compose_plants) == len(plant_set)
      print "num auts:"
      print len(model_plants)
      print "to_compose_plants:" + str(to_compose_plants)
      to_compose_plants[0]
      temp = to_compose_plants
      synctime = -time()
      temp = to_compose_plants
      if len(to_compose_plants) > 1:
        to_compose_plants[0] = tau_abstraction.synchronousproductstateweight(to_compose_plants)
      synctime += time()
      #handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(to_compose_plants[0][0].get_num_states())\
      #  + "\tedges: " + str(to_compose_plants[0][0].get_num_edges()) + "\n")
      synctime = -time()
      composition = to_compose_plants[0]
      if not model_plants:
        model_plants.append(composition)
        break
      orig.append((composition, list(model_plants)))
      synctime += time()
      maxcompup = max(maxcompup, composition[0].get_num_states())
      #handle.write("suptime: " + str(synctime) + "\t\tstates: " + str(composition[0].get_num_states()) \
      #  + "\t\tedges: " + str(composition[0].get_num_edges()) + "\n")
      global_alphabet = set()
      global_alphabet.update(*[aut.alphabet for aut,_ in model_plants])
      to_keep = composition[0].alphabet.intersection(global_alphabet)
      for aut,_ in model_plants:
        print aut.name
      print "to_keep: " + str(to_keep)
      print ""
      print count
      print ""
      abstime = -time()
      abstracted = composition
      #abstracted = tau_abstraction.get_automaton_copy_not_weighted(composition)
      #abstracted = abstraction.model_conversion_language(composition, to_keep)
      #if count == len(steps)-1:
      #abstracted.alphabet.add(tau)
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "bef.dot")
      #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted = tau_abstraction.subsetconstructionnotweighted(abstracted, set(), 0)
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted.save_as_dot('subsetconbef.dot')
      abstracted = tau_abstraction.subsetconstructionnotweightedstateweight(abstracted[0], abstracted[0].alphabet.difference(to_keep), abstracted[1])
      #abstracted.save_as_dot('subsetconbef2.dot')
      abstracted = tau_abstraction.hopcroftstateweight(abstracted[0], abstracted[1])
      #abstracted.save_as_dot('subsetconbef3.dot')
      #if (len(step) > 2):
      #    abstracted = tau_abstraction.convert_automata_to_to_be_named(abstracted)
      #if hasattr(abstracted, "language_aut"):
      #abstracted = tau_abstraction.simplify_to_be_named_base(abstracted, abstracted.alphabet.difference(to_keep))
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "after.dot")
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "revsubmerg.dot")
      #tau_abstraction.subsetconstructionnotweighted_find_equiv(abstracted, set())
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "submerg.dot")
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #abstracted = abstraction.abstraction(abstracted, to_keep)
      #sup.clear()
      #to_compose_plants[0].clear()
      abstracted[0].name = abs_name
      abstime += time()
      #handle.write("abstime: " + str(abstime) + "\t\tstates: " + str(abstracted[0].get_num_states()) \
      #  + "\t\tedges: " + str(abstracted[0].get_num_edges()) + "\n")
      #handle.flush()
      #save_automaton(abstracted, "abstracted saved in %s", abs_name + ".cfg")
      model_plants.append(abstracted)
      print str(time() - sttime)
    assert len(model_plants) == 1
    event_resource_map = defaultdict(list)
    event_state_resource_map = defaultdict(list)
    curr_alphabet = set(model_plants[0][0].alphabet)
    for i,r in enumerate(resources):
        for e in r:
            event_resource_map[e].append(i)
            #event_state_resource_map[e].append(r)
    #path = tau_abstraction.calculate_longest_path(model_plants[0][0], model_plants[0][1], weight_function)
    #maxdown = 0
    path, maxdown = tau_abstraction.calculate_longest_path2([model_plants[0]], weight_function)
    #print paths
    #print event_resource_map
    #path = tau_abstraction.generate_aut_from_path_events([e.label for e in path], curr_alphabet, coll)
    #path = tau_abstraction.tickdijkstrapath(model_plants[0], tick)
    #if not path.initial:
    #  print "No Trace"
    #  return
    while orig:
      print 'len orig', len(orig)
      origaut, origothers = orig.pop()
      curr_alphabet.update(origaut[0].alphabet)
      path_state_weight = defaultdict(lambda : 0)
      for aut, state_weight in origothers:
          transmap = dict()
          visited = set()
          state, pstate = aut.initial, path.initial
          path_state_weight[pstate] += state_weight[state]
          while not pstate.marked:
              e = pstate.get_outgoing()[0]
              pstate = e.succ
              #if state not in visited:
                  #visited.add(state)
                  #for ed in state.get_outgoing():
                    #transmap[(state, ed.label)] = ed.succ
              if e.label in aut.alphabet:
                  edges = [edge for edge in state.get_outgoing() if edge.label == e.label]
                  state = edges[0].succ
                  #state = transmap[(state, e.label)]
              path_state_weight[pstate] += state_weight[state]
      #paths = [tau_abstraction.synchronousproduct([path, origaut], 0) for path in paths]
      #paths[0].save_as_dot('check{}.dot'.format(c))
      #for path in paths:
      #    path.reduce(True, True)
      #paths = [tau_abstraction.random_walker_comp([path],
      #                                            weight_function, len(orig) == 0) for path in paths]
      #projpath = tau_abstraction.subsetconstructionnotweighted(path, path.alphabet.difference(origaut[0].alphabet), 0)
      #origaut = tau_abstraction.synchronousproductstateweight([origaut, (projpath, defaultdict(lambda:0))])
      #origaut[0].reduce(True, True)
      #paut, psweight = tau_abstraction.synchronousproductstateweight([origaut, (path, path_state_weight)])
      #statesvis = paut.get_num_states()
      #path = tau_abstraction.calculate_longest_path(paut, psweight, weight_function)
      path, statesvis = tau_abstraction.calculate_longest_path2([origaut, (path, path_state_weight)], weight_function)
      maxdown = max(maxdown, statesvis)
      #path = tau_abstraction.get_common_path(orig.pop(), path, handle)
    #tau_abstraction.testpath_not_weighted(model_orig, path, tick, handle)
    #save_automaton(path, "supervisor saved in %s", "sup.cfg")
    pedges = []
    pstate = path.initial
    while not pstate.marked:
        e = pstate.get_outgoing()[0]
        pedges.append(e)
        pstate = e.succ
    #_, noweight = compresstrace.compress_path_better(pedges, event_resource_map, event_state_resource_map, calcweight=True)
    _, mweight = compresstrace.compress_path_better(pedges, event_resource_map, event_state_resource_map)
    #print noweight
    print mweight
    handle.write(','.join(map(str, [maxcompup, maxdown, 0, mweight, time()-sttime])))
    handle.write('\n')
    handle.close()
    print 'time:', time() - sttime

def make_parralel_trace_cycle(plants, resources, steps, weight_function):
    """
    Perform aggregated sythesis abstraction.

    @param steps: A list of tuples representing the steps of aggregated synthesis.
                  A tuple is comprised of a comma seperated list of automata names
                  to be composed. A comma seperated list of event names.
                  A name for the intermediate supervisor. And a name
                  for the intermediate abstraction result
                  (None if no abstraction result is required).
    @type  aut_fnames: Tuple

    """
    print 'to be named'
    handle = file('profilingpar', 'a')
    sttime = time()
    common.print_line("Started aggregated synthesis abstraction computations "
                      "(version %s)" % automata.version)
    coll = plants[0][0].collection
    model_plants = plants
    for aut, _ in model_plants:
        print aut.name
    #tau_abstraction.handle = file("profiling", 'w')
    #handle = tau_abstraction.handle
    orig = []
    tau = coll.make_event("tau", False, False, False)
    maxcompup = 0
    for count, step in enumerate(steps):
      plant_names, abs_name = step[0], step[1]
      #handle.write(str(count) + ":\n")
      plant_set = set()
      for name in plant_names.split(","):
        plant_set.add(name.strip())
      to_compose_plants = [plant for plant in model_plants if plant[0].name in plant_set]
      model_plants = [plant for plant in model_plants if plant[0].name not in plant_set]
      print step
      print "to_compose_plants:"
      for aut,_ in to_compose_plants:
        print aut.name
      print "model_plants:"
      for aut,_ in model_plants:
        print aut.name
      print plant_set
      assert len(to_compose_plants) == len(plant_set)
      print "num auts:"
      print len(model_plants)
      print "to_compose_plants:" + str(to_compose_plants)
      to_compose_plants[0]
      temp = to_compose_plants
      synctime = -time()
      temp = to_compose_plants
      if len(to_compose_plants) > 1:
        to_compose_plants[0] = tau_abstraction.synchronousproductstateweight(to_compose_plants)
      synctime += time()
      #handle.write("synctime: " + str(synctime) + "\t\tstates: " + str(to_compose_plants[0][0].get_num_states())\
      #  + "\tedges: " + str(to_compose_plants[0][0].get_num_edges()) + "\n")
      synctime = -time()
      composition = to_compose_plants[0]
      if not model_plants:
        model_plants.append(composition)
        break
      orig.append((composition, list(model_plants)))
      synctime += time()
      maxcompup = max(maxcompup, composition[0].get_num_states())
      #handle.write("suptime: " + str(synctime) + "\t\tstates: " + str(composition[0].get_num_states()) \
      #  + "\t\tedges: " + str(composition[0].get_num_edges()) + "\n")
      global_alphabet = set()
      global_alphabet.update(*[aut.alphabet for aut,_ in model_plants])
      to_keep = composition[0].alphabet.intersection(global_alphabet)
      for aut,_ in model_plants:
        print aut.name
      print "to_keep: " + str(to_keep)
      print ""
      print count
      print ""
      abstime = -time()
      abstracted = composition
      #abstracted = tau_abstraction.get_automaton_copy_not_weighted(composition)
      #abstracted = abstraction.model_conversion_language(composition, to_keep)
      #if count == len(steps)-1:
      #abstracted.alphabet.add(tau)
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "bef.dot")
      #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted = tau_abstraction.subsetconstructionnotweighted(abstracted, set(), 0)
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted.save_as_dot('subsetconbef.dot')
      abstracted = tau_abstraction.subsetconstructionnotweightedreversestateweight(abstracted[0], abstracted[0].alphabet.difference(to_keep), abstracted[1])
      #abstracted.save_as_dot('subsetconbef2.dot')
      abstracted = tau_abstraction.subsetconstructionnotweightedreversestateweight(abstracted[0], abstracted[0].alphabet.difference(to_keep), abstracted[1])
      #abstracted.save_as_dot('subsetconbef3.dot')
      #if (len(step) > 2):
      #    abstracted = tau_abstraction.convert_automata_to_to_be_named(abstracted)
      #if hasattr(abstracted, "language_aut"):
      #abstracted = tau_abstraction.simplify_to_be_named_base(abstracted, abstracted.alphabet.difference(to_keep))
      #abstracted.alphabet.add(tau)
      #abstracted = abstraction.abstraction_refined(abstracted, to_keep)
      #abstracted.alphabet.remove(tau)
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "after.dot")
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #tau_abstraction.subsetconstructionnotweighted_find_equiv_reverse(abstracted, set())
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "revsubmerg.dot")
      #tau_abstraction.subsetconstructionnotweighted_find_equiv(abstracted, set())
      #abstracted.save_as_dot("abs" + str(count).zfill(3) + "submerg.dot")
      #tau_abstraction.prune_tick_self(abstracted, tick)
      #abstracted = abstraction.abstraction(abstracted, to_keep)
      #sup.clear()
      #to_compose_plants[0].clear()
      abstracted[0].name = abs_name
      abstime += time()
      #handle.write("abstime: " + str(abstime) + "\t\tstates: " + str(abstracted[0].get_num_states()) \
      #  + "\t\tedges: " + str(abstracted[0].get_num_edges()) + "\n")
      #handle.flush()
      #save_automaton(abstracted, "abstracted saved in %s", abs_name + ".cfg")
      model_plants.append(abstracted)
      print str(time() - sttime)
    assert len(model_plants) == 1
    event_resource_map = defaultdict(list)
    event_state_resource_map = defaultdict(list)
    curr_alphabet = set(model_plants[0][0].alphabet)
    for i,r in enumerate(resources):
        for e in r:
            event_resource_map[e].append(i)
            #event_state_resource_map[e].append(r)
    #path = tau_abstraction.calculate_longest_path(model_plants[0][0], model_plants[0][1], weight_function)
    #maxdown = 0
    path, maxdown = tau_abstraction.calculate_longest_path2([model_plants[0]], weight_function)
    #print paths
    #print event_resource_map
    #path = tau_abstraction.generate_aut_from_path_events([e.label for e in path], curr_alphabet, coll)
    #path = tau_abstraction.tickdijkstrapath(model_plants[0], tick)
    #if not path.initial:
    #  print "No Trace"
    #  return
    while orig:
      print 'len orig', len(orig)
      origaut, origothers = orig.pop()
      curr_alphabet.update(origaut[0].alphabet)
      path_state_weight = defaultdict(lambda : 0)
      for aut, state_weight in origothers:
          transmap = dict()
          visited = set()
          state, pstate = aut.initial, path.initial
          path_state_weight[pstate] += state_weight[state]
          while not pstate.marked:
              e = pstate.get_outgoing()[0]
              pstate = e.succ
              #if state not in visited:
                  #visited.add(state)
                  #for ed in state.get_outgoing():
                    #transmap[(state, ed.label)] = ed.succ
              if e.label in aut.alphabet:
                  edges = [edge for edge in state.get_outgoing() if edge.label == e.label]
                  state = edges[0].succ
                  #state = transmap[(state, e.label)]
              path_state_weight[pstate] += state_weight[state]
      #paths = [tau_abstraction.synchronousproduct([path, origaut], 0) for path in paths]
      #paths[0].save_as_dot('check{}.dot'.format(c))
      #for path in paths:
      #    path.reduce(True, True)
      #paths = [tau_abstraction.random_walker_comp([path],
      #                                            weight_function, len(orig) == 0) for path in paths]
      #projpath = tau_abstraction.subsetconstructionnotweighted(path, path.alphabet.difference(origaut[0].alphabet), 0)
      #origaut = tau_abstraction.synchronousproductstateweight([origaut, (projpath, defaultdict(lambda:0))])
      #origaut[0].reduce(True, True)
      #paut, psweight = tau_abstraction.synchronousproductstateweight([origaut, (path, path_state_weight)])
      #statesvis = paut.get_num_states()
      #path = tau_abstraction.calculate_longest_path(paut, psweight, weight_function)
      path, statesvis = tau_abstraction.calculate_longest_path2([origaut, (path, path_state_weight)], weight_function)
      maxdown = max(maxdown, statesvis)
      #path = tau_abstraction.get_common_path(orig.pop(), path, handle)
    #tau_abstraction.testpath_not_weighted(model_orig, path, tick, handle)
    #save_automaton(path, "supervisor saved in %s", "sup.cfg")
    pedges = []
    pstate = path.initial
    while not pstate.marked:
        e = pstate.get_outgoing()[0]
        pedges.append(e)
        pstate = e.succ
    #_, noweight = compresstrace.compress_path_better(pedges, event_resource_map, event_state_resource_map, calcweight=True)
    _, mweight = compresstrace.compress_path_better(pedges, event_resource_map, event_state_resource_map)
    #print noweight
    print mweight
    handle.write(','.join(map(str, [maxcompup, maxdown, 0, mweight, time()-sttime])))
    handle.write('\n')
    handle.close()
    print 'time:', time() - sttime

def make_time_optimal_accepting_trace_weighted_to_tick(plant_fnames, spec_fnames, steps_fname):
    coll = collection.Collection()
    model_specs = frontend.load_automata(coll, spec_fnames, False, False)
    model_plants = load_weighted_automata(coll, plant_fnames, False, False)
    tick = coll.make_event("tick", True, True, False)
    steps = frontend.load_steps(steps_fname)
    for aut in model_plants:
        model_specs.append(aut)
        #model_specs.append(tau_abstraction.convert_weighted_to_tick(aut, tick))
    #frontend.make_time_optimal_accepting_trace(model_specs, steps)
    frontend.make_to_be_named(model_specs, steps)

def make_time_optimal_accepting_trace_weighted_random(plant_fnames, spec_fnames, steps_fname):
    print 'stuff'
    coll = collection.Collection()
    import os
    print 'curdir', os.getcwd()
    model_specs = frontend.load_automata(coll, spec_fnames, False, False)
    model_specs = [(a, defaultdict(lambda :0)) for a in model_specs]
    model_plants = load_weighted_automata(coll, plant_fnames, False, False)
    steps = frontend.load_steps(steps_fname)
    weighted_function = {}
    for aut in model_plants:
        state_weight = defaultdict(lambda :0)
        state_weight[aut.initial.get_outgoing()[0].succ] = 1
        if aut.get_num_states() == 3:
            print aut.name
            state_weight[aut.initial.get_outgoing()[0].succ.get_outgoing()[0].succ] = 1
        model_specs.append((aut, state_weight))
        for state in aut.get_states():
            for edge in state.get_outgoing():
                weighted_function[edge.label] = edge.weight
        #model_specs.append(tau_abstraction.convert_weighted_to_tick(aut, tick))
    #frontend.make_time_optimal_accepting_trace(model_specs, steps)
    print 'to be named'
    make_parralel_trace(model_specs, [frozenset(aut.alphabet) for aut,_ in model_specs],
                        steps, weighted_function)

def run_walkthrough(plant_fnames, spec_fnames):
  coll = collection.Collection()
  plants = load_weighted_automata(coll, plant_fnames, False, True)
  specs =  frontend.load_automata(coll, spec_fnames, False, True)
  walkthrough.walkthrough(plants+specs)

    
def make_aggregated_time_optimal_supervisor(plant_fnames, spec_fnames, steps_fname):
  with open(steps_fname) as handle:
    #content = handle.readlines()
    #steps = [tuple(line.rstrip().split(" ")) for line in content]
    #make_aggregate_synthesis_weighted_abstraction(plant_fnames, spec_fnames, steps)
    coll = collection.Collection()
    model_plants = load_weighted_automata(coll, plant_fnames, True, False)
    comp = tau_abstraction.synchronousproduct_weighted(model_plants,0)
    comp.reduce()
    tau_abstraction.handle = file("profiling", 'w')
    handle = tau_abstraction.handle
    result = taskresource.compute_custom_eventdata_extended(model_plants, set(), "type2")
    eventdata, cliques = result
    tau_abstraction.uniform_polling(comp, eventdata, len(cliques), handle)