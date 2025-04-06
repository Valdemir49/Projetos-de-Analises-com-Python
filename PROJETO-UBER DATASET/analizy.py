# Algoritmo de analize do dataset: Uber Dataset
# Disponivel em: https://www.kaggle.com/datasets/ruchikakumbhar/uber-dataset?resource=download
#Algoritimo feito por: Valdemir Souza

#Objetivo: práticar conhecimentos e conceitos em analize de dados

#START_DATE : Date and time when the ride started
#END_DATE : Date and time when the ride stopped
#CATEGORY : business/personal
#START : start location
#STOP : destination
#MILES : distance covered
#PURPOSE : purpose of the ride


#######################################################################
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
#######################################################################

###################_ENTRADA DE DADOS_####################################
dataset = pd.read_csv("UberDataset.csv")
#print(dataset.head()) 

##################_LIMPEZA E ORGANIZAÇAO DE DADOS_#########################

dataset.dropna(inplace=True)  # Remove valores nulos
dataset.drop_duplicates(inplace=True)  # Remove duplicatas

#removendo: Unknown Location - 001

#dataset_001 = dataset[dataset["START"] != "Unknown Location"] #novo dataset sem as linhas Unknown Location na coluna START
#removendo: Unknown Location - 001
dataset_001 = dataset[(dataset["STOP"] != "Unknown Location") & (dataset["START"] != "Unknown Location") ]

# Convertendo para tipo datetime e extraindo apenas as horas
dataset_001["START_DATE"] = pd.to_datetime(			#Isso substitui os / por - antes da conversão.
   dataset_001["START_DATE"].str.replace("/", "-"), 
    errors="coerce", 
    format="%m-%d-%Y %H:%M"
)

dataset_001["END_DATE"] = pd.to_datetime(			#Isso substitui os / por - antes da conversão.
   dataset_001["END_DATE"].str.replace("/", "-"), 
    errors="coerce", 
    format="%m-%d-%Y %H:%M"
)

dataset_001["START_TIME"] = dataset_001["START_DATE"].dt.time # Extraindo somente a hora
dataset_001["END_TIME"] = dataset_001["END_DATE"].dt.time

# Converta as colunas para o formato datetime
dataset_001["START_TIME"] = pd.to_datetime(dataset_001["START_TIME"], format="%H:%M:%S")
dataset_001["END_TIME"] = pd.to_datetime(dataset_001["END_TIME"], format="%H:%M:%S")

# Calculndo a duração de cada viagem
dataset_001["DURATION"] = (dataset_001["END_TIME"] - dataset_001["START_TIME"]).dt.total_seconds() / 60  # Converte a diferença para minutos
dataset_001 = dataset_001[dataset_001["DURATION"] >= 0] #apenas valores positovos*
cont_comb = dataset_001.groupby(["START","STOP","DURATION"]).size()
#print(cont_comb)
#print(dataset_001["DURATION"].head(100))
cont_comb_comb = cont_comb.sort_values(ascending=False) # verifica a quantidade de commbinações
#print(cont_comb_comb)

# Calcular a média da duração para cada combinação de START e STOP
media_duracao = dataset_001.groupby(["START", "STOP"])["DURATION"].mean().reset_index()

media_duracao["TRIP"] = media_duracao["START"] + " → " + media_duracao["STOP"]

# Criar dois DataFrames: um para viagens mais rápidas, outro para mais demoradas
viagens_rapidas =dataset_001.nsmallest(15, "DURATION")  # As 15 viagens mais rápidas
# Ordenar o DataFrame de viagens mais rápidas em ordem crescente da duração
viagens_rapidas = viagens_rapidas.sort_values(by="DURATION", ascending=True)
viagens_demoradas = dataset_001.nlargest(15, "DURATION")  # As 15 viagens mais demoradas

# Criar gráficos para cada caso:

#CASO 1:
grafico_rapidas = go.Bar(x=viagens_rapidas["START"] + " → " + viagens_rapidas["STOP"],
                         y=viagens_rapidas["DURATION"],
                         name="Viagens Mais Rápidas",
                         marker_color='green')


# CASO 2:
grafico_demoradas = go.Bar(x=viagens_demoradas["START"] + " → " + viagens_demoradas["STOP"],
                           y=viagens_demoradas["DURATION"],
                           name="Viagens Mais Demoradas",
                           marker_color='red')

# Configurar a alternância interativa
fig = go.Figure()
fig.add_trace(grafico_rapidas)
fig.add_trace(grafico_demoradas)

fig.update_layout(
    updatemenus=[
        dict(
            buttons=list([
                dict(
                    label="Mais Rápidas",
                    method="update",
                    args=[{"visible": [True, False]},  # Mostrar apenas o gráfico de rápidas
                          {"title": "Viagens Mais Rápidas"}]
                ),
                dict(
                    label="Mais Demoradas",
                    method="update",
                    args=[{"visible": [False, True]},  # Mostrar apenas o gráfico de demoradas
                          {"title": "Viagens Mais Demoradas"}]
                ),
                dict(
                    label="Rápidas e Demoradas",
                    method="update",
                    args=[{"visible":[True, True]},
                          {"title": "Viagens Rápidas e Demoradas"}]
                )
            ]),
            direction="down",
            showactive=True
        )
    ],
    title="Viagens Mais Rápidas e Mais Demoradas",
    xaxis_title="Trajeto (START → STOP)",
    yaxis_title="Duração (minutos)"
)

fig.show()

##########################################################################
# Plotar o gráfico
# plt.figure(figsize=(15, 6))
# plt.barh(media_duracao["TRIP"], media_duracao["DURATION"], color='skyblue')
# plt.xlabel("Duração Média (minutos)")
# plt.ylabel("Viagens (Start → Stop)")
# plt.title("Duração Média das Viagens por Trajeto")
# plt.grid(axis="x", linestyle="--", alpha=0.7)
# plt.show()

#* o erro acontece pos a viagem que vão do dia para a noite; 05:08 - 23:48 no caso a corrida começo na madrugada. CORRIGIR (removi os valores negativos apenas)
