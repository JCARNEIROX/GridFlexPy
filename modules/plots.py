import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#Defautl configurations for the plots
plt.close('all')
plt.style.use('ggplot')
plt.rcParams["figure.figsize"] = (8,4)
plt.rcParams["figure.dpi"] = 100
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['cmr10']
plt.rcParams['axes.unicode_minus'] = False


def plot(graph,x,y,title='',xlabel='',ylabel='',figsize=(8,6),grid = True, lines=[],**kwargs):

    """ 
    Função para plotar um gráfico de linha.
    graph: tipo de gráfico
           'Power': gráfico de potência
            'Voltage': gráfico de tensão
    Parâmetros: x axis for time
                y axis for power
                title: name of the plot
                xlabel: label of x axis
                ylabel: label of y axis
                figsize: width and height of the plot in inches 
                lines: lines that will be plotted
                **kwargs: addtinional arguments for the plot like matplotlib.pyplot args
                for more kwargs informations see: https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.html
    """
    if len(lines)>1:
        fig = plot_graph_multlines(graph,x,y,lines,grid,title,xlabel,ylabel,figsize,**kwargs)

    return fig
    
def plot_graph_multlines(graph,x, y, labels,grid, title, xlabel, ylabel, figsize, **kwargs):

    fig = plt.figure(figsize=figsize)
    if graph == 'Power':
        for label in labels:
            data = y.loc[y['Name']==label,'P(kW)']
            plt.plot(x, data,label=label,**kwargs)

    plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    # Format the x axis to display readable times
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Hour:minute format
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Can change the interval of the major ticks
    plt.minorticks_on()
    
    return fig

def plot_graph(x, y, title='', xlabel='', ylabel='', figsize=(8, 6), **kwargs):

    plt.figure(figsize=figsize)
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    # Personalizar o eixo x para exibir tempos legíveis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Exemplo: apenas hora:minuto
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Intervalo de 1 hora nos ticks principais
    plt.minorticks_on()

    
    plt.show()

def plot_bus_voltages(time,voltage_df,title,xlabel,ylabel,figsize=(8,6),grid=True,**kwargs):
    fig = plt.figure(figsize=figsize)
    #List all buses in the colum 'Bus' of dataframe
    buses = voltage_df['Bus'].unique()
    for bus in buses[:len(buses)-1:1]:
        data = voltage_df.loc[voltage_df['Bus']==bus,'Voltage']
        plt.plot(time,data,label=bus,**kwargs)
    
    plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    # Personalizar o eixo x para exibir tempos legíveis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Exemplo: apenas hora:minuto
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Intervalo de 1 hora nos ticks principais
    plt.minorticks_on()

    return fig

def display_graph(fig):
    fig.show()
    plt.show(block=True)

def save_fig(fig,name_file,path):
    
    fig.savefig(path+name_file, bbox_inches='tight', dpi=300)  # 'bbox_inches' para evitar cortes no gráfico
    print(f"Figura salva em: {path}")

def plot_interface():
    print("Choose the type of plot:\n \t1 - Power\n \t2 - Voltage\n \t3 - Branch Flows")
    print("Choose an option")
    type_option = input()
    while type_option not in ['1','2','3']:
        print("Invalid Option")
        print("Choose the type of plot:\n \t1 - Power\n \t2 - Voltage\n \t3 - Branch Flows")
        print("Choose an option")
        type_option = input()
    graph_type = ''
    if type_option == '1':
        graph_type = 'Power'
        print("Do you want to see the power of:\n \t1 - Loads\n \t2 - Generators\n \t3 - Delivered\n \t4 - Total Losses\n \t5 - Buses")
        print("Choose an option")
        power_option = input()
        print("Give the graph Specifications:")
        title = input("Title: ")
        figsize = input("Figsize in inches: height width\n")
        h,w = figsize.split()
        print(h,w)
    elif type_option == '2':
        graph_type = 'Voltage'
    elif type_option == '3':
        graph_type = 'Branch'
    else:
        print("Invalid Option")

    
    



class Plot:
    def __init__(self,type,NameBus,title,multiline=False,Figsize=(8,6),grid=True):
        self.type = type
        self.NameBus = NameBus
        self.title = title
        self.multiline = multiline
        self.Figsize = Figsize
        self.grid = grid
    
    def multilines(self,lines):
        self.lines = lines

    def get_name_lines(self):
        list_lines = []
        for line in self.NameBus.split(''):
            list_lines.append(line)
        return list_lines