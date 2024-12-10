import pandas as pd
import re
from generator import add_gd, get_GneratorPower
from bess import add_bat
from load import add_load

def power_flow(date_ini,date_end,step,opendssmodel,batteries,generators,loads,dss):

    time_range = pd.date_range(date_ini, date_end, freq=str(step) + 'T')

    for timestep in time_range:
        print(f"\n\nTimestep: {timestep}")
        #Clean the prompt comand of the OpenDSS
        dss.Basic.ClearAll()
        dss.Basic.Start(0)
        dss.Command(f"Compile {opendssmodel}")
        buses = dss.Circuit.AllBusNames()

        #Add the generators to the OpenDSS model
        # for generator in generators:
        #     # Update the power of the generator in the timestep
        #     generator.update_power(timestep)
        #     # Write the command
        #     dss.Command(add_gd(generator))

        #Add the batteries to the OpenDSS model
        for battery in batteries:
            dss.Command(add_bat(battery))

        #Add the loads to the OpenDSS model
        for load in loads:
            load.update_power(timestep)
            dss.Command(add_load(load))

        #Solve the power flow
        dss.Solution.Solve()  

        # Display bus voltages
        voltages = dss.Circuit.AllBusVMag()

        print("\nBus Phase Voltages (V):")
        for bus, voltage in zip(buses, voltages):
            print(f"{bus}: {voltage:.4f}")
        
        # Get the power of the buses
        # Display powers at buses
        total_activepower,total_reactivepower = get_bus_power(buses,dss)

        # Display power and current flows in branches
        display_branch_flows(dss)

        print("\nPower delivered to circuit:")
        print("Active power (kW)\tReactive power (kvar)")
        total_power = dss.Circuit.TotalPower()
        print(f"\t{total_power[0]:.4f}\t\t{total_power[1]:.4f}")
        print("\nTotal losses (kW): ")
        active_losses,reactive_losses = dss.Circuit.Losses()
        print(f"\t{active_losses / 1000:.4f}")

        print("\nPower Balance:")
        print("Active Power (kW)\tReactive Power (kvar)")
        print(f"\t{abs(total_power[0])-(total_activepower+active_losses/1000):.4f}\t\t{abs(total_power[1])-(total_reactivepower+reactive_losses/1000):.4f}")



def get_bus_power(buses,dss):
    print("\nPowers at Buses:")
    print("Bus\tActive Power (kW)\tReactive Power (kvar)")

    total_active_power = 0
    total_reactive_power = 0
    elements = dss.Circuit.AllElementNames()
    for bus in buses:
        active_power = 0
        reactive_power = 0

        # Filtra as cargas associadas ao barramento atual
        # loads = [element for element in elements if element.startswith("Load.") and bus in element]
        loads = [element for element in elements if re.search(f"{bus}", element)]

        for load in loads:
            dss.Circuit.SetActiveElement(load)
            powers = dss.CktElement.Powers()
            active_power += sum(powers[::2])  # Somando potências ativas
            reactive_power += sum(powers[1::2])  # Somando potências reativas

        # Acumula as potências totais
        total_active_power += active_power
        total_reactive_power += reactive_power

        # Exibe as potências do barramento atual
        print(f"{bus}\t{active_power:.4f}\t\t{reactive_power:.4f}")

    # Exibe as potências totais do sistema
    print("\nTotal Active Power (kW): {:.4f}".format(total_active_power))
    print("Total Reactive Power (kvar): {:.4f}".format(total_reactive_power))

    return total_active_power,total_reactive_power

def display_branch_flows(dss):
    print("\nFlows in Branches:")
    print("Branch\t\tTotal Current (A)\tActive Power (kW)\tReactive Power (kvar)\t\tLosses (kW)")
    lines = dss.Lines.AllNames()  # List of all lines in the circuit
    for line in lines:
        dss.Circuit.SetActiveElement(f"Line.{line}")
        currents = sum(dss.CktElement.CurrentsMagAng()[::2])  # Sum of currents
        powers = dss.CktElement.Powers()  # Powers at both ends
        P_origin = sum(powers[::2][:3])  # Active power at the origin end
        Q_origin = sum(powers[1::2][:3])  # Reactive power at the origin end
        losses = dss.CktElement.Losses()[0] / 1000  # Losses (in kW)
        print(f"{line}\t\t{currents:.4f}\t\t{P_origin:.4f}\t\t\t{Q_origin:.4f}\t\t\t{losses:.4f}")

        

