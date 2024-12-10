import pandas as pd
import opendssdirect as dss
from read_spreadsheet import read_file_xlsx
from get_general_informations import get_informations
from bess import construct_bess
from generator import construct_generators
from load import construct_loads
from powerflow import power_flow


if __name__ == '__main__':
    # Here is where the path to the files should be placed
    path_xlsx = 'C:\\Users\\joao9\\GitHub\\GridFlexPy\\data\\spreadsheets\\teste_sheet.xlsx'
    path_dss = 'C:\\Users\\joao9\\GitHub\\GridFlexPy\\data\\dss_files\\'
    load_profiles = 'C:\\Users\\joao9\\GitHub\\GridFlexPy\\data\\loads\\'

    # Read the file and
    file_contents = read_file_xlsx(path_xlsx)

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

    power_flow(date_ini,date_end,timestep,file_dss,bess_list,generators_list,loads_list,dss)
