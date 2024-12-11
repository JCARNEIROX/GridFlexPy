import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Definições da MatPlotLib
plt.close('all')
plt.style.use('ggplot')
plt.rcParams["figure.figsize"] = (8,4)
plt.rcParams["figure.dpi"] = 100
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['cmr10']
plt.rcParams['axes.unicode_minus'] = False


def plot_graph_multlines(x, y,labels, title='', xlabel='', ylabel='', figsize=(8, 6)):

    plt.figure(figsize=figsize)
    plt.plot(x, y[0],label=labels[0]) 
    plt.plot(x, y[1],label=labels[1])
    plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    # Personalizar o eixo x para exibir tempos legíveis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Exemplo: apenas hora:minuto
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Intervalo de 1 hora nos ticks principais
    
    plt.show()


