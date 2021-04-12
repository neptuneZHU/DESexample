#!/usr/bin/env python
# $Id: make_optimal_weighted_supervisor.py 634 2010-01-28 11:46:01Z hat $
"""
Compute optimal weighted supervisor.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeOptimalWeightedSupervisorApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_optimal_weighted_supervisor'
        desc = 'Compute optimal weighted supervisor.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_name', frontend.AUT, 'p',
                                    'Plant (weighted automaton)'))
        self.add_parm(frontend.CmdParm('req_name', frontend.AUT, 'r',
                                'Requirement (unweighted automaton)'))
        self.add_parm(frontend.CmdParm('sup_name', frontend.AUT,
                                       's>', 'supervisor name'))

    def main(self, args):
        weighted_frontend.make_optimal_weighted_supervisor(args['comp_name'],
                                            args['req_name'], args['sup_name'])

if __name__ == '__main__':
    app = MakeOptimalWeightedSupervisorApplication()
    app.run()

