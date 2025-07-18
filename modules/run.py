# # Import all modules to run the simulation
from modules import read_file_xlsx
from modules import get_informations
from modules import construct_bess,operate_bess
from modules import construct_generators
from modules import construct_loads,construct_lights
from modules import power_flow,power_flow_bess
from modules.forecast import load_model,predict_demand_multi

#Built-in libraries
import time as t
import warnings
import opendssdirect as dss
import pandas as pd
import os
import numpy as np
import joblib

#Ingore warnings to display on console
warnings.filterwarnings("ignore")


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'
path_forecast = os.getcwd() + '/data/forecasts/'


def run(config:dict):
        
    # Read the file and
    file_contents = read_file_xlsx(path_xlsx+config['name_spreadsheet'])

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
    file_dss = path_dss + config['name_dss'] 
    date_ini = general_informations.start_date
    date_end = general_informations.end_date
    interval = general_informations.timestep

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
    if config['kind'] == 'Forecasting':
        #Load the model of prediction
        scaler_load = joblib.load(f"{path_forecast}demand/" + f"scaler_load_in{config['in_feature']}_seq{config['seq_len']}_hd{config['hidden_size']}_bt{config['batch_size']}.pkl")
        scaler_loss = joblib.load(f"{path_forecast}demand/" + f"scaler_loss_in{config['in_feature']}_seq{config['seq_len']}_hd{config['hidden_size']}_bt{config['batch_size']}.pkl")
        scaler_pv = joblib.load(f"{path_forecast}demand/" + f"scaler_pv_in{config['in_feature']}_seq{config['seq_len']}_hd{config['hidden_size']}_bt{config['batch_size']}.pkl")
        scaler_demand = joblib.load(f"{path_forecast}demand/" + f"scaler_target_in{config['in_feature']}_seq{config['seq_len']}_hd{config['hidden_size']}_bt{config['batch_size']}.pkl")
        
        path_model = f"{path_forecast}demand/" + f"lstm_model_multifeature_in{config['in_feature']}_seq{config['seq_len']}_hd{config['hidden_size']}_bt{config['batch_size']}.pth"
        model = load_model(path_model,config)
        
        #Load the file of flux smoothing
        file_demand = pd.read_csv(f"{path_forecast}demand/" + f'Demand_NoOperation_year_{config["name_dss"].split('.')[0]}.csv')
        file_demand['Timestep'] = pd.to_datetime(file_demand['Timestep'])
        
        
        # If bus is changed on a loop Update bus_node for BESS
        for bess in bess_list:
            bess.update_bus(config['bess_bus'])
        
        print('Power Flow Simulation Started')
        # Start the counter to mensure the time of execution
        start = t.time()
        for i,timestep in enumerate(time_range):

            if (i>config['seq_len']-1) and (config['kind'] == 'Forecasting'):
                load_vals = np.array([float(row[1]) for row in loaddf_list])
                loss_vals = np.array([float(row[1]) for row in lossesdf_list])
                pv_vals = np.array([float(row[1]) for row in generationdf_list])
                scalers= (scaler_load,scaler_loss,scaler_pv,scaler_demand)
                next_demand = predict_demand_multi(model,scalers,load_vals,loss_vals,pv_vals,i,window_size=config['seq_len'])
                # print(f"demand_prev: {next_demand}") # Debugging line, print the next demand
                
                demand_values = [d[1] for d in demanddf_list[i-config['past_values']:i]] 
                demand_values.append(next_demand[0])

                # Update bess power
                operate_bess(config['kind'],i,interval,demand_values,bess_list)

                # Run the power flow with the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow_bess(timestep,file_dss,bess_list,generators_list,loads_list,lights_list,dss)

                # Append the new lines
                bus_power_list.extend(bus_power)
                loaddf_list.append(load)
                generationdf_list.append(generation)
                demanddf_list.append(demand_df)
                lossesdf_list.append(losses)
                branch_df_list.extend(branch_df)
                voltage_df_list.extend(bus_voltage)
                bess_power_list.extend(bess)

                print(demanddf_list[i])
            else:

                # Run the power flow without the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow_bess(timestep,file_dss,bess_list,generators_list,loads_list,lights_list,dss)

                # Append the new lines
                bus_power_list.extend(bus_power)
                loaddf_list.append(load)
                generationdf_list.append(generation)
                demanddf_list.append(demand_df)
                lossesdf_list.append(losses)
                branch_df_list.extend(branch_df)
                voltage_df_list.extend(bus_voltage)
                bess_power_list.extend(bess)

                print(demanddf_list[i])

        # Print the time of execution of power flow
        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

        #All columns to create each dataframe
        columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
        columns_power = ['Timestep','P(kW)','Q(kvar)']
        columns_branch = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
        columns_bus_voltage = ['Timestep','Bus','Voltage (p.u.)']
        columns_bess = ['Timestep','Bess_Id','P(kW)','Q(kVar)','E(kWh)','SOC']

        #Create empty dataframes to store the values of loop
        bus_power_df1 = pd.DataFrame(bus_power_list,columns=columns_bus)
        load_df1 = pd.DataFrame(loaddf_list,columns=columns_power)
        generation_df1 = pd.DataFrame(generationdf_list,columns=columns_power)
        demand_df1 = pd.DataFrame(demanddf_list,columns=columns_power)
        losses_df1 = pd.DataFrame(lossesdf_list,columns=columns_power) 
        branch_df1 = pd.DataFrame(branch_df_list,columns=columns_branch)
        voltage_df1 = pd.DataFrame(voltage_df_list,columns=columns_bus_voltage)
        bess_power_df = pd.DataFrame(bess_power_list,columns=columns_bess)

        return bus_power_df1,load_df1,generation_df1,demand_df1,losses_df1,branch_df1,voltage_df1,bess_power_df,time_range
    
    elif (config['kind'] == 'Smoothing') or (config['kind'] == 'Simple'):
        
        #Load the file of flux smoothing
        file_demand = pd.read_csv(f"{path_forecast}demand/" + f'Demand_NoOperation_year_{config["name_dss"].split('.')[0]}.csv')
        file_demand['Timestep'] = pd.to_datetime(file_demand['Timestep'])
        
        # If bus is changed on a loop Update bus_node for BESS
        for bess in bess_list:
            bess.update_bus(config['bess_bus'])
        
        print('Power Flow Simulation Started')
        # Start the counter to mensure the time of execution
        start = t.time()
        for i,timestep in enumerate(time_range):
            # print(f"Time: {timestep},{i}")

            if (i>config['past_values']):
                # Get the next demand on the dataframe no operation
                demand_prev = file_demand[file_demand['Timestep'] == timestep]['P(kW)'].values[0]
                # Run Power Flow with the gaussian filter
                demand_values = [d[1] for d in demanddf_list[i-config['past_values']:i]]
                demand_values.append(demand_prev)
                # Update bess power
                operate_bess(config['kind'],i,interval,demand_values,bess_list)

                # Run the power flow with the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow_bess(timestep,file_dss,bess_list,generators_list,loads_list,lights_list,dss)

                # Append the new lines
                bus_power_list.extend(bus_power)
                loaddf_list.append(load)
                generationdf_list.append(generation)
                demanddf_list.append(demand_df)
                lossesdf_list.append(losses)
                branch_df_list.extend(branch_df)
                voltage_df_list.extend(bus_voltage)
                bess_power_list.extend(bess)

                print(demanddf_list[i])
            else:
                # Run the power flow without the operation of the BESS
                load,generation,bess,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow_bess(timestep,file_dss,bess_list,generators_list,loads_list,lights_list,dss)

                # Append the new lines
                bus_power_list.extend(bus_power)
                loaddf_list.append(load)
                generationdf_list.append(generation)
                demanddf_list.append(demand_df)
                lossesdf_list.append(losses)
                branch_df_list.extend(branch_df)
                voltage_df_list.extend(bus_voltage)
                bess_power_list.extend(bess)

                print(demanddf_list[i])
                

        # Print the time of execution of power flow
        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

        #All columns to create each dataframe
        columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
        columns_power = ['Timestep','P(kW)','Q(kvar)']
        columns_branch = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
        columns_bus_voltage = ['Timestep','Bus','Voltage (p.u.)']
        columns_bess = ['Timestep','Bess_Id','P(kW)','Q(kVar)','E(kWh)','SOC']

        #Create empty dataframes to store the values of loop
        bus_power_df1 = pd.DataFrame(bus_power_list,columns=columns_bus)
        load_df1 = pd.DataFrame(loaddf_list,columns=columns_power)
        generation_df1 = pd.DataFrame(generationdf_list,columns=columns_power)
        demand_df1 = pd.DataFrame(demanddf_list,columns=columns_power)
        losses_df1 = pd.DataFrame(lossesdf_list,columns=columns_power) 
        branch_df1 = pd.DataFrame(branch_df_list,columns=columns_branch)
        voltage_df1 = pd.DataFrame(voltage_df_list,columns=columns_bus_voltage)
        bess_power_df = pd.DataFrame(bess_power_list,columns=columns_bess)

        return bus_power_df1,load_df1,generation_df1,demand_df1,losses_df1,branch_df1,voltage_df1,bess_power_df,time_range
    
    else:
        print('Power Flow Simulation Started')
        # Start the counter to mensure the time of execution
        start = t.time()
        for i,timestep in enumerate(time_range):
            # print(f"Time: {timestep}")

            # Run the power flow without the operation of the BESS
            load,generation,demand_df,losses,bus_power,bus_voltage,branch_df = power_flow(timestep,file_dss,generators_list,loads_list,lights_list,dss)

            # Append the new lines
            bus_power_list.extend(bus_power)
            loaddf_list.append(load)
            generationdf_list.append(generation)
            demanddf_list.append(demand_df)
            lossesdf_list.append(losses)
            branch_df_list.extend(branch_df)
            voltage_df_list.extend(bus_voltage)

            print(demanddf_list[i])
        
        # Print the time of execution of power flow
        print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

        #All columns to create each dataframe
        columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
        columns_power = ['Timestep','P(kW)','Q(kvar)']
        columns_branch = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
        columns_bus_voltage = ['Timestep','Bus','Voltage (p.u.)']

        #Create empty dataframes to store the values of loop
        bus_power_df1 = pd.DataFrame(bus_power_list,columns=columns_bus)
        load_df1 = pd.DataFrame(loaddf_list,columns=columns_power)
        generation_df1 = pd.DataFrame(generationdf_list,columns=columns_power)
        demand_df1 = pd.DataFrame(demanddf_list,columns=columns_power)
        losses_df1 = pd.DataFrame(lossesdf_list,columns=columns_power) 
        branch_df1 = pd.DataFrame(branch_df_list,columns=columns_branch)
        voltage_df1 = pd.DataFrame(voltage_df_list,columns=columns_bus_voltage)
        
        return bus_power_df1,load_df1,generation_df1,demand_df1,losses_df1,branch_df1,voltage_df1

    
    

    
    



    
    