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

def ds_1st_order(x_n, v_delay):
    """
    Procesa una sola muestra según el diagrama de bloques
    
    Diagrama:
        x[n] -> (+) -> u[n] -> (+) -> [z^-1] -> v[n] -> [quantizer] -> y[n]
                -^              ^               |                      |
                 |              |_______________|                      |
                 |_____________________________________________________|
    Ecuaciones:
    u[n] = x[n] - y[n-1]
    v[n] = u[n] + v[n-1]
    y[n] = Q(v[n])
    
    Args:
        x_n: Muestra de entrada actual
        
    Returns:
        y_n: Muestra de salida cuantizada
    """
    # Salida anterior del cuantificador
    y_prev = quantize(v_delay)
    
    # Primera suma: u[n] = x[n] - y[n-1]
    u_n = x_n - y_prev
    
    # Segunda suma con integrador: v[n] = u[n] + v[n-1]
    v_n = u_n + v_delay
    
    # Cuantificación: y[n] = quantizer(v[n])
    y_n = quantize(v_n)
    
    # Actualizar estado del delay para la próxima muestra
    v_delay = v_n
    
    return y_n, u_n, v_n, v_delay

# ==================== Configuración de Simulación ====================

# Parámetros de simulación
fs = 64e3          # Frecuencia de muestreo (Hz)
num_samples = 50000   # Numero de muestras
f_input = 10       # Frecuencia de entrada (Hz)
amplitude = 4     # Amplitud de entrada
quantizer_levels = 2 # Niveles de cuantizacion a la salida

duration = num_samples / fs    # Duración (segundos)

# ==================== Generar Señal de Entrada ====================

t = np.linspace(0, duration, num_samples, endpoint=False)

# Constante
x = 0.5 * np.ones(num_samples)
# x = np.concatenate( [-1 * np.ones(num_samples//4), 0 * np.ones(num_samples//4), 0.5 * np.ones(num_samples//4), 1 * np.ones(num_samples//4)] )

# ==================== Procesar Señal ====================

u1 = np.zeros_like(x)
v1 = np.zeros_like(x)
y1 = np.zeros_like(x)
e1 = np.zeros_like(x)

u2 = np.zeros_like(x)
v2 = np.zeros_like(x)
y2 = np.zeros_like(x)
e2 = np.zeros_like(x)
y2t = np.zeros_like(x)

u3 = np.zeros_like(x)
v3 = np.zeros_like(x)
y3 = np.zeros_like(x)
e3 = np.zeros_like(x)

y23 = np.zeros_like(x)
y = np.zeros_like(x)

# Empezar en i = N_orden-1 para tener estados iniciales
for i in range(2,len(x)):
    v1[i] = v1[i-1] + u1[i-1]
    v2[i] = v2[i-1] + u2[i-1]
    v3[i] = v3[i-1] + u3[i-1]

    y1[i] = quantize(v1[i])
    y2[i] = quantize(v2[i])
    y3[i] = quantize(v3[i])

    u1[i] = x[i] - y1[i]
    e1[i] = v1[i] - y1[i]

    u2[i] = e1[i] - y2[i]
    e2[i] = v2[i] - y2[i]

    u3[i] = e2[i] - y3[i]

    y2t[i] = y1[i-1] + y2[i] - y2[i-1]
    y23[i] = y2[i-1] + y3[i] - y3[i-1]
    y[i] = y1[i-2] + y23[i] - y23[i-1]


# ==================== Calculo de Resultados ====================

# Calcular error de cuantificación
quantization_error = x - y
quantization_error_y2 = x - y2t
quantization_error_y1 = x - y1

# ==================== Resultados ====================

print("\n" + "=" * 60)
print("RESULTADOS")
print("=" * 60)
print(f"\nDistribución de salida y[n]:")
unique, counts = np.unique(y, return_counts=True)
for val, count in zip(unique, counts):
    percentage = count / len(y) * 100
    print(f"  Nivel {val}: {count} muestras ({percentage:.2f}%)")

print(f"\nError de cuantificación:")
print(f"  Media: {np.mean(quantization_error):.6f}")
print(f"  Desviación estándar: {np.std(quantization_error):.6f}")
print(f"  Valor pico: {np.max(np.abs(quantization_error)):.6f}")

print("=" * 60)

# ==================== Visualización ====================

fig, axes = plt.subplots(3, 1, figsize=(12, 10))
plt.subplots_adjust(hspace=0.409)
fig.suptitle('Simulación Delta-Sigma de 1er Orden', fontsize=14, fontweight='bold')

# Tiempo en ms para mejor visualización
t_ms = np.linspace(0, duration*1000, num_samples, endpoint=False)

# 1. Señal de entrada
axes[0].plot(t_ms, x, 'b-', linewidth=1, alpha=0.8)
axes[0].set_ylabel('Amplitud')
axes[0].set_title('Señal de Entrada x[n]')
axes[0].grid(True, alpha=0.3)
# axes[0].set_xlim(0, 100)

# 2. Salida del cuantificador
axes[1].plot(t_ms, y, 'r-',label='y[n]', linewidth=1, alpha=0.8, drawstyle='steps-post')
axes[1].plot(t_ms, y2t, 'g-',label='y1[n]', linewidth=0.7, alpha=0.8, drawstyle='steps-post')
axes[1].plot(t_ms, y1, 'b-',label='y1[n]', linewidth=0.7, alpha=0.8, drawstyle='steps-post')
axes[1].set_ylabel('Nivel Binario')
axes[1].set_title('Salida Cuantizada y[n]')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

axes[2].plot(t_ms, quantization_error, 'r-', label='e[n]', alpha=0.8)
axes[2].plot(t_ms, quantization_error_y2, 'g-', label='e2[n]', alpha=0.8, linewidth=0.7)
axes[2].plot(t_ms, quantization_error_y1, 'b-', label='e1[n]', alpha=0.8, linewidth=0.7)
axes[2].set_ylabel('Valor')
axes[2].set_title('Errores de Cuantizacion')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_xlabel('Tiempo (ms)')


# 4. Espectro de frecuencia (FFT)
fft_x = np.abs(np.fft.fft(x)[:len(x)//2])
fft_y = np.abs(np.fft.fft(y)[:len(y)//2])
fft_y1 = np.abs(np.fft.fft(y1)[:len(y1)//2])
fft_y2 = np.abs(np.fft.fft(y2t)[:len(y1)//2])
freq = np.fft.fftfreq(num_samples, 1/fs)[:len(fft_x)]

fig, axes = plt.subplots(1, 1, figsize=(12, 10))
fig.suptitle('Simulación Delta-Sigma de 1er Orden', fontsize=14, fontweight='bold')

axes.semilogy(freq, fft_x**2, 'b-', label='Entrada', alpha=0.8)
axes.semilogy(freq, fft_y**2, 'r-', label='Salida', alpha=0.8)
axes.semilogy(freq, fft_y1**2, 'g-', label='Y_1', alpha=0.8)
axes.semilogy(freq, fft_y2**2, 'm-', label='Y_2', alpha=0.8)
axes.set_xlabel('Frecuencia (Hz)')
axes.set_ylabel('Potencia Espectral')
axes.set_title('Espectro de Frecuencia')
axes.legend(loc='upper right')
axes.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.show()