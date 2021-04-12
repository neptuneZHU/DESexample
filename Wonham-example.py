# For N link automated supervisor design
from automata import frontend

## Compute local supervisor for each link

#frontend.make_natural_projection("PB23.cfg", "139, 241, 621, 759, mu, tau", "DetermPB23.cfg" )

frontend.make_get_size('PB23.cfg')
frontend.make_get_size('DetermPB23.cfg')


#frontend.make_product('SM13.cfg, SB1M24.cfg, SCEB23.cfg', 'central.cfg')
#frontend.make_trim('central.cfg','trim-central.cfg')
#frontend.make_language_equivalence_test('central.cfg','trim-central.cfg')


