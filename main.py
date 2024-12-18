from modules.run import run
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

    # Run the power flow
    bus_power,power_df,branch_df,voltage_df,line_voltage,bess_powers,time = run(name_spreadsheet,name_dss)

    # Save the results in a csv file
    save_csv(bus_power,'bus_power_BESS',output_csv)
    save_csv(power_df,'power_df_BESS',output_csv)
    save_csv(branch_df,'branch_df_BESS',output_csv)
    save_csv(voltage_df,'voltage_df_BESS',output_csv)
    save_csv(line_voltage,'line_voltage_BESS',output_csv)
    save_csv(bess_powers,'bess_powers',output_csv)

    #Plot data
    # powers = plot('Power',time,power_df,title='Powers on Circuit',xlabel='Time(h)',ylabel='Power(kW)',figsize=(8,6),grid=True,lines=['Load','Generation','Demand'])
    # save_fig(powers,'power_circuit',output_img)
    # display_graph(powers)

    # bess = plot_graph(time[3:],bess_powers,title='Power of BESS',xlabel='Time(h)',ylabel='Power(kW)',figsize=(8,6))
    # save_fig(bess,'power_bess',output_img) 
    # display_graph(bess)

    



    
    
