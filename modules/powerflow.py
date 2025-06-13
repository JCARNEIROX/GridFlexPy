import pandas as pd
import os
from modules import add_gd,get_GenPower
from modules import add_bat, get_BessPower
from modules import add_load,add_light,get_LoadPower
import numpy as np

# Input and output paths    
path_xlsx = os.getcwd() + '/data/spreadsheets/'
path_dss = os.getcwd() + '/data/dss_files/'	
output_csv = os.getcwd() + '/data/output/csv/'
output_img = os.getcwd() + '/data/output/img/'
path_generators = os.getcwd() + '/data/generators_profiles/'
path_forecast = os.getcwd() + '/data/forecasts'


def power_flow_bess(timestep,opendssmodel,batteries,generators,loads,light_list,dss):

    #Clean the prompt comand of the OpenDSS
    dss.Basic.ClearAll()
    dss.Basic.Start(0)
    dss.Command(f"Compile {opendssmodel}")
    buses = dss.Circuit.AllBusNames()

    #Add the generators to the OpenDSS model
    for generator in generators:
        # Update the power of the generator in the timestep
        generator.update_power(timestep)
        # Write the command
        dss.Command(add_gd(generator))

    #Add the loads to the OpenDSS model
    for load in loads:
        load.update_power(timestep)
        dss.Command(add_load(load))

    #Add the public ilumination to the OpenDSS model
    for light in light_list:
        light.update_power(timestep)
        dss.Command(add_light(light))
    
    # Add the batteries to the OpenDSS model
    for battery in batteries:
        dss.Command(add_bat(battery))

    #Solve the power flow
    dss.Solution.Solve()  

    # Get voltage values
    bus_voltage = get_bus_voltages(timestep,buses,dss)
        
    # Get the power of the buses and the power delivered to the circuit
    load = get_LoadPower(dss,timestep)
    generation = get_GenPower(dss,timestep)
    bess = get_BessPower(dss,timestep)
    demand = get_demand(timestep,dss)
    losses = get_losses(timestep,dss)
    bus_power_df = get_bus_power(buses,timestep,dss)
    
    # Display power and current flows in branches
    branch_df = get_branch_flows(timestep,dss)
  
    return load,generation,bess,demand,losses,bus_power_df,bus_voltage,branch_df


def power_flow(timestep,opendssmodel,generators,loads,light_list,dss):

    #Clean the prompt comand of the OpenDSS
    dss.Basic.ClearAll()
    dss.Basic.Start(0)
    dss.Command(f"Compile {opendssmodel}")
    buses = dss.Circuit.AllBusNames()

    #Add the generators to the OpenDSS model
    for generator in generators:
        # Update the power of the generator in the timestep
        generator.update_power(timestep)
        # Write the command
        dss.Command(add_gd(generator))

    #Add the loads to the OpenDSS model
    for load in loads:
        load.update_power(timestep)
        dss.Command(add_load(load))

    #Add the public ilumination to the OpenDSS model
    for light in light_list:
        light.update_power(timestep)
        dss.Command(add_light(light))

    #Solve the power flow
    dss.Solution.Solve()  

    # Get voltage values
    bus_voltage = get_bus_voltages(timestep,buses,dss)
        
    # Get the power of the buses and the power delivered to the circuit
    load = get_LoadPower(dss,timestep)
    generation = get_GenPower(dss,timestep)
    demand = get_demand(timestep,dss)
    losses = get_losses(timestep,dss)
    bus_power_df = get_bus_power(buses,timestep,dss)
    
    # Display power and current flows in branches
    branch_df = get_branch_flows(timestep,dss)
  
    return load,generation,demand,losses,bus_power_df,bus_voltage,branch_df


def get_bus_power(buses,timestep,dss):
   
        #Create a empty dataframe to store the active/reactive power demand at each bus
        bus_power_list = []

        for bus in buses:

            #Initializate the powers at actual bus
            bus_active_power = 0
            bus_reactive_power = 0

            elements = dss.Circuit.AllElementNames()
            bus_elements = [element for element in elements if bus in element]

            for element in bus_elements:
                if 'Load.' in element:
                    dss.Circuit.SetActiveElement(element)
                    powers = dss.CktElement.Powers()
                    bus_active_power += sum(powers[::2])
                    bus_reactive_power += sum(powers[1::2])
                elif 'Generator.' in element:
                    dss.Circuit.SetActiveElement(element)
                    powers = dss.CktElement.Powers()
                    bus_active_power += sum(powers[::2])
                    bus_reactive_power += sum(powers[1::2])
                elif 'Storage.' in element:
                    dss.Circuit.SetActiveElement(element)
                    powers = dss.CktElement.Powers()
                    bus_active_power += sum(powers[::2])
                    bus_reactive_power += sum(powers[1::2])
            
            # Create a new line with the bus information
            new_line_bus = [timestep, bus, round(bus_active_power,4),round(bus_reactive_power,4)]
            bus_power_list.append(new_line_bus)
            # print(f"{bus}\t{active_power:.4f}\t\t{reactive_power:.4f}")

        return bus_power_list

def get_branch_flows(timestep,dss):
    
    branch_list = []
    lines = dss.Lines.AllNames()  # List of all lines in the circuit
    for line in lines:
        dss.Circuit.SetActiveElement(f"Line.{line}")
        # Extract the number of conductors of line
        num_conductors = dss.CktElement.NumConductors()
        currents = dss.CktElement.CurrentsMagAng()  # Currents at both ends
        Iorigin = [round(currents[2*i],4) for i in range(num_conductors)]  # Sum of currents
        powers = dss.CktElement.Powers()  # Powers at both ends
        P_origin = sum(powers[::2][:num_conductors])  # Active power at the origin end
        Q_origin = sum(powers[1::2][:num_conductors])  # Reactive power at the origin end
        losses = dss.CktElement.Losses()[0] / 1000  # Losses (in kW)

        # Create a new line with the branch information
        new_line = [timestep,line,Iorigin,round(P_origin,4),round(Q_origin,4),round(losses,4)]
        branch_list.append(new_line)

    return branch_list

def get_bus_voltages(timestep,buses,dss):
    
    #Create a empty dataframe to store the voltages
    voltage_list = []
    for bus in buses:
        dss.Circuit.SetActiveBus(bus)
        voltages = dss.Bus.puVLL()
        pu_voltage = np.sqrt(voltages[0]**2 + voltages[1]**2)
        new_line = [timestep, bus, round(pu_voltage,4)]
        voltage_list.append(new_line)
    
    return voltage_list


def get_demand(timestep,dss):
    
    #Get the total power delivered to the circuit and total losses
    total_power = dss.Circuit.TotalPower()
    demand = [timestep, -round(total_power[0],4), -round(total_power[1],4)]
    return demand

def get_losses(timestep,dss):
    
    #Get the total power delivered to the circuit and total losses
    total_losses = dss.Circuit.Losses()# Losses in kW
    losses = [timestep, round(total_losses[0]/1000,4), round(total_losses[1]/1000,4)]
    return losses