import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# MODELO FUNCIONAL PLL + MULTI-MODULUS DIVIDER
# ============================================================
# Etapa 2:
#
# f_ref -> PD -> PI -> VCO -> f_out
#            ^              |
#            |              v
#            +---- MMD <----+
#
# Por ahora:
#   - MMD con modulo entero fijo
#   - sin Delta-Sigma
#   - sin FCW
#   - sin jitter
#
# Los valores numericos son de prueba.
# NO corresponden aun a parametros definitivos del Proyecto Marco.
# ============================================================



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
f0_vco = 0.4e6          # [Hz]

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

N_div = 2                # Módulo entero inicial del divisor

phi_ref = np.zeros(N)
phi_out = np.zeros(N)
phi_div = np.zeros(N)

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

    error = phi_ref[k] - phi_div[k]

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

    # --------------------------------------------------------
    # Multi-Modulus Divider
    # --------------------------------------------------------
    
    phi_div[k + 1] = (
        phi_div[k]
        + 2*np.pi*(f_out[k] / N_div)*Ts
    )


# Últimas muestras
f_out[-1] = f_out[-2]
phase_error[-1] = phase_error[-2]
control[-1] = control[-2]
f_div = f_out / N_div

# ============================================================
# Clock generado
# ============================================================

clk_out = (np.sin(phi_out) >= 0).astype(int)
clk_div = (np.sin(phi_div) >= 0).astype(int)
clk_ref = (np.sin(phi_ref) >= 0).astype(int)

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
plt.plot(t * 1e6, f_div / 1e6)
plt.axhline(f_ref / 1e6, linestyle="--")
plt.xlabel("Tiempo [us]")
plt.ylabel("Frecuencia [MHz]")
plt.title("Frecuencia a la salida del MMD")
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


plt.figure()
plt.plot(
    t[:10000] * 1e6,
    clk_ref[:10000],
    label="Clock referencia"
)

plt.plot(
    t[:10000] * 1e6,
    clk_div[:10000] + 1.2,
    label="Clock dividido"
)

plt.xlabel("Tiempo [us]")
plt.ylabel("Clock")
plt.title("Referencia vs realimentación del MMD")
plt.grid()
plt.legend()
plt.show()