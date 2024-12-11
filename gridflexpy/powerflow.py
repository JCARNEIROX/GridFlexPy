import warnings
import pandas as pd
import re
from gridflexpy.generator import add_gd, get_GneratorPower
from gridflexpy.bess import add_bat
from gridflexpy.load import add_load

def power_flow(date_ini,date_end,step,opendssmodel,batteries,generators,loads,dss):

    #Create a empty dataframe to store the active/reactive power demand at each bus
    columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
    bus_power = pd.DataFrame(columns=columns_bus)

    #Create a empty dataframe to store the active/reactive power delivered to circuit and the losses at actual timestep
    columns_power = ['Timestep','Name','P(kW)','Q(kvar)']
    power_df = pd.DataFrame(columns=columns_power)

    #Create a empty dataframe to store the currents, active/reactive power and losses at each line
    columns = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
    branch_df = pd.DataFrame(columns=columns)

    #Create a empty dataframe to store the voltages
    columns = ['Timestep','Bus','Voltage']
    voltage_df = pd.DataFrame(columns=columns)

    # Use this functions to supress the warnings on the terminal
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)

        time_range = pd.date_range(date_ini, date_end, freq=str(step) + 'T')
        for timestep in time_range:
            print(f"\nTime: {timestep}")
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
            
            #Add the batteries to the OpenDSS model
            # for battery in batteries:
            #     dss.Command(add_bat(battery))

            #Solve the power flow
            dss.Solution.Solve()  

            # Display bus voltages
            voltages = dss.Circuit.AllBusVMag()
            voltage = get_bus_voltages(timestep,buses,voltages)
            voltage_df = pd.concat([voltage_df,voltage],ignore_index=True)
            # print(voltage_df)

            
            # Get the power of the buses and the power delivered to the circuit
            bus_power_df,power_df = get_bus_power(buses,timestep,dss)
            bus_power = pd.concat([bus_power,bus_power_df],ignore_index=True)
            power_df = pd.concat([power_df,power_df],ignore_index=True)
            
            # print('\nPower at Buses:')
            # print(bus_power_df)
            # print('\nPower delivered to circuit:')
            # print(power_df)


            # Display power and current flows in branches
            branch_df = display_branch_flows(timestep,dss)
            branch_df = pd.concat([branch_df,branch_df],ignore_index=True)
            # print("\nBranch Flows:")
            # print(branch_df)

    return bus_power,power_df,branch_df,voltage_df,time_range
        



def get_bus_power(buses,timestep,dss):
    # print("\nPowers at Buses:")
    # print("Bus\tActive Power (kW)\tReactive Power (kvar)")

    # Powers
    load_active_power = 0
    load_reactive_power = 0

    gen_active_power = 0
    gen_reactive_power = 0

    battery_active_power = 0
    battery_reactive_power = 0
    
    elements = dss.Circuit.AllElementNames()

    #Create a empty dataframe to store the active/reactive power demand at each bus
    columns_bus = ['Timestep','Bus','P(kW)','Q(kvar)']
    bus_power_df = pd.DataFrame(columns=columns_bus)

    for bus in buses:

        bus_active_power = 0
        bus_reactive_power = 0

        # Filtra as cargas associadas ao barramento atual
        loads = [element for element in elements if element.startswith("Load.") and bus in element]
        generators = [element for element in elements if element.startswith("Generator.") and bus in element]
        batteries = [element for element in elements if element.startswith("Storage.") and bus in element]
        # loads = [element for element in elements if re.search(f"{bus}", element)]

        # Separar em funções posteriormente
        for load in loads:
            dss.Circuit.SetActiveElement(load)
            powers = dss.CktElement.Powers()
            load_active_power += sum(powers[::2])  # Somando potências ativas
            load_reactive_power += sum(powers[1::2])  # Somando potências reativas

            bus_active_power += sum(powers[::2])  # Somando potências ativas nos barramentos
            bus_reactive_power += sum(powers[1::2])  # Somando potências reativas nos barramentos

        for gen in generators:
            dss.Circuit.SetActiveElement(gen)
            powers = dss.CktElement.Powers()
            gen_active_power -= sum(powers[::2])  # Somando potências ativas
            gen_reactive_power -= sum(powers[1::2])  # Somando potências reativas

            bus_active_power += sum(powers[::2])  # Somando potências ativas nos barramentos
            bus_reactive_power += sum(powers[1::2])  # Somando potências reativas nos barramentos

        for bat in batteries:
            dss.Circuit.SetActiveElement(bat)
            powers = dss.CktElement.Powers()
            battery_active_power -= sum(powers[::2])  # Somando potências ativas
            battery_reactive_power -= sum(powers[1::2])  # Somando potências reativas

            bus_active_power += sum(powers[::2])  # Somando potências ativas nos barramentos
            bus_reactive_power += sum(powers[1::2])  # Somando potências reativas nos barramentos


        # Exibe as potências do barramento atual
        new_line_bus = pd.DataFrame([[timestep, bus, round(bus_active_power,4),round(bus_reactive_power,4)]], columns=columns_bus)
        bus_power_df = pd.concat([bus_power_df,new_line_bus],ignore_index=True)
        # print(f"{bus}\t{active_power:.4f}\t\t{reactive_power:.4f}")

    #Create a empty dataframe to store the active/reactive power delivered to circuit and the losses at actual timestep
    columns_power = ['Timestep','Name','P(kW)','Q(kvar)']
    power_df = pd.DataFrame(columns=columns_power)

    #Get the total power delivered to the circuit and total losses
    total_power = dss.Circuit.TotalPower()
    total_losses = dss.Circuit.Losses()# Losses in kW
    power_df = pd.concat([power_df, pd.DataFrame([[timestep, 'Load', round(load_active_power,4), round(load_reactive_power,4)]], columns=columns_power)], ignore_index=True)
    power_df = pd.concat([power_df, pd.DataFrame([[timestep, 'Generation', round(gen_active_power,4), round(gen_reactive_power,4)]], columns=columns_power)], ignore_index=True)
    power_df = pd.concat([power_df, pd.DataFrame([[timestep, 'Delivered', -round(total_power[0],4), -round(total_power[1],4)]], columns=columns_power)], ignore_index=True)
    power_df = pd.concat([power_df, pd.DataFrame([[timestep, 'Total Losses', round(total_losses[0]/1000,4), round(total_losses[1]/1000,4)]], columns=columns_power)], ignore_index=True)
                         
    # # Exibe as potências totais do sistema
    # print("\nTotal Active Power (kW): {:.4f}".format(total_active_power))
    # print("Total Reactive Power (kvar): {:.4f}".format(total_reactive_power))

    return bus_power_df,power_df

def display_branch_flows(timestep,dss):
    # print("\nFlows in Branches:")
    # print("Branch\t\tTotal Current (A)\tActive Power (kW)\tReactive Power (kvar)\t\tLosses (kW)")

    #Create a empty dataframe to store the currents, active/reactive power and losses at each line
    columns = ['Timestep','Branch','Current(A)','P(kW)','Q(kvar)','Losses(kW)']
    branch_df = pd.DataFrame(columns=columns)
    lines = dss.Lines.AllNames()  # List of all lines in the circuit
    for line in lines:
        dss.Circuit.SetActiveElement(f"Line.{line}")
        currents = sum(dss.CktElement.CurrentsMagAng()[::2])  # Sum of currents
        powers = dss.CktElement.Powers()  # Powers at both ends
        P_origin = sum(powers[::2][:3])  # Active power at the origin end
        Q_origin = sum(powers[1::2][:3])  # Reactive power at the origin end
        losses = dss.CktElement.Losses()[0] / 1000  # Losses (in kW)
        new_line = pd.DataFrame([[timestep,line,round(currents,4),round(P_origin,4),round(Q_origin,4),round(losses,4)]], columns=columns)
        branch_df = pd.concat([branch_df,new_line],ignore_index=True)
        # print(f"{line}\t\t{currents:.4f}\t\t{P_origin:.4f}\t\t\t{Q_origin:.4f}\t\t\t{losses:.4f}")
    
    return branch_df

def get_bus_voltages(timestep,buses,voltages):
    
    #Create a empty dataframe to store the voltages
    columns = ['Timestep','Bus','Voltage']
    voltage_df = pd.DataFrame(columns=columns)
    for bus, voltage in zip(buses, voltages):
        new_line = pd.DataFrame([[timestep, bus, round(voltage,4)]], columns=columns)
        voltage_df = pd.concat([voltage_df, new_line], ignore_index=True)

    return voltage_df

        
