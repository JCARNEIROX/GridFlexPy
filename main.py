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

if __name__ == '__main__':


    name_spreadsheet = 'teste_sheet.xlsx' # Name of your spreadsheet with parameters of the system in directory data/spreadsheets
    name_dss = 'ModelagemTeste.dss' # Name of your main dss_file in directory data/dss_files
    kind = 'Simple' # Kind of operation of the Batery Energy Storage System (BESS) in the power flow. Options: 'NoOperation', 'Simple', 'Smoothing'

    # Run the power flow
    bus_power,load_df,generation_df,demand_df,losses_df,branch_df,voltage_df,line_voltage,bess_powers,time = run(name_spreadsheet,name_dss,kind=kind)

    # Save the results in a csv file
    save_csv(bus_power,f'bus_power_{kind}',output_csv)
    save_csv(load_df,f'load_{kind}',output_csv)
    save_csv(generation_df,f'generation_{kind}',output_csv)
    save_csv(demand_df,f'demand_{kind}',output_csv)
    save_csv(losses_df,f'losses_{kind}',output_csv)
    save_csv(branch_df,f'branch_df_{kind}',output_csv)
    save_csv(voltage_df,f'voltage_df_{kind}',output_csv)
    save_csv(line_voltage,f'line_voltage_{kind}',output_csv)
    save_csv(bess_powers,f'bess_powers_{kind}',output_csv)

    #Plot data
    # powers = plot('Power',time,power_df,title='Powers on Circuit',xlabel='Time(h)',ylabel='Power(kW)',figsize=(8,6),grid=True,lines=['Load','Generation','Demand'])
    # save_fig(powers,'power_circuit',output_img)
    # display_graph(powers)

    # bess = plot_graph(time[3:],bess_powers,title='Power of BESS',xlabel='Time(h)',ylabel='Power(kW)',figsize=(8,6))
    # save_fig(bess,'power_bess',output_img) 
    # display_graph(bess)

    



    
    
