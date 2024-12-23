import pandas as pd
import os

path = os.getcwd() + '/data/generators_profiles/'

def add_gd(Generator):
    """	
    Function to write a comand that will modify the power of the generator during the power flow simulation.
    """
    name = Generator.id
    bus = str(Generator.bus_node).zfill(3)
    phases = Generator.phases
    kV = Generator.kV
    Conn = Generator.Conn
    kW = Generator.kW
    Pmax = Generator.Pmax
    Pf = Generator.Pf
    model = Generator.Model

    new_gd = f"New Generator.Gen_{name}_bus_{bus} bus1=bus_{bus} Phases={phases} kV={kV} Conn={Conn} kW={kW*Pmax} Pf={Pf} Model={model}"

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
    list_generators_objects = []

    for _, row in generators.iterrows():
        generator = Generator(row['Id'], row['Bus_node'], row['Phases'], row['kV'], 
                              row['Conn'], row['Pmax'], row['Pf'], row['Model'], row['Profile'], row['Terminals'])
        list_generators_objects.append(generator)

    return list_generators_objects


def get_GenPower(dss,timestep):
    """
    Get the power of the generators in the circuit.
    Returns a two double array with the power of the loads and bus power
    """
    elements = dss.Circuit.AllElementNames()
    generators = [element for element in elements if element.startswith("Generator.")]

    gen_power = [0,0]
    for gen in generators:
            dss.Circuit.SetActiveElement(gen)
            powers = dss.CktElement.Powers()
            gen_power[0] -= sum(powers[::2])  # Sum the active power
            gen_power[1] -= sum(powers[1::2])  # Sum reactive power
    
    columns_power = ['Timestep','P(kW)','Q(kvar)']
    gen_line = pd.DataFrame([[timestep, round(gen_power[0],4),round(gen_power[1],4)]], columns=columns_power)
    
    return gen_line
            
class Generator:
    def __init__(self, id,buss_node,phases,kV,Conn,Pmax,Pf,Model,Profile,Terminals,kW=0):
        self.id = id
        self.bus_node = buss_node
        self.phases = phases
        self.kV = kV
        self.Conn = Conn
        self.Pmax = Pmax
        self.kW = kW
        self.Pf = Pf
        self.Model = Model
        self.Profile = Profile
        self.Terminals = Terminals

    def update_power(self, timestep):
        """
        Load the profile and update the power of the load in a specific timestep.
        """
        data = pd.read_csv(f'{path}{self.Profile}.csv')
        data['datetime'] = pd.to_datetime(data['datetime'])
        Ppower = data[data['datetime'] == timestep]['Ppower'].values[0]
        self.kW = Ppower
    