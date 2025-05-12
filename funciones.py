import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
import random
from datetime import datetime, timedelta



def limpiar_dataset():
    # Cargar el archivo CSV
    df = pd.read_csv("weatherAUS.csv")

    # Definir las columnas que vamos a usar
    columnas_a_usar = ['Date','Location','Rainfall', 'Cloud3pm', 'Temp3pm', 'Weather']

    # Eliminar columnas no necesarias
    columnas_descartar = [col for col in df.columns if col not in columnas_a_usar]

    # Eliminar columnas
    df = df.drop(columns=columnas_descartar)

    # Eliminar filas con NaN en las columnas clave
    df = df.dropna(subset=['Rainfall', 'Cloud3pm', 'Temp3pm'])

    # Guardar el dataset limpio
    df.to_csv("weather_cleaned.csv", index=False)

    print("Limpieza completa. Dataset guardado como 'weather_cleaned.csv'")

def renombrar_columnas():
    df = pd.read_csv("weather_cleaned.csv")
    renombrar = {
        'Date': 'Fecha',
        'Rainfall': 'Lluvia',
        'Cloud3pm': 'Nubes',
        'Temp3pm': 'Temperatura',
        'Weather': 'Clima'
    }

    # Renombrar las columnas
    df = df.rename(columns=renombrar)

    # Asegurarnos de que la columna 'Fecha' sea de tipo datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%d')

    # Guardar el dataset con los nombres de columnas en español
    df.to_csv("datos_tiempo.csv", index=False)

    print("Renombrado de columnas completo. Dataset guardado como 'datos_tiempo.csv'")

def clasificar_clima(row):
    # Clasificar el clima en Soleado, Nublado o Lluvioso
    if row['Lluvia'] > 0:
        return 'Lluvioso'
    elif row['Nubes'] > 5:
        return 'Nublado'
    else:
        return 'Soleado'
    
def crear_matriz_transicion(df):

    # Clasificar los días en estados de clima
    df['Clima'] = df.apply(clasificar_clima, axis=1)
    
    # Crear una lista de transiciones entre días
    transiciones = []

    for i in range(1, len(df)):
        # Obtener el estado del día actual y el siguiente
        estado_actual = df.iloc[i-1]['Clima']
        estado_siguiente = df.iloc[i]['Clima']
        
        # Añadir la transición a la lista
        transiciones.append((estado_actual, estado_siguiente))

    # Contar las transiciones
    transiciones_df = pd.DataFrame(transiciones, columns=['Estado_Anterior', 'Estado_Siguiente'])

    matriz_transicion = pd.crosstab(transiciones_df['Estado_Anterior'], transiciones_df['Estado_Siguiente'], normalize='index')

    print(matriz_transicion)

    matriz_transicion.to_csv("matriz_transicion.csv")
    return matriz_transicion

def grafico_dias(df):
    df['Clima'] = df.apply(clasificar_clima, axis=1)

    conteo_estados = df['Clima'].value_counts()

    conteo_estados.plot(kind='bar', color=['pink', 'purple', 'blue'])
    plt.title('Distribución de los estados del clima')
    plt.xlabel('Estado')
    plt.ylabel('Cantidad de días')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

def heatmap(matriz_transicion):
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.imshow(matriz_transicion.values, cmap='Blues')

    estados = matriz_transicion.columns
    ax.set_xticks(range(len(estados)))
    ax.set_yticks(range(len(estados)))
    ax.set_xticklabels(estados)
    ax.set_yticklabels(matriz_transicion.index)

    for i in range(len(estados)):
        for j in range(len(estados)):
            valor = matriz_transicion.iloc[i, j]
            ax.text(j, i, f"{valor:.2f}", ha='center', va='center', color='black')

    plt.title("Heatmap de la Matriz de Transición del Clima")
    plt.xlabel("Estado Siguiente")
    plt.ylabel("Estado Anterior")
    fig.colorbar(cax)
    plt.tight_layout()
    plt.show()

def grafico_transiciones(df):
    df['Clima'] = df.apply(clasificar_clima, axis=1)
    df = df.sort_values('Fecha')
    
    transiciones = []
    for i in range(1, len(df)):
        estado_anterior = df.iloc[i-1]['Clima']
        estado_actual = df.iloc[i]['Clima']
        transiciones.append(f"{estado_anterior} → {estado_actual}")

    conteo = pd.Series(transiciones).value_counts()

    conteo.plot(kind='bar', color='pink')
    plt.title("Frecuencia de Transiciones entre Estados de Clima")
    plt.ylabel("Cantidad")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def diagrama_markov(matriz):
    G = nx.DiGraph()

    estados = matriz.columns.tolist()
    for estado in estados:
        G.add_node(estado)

    for origen in matriz.index:
        for destino in matriz.columns:
            prob = matriz.loc[origen, destino]
            if prob > 0.01:
                G.add_edge(origen, destino, weight=prob)

    pos = {
        'Soleado': (0, 0),
        'Lluvioso': (2, 0),
        'Nublado': (1, 1.5)
    }

    fig, ax = plt.subplots(figsize=(8, 6))

    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='pink', alpha=0.8, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=12, ax=ax)

    # Dibujar aristas normales (sin autotransiciones)
    edges = G.edges(data=True)
    curved_edges = []
    loop_edges = []

    for u, v, d in edges:
        if u != v:
            curved_edges.append((u, v, d))
        else:
            loop_edges.append((u, v, d))

    # Aristas entre diferentes nodos
    nx.draw_networkx_edges(
        G, pos,
        edgelist=[(u, v) for u, v, d in curved_edges],
        width=[d['weight'] * 5 for u, v, d in curved_edges],
        arrowstyle='-|>',
        arrowsize=25,
        edge_color='black',
        ax=ax
    )

    # Etiquetas de las transiciones normales
    edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in curved_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, ax=ax)

    # Autotransiciones (dibujadas como arcos circulares)
    for u, v, d in loop_edges:
        x, y = pos[u]
        radius = 0.25
        angle = 0
        if u == 'Soleado':
            angle = 270
        elif u == 'Lluvioso':
            angle = 0
        elif u == 'Nublado':
            angle = 90

        # Dibujar flecha curva con FancyArrow
        arc = mpatches.Arc((x, y), 1, 1, angle=angle, theta1=0, theta2=270,
                           linewidth=d['weight'] * 5, color='black')
        ax.add_patch(arc)

        # Etiqueta para la autotransición
        offset_x, offset_y = 0.4, 0.4
        ax.text(x + offset_x, y + offset_y, f"{d['weight']:.2f}",
                fontsize=10, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='black'))

    plt.title("Diagrama de Transición de Clima (Cadena de Markov)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()





states = ['Lluvioso', 'Nublado', 'Soleado']
transition_matrix = {
    'Lluvioso': [0.602205, 0.182489, 0.215306],
    'Nublado':  [0.413195, 0.287105, 0.299699],
    'Soleado':  [0.130646, 0.241171, 0.628183]
}

def simulate_weather(initial_state, start_date, end_date):
    """
    Simula el clima día a día usando la matriz de transición.
    
    Parámetros:
      - initial_state: Estado climático inicial (ej. 'Soleado')
      - start_date: Fecha de inicio (objeto datetime)
      - end_date: Fecha final (objeto datetime)
      
    Retorna:
      - DataFrame con la fecha y el estado climático simulado.
    """
    current_state = initial_state
    current_date = start_date
    simulation = []

    while current_date <= end_date:
        simulation.append((current_date, current_state))
        # Obtener las probabilidades de transitar desde el estado actual
        probabilities = transition_matrix[current_state]
        # Elegir el siguiente estado usando random.choices
        next_state = random.choices(states, weights=probabilities)[0]
        current_state = next_state
        current_date += timedelta(days=1)

    return pd.DataFrame(simulation, columns=['Date', 'Weather'])

