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
    Pf = Generator.Pf
    model = Generator.Model

    new_gd = f"New Generator.Gen_{name}_bus_{bus} bus1=bus_{bus} Phases={phases} kV={kV} Conn={Conn} kW={kW} Pf={Pf} Model={model}"

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
                              row['Conn'], row['Pf'], row['Model'], row['Profile'], row['Terminals'])
        list_generators_objects.append(generator)

    return list_generators_objects

class Generator:
    def __init__(self, id,buss_node,phases,kV,Conn,Pf,Model,Profile,Terminals,kW=0):
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

    def update_power(self, timestep):
        """
        Load the profile and update the power of the load in a specific timestep.
        """
        data = pd.read_csv(f'{path}{self.Profile}.csv')
        data['datetime'] = pd.to_datetime(data['datetime'])
        Ppower = data[data['datetime'] == timestep]['Ppower'].values[0]
        self.kW = Ppower
    