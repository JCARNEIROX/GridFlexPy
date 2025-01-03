import pandas as pd
import os

# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'
path_forecast = os.getcwd() + '/data/forecasts'
path_loads = os.getcwd() + '/data/loads/'

def add_load(Load):
  
  #Extract all atributes from object Load
  name = Load.id
  bus = str(Load.bus_node).zfill(3)
  Terminals = str(Load.Terminals)
  phases = Load.phases
  Conn = Load.Conn
  kV = Load.kV
  kW = Load.kW
  Pmax = Load.Pmax
  Pf = Load.Pf
  model = Load.Model
  classe = Load.Class
  Vminpu = Load.Vminpu
  ZIPV = Load.ZIPV
  conductors = ".".join(map(str, Terminals))

  new_load = f"New Load.Load_{name}_{bus} bus1={bus}.{conductors} Phases={phases} Conn={Conn} kV={kV} kW={kW*Pmax} Pf={Pf} Model={model} Class={classe} Vminpu={Vminpu} ZIPV={ZIPV}"
#   new_load = f"New Load.Load_{name}_bus_{bus} bus1=bus_{bus}.{conductors} Phases={phases} Con={Conn} kV={kV} kW=5 Pf=1 Model={model} Class={classe} Vminpu={Vminpu} ZIPV={ZIPV}"

  return new_load

def add_light(Load):
    
    #Extract all atributes from object Load
    name = Load.id
    bus = str(Load.bus_node)
    Terminals = str(Load.Terminals)
    phases = Load.phases
    Conn = Load.Conn
    kV = Load.kV
    kW = Load.kW
    Pmax = Load.Pmax
    Pf = Load.Pf
    model = Load.Model
    classe = Load.Class
    Vminpu = Load.Vminpu
    ZIPV = Load.ZIPV
    conductors = ".".join(map(str, Terminals))
    
    new_load = f"New Load.{name}_{bus} bus1={bus}.{conductors} Phases={phases} Conn={Conn} kV={kV} kW={kW*Pmax} Pf={Pf} Model={model} Class={classe} Vminpu={Vminpu} ZIPV={ZIPV}"
    return new_load

def construct_loads(loads):
    """
    Construct the load objects from the spreadsheet content.
    """
    list_loads_objects = []

    for _, row in loads.iterrows():
        load = Load(row['Id'],row['Profile'], row['Bus_node'], row['Phases'], row['Conn'], row['kV'], row['Pf'], 
                    row['Model'], row['Class'], row['Vminpu'], row['Terminals'],Pmax=row['Pmax'])
        list_loads_objects.append(load)
    
    return list_loads_objects

def construct_lights(public_ilumination):
    """
    Construct the public ilumination objects from the spreadsheet content.
    """
    list_lights_objects = []

    for _, row in public_ilumination.iterrows():
        light = Load(row['Id'],row['Profile'], row['Bus_node'], row['Phases'], row['Conn'], row['kV'], row['Pf'], 
                     row['Model'], row['Class'], row['Vminpu'], row['Terminals'],Pmax=row['Pmax'], ZIPV=(-0.16, 1.2, -0.04, 3.26, -4.11, 1.85, 0.52))
        list_lights_objects.append(light)
    
    return list_lights_objects

def get_LoadPower(dss,timestep):
    """
    Get the power of the loads in the circuit.
    Returns a two double array with the power of the loads and bus power
    """
    loads = dss.Loads.AllNames()
    load_power = [0,0]
    
    for load in loads:
            dss.Circuit.SetActiveElement(f'Load.{load}')
            powers = dss.CktElement.Powers()
            load_power[0] += sum(powers[::2])  # Sum the active power
            load_power[1] += sum(powers[1::2])  # Sum the reactive

    columns_power = ['Timestep','P(kW)','Q(kvar)']
    load_line = pd.DataFrame([[timestep, round(load_power[0],4),round(load_power[1],4)]], columns=columns_power)
    return load_line

class Load:
    def __init__(self, id,Profile,buss_node,phases,Conn,kV,Pf,Model,Class,Vminpu,Terminals, Pmax=1,ZIPV=(0.5, 0, 0.5, 1, 0, 0, 0.5) ,kW=0):

        self.id = id
        self.Profile = pd.read_csv(f'{path_loads}{Profile}')
        self.bus_node = buss_node
        self.phases = phases
        self.Conn = Conn
        self.kV = kV
        self.Pf = Pf
        self.Pmax = Pmax
        self.kW = kW
        self.Model = Model
        self.Class = Class
        self.Vminpu = Vminpu
        self.Terminals = Terminals
        self.ZIPV = ZIPV

    def update_power(self, timestep):
        """
        Load the profile and update the power of the load in a specific timestep.
        """
        self.Profile['datetime'] = pd.to_datetime(self.Profile['datetime'])
        Ppower = self.Profile[self.Profile['datetime'] == timestep]['Ppower'].values[0]
        self.kW = Ppower
    
    def change_ZIPV(self, ZIPV):
        """
        Change the ZIPV of the load.
        """
        self.ZIPV = ZIPV

    