def get_informations(general_informations):
    """
    Get all the general informations from the spreadsheet and return a dictionary with the content of each information.
    """
    start_date = general_informations.loc[general_informations['Parameter'] == 'start_date', 'Value'].values[0]
    end_date = general_informations.loc[general_informations['Parameter'] == 'end_date', 'Value'].values[0]
    timestep = general_informations.loc[general_informations['Parameter'] == 'timestep', 'Value'].values[0]

    # Create a dict with all informations collected
    general_informations = {'start_date': start_date, 'end_date': end_date, 'timestep': timestep}

    return general_informations