import pandas as pd
import os

path = os.getcwd() + '/data/loads/'

def add_load(Load):
  
  #Extract all atributes from object Load
  name = Load.id
  bus = str(Load.bus_node).zfill(3)
  Terminals = str(Load.Terminals)
  phases = Load.phases
  Conn = Load.Conn
  kV = Load.kV
  kW = Load.kW
  Pf = Load.Pf
  model = Load.Model
  classe = Load.Class
  Vminpu = Load.Vminpu
  ZIPV = Load.ZIPV
  conductors = ".".join(map(str, Terminals))

  new_load = f"New Load.Load_{name}_bus_{bus} bus1=bus_{bus}.{conductors} Phases={phases} Con={Conn} kV={kV} kW={kW} Pf={Pf} Model={model} Class={classe} Vminpu={Vminpu} ZIPV={ZIPV}"
#   new_load = f"New Load.Load_{name}_bus_{bus} bus1=bus_{bus}.{conductors} Phases={phases} Con={Conn} kV={kV} kW=5 Pf=1 Model={model} Class={classe} Vminpu={Vminpu} ZIPV={ZIPV}"

  return new_load


def construct_loads(loads):
    """
    Construct the load objects from the spreadsheet content.
    """
    list_loads_objects = []

    for _, row in loads.iterrows():
        load = Load(row['Id'], row['Bus_node'], row['Phases'], row['Conn'], row['kV'], row['Pf'], row['Pmax'], row['Model'], row['Class'], row['Vminpu'], row['Terminals'])
        list_loads_objects.append(load)
    
    return list_loads_objects

def get_LoadPower(loads,dss):
    """
    Get the power of the loads in the circuit.
    Returns a two double array with the power of the loads and bus power
    """
    load_power = [0,0]
    bus_power = [0,0]
    
    for load in loads:
            dss.Circuit.SetActiveElement(load)
            powers = dss.CktElement.Powers()
            load_power[0] += sum(powers[::2])  # Sum the active power
            load_power[1] += sum(powers[1::2])  # Sum the reactive

            bus_power[0] += sum(powers[::2])  # Sum the active power at bus
            bus_power[1] += sum(powers[1::2])  # Sum the reactive power at bus

    return load_power,bus_power

class Load:
    def __init__(self, id,buss_node,phases,Conn,kV,Pf,Pmax,Model,Class,Vminpu,Terminals, ZIPV=(0.5, 0, 0.5, 1, 0, 0, 0.5),kW=0):

        self.id = id
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
        data = pd.read_csv(f'{path}{self.id}.csv')
        data['datetime'] = pd.to_datetime(data['datetime'])
        Ppower = data[data['datetime'] == timestep]['Ppower'].values[0]
        self.kW = Ppower
    
    def change_ZIPV(self, ZIPV):
        """
        Change the ZIPV of the load.
        """
        self.ZIPV = ZIPV

    