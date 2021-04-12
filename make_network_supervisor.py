#!/usr/bin/env python
# $Id: make_supervisor.py 672 2010-03-24 10:26:31Z hat $
"""
Compute the supremal controllable and normal sublanguage of a plant with
respect to a specification. The alphabet of the specification need not be
the same as that of the plant.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend
from SimonStuff import NetworkControl

class MakeNetworkSupervisorApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_supervisor'
        desc = 'Compute the supremal controllable and normal sublanguage of ' \
               'a plant with respect to a requirement model, over a network.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('plants', frontend.AUTLIST,
                                       '+p', 'plant models'))
        self.add_parm(frontend.CmdParm('specs', frontend.AUTLIST,
                                       '+r', 'requirement models'))
        self.add_parm(frontend.CmdParm('limit', frontend.VALUE,
                                       '+r', 'requirement models'))
        #self.add_parm(frontend.CmdParm('supervisor', frontend.AUT,
        #                               'so>', 'supervisor'))

    def main(self, args):
        NetworkControl.make_translated_model(args['plants'], args['specs'],
                                             int(args['limit']))

if __name__ == '__main__':
    app = MakeNetworkSupervisorApplication()
    app.run()

