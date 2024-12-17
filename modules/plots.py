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


class Plot:
    def __init__(self,type='',NameObject=[],title='',multiline=False,Figsize=(8,6),grid=True):
        self.type = type
        self.NameObject = NameObject
        self.title = title
        self.multiline = multiline
        self.Figsize = Figsize
        self.grid = grid

    def update_type(self,type):
        self.type = type
    
    def nameobjects(self,list_object):
        if type(list_object) == str:
            self.NameObject = list_object
        else:
            self.NameObject = list_object
    
    def update_title(self,title):
        self.title = title
    
    def multilines(self,bool):
        self.multiline = bool
    
    def FigSize(self,size):
        self.FigSize =size
    
    def AddGrid(self,bool):
        self.grid = bool
    
