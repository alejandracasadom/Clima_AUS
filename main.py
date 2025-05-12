import pandas as pd
import funciones as f
import seaborn as sns
import random
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
   #Limpiamos y renombramos el dataser
   f. limpiar_dataset()
   f.renombrar_columnas()

   #Creamos la matriz
   df = pd.read_csv("datos_tiempo.csv")
   matriz=f.crear_matriz_transicion(df)


   # GRÁFICO 1: ¿cuántos días fueron Soleados, Nublados, Lluviosos?
   df_fecha = pd.read_csv("datos_tiempo.csv", parse_dates=['Fecha'])
   #f.grafico_dias(df_fecha)


   # GRÁFICO 2: heatmap de la matriz de transición
   #f.heatmap(matriz)


   # GRÁFICO 3: ver que transiciones ocurren más
   #f.grafico_transiciones(df)


   # GRÁFICO 4: explica visualmente cómo se transita entre los estados y con qué probabilidad.
   #Cada nodo representa un estado del clima, las flechas indican las probabilidades de transición entre los estados y el grosor de la flecha representa la fuerza de la probabilidad.
   #f.diagrama_markov(matriz)



   # Por ejemplo, simular desde el 1 de enero de 2018 hasta el 31 de diciembre de 2025.
   start_date = datetime(2018, 1, 1)
   end_date   = datetime(2025, 12, 31)
   initial_state = 'Soleado'

   # Ejecutar la simulación
   df_simulation = f.simulate_weather(initial_state, start_date, end_date)

   # Mostrar las primeras y últimas filas de la simulación
   print("Primeros registros de la simulación:")
   print(df_simulation.head())
   print("\nÚltimos registros de la simulación:")
   print(df_simulation.tail())

   df_simulation['Year'] = df_simulation['Date'].dt.year
   conteo_anual = df_simulation.groupby(['Year', 'Weather']).size().unstack(fill_value=0)

   conteo_anual.plot(kind='bar', figsize=(10,6))
   plt.title("Distribución anual de estados climáticos simulados")
   plt.xlabel("Año")
   plt.ylabel("Cantidad de días")
   plt.legend(title="Clima")
   plt.tight_layout()
   plt.show()



