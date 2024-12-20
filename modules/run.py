import warnings
import opendssdirect as dss
import pandas as pd
import os
from modules.read_spreadsheet import read_file_xlsx
from modules.get_general_informations import get_informations
from modules.bess import construct_bess,bess_operation,simple_bess,simple_bess_load
from modules.generator import construct_generators
from modules.load import construct_loads
from modules.powerflow import power_flow
from modules.plots import plot, display_graph,save_fig,plot_bus_voltages
from modules.utils import save_csv
import time as t


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'

def return_general_informations(name_spreadsheet):
    """
    Return the general informations of the spreadsheet
    """
    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)
    general_informations = file_contents['General']
    general_informations = get_informations(general_informations)
    return general_informations

def return_bess(name_spreadsheet):
    """
    Return the batteries of the spreadsheet
    """
    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)
    batteries = file_contents['BESS']
    bess_list = construct_bess(batteries)
    return bess_list

def return_generators(name_spreadsheet):
    """
    Return the generators of the spreadsheet
    """
    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)
    generators = file_contents['Generators']
    generators_list = construct_generators(generators)
    return generators_list

def return_loads(name_spreadsheet):
    """
    Return the loads of the spreadsheet
    """

    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)
    loads = file_contents['Loads']
    loads_list = construct_loads(loads)
    return loads_list

def run_powerflow(file_dss):
    power_flow(return_general_informations(),file_dss,return_bess(),return_generators(),return_loads(),dss)
    return



def run(name_spreadsheet,name_dss,bus,kind='Smooth'):
        
    # Read the file and
    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)

    # Read the file of forecasted generation
    file_pv = pd.read_csv(path_generators + 'pv_generation_prev.csv')
    pv_forec = file_pv["Ppower"].values

    # Read the file of forecasted demand
    file_demand = pd.read_csv(output_csv + 'demand_NoOperation.csv')
    demand_prev = file_demand["P(kW)"].values

    # Get the content of each page of the spreadsheet
    general_informations = file_contents['General']
    batteries = file_contents['BESS']
    generators = file_contents['Generators']
    loads = file_contents['Loads']

    # Get the general informations
    general_informations = get_informations(general_informations)
    bess_list = construct_bess(batteries)
    generators_list = construct_generators(generators)
    loads_list = construct_loads(loads)
    

    #Run the power flow
    file_dss = path_dss + name_dss 
    date_ini = general_informations.start_date
    date_end = general_informations.end_date
    interval = general_informations.timestep

    #Create a empty dataframe to store the active/reactive power demand at each bus
    columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
    bus_power_df1 = pd.DataFrame(columns=columns_bus)

    #Create a empty dataframe to store the active/reactive power delivered to circuit and the losses at actual timestep
    columns_power = ['Timestep','P(kW)','Q(kvar)']
    load_df1 = pd.DataFrame(columns=columns_power)
    generation_df1 = pd.DataFrame(columns=columns_power)
    demand_df1 = pd.DataFrame(columns=columns_power)
    losses_df1 = pd.DataFrame(columns=columns_power)

    #Create a empty dataframe to store the currents, active/reactive power and losses at each line
    columns_branch = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
    branch_df1 = pd.DataFrame(columns=columns_branch)

    #Create a empty dataframe to store the voltages
    columns_bus_voltage = ['Timestep','Bus','Voltage']
    voltage_df1 = pd.DataFrame(columns=columns_bus_voltage)

    #Create a empty dataframe to store the source line voltage
    columns_voltage = ['Timestep','Line_Voltage']
    voltage_line_df = pd.DataFrame(columns=columns_voltage)

    #Create a empty dataframe to store the bateries power
    columns_bess = ['Timestep','Bess_Id','P(kW)','Q(kVar)','E(kWh)','SOC']
    bess_power_df = pd.DataFrame(columns=columns_bess)

    # Use warnings to ignore FutureWarnings
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        start = t.time()
        # Time range to iterate
        time_range = pd.date_range(date_ini, date_end, freq=str(interval) + 'T')
        print('Power Flow Simulation Started')
        for i in range(len(time_range)):
            timestep = time_range[i]

            # Dont operate the BESS in the first three iterations
            if i>2:

                #Extract all values from column "Load" in power_df1 dataframe
                load_power = load_df1['P(kW)'].values

                # Extract the actual value of generation
                gen_power = generation_df1['P(kW)'].values
                gen_forec = pv_forec[i+1]
                # Extract the values from column "Demand" in power_df1 dataframe
                demand = demand_df1['P(kW)'].values
                demand_forec = demand_prev[i]
                # Extract the values from column "Losses" in power_df1 dataframe
                losses = losses_df1['P(kW)'].values

                # Define the next power of BESS based on the operation
                if kind == 'Smoothing':
                    for bess in bess_list:
                        next_bess_power,soc,energy = bess_operation(i,interval,demand,load_power,gen_power,gen_forec,alpha=0.5,bheta=0.5,sigma=45,bess_object=bess)
                        bess.update_power(next_bess_power)
                        bess.update_energy(energy)
                        bess.update_soc(soc)
                        bess.update_bus(bus)

                elif kind == 'Simple':
                    for bess in bess_list:
                        # next_bess_power,soc,energy = simple_bess_load(interval,demand_forec,bess) # Voltar depois para demand e na função de operação
                        next_bess_power,soc,energy,state = simple_bess(interval,demand_forec,bess) # Voltar depois para demand e na função de operação
                        bess.update_power(next_bess_power)
                        bess.update_energy(energy)
                        bess.update_soc(soc)
                        bess.update_state(state)
                        bess.update_bus(bus)
            
                # elif kind == 'NoOperation':
                #     for bess in bess_list:
                #         bess.update_bus(bus)
                #         new_line_bess = pd.DataFrame([[timestep, bess.id, round(bess.Pt,4),round(bess.Et,4),round(bess.SOC,4)]], columns=columns_bess)
                #         bess_power_df = pd.concat([bess_power_df,new_line_bess],ignore_index=True)
                
                # Run the power flow with the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,line_voltage,branch_df = power_flow(timestep,file_dss,bess_list,generators_list,loads_list,dss)

                # Concatenate the new lines in their dataframes
                bus_power_df1 = pd.concat([bus_power_df1,bus_power],ignore_index=True) # Store the power at each bus
                voltage_df1 = pd.concat([voltage_df1,bus_voltage],ignore_index=True) # Store the voltages at each bus
                load_df1 = pd.concat([load_df1,load],ignore_index=True) # Store the total load powers in the circuit
                generation_df1 = pd.concat([generation_df1,generation],ignore_index=True) # Store the total power generated
                demand_df1 = pd.concat([demand_df1,demand_df],ignore_index=True) # Store the demand in the circuit
                losses_df1 = pd.concat([losses_df1,losses],ignore_index=True) # Store the total losses
                branch_df1 = pd.concat([branch_df1,branch_df],ignore_index=True) # Store the branch flows
                voltage_line_df = pd.concat([voltage_line_df,line_voltage],ignore_index=True) # Store the line voltage of source voltage
                bess_power_df = pd.concat([bess_power_df,bess],ignore_index=True) # Store the power of the BESS

            else:
                # Update bus_node for BESS
                for bess in bess_list:
                    bess.update_bus(bus)

                # Run the power flow with the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,line_voltage,branch_df = power_flow(timestep,file_dss,bess_list,generators_list,loads_list,dss)

                # Concatenate the new lines in their dataframes
                bus_power_df1 = pd.concat([bus_power_df1,bus_power],ignore_index=True) # Store the power at each bus
                voltage_df1 = pd.concat([voltage_df1,bus_voltage],ignore_index=True) # Store the voltages at each bus
                load_df1 = pd.concat([load_df1,load],ignore_index=True) # Store the total load powers in the circuit
                generation_df1 = pd.concat([generation_df1,generation],ignore_index=True) # Store the total power generated
                demand_df1 = pd.concat([demand_df1,demand_df],ignore_index=True) # Store the demand in the circuit
                losses_df1 = pd.concat([losses_df1,losses],ignore_index=True) # Store the total losses
                branch_df1 = pd.concat([branch_df1,branch_df],ignore_index=True) # Store the branch flows
                voltage_line_df = pd.concat([voltage_line_df,line_voltage],ignore_index=True) # Store the line voltage of source voltage
                bess_power_df = pd.concat([bess_power_df,bess],ignore_index=True) # Store the power of the BESS

        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

    return bus_power_df1,load_df1,generation_df1,demand_df1,losses_df1,branch_df1,voltage_df1,voltage_line_df,bess_power_df,time_range
    



    
    
