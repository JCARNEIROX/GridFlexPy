import warnings
import opendssdirect as dss
import pandas as pd
import os
from modules.read_spreadsheet import read_file_xlsx
from modules.get_general_informations import get_informations
from modules.bess import construct_bess,bess_operation,simple_bess
from modules.generator import construct_generators
from modules.load import construct_loads
from modules.powerflow import power_flow
from modules.plots import plot, display_graph,save_fig,plot_bus_voltages
from modules.utils import save_csv
import time as t

# # Input and output paths
# path_xlsx = os.getcwd() + '/data/spreadsheets/'
# path_dss = os.getcwd() + '/data/dss_files/'	
# output_csv = os.getcwd() + '/data/output/csv/'
# output_img = os.getcwd() + '/data/output/img/'

# # Name of dss file
# file_dss = path_dss + 'ModelagemTeste.dss' 



# def return_general_informations():
#     """
#     Return the general informations of the spreadsheet
#     """
#     file_contents = read_file_xlsx(path_xlsx+'teste_sheet.xlsx')
#     general_informations = file_contents['General']
#     general_informations = get_informations(general_informations)
#     return general_informations

# def return_bess():
#     """
#     Return the batteries of the spreadsheet
#     """
#     file_contents = read_file_xlsx(path_xlsx+'teste_sheet.xlsx')
#     batteries = file_contents['BESS']
#     bess_list = construct_bess(batteries)
#     return bess_list

# def return_generators():
#     """
#     Return the generators of the spreadsheet
#     """
#     file_contents = read_file_xlsx(path_xlsx+'teste_sheet.xlsx')
#     generators = file_contents['Generators']
#     generators_list = construct_generators(generators)
#     return generators_list

# def return_loads():
#     """
#     Return the loads of the spreadsheet
#     """

#     file_contents = read_file_xlsx(path_xlsx+'teste_sheet.xlsx')
#     loads = file_contents['Loads']
#     loads_list = construct_loads(loads)
#     return loads_list

# def run_powerflow():
#     power_flow(return_general_informations(),file_dss,return_bess(),return_generators(),return_loads(),dss)
#     return

# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'

def run(name_spreadsheet,name_dss):
        
    # Read the file and
    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)

    # Read the file of forecasted generation
    file_pv = pd.read_csv(path_generators + 'pv_generation_prev.csv')
    pv_forec = file_pv["Ppower"].values

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
    columns_power = ['Timestep','Name','P(kW)','Q(kvar)']
    power_df1 = pd.DataFrame(columns=columns_power)

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
    columns_bess = ['Timestep','Bess_Id','P(kW)','E(kWh)','SOC']
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
            bus_power,power_df,branch_df,voltage_df,line_voltage = power_flow(timestep,file_dss,bess_list,generators_list,loads_list,dss)
            # Concatenate the dataframes
            bus_power_df1 = pd.concat([bus_power_df1,bus_power],ignore_index=True) # Store the power at each bus
            voltage_df1 = pd.concat([voltage_df1,voltage_df],ignore_index=True) # Store the voltages at each bus
            power_df1 = pd.concat([power_df1,power_df],ignore_index=True) # Store the Load,Generation,Delivered and Losses powers in circuit
            branch_df1 = pd.concat([branch_df1,branch_df],ignore_index=True) # Store the branch flows
            voltage_line_df = pd.concat([voltage_line_df,line_voltage],ignore_index=True) # Store the line voltage


            #Extract all values from column "Load" in power_df1 dataframe
            load_power = power_df1.loc[power_df1['Name']=='Load','P(kW)'].values
            # Extract the actual value of generation
            gen_power = power_df1.loc[power_df1['Name']=='Generation','P(kW)'].values
            gen_forec = pv_forec[i+1]
            # Extract the values from column "Demand" in power_df1 dataframe
            demand = power_df1.loc[power_df1['Name']=='Demand','P(kW)'].values

            
            if i>2: # Next 3 iterations to initiate the operation of bess
                #Call the function of bess operation and manage all batteries
                for bess in bess_list:
                    # next_bess_power,soc,energy = bess_operation(i,interval,demand,load_power,gen_power,gen_forec,alpha=0.5,bheta=0.5,sigma=45,bess_object=bess)
                    next_bess_power,soc,energy = simple_bess(i,interval,demand,bess)
                    bess.update_power(next_bess_power)
                    bess.update_energy(energy)
                    bess.update_soc(soc)
                    new_line_bess = pd.DataFrame([[timestep, bess.id, round(next_bess_power,4),round(energy,4),round(soc,4)]], columns=columns_bess)
                    bess_power_df = pd.concat([bess_power_df,new_line_bess],ignore_index=True)
            else:
                # Dont atuate the bess in the first 3 iterations and actualizate dataframe with the defaut values
                for bess in bess_list:
                    new_line_bess = pd.DataFrame([[timestep, bess.id, round(bess.Pt,4),round(bess.Et,4),round(bess.SOC,4)]], columns=columns_bess)
                    bess_power_df = pd.concat([bess_power_df,new_line_bess],ignore_index=True)
            

        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

    return bus_power_df1,power_df1,branch_df1,voltage_df1,voltage_line_df,bess_power_df,time_range
    



    
    