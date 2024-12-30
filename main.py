from modules.run import run,return_general_informations
from modules.utils import save_csv
from modules.plots import plot,display_graph,save_fig,plot_graph
import os


# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'

# if __name__ == '__main__':


#     name_spreadsheet = 'teste_sheet.xlsx' # Name of your spreadsheet with parameters of the system in directory data/spreadsheets
#     name_dss = 'ModelagemTeste.dss' # Name of your main dss_file in directory data/dss_files
#     kind = 'Smoothing' # Kind of operation of the Batery Energy Storage System (BESS) in the power flow. Options: 'NoOperation', 'Simple', 'Smoothing'
    
#     for i in range(1,6,1):
#         bess_bus = i
#         print(f'Running power flow for BESS in bus {bess_bus} with kind of operation {kind}')

#         # Run the power flow
#         bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,bess_powers,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

#         # Save the results in a csv file
#         if not kind == 'NoOperation':
#             save_csv(bus_power,f'bus_power_{kind}_bus{bess_bus}',output_csv + 'bus_power/')
#             save_csv(load_df,f'load_{kind}_bus{bess_bus}',output_csv + 'load/')
#             save_csv(generation_df,f'generation_{kind}_bus{bess_bus}',output_csv + 'generation/')
#             save_csv(demand_df,f'demand_{kind}_bus{bess_bus}',output_csv + 'demand/')
#             save_csv(losses_df,f'losses_{kind}_bus{bess_bus}',output_csv + 'losses/')
#             save_csv(branch_df,f'branch_df_{kind}_bus{bess_bus}',output_csv + 'branch_flows/')
#             save_csv(bus_voltage_df,f'bus_voltage_df_{kind}_bus{bess_bus}',output_csv + 'bus_voltage/')
#             save_csv(bess_powers,f'bess_powers_{kind}_bus{bess_bus}',output_csv + 'bess/')
#         else:
#             save_csv(bus_power,f'bus_power_{kind}',output_csv + 'bus_power/')
#             save_csv(load_df,f'load_{kind}',output_csv + 'load/')
#             save_csv(generation_df,f'generation_{kind}',output_csv + 'generation/')
#             save_csv(demand_df,f'demand_{kind}',output_csv + 'demand/')
#             save_csv(losses_df,f'losses_{kind}',output_csv + 'losses/')
#             save_csv(branch_df,f'branch_df_{kind}',output_csv + 'branch_flows/')
#             save_csv(bus_voltage_df,f'bus_voltage_df_{kind}',output_csv + 'bus_voltage/')
#             save_csv(bess_powers,f'bess_powers_{kind}',output_csv + 'bess/')

if __name__ == '__main__':


    name_spreadsheet = 'sheet_IEEE13Node.xlsx' # Name of your spreadsheet with parameters of the system in directory data/spreadsheets
    name_dss = 'IEEE13Nodeckt.dss' # Name of your main dss_file in directory data/dss_files
    kind = 'NoOperation' # Kind of operation of the Batery Energy Storage System (BESS) in the power flow. Options: 'NoOperation', 'Simple', 'Smoothing'
    bess_bus = 1
   
    print(f'Running power flow for BESS in bus {bess_bus} with kind of operation {kind}')

    # Run the power flow
    bus_power,load_df,generation_df,demand_df,losses_df,branch_df,bus_voltage_df,bess_powers,time = run(name_spreadsheet,name_dss,bess_bus,kind=kind)

    # Save the results in a csv file
    if not kind == 'NoOperation':
        save_csv(bus_power,f'bus_power_{kind}_bus{bess_bus}',output_csv + 'bus_power/')
        save_csv(load_df,f'load_{kind}_bus{bess_bus}',output_csv + 'load/')
        save_csv(generation_df,f'generation_{kind}_bus{bess_bus}',output_csv + 'generation/')
        save_csv(demand_df,f'demand_{kind}_bus{bess_bus}',output_csv + 'demand/')
        save_csv(losses_df,f'losses_{kind}_bus{bess_bus}',output_csv + 'losses/')
        save_csv(branch_df,f'branch_df_{kind}_bus{bess_bus}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'bus_voltage_df_{kind}_bus{bess_bus}',output_csv + 'bus_voltage/')
        save_csv(bess_powers,f'bess_powers_{kind}_bus{bess_bus}',output_csv + 'bess/')
    else:
        save_csv(bus_power,f'bus_power_{kind}',output_csv + 'bus_power/')
        save_csv(load_df,f'load_{kind}',output_csv + 'load/')
        save_csv(generation_df,f'generation_{kind}',output_csv + 'generation/')
        save_csv(demand_df,f'demand_{kind}',output_csv + 'demand/')
        save_csv(losses_df,f'losses_{kind}',output_csv + 'losses/')
        save_csv(branch_df,f'branch_df_{kind}',output_csv + 'branch_flows/')
        save_csv(bus_voltage_df,f'bus_voltage_df_{kind}',output_csv + 'bus_voltage/')
        save_csv(bess_powers,f'bess_powers_{kind}',output_csv + 'bess/')

    



    
    
