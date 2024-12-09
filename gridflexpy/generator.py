

def add_gd(name, bus, phases, conn, kV, kW, Pf, model=1):
    """	
    Function to write a comand that will modify the power of the generator during the power flow simulation.
    """
  
    new_gd = f"New Generator.{name} bus1={bus} Phases={phases} kV={kV} Conn={conn} kW={kW} Pf={Pf} Model={model}"

    return new_gd

def get_GneratorPower(timestep, profile):
    """
    Function to get the power of the generator in a specific timestep.
    """
    return profile.loc[timestep, 'Ppower']

def construct_generators(generators):
    """
    Construct the generator objects from the spreadsheet content.
    """
    ids = generators['Id'].values
    list_generators_objects = []

    for id in ids:
        generator = Generator(id, generators.loc[generators['Id'] == id, 'Bus_node'].values[0], generators.loc[generators['Id'] == id, 'Phases'].values[0], generators.loc[generators['Id'] == id, 'kV'].values[0], 
                              generators.loc[generators['Id'] == id, 'Conn'].values[0], generators.loc[generators['Id'] == id, 'kW'].values[0], generators.loc[generators['Id'] == id, 'Pf'].values[0],
                              generators.loc[generators['Id'] == id, 'Model'].values[0], generators.loc[generators['Id'] == id, 'Profile'].values[0], generators.loc[generators['Id'] == id, 'Terminals'].values[0])
        list_generators_objects.append(generator)

    return list_generators_objects

class Generator:
    def __init__(self, id,buss_node,phases,kV,Conn,kW,Pf,Model,Profile,Terminals):
        self.id = id
        self.bus_node = buss_node
        self.phases = phases
        self.kV = kV
        self.Conn = Conn
        self.kW = kW
        self.Pf = Pf
        self.Model = Model
        self.Profile = Profile
        self.Terminals = Terminals
