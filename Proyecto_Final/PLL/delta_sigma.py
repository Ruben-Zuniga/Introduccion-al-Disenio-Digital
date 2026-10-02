import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

class DeltaSigmaModulator:
    """
    Modulador Delta-Sigma de 1er orden
    Implementación basada en el diagrama de bloques proporcionado
    """
    
    def __init__(self, quantizer_levels=2):
        """
        Inicializa el modulador
        
        Args:
            quantizer_levels: Número de niveles del cuantificador (2 = binario por defecto)
        """
        self.quantizer_levels = quantizer_levels
        # Estado inicial del delay z^-1
        self.v_delay = 0
        # Pre-calcular los niveles posibles
        self.quantizer_levels_array = self._compute_quantizer_levels()

    def _compute_quantizer_levels(self):
        """
        Calcula los valores posibles del cuantificador según las reglas:
        - Niveles impares: simétricos alrededor de 0
        - Niveles pares: desde -(N-2)/2 hasta N/2
        """
        if self.quantizer_levels % 2 == 1:
            # Impar: simétrico alrededor de 0
            min_level = -(self.quantizer_levels - 1) // 2
            max_level = (self.quantizer_levels - 1) // 2
        else:
            # Par: asimétrico
            min_level = -(self.quantizer_levels - 2) // 2
            max_level = self.quantizer_levels // 2
        
        return np.arange(min_level, max_level + 1)
    
    def quantize(self, v):
        """
        Cuantificador simple (mid-tread)
        
        Args:
            v: Entrada al cuantificador
            
        Returns:
            y: Salida cuantizada (+1 o -1 para 2 niveles)
        """
        y_int = int(np.round(v))
        y_quantized = np.clip(y_int, self.quantizer_levels_array[0], self.quantizer_levels_array[-1])

        return y_quantized
    
    def process_sample(self, x_n):
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
        y_prev = self.quantize(self.v_delay)  # y[n-1] = v[n-1] en esta arquitectura
        
        # Primera suma: u[n] = x[n] - y[n-1]
        u_n = x_n - y_prev
        
        # Segunda suma con integrador: v[n] = u[n] + v[n-1]
        v_n = u_n + self.v_delay
        
        # Cuantificación: y[n] = quantizer(v[n])
        y_n = self.quantize(v_n)
        
        # Actualizar estado del delay para la próxima muestra
        self.v_delay = v_n
        
        return y_n, u_n, v_n
    
    def process_sequence(self, x):
        """
        Procesa una secuencia completa de muestras
        
        Args:
            x: Array de muestras de entrada
            
        Returns:
            y: Array de muestras de salida cuantizadas
        """
        self.v_delay = 0  # Resetear estado inicial
        u = np.zeros_like(x)
        v = np.zeros_like(x)
        y = np.zeros_like(x)
        
        for i in range(len(x)):
            y[i], u[i], v[i] = self.process_sample(x[i])
        
        return y, u, v
    
    def reset(self):
        """Resetea el estado interno del modulador"""
        self.v_delay = 0


def generate_sine_wave(frequency, amplitude, sampling_rate, duration, num_samples):
    """Genera una onda sinusoidal de prueba"""
    t = np.linspace(0, duration, num_samples, endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)


def calculate_signal_to_noise_ratio(signal, noise):
    """Calcula la relación señal-ruido en dB"""
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)
    
    if noise_power == 0:
        return float('inf')
    
    snr_db = 10 * np.log10(signal_power / noise_power)
    return snr_db


if __name__ == "__main__":
    # ==================== Configuración de Simulación ====================
    
    # Parámetros de simulación
    fs = 64000          # Frecuencia de muestreo (Hz)
    num_samples = 10000   # Numero de muestras
    f_input = 20       # Frecuencia de entrada (Hz)
    amplitude = 4     # Amplitud de entrada
    quantizer_levels = 3 # Niveles de cuantizacion a la salida
    
    duration = num_samples / fs    # Duración (segundos)
    
    # print("=" * 60)
    # print("SIMULACIÓN DEL MODULATOR DELTA-SIGMA DE 1ER ORDEN")
    # print("=" * 60)
    # print(f"Frecuencia de muestreo: {fs} Hz")
    # print(f"Frecuencia de entrada: {f_input} Hz")
    # print(f"Número de muestras: {num_samples}")
    # print(f"Relación OSR (Oversampling Ratio): ~{fs // (2 * f_input)}")
    # print("=" * 60)
    
    # ==================== Generar Señal de Entrada ====================
    
    ## Sinusoidal
    # x_n = generate_sine_wave(f_input, amplitude, fs, duration, num_samples)

    ## Constantes: 0, 0.5, -1 y 1
    ## En 0, la frecuencia a la salida es maxima. En 1 y -1, la frecuencia es 0
    # x_n = np.array([0]*(num_samples//4) + [0.5]*(num_samples//4) + [-1]*(num_samples//4) + [1]*(num_samples//4))

    ## Rampa
    t = np.linspace(0, duration, num_samples, endpoint=False)
    x_n = 1 * signal.sawtooth(2 * np.pi * f_input * t, width=0.5) # 3 niveles
    # x_n = 0.5 + 2.5 * signal.sawtooth(2 * np.pi * f_input * t, width=0.5) # 6 niveles
    print(x_n)
    
    # Crear instancia del modulador
    modulator = DeltaSigmaModulator(quantizer_levels=quantizer_levels)
    
    # ==================== Procesar Señal ====================
    
    # Procesar la señal completa
    y_n, u_n, v_n = modulator.process_sequence(x_n)
    
    # ==================== Análisis de Resultados ====================
    
    # Calcular error de cuantificación
    quantization_error = x_n - y_n
    
    # Calcular SNR
    snr = calculate_signal_to_noise_ratio(x_n, quantization_error)
    
    print(f"\nResultados:")
    print(f"SNR: {snr:.2f} dB")
    print(f"Pico de codificación: {'Binario' if modulator.quantizer_levels == 2 else 'Múltiples niveles'}")
    
    # ==================== Visualización ====================
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    plt.subplots_adjust(hspace=0.409)
    fig.suptitle('Simulación Delta-Sigma de 1er Orden', fontsize=14, fontweight='bold')
    
    # Tiempo en ms para mejor visualización
    t_ms = np.linspace(0, duration*1000, num_samples, endpoint=False)
    
    # 1. Señal de entrada
    axes[0].plot(t_ms, x_n, 'b-', linewidth=1, alpha=0.8)
    axes[0].set_ylabel('Amplitud')
    axes[0].set_title('Señal de Entrada x[n]')
    axes[0].grid(True, alpha=0.3)
    # axes[0].set_xlim(0, 100)
    
    # 2. Salida del cuantificador
    axes[1].plot(t_ms, y_n, 'r-', linewidth=1, alpha=0.8, drawstyle='steps-post')
    axes[1].set_ylabel('Nivel Binario')
    axes[1].set_title('Salida Cuantizada y[n]')
    axes[1].grid(True, alpha=0.3)
    # axes[1].set_ylim(-1.5, 1.5)
    # axes[1].set_xlim(0, 100)
    
    # # 3. Señales internas u[n] y v[n]
    # modulator.reset()
    # u_seq = []
    # v_seq = []
    # for i in range(min(500, num_samples)):
    #     u = x_n[i] - (modulator.v_delay if i > 0 else 0)
    #     v = u + modulator.v_delay
    #     y_out = modulator.quantize(v)
    #     modulator.v_delay = v
    #     u_seq.append(u)
    #     v_seq.append(v)
    
    # u_seq = np.array(u_seq)
    # v_seq = np.array(v_seq)
    
    axes[2].plot(t_ms, u_n, 'g-', label='u[n]', alpha=0.8)
    axes[2].plot(t_ms, v_n, 'm-', label='v[n]', alpha=0.8, linewidth=0.7)
    axes[2].set_ylabel('Valor')
    axes[2].set_title('Señales Internas del Modulador')
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlabel('Tiempo (ms)')
    # axes[2].set_xlim(0, 100)
    

    # 4. Espectro de frecuencia (FFT)
    fft_x = np.abs(np.fft.fft(x_n)[:len(x_n)//2])
    fft_y = np.abs(np.fft.fft(y_n)[:len(y_n)//2])
    freq = np.fft.fftfreq(num_samples, 1/fs)[:len(fft_x)]
    
    fig, axes = plt.subplots(1, 1, figsize=(12, 10))
    fig.suptitle('Simulación Delta-Sigma de 1er Orden', fontsize=14, fontweight='bold')
    
    axes.semilogy(freq, fft_x**2, 'b-', label='Entrada', alpha=0.8)
    axes.semilogy(freq, fft_y**2, 'r-', label='Salida', alpha=0.8)
    axes.set_xlabel('Frecuencia (Hz)')
    axes.set_ylabel('Potencia Espectral')
    axes.set_title('Espectro de Frecuencia (Primeros 5 kHz)')
    axes.legend(loc='upper right')
    axes.grid(True, alpha=0.3)
    # axes.set_xlim(0, 5000)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    # plt.savefig('delta_sigma_simulation.png', dpi=150, bbox_inches='tight')
    # print("\nGráficos guardados como 'delta_sigma_simulation.png'")
    
    plt.show()
    
    # ==================== Estadísticas Adicionales ====================
    
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS ADICIONALES")
    print("=" * 60)
    print(f"Distribución de salida y[n]:")
    unique, counts = np.unique(y_n, return_counts=True)
    for val, count in zip(unique, counts):
        percentage = count / len(y_n) * 100
        print(f"  Nivel {val}: {count} muestras ({percentage:.2f}%)")
    
    print(f"\nError de cuantificación:")
    print(f"  Media: {np.mean(quantization_error):.6f}")
    print(f"  Desviación estándar: {np.std(quantization_error):.6f}")
    print(f"  Valor pico: {np.max(np.abs(quantization_error)):.6f}")
    
    print("=" * 60)