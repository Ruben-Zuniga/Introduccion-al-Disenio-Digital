import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Parámetros de simulación
# ============================================================

Ts = 1e-9                # Paso de simulación [s]
Tsim = 20e-6             # Tiempo total [s]

t = np.arange(0, Tsim, Ts)
N = len(t)

# ============================================================
# Referencia y VCO
# ============================================================

f_ref = 1e6              # Frecuencia de referencia [Hz]

# Frecuencia libre inicial del VCO.
# La ponemos distinta para observar cómo el PLL corrige el error.
f0_vco = 0.98e6          # [Hz]

Kvco = 100e3             # Sensibilidad VCO [Hz / unidad]

# ============================================================
# Loop filter PI
# Valores iniciales de prueba, NO definitivos
# ============================================================

Kp = 0.5
Ki = 1e3

# ============================================================
# Variables
# ============================================================

phi_ref = np.zeros(N)
phi_out = np.zeros(N)

phase_error = np.zeros(N)
control = np.zeros(N)
f_out = np.zeros(N)

integral_error = 0.0

# ============================================================
# Simulación
# ============================================================

for k in range(N - 1):

    # --------------------------------------------------------
    # Referencia
    # --------------------------------------------------------

    phi_ref[k + 1] = phi_ref[k] + 2*np.pi*f_ref*Ts

    # --------------------------------------------------------
    # Phase Detector: devuelvo error entre [-pi, pi]
    # --------------------------------------------------------

    error = phi_ref[k] - phi_out[k]

    error = np.arctan2(
        np.sin(error),
        np.cos(error)
    )

    phase_error[k] = error

    # --------------------------------------------------------
    # Loop Filter PI
    # --------------------------------------------------------

    integral_error += error * Ts

    control[k] = (
        Kp * error +
        Ki * integral_error
    )

    # --------------------------------------------------------
    # VCO
    # --------------------------------------------------------

    f_out[k] = f0_vco + Kvco * control[k]

    # --------------------------------------------------------
    # Integración frecuencia -> fase
    # --------------------------------------------------------

    phi_out[k + 1] = (
        phi_out[k]
        + 2*np.pi*f_out[k]*Ts
    )

# Últimas muestras
f_out[-1] = f_out[-2]
phase_error[-1] = phase_error[-2]
control[-1] = control[-2]

# ============================================================
# Clock generado
# ============================================================

clk_out = (np.sin(phi_out) >= 0).astype(int)

# ============================================================
# Gráficos
# ============================================================

plt.figure()
plt.plot(t * 1e6, f_out / 1e6)
plt.axhline(f_ref / 1e6, linestyle="--")
plt.xlabel("Tiempo [us]")
plt.ylabel("Frecuencia [MHz]")
plt.title("Frecuencia de salida del PLL")
plt.grid()
plt.show()

plt.figure()
plt.plot(t * 1e6, phase_error)
plt.xlabel("Tiempo [us]")
plt.ylabel("Error de fase [rad]")
plt.title("Error de fase")
plt.grid()
plt.show()

plt.figure()
plt.plot(t[:10000] * 1e6, clk_out[:10000])
plt.xlabel("Tiempo [us]")
plt.ylabel("Clock")
plt.title("Clock generado")
plt.grid()
plt.show()