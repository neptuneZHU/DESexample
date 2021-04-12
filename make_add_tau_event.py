#!/usr/bin/env python
# $Id: make_add_tau_event.py 554 2009-11-19 14:04:23Z hat $
"""
Add an initial tau event to an input file.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeAddTauEventApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_add_tau_event'
        desc = 'Add an initial tau event to an input file.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('input_name', frontend.EXIST_AUT,
                                       '<', 'source automaton'))

        self.add_parm(frontend.CmdParm('output_name', frontend.AUT,
                                       'o>', 'name of the result'))


    def main(self, args):
        frontend.make_add_tau_event(args['input_name'], args['output_name'])


if __name__ == '__main__':
    app = MakeAddTauEventApplication()
    app.run()

