# Importar a interface de plotagem
from plots import plot_interface

# Dicionário com textos para os menus
menus = {
    "main": """What do you want to do?
Options:
    1 - Run Power Flux
    2 - See available graphs
    3 - See DataFrames
    4 - Plot Graphs
    9 - Quit
Choose an option""",
    "invalid_option": "Invalid Option. Please try again.",
    "plot_menu": """Choose the type of plot
    1 - Power
    2 - Voltage
    3 - Branch Flows
Choose an option""",
    "powers_plot_menu": """Do you want to see the power of:
    1 - Loads
    2 - Generators
    3 - Delivered to Circuit
    4 - Total Losses
    5 - Buses
Choose an option""",
    "graph_specifications": """Give the graph Specifications:
    Title
    FigSize in inches: height width
"""
}

# Função para exibir menus
def display_menu(menu_key):
    print(menus[menu_key])

# Loop principal de interação
while True:
    display_menu("main")  # Exibe o menu principal
    option = input()

    # Verificar se a opção é válida
    while not option.isdigit() or int(option) not in [1, 2, 3, 4, 9]:
        print(menus["invalid_option"])
        display_menu("main")
        option = input()

    # Processar as opções escolhidas
    option = int(option)
    if option == 1:
        print("Running Power Flux...")
        # Código para executar o fluxo de potência
    elif option == 2:
        print("Available graphs:")
        # Código para listar gráficos disponíveis
    elif option == 3:
        print("Displaying DataFrames...")
        # Código para exibir DataFrames
    elif option == 4:
        display_menu("plot_menu")  # Exibe o menu de plotagem
        plot_option = input()
        while not plot_option.isdigit() or int(plot_option) not in [1, 2, 3]:
            print(menus["invalid_option"])
            display_menu("plot_menu")
            plot_option = input()

        plot_option = int(plot_option)
        if plot_option == 1:
            display_menu("powers_plot_menu")
            power_option = input()
            while not power_option.isdigit() or int(plot_option) not in [1, 2, 3, 4, 5]:
                print(menus["invalid_option"])
                display_menu("powers_plot_menu")
                power_option = input()
            else:
                display_menu("graph_specifications")
                title = input('Title: ')
                h,w = input('FigSize: ').split(' ')
        elif plot_option == 2:
            print("Generating Power Plot...")
            plot_interface("power")  # Função para plotar gráfico de potência
        elif plot_option == 3:
            continue  # Retorna ao menu principal
    elif option == 9:
        print("Exiting the program. Goodbye!")
        break
