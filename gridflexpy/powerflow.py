import pandas as pd
import opendssdirect as dss
from generator import add_gd, get_GneratorPower

def power_flow(date_ini,date_end,step,opendssmodel,batteries,generators,loads):

    time_range = pd.date_range(date_ini, date_end, freq=step)

    for timestep in time_range:

        #Clean the prompt comand of the OpenDSS
        dss.Basic.ClearAll()
        dss.Basic.Start(0)
        dss.Command(f"Compile {opendssmodel}")

        #List all buses in the model
        

