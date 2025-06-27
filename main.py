from modules import *
import os


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'; os.makedirs(path_xlsx,exist_ok=True)
path_dss = os.getcwd() + '/data/dss_files/' ; os.makedirs(path_dss,exist_ok=True)
output_csv = os.getcwd() + '/data/output/csv/'; os.makedirs(output_csv,exist_ok=True)
output_img = os.getcwd() + '/data/output/img/'; os.makedirs(output_img,exist_ok=True)
path_generators = os.getcwd() + '/data/generators_profiles/'; os.makedirs(path_generators,exist_ok=True)

if __name__ == '__main__':

    config ={
        'name_spreadsheet': 'sheet_IEEE13Node.xlsx',
        'name_dss': 'CondominioDosIpes.dss',
        'kind': 'Forecasting',  # Options: 'NoOperation', 'Simple', 'Smoothing', 'Forecasting'
        'bess_bus': 'bus_013',
        'seq_len': 162,  # Tamanho da janela de entrada
        'past_values': 3,  # Past values to start operation in 'Smoothing' or 'Simple' mode
        'in_feature': 3,  # Features in on mode Forcasting: Load, Losses and PV
        'n_future': 1,    # Number of future values to predict (1 for next timestep)
        'hidden_size': 64, # Hidden size of the LSTM
        'batch_size': 32, # Batch size for training
        'learning_rate': 1e-4, # Learning rate for the optimizer
        'num_layers': 3,
        'dropout': 0.2,
    }
    
    # Save the results in a csv file
    if not config['kind'] == 'NoOperation':
        print(f'Running power flow for BESS in bus {config["bess_bus"]} with kind of operation {config["kind"]}')
        # Run the power flow
        # bus_power,load_df,generation_df,demand_df_smoothing,demand_df_noop,losses_df,branch_df,bus_voltage_df,bess_powers = run(name_spreadsheet,name_dss,bess_bus,kind=kind)
        bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,bess_powers,time = run(config)

        # Save the results in a csv file
        save_csv(bus_power,f'BusPowers_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'bus_power/')
        save_csv(load_df,f'Load_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'load/')
        save_csv(generation_df,f'Generation_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'generation/')
        save_csv(demand_df,f'Demand_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'demand/')
        save_csv(losses_df,f'Losses_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'losses/')
        save_csv(branch_df,f'BranchFlow_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'BusVoltage_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'bus_voltage/')
        save_csv(bess_powers,f'BessPowers_{config['kind']}_bus{config["bess_bus"].split('_')[1]}_year_{config["name_dss"].split('.')[0]}',output_csv + 'bess/')


    else:
        print(f'Running power flow kind of operation {config['kind']}')
        # Run the power flow
        bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df = run(config)

        # Save the results in a csv file
        save_csv(bus_power,f'BusPowers_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'bus_power/')
        save_csv(load_df,f'Load_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'load/')
        save_csv(generation_df,f'Generation_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'generation/')
        save_csv(demand_df,f'Demand_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'demand/')
        save_csv(losses_df,f'Losses_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'losses/')
        save_csv(branch_df,f'BranchFlow_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'BusVoltage_{config['kind']}_year_{config["name_dss"].split('.')[0]}',output_csv + 'bus_voltage/')




    

    



    
    
