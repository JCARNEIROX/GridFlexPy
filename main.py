# from modules.run import run
# from modules.utils import save_csv
# from modules.plots import plot,display_graph,save_fig,plot_graph
# from modules import run
# from modules import save_csv
# from modules.plots import *
from modules import *
import os


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'; os.makedirs(path_xlsx,exist_ok=True)
path_dss = os.getcwd() + '/data/dss_files/' ; os.makedirs(path_dss,exist_ok=True)
output_csv = os.getcwd() + '/data/output/csv/'; os.makedirs(output_csv,exist_ok=True)
output_img = os.getcwd() + '/data/output/img/'; os.makedirs(output_img,exist_ok=True)
path_generators = os.getcwd() + '/data/generators_profiles/'; os.makedirs(path_generators,exist_ok=True)

if __name__ == '__main__':


    # General informations
    name_spreadsheet = 'sheet_5Node.xlsx' # Name of your spreadsheet with parameters of the system in directory data/spreadsheets
    name_dss = '5Nodeckt.dss' # Name of your main dss_file in directory data/dss_files
    kind = 'NoOperation' # Kind of operation of the Batery Energy Storage System (BESS) in the power flow. Options: 'NoOperation', 'Simple', 'Smoothing'
    bess_bus = 'bus_001'

    # Save the results in a csv file
    if not kind == 'NoOperation':
        print(f'Running power flow for BESS in bus {bess_bus} with kind of operation {kind}')
        # Run the power flow
        bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,bess_powers,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

        # Save the results in a csv file
        save_csv(bus_power,f'BusPowers_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'bus_power/')
        save_csv(load_df,f'Load_{kind}_bus{bess_bus.split('_')[0]}_year_{name_dss.split('.')[0]}',output_csv + 'load/')
        save_csv(generation_df,f'Generation_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'generation/')
        save_csv(demand_df,f'Demand_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'demand/')
        save_csv(losses_df,f'Losses_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'losses/')
        save_csv(branch_df,f'BranchFlow_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'BusVoltage_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'bus_voltage/')
        save_csv(bess_powers,f'BessPowers_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'bess/')

    else:
        print(f'Running power flow kind of operation {kind}')
        # Run the power flow
        bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

        # Save the results in a csv file
        save_csv(bus_power,f'BusPowers_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'bus_power/')
        save_csv(load_df,f'Load_{kind}_year_{name_dss.split('.')[1]}',output_csv + 'load/')
        save_csv(generation_df,f'Generation_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'generation/')
        save_csv(demand_df,f'Demand_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'demand/')
        save_csv(losses_df,f'Losses_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'losses/')
        save_csv(branch_df,f'BranchFlow_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'BusVoltage_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'bus_voltage/')

    # # General informations
    name_spreadsheet = 'sheet_IEEE13Node.xlsx' # Name of your spreadsheet with parameters of the system in directory data/spreadsheets
    name_dss = 'CondominioDosIpes.dss' # Name of your main dss_file in directory data/dss_files
    #kind = 'Simple' # Kind of operation of the Batery Energy Storage System (BESS) in the power flow. Options: 'NoOperation', 'Simple', 'Smoothing'
    #bess_bus = 'bus_001'
    kinds = ['Simple','Smoothing']
    for kind in kinds:
        for i in range(6,15):
            bess_bus = f'bus_{str(i).zfill(3)}'

            print(f'Running power flow for BESS in bus {bess_bus} with kind of operation {kind}')

            # Save the results in a csv file
            if not kind == 'NoOperation':
                # Run the power flow
                bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,bess_powers,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

                # Save the results in a csv file
                save_csv(bus_power,f'BusPowers_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'bus_power/')
                save_csv(load_df,f'Load_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'load/')
                save_csv(generation_df,f'Generation_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'generation/')
                save_csv(demand_df,f'Demand_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'demand/')
                save_csv(losses_df,f'Losses_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'losses/')
                save_csv(branch_df,f'BranchFlow_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'branch_flows/')
                save_csv(bus_voltage_df,f'BusVoltage_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'bus_voltage/')
                save_csv(bess_powers,f'BessPowers_{kind}_bus{bess_bus.split('_')[1]}_year_{name_dss.split('.')[0]}',output_csv + 'bess/')
            else:
                # Run the power flow
                bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

                # Save the results in a csv file
                save_csv(bus_power,f'BusPowers_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'bus_power/')
                save_csv(load_df,f'Load_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'load/')
                save_csv(generation_df,f'Generation_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'generation/')
                save_csv(demand_df,f'Demand_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'demand/')
                save_csv(losses_df,f'Losses_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'losses/')
                save_csv(branch_df,f'BranchFlow_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'branch_flows/')
                save_csv(bus_voltage_df,f'BusVoltage_{kind}_year_{name_dss.split('.')[0]}',output_csv + 'bus_voltage/')
        



    

    



    
    
