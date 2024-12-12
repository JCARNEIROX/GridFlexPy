
def add_bat(Bess):
    """	
    Function to write a comand that will modify the power of the battery during the power flow simulation.
    """
    name = Bess.id
    bus = str(Bess.bus_node).zfill(3)
    Phases = Bess.Phases
    kV = Bess.kV
    kW = Bess.Pt # Instanteneous power of the battery, kw>0: charging, kw<0: discharging
    Emax = Bess.Emax
    Et = Bess.Et  # Instanteneous energy stored in the battery, %stored
    Eff = Bess.Efficiency
    Emin = Bess.Emin

    new_bat = f"New Storage.Bess_{name}_bus_{bus} bus1=bus_{bus} Phases={Phases} kV={kV} kW={kW} kWhRated={Emax} %stored={Et} %EffCharge={Eff} %EffDischarge={Eff} %reserve={Emin}"
    # new_bat = f"New Storage.Bess_{name}_bus_{bus} bus1=bus_{bus} Phases=3 kV=0.22 kW=5 kWhRated=10 %stored=100 %EffCharge=95 %EffDischarge=95 %reserve=20 "
    
    return new_bat


def construct_bess(batteries):

    ids = batteries['Id'].values
    list_bess_objects = []

    for id in ids:
        bess = Bess(id, batteries.loc[batteries['Id'] == id, 'Bus_node'].values[0], batteries.loc[batteries['Id'] == id, 'Phases'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'kV'].values[0], batteries.loc[batteries['Id'] == id, 'Pmax'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'Einit'].values[0], batteries.loc[batteries['Id'] == id, 'Emax'].values[0],
                    batteries.loc[batteries['Id'] == id, 'Emin(%)'].values[0], batteries.loc[batteries['Id'] == id, 'Efficiency'].values[0])
        list_bess_objects.append(bess)

    return list_bess_objects

def get_BessPower(batteries,dss):

    battery_power = [0,0]
    bus_power = [0,0]

    for bat in batteries:
            dss.Circuit.SetActiveElement(bat)
            powers = dss.CktElement.Powers()
            battery_power[0] -= sum(powers[::2])  # Somando potências ativas
            battery_power[1] -= sum(powers[1::2])  # Somando potências reativas

            bus_power[0] += sum(powers[::2])  # Somando potências ativas nos barramentos
            bus_power[1] += sum(powers[1::2])  # Somando potências reativas nos barramentos
    
    return battery_power,bus_power

class Bess:
    def __init__(self, id,buss_node,Phases,kV,Pmax,Einit,Emax,Emin,Efficiency):
        self.id = id
        self.bus_node = buss_node
        self.Phases = Phases
        self.kV = kV
        self.Pmax = Pmax
        self.Pt = 0
        self.Et = (Einit/Emax)*100
        self.Einit = (Einit/Emax)*100
        self.Emax = Emax
        self.Emin = Emin
        self.Efficiency = Efficiency

    def update_power(self, new_power):
        """
        Change the actual power of the battery.
        kw > 0: Charging.
        kw < 0: Discharging.
        """
        if abs(new_power) > self.Pmax:
            self.Pt = self.Pmax if new_power > 0 else -self.Pmax
        else:
            self.Pt = new_power

    def update_energy(self, timestep):
        """
        Change the energy storaged off battery with timestep in min.
        """
        if self.Pt > 0:  # Carregando
            energy_change = self.Pt * (timestep/60) * (self.Efficiency / 100)
        else:  # Descarregando
            energy_change = self.Pt * (timestep/60) * (1 / (self.Efficiency / 100))

        new_energy = self.Et + energy_change
        if new_energy > self.Emax:
            self.Et = self.Emax
        elif new_energy < self.Emin:
            self.Et = self.Emin
        else:
            self.Et = new_energy
    
    def get_Pt(self):
        return self.Pt
    
    def get_Et(self):
        return self.Et
        
    