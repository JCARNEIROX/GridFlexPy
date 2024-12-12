import opendssdirect as dss
import pandas as pd
import os
from gridflexpy.read_spreadsheet import read_file_xlsx
from gridflexpy.get_general_informations import get_informations
from gridflexpy.bess import construct_bess
from gridflexpy.generator import construct_generators
from gridflexpy.load import construct_loads
from gridflexpy.powerflow import power_flow
from gridflexpy.plots import plot, display_graph,save_fig
import time as t


if __name__ == '__main__':
    # Here is where the path to the files should be placed
    path_xlsx = os.getcwd() + '/data/spreadsheets/'
    path_dss = os.getcwd() + '/data/dss_files/'	
    output_csv = os.getcwd() + '/data/output/csv/'
    output_img = os.getcwd() + '/data/output/img/'
    
    # Read the file and
    file_contents = read_file_xlsx(path_xlsx+'teste_sheet.xlsx')

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
    file_dss = path_dss + 'ModelagemTeste.dss' 
    date_ini = general_informations['start_date']
    date_end = general_informations['end_date']
    timestep = general_informations['timestep']

    # Measure the time of the power flow simulation
    start = t.time()
    bus_power,power_df,branch_df,voltage_df,time = power_flow(date_ini,date_end,timestep,file_dss,bess_list,generators_list,loads_list,dss)
    print(f"Time of the power flow simulation: {round(t.time()-start,4)} seconds")

    power_balance = plot(time,power_df,'Powers at Circuit','Time(h)', 'Power(kW)',lines=['Load','Generation','Delivered'])
    display_graph(power_balance)
    save_fig(power_balance,'power_balance',output_img)



    
    
