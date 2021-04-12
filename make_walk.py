import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeWalk(frontend.Application):
    def __init__(self):
        cmd = 'make walk'
        desc = 'Walkthrough a DES.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p+',
                                    'list of components (weighted automata)'))
        self.add_parm(frontend.CmdParm('spec_names', frontend.AUTLIST, 'p+',
                                    'list of components (unweighted automata)'))

    def main(self, args):
        weighted_frontend.run_walkthrough(args['comp_names'], args['spec_names'])

if __name__ == '__main__':
    app = MakeWalk()
    app.run()


