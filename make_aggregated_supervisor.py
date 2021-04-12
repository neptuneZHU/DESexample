#!/usr/bin/env python
# $Id: make_time_optimal_supervisor.py 683 2010-03-26 15:33:49Z hat $
"""
Compute time optimal supervisor.

@note: The weight is associated with the event rather than the edge!
"""
import sys
import cProfile
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeTauAbstractedSupervisorApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_tau_abstracted_supervisor'
        desc = 'Compute time optimal supervisor.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p+',
                                    'list of components (unweighted automata)'))
        self.add_parm(frontend.CmdParm('req_names', frontend.AUTLIST, 'r+',
                                'list of requirements (unweighted automata)'))
        self.add_parm(frontend.CmdParm('steps', frontend.AUT,
                                       's>', 'step file'))

    def main(self, args):
        frontend.make_aggregated_supervisor(args['comp_names'],
                                            args['req_names'],
                                            args['steps'])
        #weighted_frontend.make_time_optimal_string(args['comp_names'],
        #                                           args['req_names'],
        #                                           args['steps'])            
                                                                       
if __name__ == '__main__':
    app = MakeTauAbstractedSupervisorApplication()
    #cProfile.run('app.run()')
    app.run()
