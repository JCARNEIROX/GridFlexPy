
from scipy.ndimage import gaussian_filter,gaussian_filter1d
import numpy as np
import pandas as pd

def add_bat(Bess):
    """	
    Function to write a comand that will modify the power of the battery during the power flow simulation.
    """
    name = Bess.id
    state = Bess.state
    bus = str(Bess.bus_node).zfill(3)
    Phases = Bess.Phases
    kV = Bess.kV
    kW = Bess.Pt # Instanteneous power of the battery, kw>0: dischargin, kw<0: charging
    Cmax = Bess.Cmax
    Emax = Bess.Emax
    Et = Bess.Et  # Instanteneous energy stored in the battery
    Eff = Bess.Efficiency*100
    soc_min = Bess.soc_min

    new_bat = f"New Storage.Bess_{name}_bus_{bus} bus1=bus_{bus} DispMode=DEFAULT State={state} Phases={Phases} kV={kV} kW={kW} kWhRated={Cmax} kWhstored={Et} %EffCharge={Eff} %IdlingkW=0 %EffDischarge={Eff} %reserve={soc_min} %X=0"
    # new_bat = f"New Storage.Bess_{name}_bus_{bus} bus1=bus_{bus} DispMode=DEFAULT State={state} Phases={Phases} kV={kV} kW={kW} kWrated={Pmax} kWhRated={Emax} kWhstored={Et} %stored={SOC} %EffCharge={Eff} %IdlingkW=0 %EffDischarge={Eff} %reserve={soc_min} %X=0"
    # new_bat = f"New Load.Bess_{name}_bus_{bus} bus1=bus_{bus} Phases={Phases} Conn=wye kV={kV} kW={kW} kVAr=0 Model=1 Vminpu=0.92"
    
    return new_bat


def construct_bess(batteries):

    ids = batteries['Id'].values
    list_bess_objects = []

    for id in ids:
        bess = Bess(id, batteries.loc[batteries['Id'] == id, 'Bus_node'].values[0], batteries.loc[batteries['Id'] == id, 'Phases'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'kV'].values[0], batteries.loc[batteries['Id'] == id, 'Pmax'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'Einit(%)'].values[0], batteries.loc[batteries['Id'] == id, 'Cmax'].values[0],
                    batteries.loc[batteries['Id'] == id, 'SOC_min(%)'].values[0],batteries.loc[batteries['Id'] == id, 'SOC_max(%)'].values[0],
                    batteries.loc[batteries['Id'] == id, 'Efficiency'].values[0])
        list_bess_objects.append(bess)

    return list_bess_objects

def get_BessPower(dss,timestep):

    elements = dss.Circuit.AllElementNames()
    batteries = [element for element in elements if element.startswith("Storage.")]


    #Create a empty dataframe to store the bateries power
    columns_bess = ['Timestep','Bess_Id','P(kW)','Q(kVar)','E(kWh)','SOC']
    bess_power_df = pd.DataFrame(columns=columns_bess)

    for bat in batteries:
            dss.Circuit.SetActiveElement(bat)
            powers = dss.CktElement.Powers()
            name = bat.split('.')[1]
            Et = float(dss.Properties.Value('kWhstored'))
            SOC = float(dss.Properties.Value('%stored'))
            active_power = -sum(powers[::2])  #  Sum the active power
            reactive_power = -sum(powers[1::2])  # Sum the reacti power
            bat_line = pd.DataFrame([[timestep, name, round(active_power,4),round(reactive_power,4),round(Et,2),round(SOC/100,2)]], columns=columns_bess)
            bess_power_df = pd.concat([bess_power_df,bat_line],ignore_index=True)

    return bess_power_df

class Bess:
    def __init__(self, id, buss_node, Phases, kV, Pmax, Einit, Cmax, soc_min,soc_max, Efficiency,state='IDLING'):
        self.id = id
        self.bus_node = buss_node
        self.Phases = Phases
        self.kV = kV
        self.Pmax = Pmax
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
        

def bess_operation_load(i,timestep,demand,load,gen_power,gen_forec,alpha,bheta,sigma,bess_object):

    #Values for pv generation
    pv_med = np.mean(gen_power[i:i-3:-1])
    next_pv = (alpha * gen_forec) + (bheta * pv_med) # wheighting for the forecasting of pv generation

    #Mean of the previous 3 time steps
    load_prev = np.mean(load[i:i-3:-1])
    next_demand = load_prev-next_pv

    #Values of demand
    actual_demand = demand[i]
    prev_demand = demand[i-1]

    #Gauss calculus
    vec_gauss = [prev_demand,actual_demand,next_demand] # Vetor a ser aplicado o Filtro Gaussiano
    gauss_value = gaussian_filter1d(vec_gauss,sigma=sigma,radius=1)[1] #Valor a ser utilizado para definir a potência do BESS

    #Define the next bess_power based on the actual demand and gaus value returned
    PBessSeg = (actual_demand-gauss_value)

    #Actual state of charge of battery
    Soc = bess_object.SOC

    if PBessSeg> 0 : #Bateria vai carregar

      if PBessSeg>bess_object.Pmax: #Potência seguinte maior que a maxima
         Pseg = bess_object.Pmax
         Bess_E_seg = bess_object.Et + Pseg*(timestep/60)*bess_object.Efficiency # Energia da bateria no instante seguinte

         if Bess_E_seg>bess_object.Emax: #Energia seguinte maior que máxima permitida
            Pseg = (bess_object.Emax-bess_object.Et)/(timestep/60) #carrega para atingir capacidade máxima
            if Pseg>bess_object.Pmax:
               Pseg = bess_object.Pmax
               # print('Aqui1')
               return [Pseg,Soc + (Pseg*(timestep/60)*bess_object.Efficiency / bess_object.Cmax),bess_object.Emax]
            else:
               # print('Aqui2')
               return [Pseg,Soc + (Pseg*(timestep/60)*bess_object.Efficiency / bess_object.Cmax),bess_object.Emax]

         else: #Carrega com a potência máxima
            # print('Aqui3')
            return [Pseg,Soc + (Pseg*(timestep/60)*bess_object.Efficiency / bess_object.Cmax),Bess_E_seg]
         
      else: # Potência menor que a potência máxima
         Pseg = PBessSeg
         Bess_E_seg = bess_object.Et + Pseg*(timestep/60)*bess_object.Efficiency # Energia da bateria no instante seguinte

         if Bess_E_seg>bess_object.Emax: #Energia seguinte maior que máxima permitida
            Pseg = (bess_object.Emax-bess_object.Et)/(timestep/60) #carrega para atingir capacidade máxima
            if Pseg>bess_object.Pmax:
               Pseg = bess_object.Pmax
               # print('Aqui4')
               return [Pseg,Soc + (Pseg*(timestep/60)*bess_object.Efficiency / bess_object.Cmax),bess_object.Emax]
            else:
               # print('Aqui5')
               return [Pseg,Soc + (Pseg*(timestep/60)*bess_object.Efficiency / bess_object.Cmax),bess_object.Emax]

         else: #Carrega com a potência seguinte definida
            # print('Aqui6')
            return [Pseg,Soc + (Pseg*(timestep/60)*bess_object.Efficiency / bess_object.Cmax),Bess_E_seg]

    else: # Bateria vai descarregar
      if PBessSeg<-bess_object.Pmax: #Potência seguinte maior que a maxima
         Pseg = -bess_object.Pmax
         Bess_E_seg = bess_object.Et + Pseg*(timestep/60)*(1 / bess_object.Efficiency) # Energia da bateria no instante seguinte

         if Bess_E_seg<bess_object.Emin: #Energia seguinte menor que a máxima permitida
            Pseg = (bess_object.Emin-bess_object.Et)/(timestep/60) #descarregar para atingir no máximo a capacidade mínima
            if Pseg<-bess_object.Pmax:
               Pseg = -bess_object.Pmax
               # print('Aqui7')
               return [Pseg,Soc + ( Pseg*(timestep/60)*(1 / bess_object.Efficiency) / bess_object.Cmax),bess_object.Emin]
            else:
               # print('Aqui8')
               return [Pseg,Soc + ( Pseg*(timestep/60)*(1 / bess_object.Efficiency) / bess_object.Cmax),bess_object.Emin]

         else: #Descarrega com a potência máxima
            # print('Aqui9')
            return [Pseg, Soc + ( Pseg*(timestep/60)*(1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg] 
      else:
          Pseg = PBessSeg
          Bess_E_seg = bess_object.Et + Pseg*(timestep/60)*(1 / bess_object.Efficiency) # Energia da bateria no instante seguinte

          if Bess_E_seg<bess_object.Emin: #Energia seguinte menor que a minima permitida
              Pseg = (bess_object.Emin-bess_object.Et)/(timestep/60) #descarrega para atingir no máximo a capacidade mínima
              if Pseg<-bess_object.Pmax:
                Pseg = -bess_object.Pmax
               #  print('Aqui10')
                return [Pseg,Soc + ( Pseg*(timestep/60)*(1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin]
              else:
               #  print('Aqui11')
                return [Pseg,Soc + ( Pseg*(timestep/60)*(1 / bess_object.Efficiency) / bess_object.Cmax), bess_object.Emin]

          else: #Descarrega com a potência máxima
            #   print('Aqui12')
              return [Pseg, Soc + ( Pseg*(timestep/60)*(1 / bess_object.Efficiency) / bess_object.Cmax), Bess_E_seg]   
          

          
def bess_operation(i, timestep, demand, load, gen_power, gen_forec, alpha, bheta, sigma, bess_object):
    # Values for PV generation
    # pv_med = np.mean(gen_power[i - 3:i])
    # next_pv = (alpha * gen_forec) + (bheta * pv_med)  # Weighting for the forecasting of PV generation

    # Mean of the previous 3 time steps
    # load_prev = np.mean(load[i - 3:i])
    # next_demand = load_prev - next_pv
    next_demand = demand[i+1]

    # Values of demand
    actual_demand = demand[i]
    prev_demand = demand[i - 1]

    # Gauss calculus
    vec_gauss = [prev_demand, actual_demand, next_demand]  # Vector for Gaussian filter
    gauss_value = gaussian_filter1d(vec_gauss, sigma=sigma, radius=1)[1]  # Value used to define BESS power

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
 


def simple_bess(timestep, demand,bess_object):

    # Calculate the next demand based on mean of the previous 3 time steps
    PBessSeg = demand
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

def simple_bess_load(timestep, demand,bess_object):

    # Calculate the next demand based on mean of the previous 3 time steps
    PBessSeg = demand
    Soc = bess_object.SOC
    if PBessSeg> 0 : #Bateria vai carregar
      if PBessSeg>bess_object.Pmax: #Potência seguinte maior que a maxima
         Pseg = bess_object.Pmax
         Bess_E_seg = bess_object.Et+Pseg*(timestep/60) * bess_object.Efficiency # Energia da bateria no instante seguinte

         if Bess_E_seg>bess_object.Emax: #Energia seguinte maior que máxima permitida
            Pseg = (bess_object.Emax-bess_object.Et)/(timestep/60) #carrega para atingir capacidade máxima               
            return [Pseg,Soc + (Pseg*(timestep/60) * bess_object.Efficiency/bess_object.Cmax),bess_object.Emax]
    
         else: #Carrega com a potência máxima
            # print('Aqui3')
            return [Pseg,Soc + (Pseg*(timestep/60) * bess_object.Efficiency/bess_object.Cmax),Bess_E_seg]
         
      else: # Potência menor que a potência máxima
         Pseg = PBessSeg
         Bess_E_seg = bess_object.Et + Pseg*(timestep/60) # Energia da bateria no instante seguinte

         if Bess_E_seg>bess_object.Emax: #Energia seguinte maior que máxima permitida
            Pseg = (bess_object.Emax-bess_object.Et)/(timestep/60) #carrega para atingira capacidade máxima
            return [Pseg,Soc + (Pseg*(timestep/60) * bess_object.Efficiency/bess_object.Cmax),bess_object.Emax]

         else: #Carrega com a potência seguinte definida
            # print('Aqui6')
            return [Pseg,Soc + (Pseg*(timestep/60) * bess_object.Efficiency/bess_object.Cmax),Bess_E_seg]

    else: # Bateria vai descarregar
      if PBessSeg<-bess_object.Pmax: #Potência seguinte maior que a maxima
         Pseg = -bess_object.Pmax
         Bess_E_seg = bess_object.Et+ Pseg * (timestep/60) * (1 / bess_object.Efficiency) # Energia da bateria no instante seguinte

         if Bess_E_seg<bess_object.Emin: #Energia seguinte menor que a máxima permitida
            Pseg = (bess_object.Emin-bess_object.Et)/(timestep/60) #descarregar para atingir no máximo 10% da capacidade
            return [Pseg,Soc + (Pseg*(timestep/60) * (1 / bess_object.Efficiency)/ bess_object.Cmax),bess_object.Emin]
            
         else: #Descarrega com a potência máxima e a energia seguinte é a calculada
            # print('Aqui9')
            return [Pseg,Soc + (Pseg*(timestep/60) * (1 / bess_object.Efficiency) / bess_object.Cmax),Bess_E_seg]
      else:
          Pseg = PBessSeg
          Bess_E_seg = bess_object.Et + (Pseg*(timestep/60) * (1 / bess_object.Efficiency)) # Energia da bateria no instante seguinte

          if Bess_E_seg<bess_object.Emin: #Energia seguinte menor que a máxima permitida
            Pseg = (bess_object.Emin-bess_object.Et)/(timestep/60) #descarregar para atingir no máximo 10% da capacidade
            return [Pseg,Soc + (Pseg*(timestep/60) * (1 / bess_object.Efficiency)/ bess_object.Cmax),bess_object.Emin]
            
          else: #Descarrega com a potência máxima e a energia seguinte é a calculada
            # print('Aqui9')
            return [Pseg,Soc + (Pseg*(timestep/60) * (1 / bess_object.Efficiency) / bess_object.Cmax),Bess_E_seg]

          