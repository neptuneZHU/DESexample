"""
Compute greedy time optimal supervisor.

@note: The weight is associated with the event rather than the edge!
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeGreedyTimeOptimalSupervisorCorrectlyApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_greedy_time_optimal_supervisor_correctly'
        desc = "Compute greedy time optimal supervisor - Marijn's corrected version."
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p+',
                                    'list of components (weighted automata)'))
        self.add_parm(frontend.CmdParm('req_names', frontend.AUTLIST, 'r+',
                                'list of requirements (unweighted automata)'))
        self.add_parm(frontend.CmdParm('evt_pairs', frontend.EVTPAIRS,
                                'e', 'set of event pairs'))
        self.add_parm(frontend.CmdParm('sup_name', frontend.AUT,
                                       's>', 'supervisor name'))
        self.add_parm(frontend.CmdParm('L', frontend.VALUE,
                                       's>', 'L value (L >= 2)'))

    def main(self, args):
        weighted_frontend.make_greedy_time_optimal_supervisor_correctly(args['comp_names'],
                                        args['req_names'], args['evt_pairs'],
                                        args['sup_name'], args['L'])

if __name__ == '__main__':
    app = MakeGreedyTimeOptimalSupervisorCorrectlyApplication()
    app.run()

