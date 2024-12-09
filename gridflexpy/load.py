
def add_load(name, bus, phases, Conn, kV, kW, Pf,Terminals, model=8, classe=1, vminpu=0.92, ZIPV=(0.5, 0, 0.5, 1, 0, 0, 0.5)):
 
  conductors = ".".join(map(str, Terminals))
  new_load = f"New Load.Load_{name}_{bus} bus1={bus}.{conductors} Phases={phases} Con={Conn} kV={kV} kW={kW} Pf{Pf} Model={model} Class={classe} Vminpu={vminpu} ZIPV={ZIPV}"

  return new_load


def construct_loads(loads):
    """
    Construct the load objects from the spreadsheet content.
    """
    ids = loads['Id'].values
    list_loads_objects = []

    for id in ids:
        load = Load(id, loads.loc[loads['Id'] == id, 'Bus_node'].values[0], loads.loc[loads['Id'] == id, 'Phases'].values[0], loads.loc[loads['Id'] == id, 'Conn'].values[0], 
                              loads.loc[loads['Id'] == id, 'kV'].values[0], loads.loc[loads['Id'] == id, 'kW'].values[0], loads.loc[loads['Id'] == id, 'Pf'].values[0],
                              loads.loc[loads['Id'] == id, 'Model'].values[0], loads.loc[loads['Id'] == id, 'Class'].values[0], loads.loc[loads['Id'] == id, 'Vminpu'].values[0],
                              loads.loc[loads['Id'] == id, 'Vminpu'].values[0], loads.loc[loads['Id'] == id, 'Terminals'].values[0])
        list_loads_objects.append(load)

    return list_loads_objects

class Load:
    def __init__(self, id,buss_node,phases,Conn,kV,kW,Pf,Model,Class,Vminpu,Vmaxpu,Terminals):
        self.id = id
        self.bus_node = buss_node
        self.phases = phases
        self.Conn = Conn
        self.kV = kV
        self.kW = kW
        self.Pf = Pf
        self.Model = Model
        self.Class = Class
        self.Vminpu = Vminpu
        self.Vmaxpu = Vmaxpu
        self.Terminals = Terminals

    def get_id(self):
        return self.id
    
    def get_bus_node(self):
        return self.bus_node
    
    def get_phases(self):
        return self.phases
    
    def get_conn(self):
        return self.Conn
    
    def get_kv(self):
        return self.kV
    
    def get_kw(self):
        return self.kW
    
    def get_pf(self):
        return self.Pf
    
    def get_model(self):
        return self.Model
    
    def get_class(self):
        return self.Class
    
    def get_vminpu(self):
        return self.Vminpu
    
    def get_vmaxpu(self):
        return self.Vmaxpu
    
    def get_terminals(self):
        return self.Terminals
    
    def get_profile(self):
        return self.Profile