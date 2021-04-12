import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeTauAbstractionApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_tau_abstraction'
        desc = 'Make the tau abstraction of automata.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p+',
                                    'list of components (weighted automata)'))
        self.add_parm(frontend.CmdParm('req_names', frontend.AUTLIST, 'r+',
                                'list of requirements (unweighted automata)'))
        self.add_parm(frontend.CmdParm('evt_pairs', frontend.EVTPAIRS,
                                'e', 'set of event pairs'))

    def main(self, args):
        weighted_frontend.make_tau_abstraction(args['comp_names'], args['req_names'], args['evt_pairs'])

if __name__ == '__main__':
    app = MakeTauAbstractionApplication()
    app.run()

