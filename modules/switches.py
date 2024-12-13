
def add_switch(switch):
    """
    Add a switch to the OpenDSS model.
    """
    name = switch.id
    bus1 = str(switch.bus_node1).zfill(3)
    bus2 = str(switch.bus_node2).zfill(3)
    phases = switch.phases
    status = switch.status
    new_switch = f"New Line.Sw_{bus1}_{bus2} Phases=3 Bus1=671   Bus2=692  Switch=y  r1=1e-4 r0=1e-4 x1=0.000 x0=0.000 c1=0.000 c0=0.000"
    return new_switch


import opendssdirect as dss

