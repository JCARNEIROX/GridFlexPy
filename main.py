from modules.run import run
from modules.utils import save_csv
from modules.plots import plot,display_graph,save_fig,plot_graph
import os


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'; os.makedirs(path_xlsx,exist_ok=True)
path_dss = os.getcwd() + '/data/dss_files/' ; os.makedirs(path_dss,exist_ok=True)
output_csv = os.getcwd() + '/data/output/csv/'; os.makedirs(output_csv,exist_ok=True)
output_img = os.getcwd() + '/data/output/img/'; os.makedirs(output_img,exist_ok=True)
path_generators = os.getcwd() + '/data/generators_profiles/'; os.makedirs(path_generators,exist_ok=True)

if __name__ == '__main__':

    # General informations
    name_spreadsheet = 'sheet_IEEE13Node.xlsx' # Name of your spreadsheet with parameters of the system in directory data/spreadsheets
    name_dss = 'CondominioDosIpes.dss' # Name of your main dss_file in directory data/dss_files
    kind = 'NoOperation' # Kind of operation of the Batery Energy Storage System (BESS) in the power flow. Options: 'NoOperation', 'Simple', 'Smoothing'
    bess_bus = 'bus_001'
    
    print(f'Running power flow for BESS in bus {bess_bus} with kind of operation {kind}')

    

    # Save the results in a csv file
    if not kind == 'NoOperation':
        # Run the power flow
        bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,bess_powers,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

        # Save the results in a csv file
        save_csv(bus_power,f'bus_power_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'bus_power/')
        save_csv(load_df,f'load_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'load/')
        save_csv(generation_df,f'generation_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'generation/')
        save_csv(demand_df,f'demand_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'demand/')
        save_csv(losses_df,f'losses_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'losses/')
        save_csv(branch_df,f'branch_df_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'bus_voltage_df_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'bus_voltage/')
        save_csv(bess_powers,f'bess_powers_{kind}_bus{bess_bus}_year{name_dss.split('.')[0]}',output_csv + 'bess/')
    else:
        # Run the power flow
        bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

        # Save the results in a csv file
        save_csv(bus_power,f'bus_power_{kind}_year{name_dss.split('.')[0]}',output_csv + 'bus_power/')
        save_csv(load_df,f'load_{kind}_year{name_dss.split('.')[0]}',output_csv + 'load/')
        save_csv(generation_df,f'generation_{kind}_year{name_dss.split('.')[0]}',output_csv + 'generation/')
        save_csv(demand_df,f'demand_{kind}_year{name_dss.split('.')[0]}',output_csv + 'demand/')
        save_csv(losses_df,f'losses_{kind}_year{name_dss.split('.')[0]}',output_csv + 'losses/')
        save_csv(branch_df,f'branch_df_{kind}_year{name_dss.split('.')[0]}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'bus_voltage_df_{kind}_year{name_dss.split('.')[0]}',output_csv + 'bus_voltage/')
    



    

    



    
    
