from plots import Plot
from get_general_informations import GenInformations
from main import return_general_informations,run_powerflow
# Dicionário com textos para os menus
menus = {
    "main": """What do you want to do?
Options:
    1 - Run Power Flux
    2 - See available graphs
    3 - See DataFrames
    4 - Plot Graphs
    5 - Quit
Choose an option""",

    "power_flux_menu": {
        "power_flux_options": """Choose the power flux option:
    1 - Run Power Flux
    2 - Check general informations""",
        "check_general_informations": """All the general informations is ok?
Type Yes or No (Y/N)"""
    },

    "invalid_option": "Invalid Option. Please try again.",

    "plot_menu": """Choose the type of plot
    1 - Power
    2 - Voltage
Choose an option""",

    "powers_plot_menu": """Do you want to see the power of:
    1 - Loads
    2 - Generators
    3 - Delivered to Circuit
    4 - Total Losses
    5 - Buses
Choose an option""",

    "voltage_plot_menu":{
        "voltage_options":"""Do you want to see the voltage of specific bus,list of buses or all buses togehter?
    1 - Specific bus
    2 - List of buses
    3 - All buses""" ,
        "specific_bus":"""Please enter the name of the bus saved in the spreadsheet:""",
        "list_buses":"""Please enter the names of the buses separated by commas:"""
    },

    "graph_specifications": """Give the graph Specifications:""",

    "n_generators":{
        "generator_options":"""Do you want to see the power of specific generator,list of generators or all generators togehter?
    1 - Specific generator
    2 - List of generators
    3 - All generators""" ,
        "specific_generator":"""Please enter the name of the generator saved in the spreadsheet:""",
        "list_generators":"""Please enter the names of the generators separated by commas:"""
    } ,

    "n_buses":""""Do you want to see the power of specific bus,list of buses or all buses togehter?\n
    1 - Specific bus
    2 - List of buses
    3 - All buses
"""
}

actual_menu_option = { "menu" : "main", "option": 99} ## Load the actual menu and option, 99 is a default value and the initial is main menu

options_dict = {    ## Define the options for each menu
    "main" : [1, 2, 3, 4, 9],
    "plot_menu" : [1, 2, 3],
    "powers_plot_menu" : [1, 2, 3, 4, 5]
}

# Função para exibir menus
def display_menu(menu_key):
    print(menus[menu_key])

def display_submenu(menu,submenu):
    print(menus[menu][submenu])

previous_menu = None

plot = Plot()

# Loop principal de interação
while True:
    display_menu(actual_menu_option["menu"])  # Show the main menu
    option = input()

    # Check if the input is a digit and if it is a valid option
    while not option.isdigit() or int(option) not in [1, 2, 3, 4, 5]:
        print(menus["invalid_option"])
        display_menu(actual_menu_option["menu"])
        option = input()

    else:
        option = int(option)
        actual_menu_option["option"] = option
        if option == 1: # Power Flux
            while True:
                gen_inform = return_general_informations()
                actual_menu_option["menu"] = "power_flux_menu"
                display_submenu("power_flux_menu","power_flux_options")
                power_flux_option = input()
                while not power_flux_option.isdigit() or int(power_flux_option) not in [1, 2]:
                    print(menus["invalid_option"])
                    display_submenu("power_flux_menu","power_flux_options")
                    power_flux_option = input()
                else:
                    power_flux_option = int(power_flux_option)
                    actual_menu_option["option"] = power_flux_option
                    if power_flux_option == 1: # Run Power Flux
                        actual_menu_option["menu"] = "main"
                        print("Running Power Flux...\n")
                        del gen_inform
                        run_powerflow()
                        break
                        # Código para executar o fluxo de potência
                    elif power_flux_option == 2: # Check general informations
                        print(f'Start Date: {gen_inform.start_date}')
                        print(f'End Date: {gen_inform.end_date}')
                        print(f'Timestep: {gen_inform.timestep}')
                        display_submenu("power_flux_menu","check_general_informations")
                        check = input()

                        while check.lower() not in ['y', 'n', 'yes', 'no']:
                            print(menus["invalid_option"])
                            display_submenu("power_flux_menu","check_general_informations")
                            check = input()
                        else:
                            if check.lower() in ['y', 'yes']:
                                print("All general informations are correct.")
                                continue
                            elif check.lower() in ['n', 'no']:
                                del gen_inform
                                print("Please, correct the general informations in the spreadsheet file and save again!.")
                                # Return to the previous menu
                                continue

                                # Código para corrigir as informações gerais
                        # Código para exibir informações gerais

            # Código para executar o fluxo de potência
        elif option == 2: # Available Graphs
            print("Available graphs:")
            # Código para listar gráficos disponíveis
        elif option == 3: # DataFrames
            print("Displaying DataFrames...")
            # Código para exibir DataFrames
        elif option == 4: # Plot Graphs
            actual_menu_option["menu"] = "plot_menu"
            display_menu(actual_menu_option["menu"])  # Exibe o menu de plotagem
            type_plot = input()
            while not type_plot.isdigit() or int(type_plot) not in [1, 2]:
                print(menus["invalid_option"])
                display_menu(actual_menu_option["menu"])
                type_plot = input()
            else:
                type_plot = int(type_plot)
                actual_menu_option["option"] = type_plot
                if type_plot == 1: ## Power
                    plot.update_type('Power') ## Set the type of plot
                    actual_menu_option["menu"] = "powers_plot_menu"
                    display_menu(actual_menu_option["menu"])  # Exibe o menu de escolha de potências
                    power_option = input()
                    while not power_option.isdigit() or int(type_plot) not in [1, 2, 3, 4, 5]:
                        print(menus["invalid_option"])
                        display_menu(actual_menu_option["menu"])
                        power_option = input()
                    else:
                        power_option = int(power_option)
                        actual_menu_option["option"] = power_option
                        if power_option == 2:  # Generators
                            actual_menu_option["menu"] = menus["n_generators"]
                            display_submenu("n_generators","generator_options")
                            n_generators = input()
                            while not n_generators.isdigit() or int(n_generators) not in [1, 2, 3]:
                                print(menus["invalid_option"])
                                display_menu(actual_menu_option["menu"])
                                n_generators = input()
                            else:
                                n_generators = int(n_generators)
                                actual_menu_option["option"] = n_generators
                                if n_generators == 1: # Specific generator
                                    plot.multilines(False) # Only one line
                                    actual_menu_option["menu"] = menus["n_generators"]
                                    display_submenu("n_generators","specific_generator")
                                    plot.nameobjects(input())
                                    # Show to user choose the specifications of the graph
                                    actual_menu_option["menu"] = "graph_specifications"
                                    display_menu(actual_menu_option["menu"])
                                    plot.update_title(input("Title: "))
                                    h,w = input("FigSize in inches: height width\n").split(' ')
                                    plot.FigSize((int(h),int(w)))
                                    plot.AddGrid(True if input("Grid: Y/N\n").lower() == 'y' else False)
                                    print("Generating Power Plot...")
                                elif n_generators == 2: # List of generators
                                    plot.multilines(True)
                                    actual_menu_option["menu"] = menus["n_generators"]
                                    display_submenu("n_generators","list_generators")
                                    plot.nameobjects([x.strip() for x in input().split(",")]) # List of generators
                                    # Show to user choose the specifications of the graph
                                    actual_menu_option["menu"] = "graph_specifications"
                                    display_menu(actual_menu_option["menu"])
                                    plot.update_title(input("Title: ")) # Title
                                    h,w = input("FigSize in inches: height width\n").split(' ')
                                    plot.FigSize((int(h),int(w)))
                                    plot.AddGrid(True if input("Grid: Y/N\n").lower() == 'y' else False)
                                    print("Generating Power Plot...")
                                elif n_generators == 3: # All generators
                                    plot.multilines(True)
                                    actual_menu_option["menu"] = menus["n_generators"]
                                    # Show to user choose the specifications of the graph
                                    actual_menu_option["menu"] = "graph_specifications"
                                    display_menu(actual_menu_option["menu"])
                                    plot.update_title(input("Title: ")) # Title
                                    h,w = input("FigSize in inches: height width\n").split(' ')
                                    plot.FigSize((int(h),int(w)))
                                    plot.AddGrid(True if input("Grid: Y/N\n").lower() == 'y' else False)
                                    # Código para plotar gráfico de potência de lista de geradores
                                    print("Generating Power Plot...")
                elif type_plot == 2: # Voltage
                    plot.update_type('Voltage')
                    actual_menu_option["menu"] = "voltage_plot_menu"
                    display_submenu("voltage_plot_menu","voltage_options")
                    voltage_option = input()
                    while not voltage_option.isdigit() or int(voltage_option) not in [1, 2, 3]:
                        print(menus["invalid_option"])
                        display_menu(actual_menu_option["menu"])
                        voltage_option = input()
                    else:
                        voltage_option = int(voltage_option)
                        actual_menu_option["option"] = voltage_option
                        if voltage_option == 1: # Specific bus
                            actual_menu_option["menu"] = "voltage_plot_menu"
                            display_submenu("voltage_plot_menu","specific_bus")
                            plot.nameobjects(input())
                            # Show to user choose the specifications of the graph
                            actual_menu_option["menu"] = "graph_specifications"
                            display_menu(actual_menu_option["menu"])
                            plot.update_title(input("Title: "))
                            h,w = input("FigSize in inches: height width\n").split(' ')
                            plot.FigSize((int(h),int(w)))
                            plot.AddGrid(True if input("Grid: Y/N\n").lower() == 'y' else False)
                            print("Generating Voltage Plot...")
                        elif voltage_option == 2: # List of buses
                            actual_menu_option["menu"] = "voltage_plot_menu"
                            display_submenu("voltage_plot_menu","list_buses")
                            plot.nameobjects([x.strip() for x in input().split(",")])
                            # Show to user choose the specifications of the graph
                            actual_menu_option["menu"] = "graph_specifications"
                            display_menu(actual_menu_option["menu"])
                            plot.update_title(input("Title: "))
                            h,w = input("FigSize in inches: height width\n").split(' ')
                            plot.FigSize((int(h),int(w)))
                            plot.AddGrid(True if input("Grid: Y/N\n").lower() == 'y' else False)
                            print("Generating Voltage Plot...")
                        elif voltage_option == 3: # All buses
                            # Show to user choose the specifications of the graph
                            actual_menu_option["menu"] = "graph_specifications"
                            display_menu(actual_menu_option["menu"])
                            plot.update_title(input("Title: "))
                            h,w = input("FigSize in inches: height width\n").split(' ')
                            plot.FigSize((int(h),int(w)))
                            plot.AddGrid(True if input("Grid: Y/N\n").lower() == 'y' else False)
                            print("Generating Voltage Plot...")


        elif option == 5: # Quit
            print("Exiting the program. Goodbye!")
            break
