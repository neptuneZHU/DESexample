#!/usr/bin/env python
# $Id: make_time_optimal_supervisor.py 683 2010-03-26 15:33:49Z hat $
"""
Compute time optimal supervisor.

@note: The weight is associated with the event rather than the edge!
"""
import sys
import cProfile
from automata import progressive
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeAggregatedTimeOptimalSupervisor(frontend.Application):
    def __init__(self):
        cmd = 'make_tau_abstracted_supervisor'
        desc = 'Compute time optimal supervisor.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p+',
                                    'list of components (unweighted automata)'))
        self.add_parm(frontend.CmdParm('supervisors', frontend.AUTLIST, 'p+',
                                    'list of components (unweighted automata)'))
        #self.add_parm(frontend.CmdParm('req_names', frontend.AUTLIST, 'r+',
                                #'list of requirements (unweighted automata)'))

    def main(self, args):
        progressive.load_test_mult_supervisors(args['comp_names'],
                                              args['supervisors'],
                                              set(),
                                              "type2")            
                                                                       
if __name__ == '__main__':
    app = MakeAggregatedTimeOptimalSupervisor()
    #cProfile.run('app.run()')
    app.run()
