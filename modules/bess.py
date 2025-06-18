from scipy.ndimage import gaussian_filter1d
from filterpy.kalman import KalmanFilter
import numpy as np
import pandas as pd
import os

# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'
path_forecast = os.getcwd() + '/data/forecasts'

def add_bat(Bess):
    """	
    Function to write a comand that will modify the power of the battery during the power flow simulation.
    """
    name = Bess.id
    state = Bess.state
    bus = str(Bess.bus_node)
    Phases = Bess.Phases
    Conn = Bess.Conn
    Terminals = str(Bess.Terminals)
    kV = Bess.kV
    kW = Bess.Pt # Instanteneous power of the battery, kw>0: dischargin, kw<0: charging
    Cmax = Bess.Cmax
    Emax = Bess.Emax
    Et = Bess.Et  # Instanteneous energy stored in the battery
    Eff = Bess.Efficiency*100
    soc_min = Bess.soc_min
    conductors = ".".join(map(str, Terminals))

    new_bat = f"New Storage.Bess_{name}_{bus} bus1={bus}.{conductors} DispMode=DEFAULT State={state} Phases={Phases} Conn={Conn} kV={kV} kW={kW} kWhRated={Cmax} kWhstored={Et} %EffCharge={Eff} %IdlingkW=0 %EffDischarge={Eff} %reserve={soc_min} %X=0"
    
    return new_bat


def construct_bess(batteries):

    ids = batteries['Id'].values
    list_bess_objects = []

    for id in ids:
        bess = Bess(id, batteries.loc[batteries['Id'] == id, 'Bus_node'].values[0], batteries.loc[batteries['Id'] == id, 'Phases'].values[0],
                    batteries.loc[batteries['Id'] == id, 'Conn'].values[0], batteries.loc[batteries['Id'] == id, 'kV'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'Pmax'].values[0], batteries.loc[batteries['Id'] == id, 'Terminals'].values[0],
                    batteries.loc[batteries['Id'] == id, 'Einit(%)'].values[0], batteries.loc[batteries['Id'] == id, 'Cmax'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'SOC_min(%)'].values[0], batteries.loc[batteries['Id'] == id, 'SOC_max(%)'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'Efficiency'].values[0])
        list_bess_objects.append(bess)

    return list_bess_objects

def get_BessPower(dss,timestep):

    batteries = dss.Storages.AllNames()
    bess_power_list = []

    for bat in batteries:
            dss.Circuit.SetActiveElement(f'Storage.{bat}')
            powers = dss.CktElement.Powers()
            Et = float(dss.Properties.Value('kWhstored'))
            SOC = float(dss.Properties.Value('%stored'))
            active_power = -sum(powers[::2])  #  Sum the active power
            reactive_power = -sum(powers[1::2])  # Sum the reacti power
            bat_line = [timestep, bat, round(active_power,4),round(reactive_power,4),round(Et,2),round(SOC/100,2)]
            bess_power_list.append(bat_line)

    return bess_power_list

class Bess:
    def __init__(self, id, buss_node, Phases,Conn, kV, Pmax,Terminals, Einit, Cmax, soc_min,soc_max, Efficiency,state='IDLING'):
        self.id = id
        self.bus_node = buss_node
        self.Phases = Phases
        self.Conn = Conn
        self.kV = kV
        self.Pmax = Pmax
        self.Terminals = Terminals
        self.Pt = 0
        self.soc_min = soc_min
        self.soc_max = soc_max
        self.SOC = (Einit/100)
        self.Et = self.SOC * Cmax
        self.Cmax = Cmax
        self.Emax = (soc_max/100) * Cmax
        self.Emin = (soc_min/100) * Cmax
        self.Efficiency = Efficiency
        self.state = state

    def update_power(self, new_power):
        """
        Change the actual power of the battery.
        kw > 0: Charging.
        kw < 0: Discharging.
        """
        self.Pt = new_power

    def update_energy(self, Et):
        """
        Change the energy storaged off battery with timestep in min.
        """
        self.Et = Et
    
    def update_soc(self,soc):
        self.SOC = soc
    
    def get_Pt(self):
        return self.Pt
    
    def get_Et(self):
        return self.Et
    
    def update_state(self,state):
        self.state = state
    
    def update_bus(self,bus):
        self.bus_node = bus
        
# Function to update Bess properties based of kind of operation
def operate_bess(kind, i, interval, demand_prev,bess_list):
    if kind == "Smoothing":
        for bess in bess_list:
            next_bess_power, soc, energy, state = smoothing_operation(i,interval,demand_prev,sigma=90,bess_object=bess)
            bess.update_power(next_bess_power)
            bess.update_energy(energy)
            bess.update_soc(soc)
            bess.update_state(state)
    elif kind == "Simple":
        for bess in bess_list:
            next_bess_power, soc, energy, state = zero_demand(i, interval, demand_prev, bess)
            bess.update_power(next_bess_power)
            bess.update_energy(energy)
            bess.update_soc(soc)
            bess.update_state(state)
    
    elif kind == "Forecasting":
        for bess in bess_list:
            next_bess_power, soc, energy, state = forecast_operation(i,interval,demand_prev,sigma=90,bess_object=bess)
            bess.update_power(next_bess_power)
            bess.update_energy(energy)
            bess.update_soc(soc)
            bess.update_state(state)

##------------------------------------------------------------Functions to Operate Bess-----------------------------------------###

# Power smoothing Function
def smoothing_operation(i, timestep, demand, sigma, bess_object):

    # # Values of demand
    # prev_demand = demand[i - 1]
    actual_demand = demand[-1]
    # next_demand = demand[i+1]
    

    # # Gauss calculus
    # vec_gauss = [prev_demand, actual_demand, next_demand]  # Vector for Gaussian filter
    vec_gauss = demand  # Vector for Gaussian filter

    # get the past 6 values and next 6 values in demand starting from i
    # vec_gauss = demand[i-6:i+6]  # Vector for Gaussian filter
    gauss_value = gaussian_filter1d(vec_gauss, sigma=sigma, radius=11)[-1]  # Value used to define BESS power

    # Define the next BESS power based on actual demand and Gaussian value
    PBessSeg = (actual_demand - gauss_value)

    # Actual state of charge of battery
    Soc = bess_object.SOC

    if PBessSeg > 0:  # Bateria vai descarregar
        state = 'DISCHARGING'
        if PBessSeg > bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = PBessSeg
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]

    else:  # Bateria vai carregar
        state = 'CHARGING'
        if PBessSeg < -bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = -PBessSeg
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]
 
# Function to reduce to zero the power demand from energy company
def zero_demand(i,timestep, demand,bess_object):

    # Calculate the next demand based on mean of the previous 3 time steps
    PBessSeg = demand[-1]
    Soc = bess_object.SOC
    if PBessSeg > 0:  # Bateria vai descarregar
        state = 'DISCHARGING'
        if PBessSeg > bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = PBessSeg
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]

    else:  # Bateria vai carregar
        state = 'CHARGING'
        if PBessSeg < -bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = -PBessSeg
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]


# Function to operate the BESS based on the forecasted demand
def forecast_operation(i,timestep, demand, sigma, bess_object):

    # Values of demand
    if (i>161):
        # # Values of demand
        # prev_demand = demand[0]
        actual_demand = demand[-1]
        # next_demand = demand[2]
        
        # get the past 6 values and next 6 values in demand starting from i
        vec_gauss = demand
        gauss_value = gaussian_filter1d(vec_gauss, sigma=sigma, radius=11)[-1]  # Value used to define BESS power

        # Define the next BESS power based on actual demand and Gaussian value
        PBessSeg = (actual_demand - gauss_value)
    else:
        actual_demand = demand[-1]
        
        # # Gauss calculus
        vec_gauss = demand  # Vector for Gaussian filter

        # get the past 6 values and next 6 values in demand starting from i
        # vec_gauss = demand[i-6:i+6]  # Vector for Gaussian filter
        gauss_value = gaussian_filter1d(vec_gauss, sigma=sigma, radius=11)[-1]  # Value used to define BESS power

        # Define the next BESS power based on actual demand and Gaussian value
        PBessSeg = (actual_demand - gauss_value)


    # Actual state of charge of battery
    Soc = bess_object.SOC

    if PBessSeg > 0:  # Bateria vai descarregar
        state = 'DISCHARGING'
        if PBessSeg > bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = PBessSeg
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]

    else:  # Bateria vai carregar
        state = 'CHARGING'
        if PBessSeg < -bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = -PBessSeg
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]
            

def kalman_operation(i,timestep, demand, sigma, bess_object):

    # Values of demand
    if (i>161):

        # Pegue os valores reais
        real_values = demand[:-1]
        prediction = demand[-1]  # previsão da LSTM

        kf = KalmanFilter(dim_x=1, dim_z=1)
        kf.x = np.array([[real_values[-1]]])
        kf.F = np.array([[1]])
        kf.H = np.array([[1]])
        kf.P *= 1000.
        kf.R = 0.1
        kf.Q = 0.01

        # Alimente o filtro com valores reais
        for z in real_values:
            kf.predict()
            kf.update(z)

        # Agora use a previsão LSTM como o próximo passo de atualização
        kf.predict()
        kf.update(prediction)

        kalman_filtered_demand = float(kf.x)
        PBessSeg = prediction - kalman_filtered_demand
        
    else:
        actual_demand = demand[-1]
        
        # # Gauss calculus
        vec_gauss = demand  # Vector for Gaussian filter

        # get the past 6 values and next 6 values in demand starting from i
        # vec_gauss = demand[i-6:i+6]  # Vector for Gaussian filter
        gauss_value = gaussian_filter1d(vec_gauss, sigma=sigma, radius=11)[-1]  # Value used to define BESS power

        # Define the next BESS power based on actual demand and Gaussian value
        PBessSeg = (actual_demand - gauss_value)


    # Actual state of charge of battery
    Soc = bess_object.SOC

    if PBessSeg > 0:  # Bateria vai descarregar
        state = 'DISCHARGING'
        if PBessSeg > bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = PBessSeg
            Bess_E_seg = bess_object.Et - Pseg * (timestep / 60) * (1 / bess_object.Efficiency)  # Energia da bateria no instante seguinte

            if Bess_E_seg < bess_object.Emin:  # Energia seguinte menor que a mínima permitida
                Pseg = (bess_object.Et - bess_object.Emin) / (timestep / 60)  # Descarregar para atingir no máximo a capacidade mínima
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin,state]
        
            else:  # Descarrega com a potência máxima e a energia seguinte é a calculada
                return [Pseg, Soc - (Pseg * (timestep / 60) * (1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg,state]

    else:  # Bateria vai carregar
        state = 'CHARGING'
        if PBessSeg < -bess_object.Pmax:  # Potência seguinte maior que a máxima
            Pseg = bess_object.Pmax
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]
        else:
            Pseg = -PBessSeg
            Bess_E_seg = bess_object.Et + Pseg * (timestep / 60) * bess_object.Efficiency  # Energia da bateria no instante seguinte

            if Bess_E_seg > bess_object.Emax:  # Energia seguinte maior que a máxima permitida
                Pseg = (bess_object.Emax - bess_object.Et) / (timestep / 60)  # Carregar para atingir no máximo a capacidade mínima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), bess_object.Emax,state]
            
            else:  # Carrega com a potência máxima
                return [-Pseg, Soc + (Pseg * (timestep / 60) * bess_object.Efficiency / bess_object.Cmax), Bess_E_seg,state]