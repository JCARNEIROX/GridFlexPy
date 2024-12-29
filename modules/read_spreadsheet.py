import pandas as pd

def read_file_xlsx(path):
    """
    Read the file and return a dictionary with the content of each page of spreadsheet.
    The spreadsheet should have the following pages: General, BESS, Generator and Load.
    """
    file = pd.read_excel(path, sheet_name=None, engine='openpyxl')

    general_informations = file['General']
    bess = file['BESS']
    generators = file['Generator']
    loads = file['Load']
    public_ilumination = file['Public_Ilumination']

    dict_contet = {'General': general_informations, 'BESS': bess, 'Generators': generators, 'Loads': loads, 'Public_Ilumination': public_ilumination}
    return dict_contet