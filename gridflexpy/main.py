import pandas as pd
from read_spreadsheet import read_file_xlsx
from get_general_informations import get_informations
from bess import construct_bess
from generator import construct_generators
from load import construct_loads

if __name__ == '__main__':
    # Here is where the path to the files should be placed
    path_xlsx = 'data/spreadsheets/teste_sheet.xlsx'
    path_dss = 'data/dss_files/lucas.dss'
    load_profiles = 'data/loads/'

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
    print(generators_list)