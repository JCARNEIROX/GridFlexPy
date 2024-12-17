def get_informations(general_informations):
    """
    Get all the general informations from the spreadsheet and return a dictionary with the content of each information.
    """
    start_date = general_informations.loc[general_informations['Parameter'] == 'start_date', 'Value'].values[0]
    end_date = general_informations.loc[general_informations['Parameter'] == 'end_date', 'Value'].values[0]
    timestep = general_informations.loc[general_informations['Parameter'] == 'timestep', 'Value'].values[0]

    # Create a dict with all informations collected
    general_informations = GenInformations(start_date,end_date,timestep)
    return general_informations


class GenInformations:
    def __init__(self,start_date='',end_date='',timestep=0):
        self.start_date = start_date
        self.end_date = end_date
        self.timestep = timestep
    
    def update_start_date(self,start_date):
        self.start_date = start_date
    
    def update_end_date(self,end_date):
        self.end_date = end_date
    
    def update_timestep(self,timestep):
        self.timestep = timestep