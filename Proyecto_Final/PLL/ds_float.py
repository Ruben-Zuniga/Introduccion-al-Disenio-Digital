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
    y_int = int(np.round(v))
    y_quantized = np.clip(y_int, quantizer_levels_v[0], quantizer_levels_v[-1])

    return y_quantized

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
x = np.concatenate( [-1 * np.ones(num_samples//4), 0.2 * np.ones(num_samples//4), 0.5 * np.ones(num_samples//4), 1 * np.ones(num_samples//4)] )

# # Sinusoidal
# x_n = 0.5 + 0.5 * np.sin(2 * np.pi * f_input * t)

# # Rampa
# x = 0.5 + 0.5 * signal.sawtooth(2 * np.pi * f_input * t, width=0.5) # 3 niveles

# ==================== Procesar Señal ====================

# Generacion de niveles de cuantizacion
if quantizer_levels % 2 == 1:
    # Impar: simétrico alrededor de 0
    min_level = -(quantizer_levels - 1) // 2
    max_level = (quantizer_levels - 1) // 2
else:
    # Par: asimétrico
    min_level = -(quantizer_levels - 2) // 2
    max_level = quantizer_levels // 2

quantizer_levels_v = np.arange(min_level, max_level + 1)
print(quantizer_levels_v)
# Procesar la señal completa
v1_delay = 0  # Resetear estado inicial
v2_delay = 0
u1 = np.zeros_like(x)
v1 = np.zeros_like(x)
y1 = np.zeros_like(x)
e1 = np.zeros_like(x)

u2 = np.zeros_like(x)
v2 = np.zeros_like(x)
y2 = np.zeros_like(x)
e2 = np.zeros_like(x)

y = np.zeros_like(x)

for i in range(2,len(x)):
    # 1ra etapa
    y1[i], u1[i], v1[i], v1_delay = ds_1st_order(x[i], v1_delay)
    e1[i] = v1[i] - y1[i]

    # 2da etapa
    y2[i], u2[i], v2[i], v2_delay = ds_1st_order(e1[i], v2_delay)
    e2[i] = v2[i] - y2[i]


    y[i] = y2[i] - y2[i-1] + y1[i-1]


# ==================== Calculo de Resultados ====================

# Calcular error de cuantificación
quantization_error = x - y

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
axes[1].plot(t_ms, y1, 'g-',label='y1[n]', linewidth=1, alpha=0.8, drawstyle='steps-post')
axes[1].set_ylabel('Nivel Binario')
axes[1].set_title('Salida Cuantizada y[n]')
axes[2].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

axes[2].plot(t_ms, e1, 'g-', label='e1[n]', alpha=0.8)
axes[2].plot(t_ms, e2, 'm-', label='e2[n]', alpha=0.8, linewidth=0.7)
axes[2].set_ylabel('Valor')
axes[2].set_title('Errores de Cuantizacion')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_xlabel('Tiempo (ms)')


# 4. Espectro de frecuencia (FFT)
fft_x = np.abs(np.fft.fft(x)[:len(x)//2])
fft_y = np.abs(np.fft.fft(y)[:len(y)//2])
fft_y1 = np.abs(np.fft.fft(y1)[:len(y1)//2])
freq = np.fft.fftfreq(num_samples, 1/fs)[:len(fft_x)]

fig, axes = plt.subplots(1, 1, figsize=(12, 10))
fig.suptitle('Simulación Delta-Sigma de 1er Orden', fontsize=14, fontweight='bold')

axes.semilogy(freq, fft_x**2, 'b-', label='Entrada', alpha=0.8)
axes.semilogy(freq, fft_y**2, 'r-', label='Salida', alpha=0.8)
axes.semilogy(freq, fft_y1**2, 'g-', label='Y_1', alpha=0.8)
axes.set_xlabel('Frecuencia (Hz)')
axes.set_ylabel('Potencia Espectral')
axes.set_title('Espectro de Frecuencia')
axes.legend(loc='upper right')
axes.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.show()