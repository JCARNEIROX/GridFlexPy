import pandas as pd
import os

# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'
path_forecast = os.getcwd() + '/data/forecasts'


def add_gd(Generator):
    """	
    Function to write a comand that will modify the power of the generator during the power flow simulation.
    """
    name = Generator.id
    bus = str(Generator.bus_node)
    phases = Generator.phases
    Terminals = str(Generator.Terminals)
    kV = Generator.kV
    Conn = Generator.Conn
    kW = Generator.kW
    Pmax = Generator.Pmax
    Pf = Generator.Pf
    model = Generator.Model
    conductors = ".".join(map(str, Terminals))

    new_gd = f"New Generator.Gen_{name}_{bus} bus1={bus}.{conductors} Phases={phases} kV={kV} Conn={Conn} kW={kW*Pmax} Pf={Pf} Model={model}"

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
    generators = dss.Generators.AllNames()

    gen_power = [0,0]
    for gen in generators:
            dss.Circuit.SetActiveElement(f'Generator.{gen}')
            gen_power[0] += dss.Generators.kW()  # Sum the active power
            gen_power[1] += dss.Generators.kvar()  # Sum reactive power
    
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
        self.Profile = pd.read_csv(f'{path_generators}{Profile}')
        self.Terminals = Terminals

    def update_power(self, timestep):
        """
        Load the profile and update the power of the load in a specific timestep.
        """    
        self.Profile['datetime'] = pd.to_datetime(self.Profile['datetime'])
        Ppower = self.Profile[self.Profile['datetime'] == timestep]['Ppower'].values[0]
        self.kW = Ppower
    