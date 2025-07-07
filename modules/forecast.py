import torch
import torch.nn as nn
import numpy as np

 # Use cuda if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Simplified LSTM model for time series forecasting
# class LSTMModel(nn.Module):
#     def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
#         super().__init__()
#         self.hidden_size = hidden_size
#         self.num_layers = num_layers
#         self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
#         self.fc   = nn.Linear(hidden_size, output_size)

#     def forward(self, x):
#         h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, device=x.device)
#         c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, device=x.device)
#         out, _ = self.lstm(x, (h0, c0))
#         return self.fc(out[:, -1, :])

class LSTMModel(nn.Module):
    def __init__(self,input_size: int = 1,hidden_size: int = 50,num_layers: int = 2, output_size: int = 1,dropout: float = 0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM com dropout entre camadas
        self.lstm = nn.LSTM(input_size,hidden_size,num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0.0)

        # Dropout após LSTM para evitar overfitting
        self.dropout = nn.Dropout(dropout)

        # Duas camadas fully-connected para maior capacidade não-linear
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size // 2, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, seq_len, input_size]
        batch_size = x.size(0)
        # inicializa estados ocultos
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)

        # forward LSTM
        out, _ = self.lstm(x, (h0, c0))
        # pega saída do último time step
        out = out[:, -1, :]  # [batch, hidden_size]
        out = self.dropout(out)

        # cabeçalho fully-connected
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out

def load_model(model_path,config:dict):
   
    # Load the model
    # model = LSTMModel(config['in_feature'], hidden_size=config['hidden_size'],num_layers=config['num_layers'], output_size=config['n_future']).to(device)   # mesmo hidden_size!
    model = LSTMModel(config['in_feature'], hidden_size=config['hidden_size'],num_layers=config['num_layers'], output_size=config['n_future'],dropout=config['dropout']).to(device)   # mesmo hidden_size!

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def predict_demand(model, scaler, demand_prev, i, window_size):
    """
    Recebe:
      - model: LSTM treinada com output_size = n_future
      - scaler: MinMaxScaler já “fitado” no conjunto de treino
      - device: 'cpu' ou 'cuda'
      - demand_prev: lista (ou array) de tuplas/linhas, onde row[1] é o valor numérico da demanda
      - i: índice atual em demand_prev
      - window_size: quantos pontos anteriores usar (ex.: 151)

    Retorna:
      - Um array de tamanho n_future com [demand(t), demand(t+1), …]
    """
    # 1) Extrai apenas os valores numéricos (coluna P(kW)) de demand_prev
    # p_vals = np.array([float(row[1]) for row in demand_prev])
    p_vals = demand_prev

    # 2) Seleciona a janela de window_size pontos: de (i-window_size+1) até i (inclusive)
    window = p_vals[i - (window_size - 1) : i + 1]  # shape: (window_size,)

    # 3) Normaliza usando o scaler já “fitado” no treino
    window_scaled = scaler.transform(window.reshape(-1, 1)).flatten()  # shape: (window_size,)

    # 4) Monta o tensor no formato [batch, seq_len, 1]
    x = (
        torch.tensor(window_scaled, dtype=torch.float32)
             .unsqueeze(0)   # -> (1, window_size)
             .unsqueeze(2)   # -> (1, window_size, 1)
             .to(device)
    )

    # 5) Faz a predição (sem gradiente)
    model.eval()
    with torch.no_grad():
        y_pred_scaled = model(x).cpu().numpy()  # shape: (1, n_future)

    # 6) Desnormaliza as n_future saídas de volta à escala original
    #    y_pred_scaled tem shape (1, n_future),
    #    scaler.inverse_transform espera (n_amostras, 1) ou (n_amostras, n_features).
    #    Aqui n_amostras = 1, n_features = n_future.
    y_pred_desnorm = scaler.inverse_transform(y_pred_scaled)  # shape: (1, n_future)

    # 7) Retorna como vetor 1D com n_future valores
    return y_pred_desnorm[0]  # array de tamanho n_future

def predict_demand_multi(model, scalers, load_prev, loss_prev,pv_prev,i, window_size):
    """
    Usa o modelo multifeature treinado para prever demanda a partir de:
      - janelas de tamanho window_size das séries: load, loss, pv, bess
    Retorna um array 1D de tamanho n_future com o(s) próximo(s) valor(es) de demanda.
    """
    # desempacota scalers
    scaler_load, scaler_loss, scaler_pv, scaler_target = scalers

    # extrai as janelas de cada série: último window_size valores até i
    start = i - window_size + 1
    load_w = np.array(load_prev[start:i+1], dtype=float)
    loss_w = np.array(loss_prev[start:i+1], dtype=float)
    pv_w   = np.array(pv_prev[start:i+1],   dtype=float)

    # aplica cada scaler individualmente
    load_s = scaler_load.transform(load_w.reshape(-1,1)).flatten()
    loss_s = scaler_loss.transform(loss_w.reshape(-1,1)).flatten()
    pv_s   = scaler_pv.transform(pv_w.reshape(-1,1)).flatten()

    # monta matriz de features: shape (window_size, 4)
    X_window = np.stack([load_s, loss_s, pv_s], axis=1)

    # converte para tensor shape (1, window_size, 4)
    x = torch.tensor(X_window, dtype=torch.float32)
    x = x.unsqueeze(0).to(device)

    # predição sem gradiente
    model.eval()
    with torch.no_grad():
        y_scaled = model(x).cpu().numpy()  # shape (1, n_future)

    # desnormaliza a saída
    y_des = scaler_target.inverse_transform(y_scaled)  # shape (1, n_future)

    # retorna vetor 1D
    return y_des.flatten()

