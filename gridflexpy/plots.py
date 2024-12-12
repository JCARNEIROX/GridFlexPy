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


def plot(x,y,title='',xlabel='',ylabel='',figsize=(8,6),grid = True, lines=[],**kwargs):

    """ 
    Função para plotar um gráfico de linha.
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
        fig = plot_graph_multlines(x,y,lines,grid,title,xlabel,ylabel,figsize,**kwargs)

    return fig
    
def plot_graph_multlines(x, y, labels,grid, title, xlabel, ylabel, figsize, **kwargs):

    fig = plt.figure(figsize=figsize)
    for label in labels:
        data = y.loc[y['Name']==label,'P(kW)']
        plt.plot(x, data,label=label,**kwargs)

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

def display_graph(fig):
    fig.show()
    plt.show(block=True)

def save_fig(fig,name_file,path):
    ax = fig.gca()  # Obter o eixo atual
    ax.set_aspect('auto')  # Configurar o aspecto para automático ou um valor específico
    fig.tight_layout()
    fig.savefig(path+name_file, bbox_inches='tight', dpi=300)  # 'bbox_inches' para evitar cortes no gráfico
    print(f"Figura salva em: {path}")

