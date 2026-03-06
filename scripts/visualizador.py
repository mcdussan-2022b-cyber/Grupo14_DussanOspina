#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Cargar datos
df = pd.read_csv('data/clima.csv')

# Configurar figura con 4 gráficas
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('🌦️ Análisis Climático - Ciudades de Colombia', fontsize=16, fontweight='bold', y=1.02)

colores = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

# 1. Temperatura vs Sensación Térmica
ax1 = axes[0, 0]
x = np.arange(len(df))
width = 0.35
ax1.bar(x - width/2, df['temperatura'], width, label='Temperatura', color='#3498db', alpha=0.8)
ax1.bar(x + width/2, df['sensacion_termica'], width, label='Sensación Térmica', color='#e74c3c', alpha=0.8)
ax1.set_title('Temperatura vs Sensación Térmica (°C)', fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(df['ciudad'], rotation=15)
ax1.set_ylabel('°C')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 2. Humedad por ciudad
ax2 = axes[0, 1]
bars = ax2.bar(df['ciudad'], df['humedad'], color=colores, alpha=0.8, edgecolor='white')
ax2.set_title('Humedad Relativa (%)', fontweight='bold')
ax2.set_ylabel('%')
ax2.set_ylim(0, 110)
ax2.tick_params(axis='x', rotation=15)
ax2.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, df['humedad']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val}%', ha='center', va='bottom', fontsize=9)

# 3. Velocidad del viento
ax3 = axes[1, 0]
ax3.plot(df['ciudad'], df['velocidad_viento'], marker='o', color='#2ecc71',
         linewidth=2, markersize=8, markerfacecolor='white', markeredgewidth=2)
ax3.fill_between(range(len(df)), df['velocidad_viento'], alpha=0.2, color='#2ecc71')
ax3.set_title('Velocidad del Viento (km/h)', fontweight='bold')
ax3.set_ylabel('km/h')
ax3.tick_params(axis='x', rotation=15)
ax3.grid(alpha=0.3)
for i, val in enumerate(df['velocidad_viento']):
    ax3.text(i, val + 0.3, f'{val}', ha='center', fontsize=9)

# 4. Mapa de calor de variables
ax4 = axes[1, 1]
variables = ['temperatura', 'humedad', 'velocidad_viento']
data_matrix = df[variables].T.values
im = ax4.imshow(data_matrix, aspect='auto', cmap='YlOrRd')
ax4.set_xticks(range(len(df)))
ax4.set_xticklabels(df['ciudad'], rotation=15)
ax4.set_yticks(range(len(variables)))
ax4.set_yticklabels(['Temp (°C)', 'Humedad (%)', 'Viento (km/h)'])
ax4.set_title('Mapa de Calor - Variables Climáticas', fontweight='bold')
plt.colorbar(im, ax=ax4)
for i in range(len(variables)):
    for j in range(len(df)):
        ax4.text(j, i, f'{data_matrix[i, j]:.0f}', ha='center', va='center',
                fontsize=9, color='black')

plt.tight_layout()
plt.savefig('data/clima_analysis.png', dpi=150, bbox_inches='tight')
print("✅ Gráfica guardada en data/clima_analysis.png")
plt.show()