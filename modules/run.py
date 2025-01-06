import warnings
import opendssdirect as dss
import pandas as pd
import os
from modules.read_spreadsheet import read_file_xlsx
from modules.get_general_informations import get_informations
from modules.bess import construct_bess,smoothing_operation,simple_bess,operate_bess
from modules.generator import construct_generators
from modules.load import construct_loads,construct_lights
from modules.powerflow import power_flow,power_flow_bess
from modules.plots import plot, display_graph,save_fig,plot_bus_voltages
from modules.utils import save_csv
import time as t

#Ingore warnings to display on console
warnings.filterwarnings("ignore")


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'
path_forecast = os.getcwd() + '/data/forecasts/'


def run(name_spreadsheet,name_dss,bus,kind='NoOperation'):
        
    # Read the file and
    file_contents = read_file_xlsx(path_xlsx+name_spreadsheet)

    # Get the content of each page of the spreadsheet
    general_informations = file_contents['General']
    batteries = file_contents['BESS']
    generators = file_contents['Generators']
    loads = file_contents['Loads']
    public_ilumination = file_contents['Public_Ilumination']

    # Get the general informations
    general_informations = get_informations(general_informations)
    bess_list = construct_bess(batteries)
    
    generators_list = construct_generators(generators)
    loads_list = construct_loads(loads)
    lights_list = construct_lights(public_ilumination)
    

    #Run the power flow
    file_dss = path_dss + name_dss 
    date_ini = general_informations.start_date
    date_end = general_informations.end_date
    interval = general_informations.timestep

    #All columns to create each dataframe
    columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
    columns_power = ['Timestep','P(kW)','Q(kvar)']
    columns_branch = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
    columns_bus_voltage = ['Timestep','Bus','Voltage (p.u.)']
    columns_bess = ['Timestep','Bess_Id','P(kW)','Q(kVar)','E(kWh)','SOC']

    #Create empty dataframes to store the values of loop
    bus_power_df1 = pd.DataFrame(columns=columns_bus)
    load_df1 = pd.DataFrame(columns=columns_power)
    generation_df1 = pd.DataFrame(columns=columns_power)
    demand_df1 = pd.DataFrame(columns=columns_power)
    losses_df1 = pd.DataFrame(columns=columns_power) 
    branch_df1 = pd.DataFrame(columns=columns_branch)
    voltage_df1 = pd.DataFrame(columns=columns_bus_voltage)
    bess_power_df = pd.DataFrame(columns=columns_bess)

    # Create empty arrays to store the new lines to be added to dataframes
    bus_power_list = []
    loaddf_list = []
    generationdf_list = []
    demanddf_list = []
    lossesdf_list = []
    branch_df_list = []
    voltage_df_list = []
    bess_power_list = []

    # Time range to iterate
    time_range = pd.date_range(date_ini, date_end, freq=f"{interval}T").to_list()

    # If the kind of operation is different from NoOperation, the BESS will be operated
    if not kind == 'NoOperation':

        # Read the file of forecasted demand
        file_demand = pd.read_csv(f"{path_forecast}demand/" + f'demand_NoOperation_year{name_dss.split('.')[0]}.csv')
        demand_prev = file_demand["P(kW)"].values

        # If bus is changed on a loop Update bus_node for BESS
        for bess in bess_list:
            bess.update_bus(bus)

        print('Power Flow Simulation Started')
        # Start the counter to mensure the time of execution
        start = t.time()
        for i,timestep in enumerate(time_range):
            print(f"Time: {timestep}")
            # Dont operate the BESS in the first three iterations
            if i>2:
                
                # Update bess power
                operate_bess(kind,i,interval,demand_prev,bess_list)

                # Run the power flow with the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow_bess(timestep,file_dss,bess_list,generators_list,loads_list,lights_list,dss)

                # Append the new lines
                bus_power_list.append(bus_power)
                loaddf_list.append(load)
                generationdf_list.append(generation)
                demanddf_list.append(demand_df)
                lossesdf_list.append(losses)
                branch_df_list.append(branch_df)
                voltage_df_list.append(bus_voltage)
                bess_power_list.append(bess)

            else:
                
                # Run the power flow without the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow_bess(timestep,file_dss,bess_list,generators_list,loads_list,lights_list,dss)

                # Append the new lines
                bus_power_list.append(bus_power)
                loaddf_list.append(load)
                generationdf_list.append(generation)
                demanddf_list.append(demand_df)
                lossesdf_list.append(losses)
                branch_df_list.append(branch_df)
                voltage_df_list.append(bus_voltage)
                bess_power_list.append(bess)

        # Print the time of execution of power flow
        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

        # Concatenate all dataframes
        bus_power_df1 = pd.concat(bus_power_list,ignore_index=True)
        load_df1 = pd.concat(loaddf_list,ignore_index=True)
        generation_df1 = pd.concat(generationdf_list,ignore_index=True)
        demand_df1 = pd.concat(demanddf_list,ignore_index=True)
        losses_df1 = pd.concat(lossesdf_list,ignore_index=True)
        branch_df1 = pd.concat(branch_df_list,ignore_index=True)
        voltage_df1 = pd.concat(voltage_df_list,ignore_index=True)
        bess_power_df = pd.concat(bess_power_list,ignore_index=True)

        return bus_power_df1,load_df1,generation_df1,demand_df1,losses_df1,branch_df1,voltage_df1,bess_power_df,time_range

    # If the kind of operation is NoOperation, the BESS will not be operated
    else:
        print('Power Flow Simulation Started')
        # Start the counter to mensure the time of execution
        start = t.time()
        for i,timestep in enumerate(time_range):
            print(f"Time: {timestep}")

            # Run the power flow without the operation of the BESS
            load,generation,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow(timestep,file_dss,generators_list,loads_list,lights_list,dss)

            # Append the new lines
            bus_power_list.append(bus_power)
            loaddf_list.append(load)
            generationdf_list.append(generation)
            demanddf_list.append(demand_df)
            lossesdf_list.append(losses)
            branch_df_list.append(branch_df)
            voltage_df_list.append(bus_voltage)
        
        # Print the time of execution of power flow
        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

        # Concatenate all dataframes
        bus_power_df1 = pd.concat(bus_power_list,ignore_index=True)
        load_df1 = pd.concat(loaddf_list,ignore_index=True)
        generation_df1 = pd.concat(generationdf_list,ignore_index=True)
        demand_df1 = pd.concat(demanddf_list,ignore_index=True)
        losses_df1 = pd.concat(lossesdf_list,ignore_index=True)
        branch_df1 = pd.concat(branch_df_list,ignore_index=True)
        voltage_df1 = pd.concat(voltage_df_list,ignore_index=True)
        
        return bus_power_df1,load_df1,generation_df1,demand_df1,losses_df1,branch_df1,voltage_df1,time_range

    

    
    



    
    
