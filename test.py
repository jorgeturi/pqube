import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# Función que convierte cualquier valor a kW
def convertir_a_kw(valor):
    if pd.isna(valor):
        return None
    valor = str(valor).strip()
    if 'kW' in valor:
        return float(valor.replace(' kW',''))
    elif 'W' in valor:
        return float(valor.replace(' W','')) / 1000
    else:
        return None  # descarta valores sin unidad reconocida



# Leer CSV
df = pd.read_csv("potencia.csv")
df.columns = df.columns.str.replace('"', '')

# Convertir columna Time a datetime
df['Time'] = pd.to_datetime(df['Time'])

# Poner Time como índice
df.set_index('Time', inplace=True)
print(df)
# Resample: quedarnos con 1 muestra por hora
df_hora = df
#df = df.resample('1H').first()

print(df_hora["P1"])
# Asegurarse que P1 sea numérico y eliminar NaN
#df_hora["P1"] = pd.to_numeric(df_hora["P1"], errors='coerce')
df_hora = df_hora.dropna(subset=["P1"])
df_hora = df_hora[df_hora['P1'].str.contains('kW')]


# Aplicar la función a toda la columna
df['P1_kw'] = df['P1'].apply(convertir_a_kw)

print(df)

#print(df_hora["P1"])
# Graficar
fig, ax = plt.subplots(figsize=(12,5))
ax.plot(df['P1_kw'], label='P1')

# Limitar número de ticks en el eje Y
ax.yaxis.set_major_locator(MaxNLocator(nbins=6))  # máximo 6 valores en Y

# Detalles del gráfico
ax.set_title("Serie temporal P1 (solo kW)")
ax.set_xlabel("Tiempo")
ax.set_ylabel("Potencia [kW]")
ax.grid(True)
ax.legend()
plt.tight_layout()
plt.show()





