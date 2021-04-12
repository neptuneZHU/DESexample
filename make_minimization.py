#!/usr/bin/env python
# $Id: make_minimization.py 538 2009-11-09 14:51:19Z hat $
"""
Minimize automaton.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeMinimizationApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_minimization'
        desc = 'Minimize automaton.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_name', frontend.EXIST_AUT,
                                       'i<', 'automaton'))
        self.add_parm(frontend.CmdParm('result_name', frontend.AUT,
                                       'o>', 'minimized result'))

    def main(self, args):
        frontend.make_minimized(args['aut_name'], args['result_name'])

if __name__ == '__main__':
    app = MakeMinimizationApplication()
    app.run()

