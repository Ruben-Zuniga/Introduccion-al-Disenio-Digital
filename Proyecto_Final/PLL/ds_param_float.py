import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
    
def quantize(v):
    """
    Cuantificador
    
    Args:
        v: Entrada al cuantificador
        
    Returns:
        y: Salida cuantizada (+1 o -1 para 2 niveles)
    """
    if v >= 0:
        return 1
    else:
        return -1

# ==================== Configuración de Simulación ====================

# Parámetros de simulación
N_ORDER = 3             # Orden del modulador
N_SAMPLES = 50000       # Numero de muestras
fs = 64e3               # Frecuencia de muestreo (Hz)

duration = N_SAMPLES / fs    # Duración (segundos)

# ==================== Generar Señal de Entrada ====================

t = np.linspace(0, duration, N_SAMPLES, endpoint=False)

# Constante
x = 1/5 * np.ones(N_SAMPLES)

# ==================== Procesar Señal ====================

u      = np.zeros((N_ORDER, N_SAMPLES), np.float64)
v      = np.zeros((N_ORDER, N_SAMPLES), np.float64)
e      = np.zeros((N_ORDER, N_SAMPLES), np.float64)
y      = np.zeros(N_SAMPLES, np.float64)
y_parc = np.zeros((N_ORDER, N_SAMPLES), np.float64)
y_diff = np.zeros((N_ORDER, N_SAMPLES), np.float64)
y_sum  = np.zeros((N_ORDER, N_SAMPLES), np.float64)

# Empezar en i = N_orden-1 para tener estados iniciales
for i in range(N_ORDER-1, len(x)):

    for j in range(N_ORDER):
        # Actualizacion de registros
        v[j][i] = v[j][i-1] + u[j][i-1]
        # Salida de los cuantizadores
        y_parc[j][i] = quantize(v[j][i])

    # Señales intermedias
    u[0][i] = x[i] - y_parc[0][i]
    for j in range(N_ORDER-1):
        e[j][i] = v[j][i] - y_parc[j][i]
        u[j+1][i] = e[j][i] - y_parc[j+1][i]

    # Red de cancelacion de error si el orden es mayor a 1
    if N_ORDER == 1:
        y[i] = y_parc[0][i]

    else:
        y_diff[N_ORDER-1][i] = y_parc[N_ORDER-1][i] - y_parc[N_ORDER-1][i-1]
        for j in range(N_ORDER-2):
            y_sum[N_ORDER-2 - j][i] = y_parc[N_ORDER-2 - j][i - (j+1)] + y_diff[N_ORDER-1 - j][i]
            y_diff[N_ORDER-2 - j][i] = y_sum[N_ORDER-2 - j][i] - y_sum[N_ORDER-2 - j][i-1]

        y_sum [0][i] = y_parc[0][i - (N_ORDER-1)] + y_diff[1][i]

        y[i] = y_sum[0][i]


    # y_sum [2][i] = y_parc[2][i-1] + y_diff[3][i]
    # y_diff[2][i] = y_sum [2][i]   - y_sum [2][i-1]

    # y_sum [1][i] = y_parc[1][i-2] + y_diff[2][i]
    # y_diff[1][i] = y_sum [1][i]   - y_sum [1][i-1]


    # y[i] = y0[i-1] + y1[i] - y1[i-1] #2

    # y[i] = y0[i-2] + (y1[i-1] + (y2[i] - y2[i-1])) - (y1[i-2] + (y2[i-1] - y2[i-2])) #3

    # y[i] = y0[i-3] + (y1[i-2] + (y2[i-1] + (y3[i] - y3[i-1]))) - (y1[i-3] + (y2[i-2] + (y3[i-1] - y3[i-2]))) #4



# ==================== Calculo de Resultados ====================

# Calcular error de cuantizacion
quantization_error = x - y      # Error final

# ==================== Resultados ====================

print("\n" + "=" * 60)
print("RESULTADOS")
print("=" * 60)
print(f"\nSalida y[n]:")
print(f"  Media: {np.mean(y):.6f}")
print(f"  Desviación estándar: {np.std(y):.6f}")
print(f"  Distribución:")
unique, counts = np.unique(y, return_counts=True)
for val, count in zip(unique, counts):
    percentage = count / len(y) * 100
    print(f"    Nivel {val}: {count} muestras ({percentage:.2f}%)")

print(f"\nError de cuantización:")
print(f"  Media: {np.mean(quantization_error):.6f}")
print(f"  Desviación estándar: {np.std(quantization_error):.6f}")
print(f"  Valor pico: {np.max(np.abs(quantization_error)):.6f}")

print("=" * 60)

# ==================== Visualización ====================

fig, axes = plt.subplots(3, 1, figsize=(12, 10))
plt.subplots_adjust(hspace=0.409)
fig.suptitle(f'Simulación Delta-Sigma de Orden {N_ORDER}', fontsize=14, fontweight='bold')

# Tiempo en ms
t_ms = np.linspace(0, duration*1000, N_SAMPLES, endpoint=False)

# 1. Señal de entrada
axes[0].plot(t_ms, x, 'b-', linewidth=1, alpha=0.8)
axes[0].set_ylabel('Amplitud')
axes[0].set_title('Señal de Entrada x[n]')
axes[0].grid(True, alpha=0.3)
# axes[0].set_xlim(0, 100)

# 2. Salida del cuantificador
axes[1].plot(t_ms, y, 'r-',label='y[n]', linewidth=1, alpha=0.8, drawstyle='steps-post')
axes[1].set_ylabel('Nivel Binario')
axes[1].set_title('Salida Cuantizada y[n]')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

axes[2].plot(t_ms, quantization_error, 'r-', label='e[n]', alpha=0.8)
axes[2].set_ylabel('Valor')
axes[2].set_title('Errores de Cuantizacion')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_xlabel('Tiempo (ms)')


# 4. Espectro de frecuencia (FFT)
fft_x = np.abs(np.fft.fft(x[10:])[:len(x)//2])
fft_y = np.abs(np.fft.fft(y[10:])[:len(y)//2])
freq = np.fft.fftfreq(N_SAMPLES, 1/fs)[:len(fft_x)]

fig, axes = plt.subplots(1, 1, figsize=(12, 10))
fig.suptitle(f'Simulación Delta-Sigma de Orden {N_ORDER}', fontsize=14, fontweight='bold')

axes.semilogy(freq, fft_x**2, 'b-', label='Entrada', alpha=0.8)
axes.semilogy(freq, fft_y**2, 'r-', label='Salida', alpha=0.8)
axes.set_xlabel('Frecuencia (Hz)')
axes.set_ylabel('Potencia Espectral')
axes.set_title('Espectro de Frecuencia')
axes.legend(loc='upper right')
axes.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.show()