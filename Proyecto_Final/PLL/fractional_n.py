"""
Simulación conductual de un PLL totalmente digital (ADPLL) con divisor
fraccional-N mediante modulador delta-sigma MASH 1-1-1.

Modelo (un paso por periodo de referencia Tref):
  - Detector de fase digital: error = fase de referencia - ciclos emitidos
    por el divisor (en unidades de ciclos del reloj dividido).
  - Filtro de lazo: PI digital (proporcional + integral).
  - DCO: F = F0 + KDCO * u + ruido FM blanco + offset de fabricación.
  - Divisor: módulo entero conmutado en cada flanco de salida;
    el módulo proviene del MASH (media = N_INT + FRAC).

Requisitos: numpy, scipy, matplotlib.
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Parámetros del sistema
# ----------------------------------------------------------------------
FREF       = 50e6        # Hz   - frecuencia de referencia
N_INT      = 80          #      - parte entera del divisor
FRAC       = 0.9         #      - parte fraccional -> división media 80.4
N_AVG      = N_INT + FRAC
FOUT_NOM   = FREF * N_AVG          # ~4.02 GHz
KDCO       = 80e6        # Hz/LSB - ganancia del DCO
DCO_OFFSET = 1.0e6       # Hz    - error inicial de frecuencia del DCO
FREQ_NOISE = 300.0       # Hz rms- ruido de frecuencia del DCO
KP         = 8.0         # ganancia proporcional del lazo
KI         = 0.05        # ganancia integral del lazo
NS         = 20_000      # número de periodos de referencia simulados
LOCK_SKIP  = 1_000       # muestras descartadas para métricas en régimen


class MashDeltaSigma:
    """Modulador MASH 1-1-1.

    Genera una secuencia de enteros y[k] con media igual a `frac`.
    El ruido de cuantización queda moldeado en alta frecuencia
    (pendiente de primer orden por etapa sobre el espectro de fase,
    40 dB/déc sobre el espectro de frecuencia del divisor).
    """

    def __init__(self, stages: int = 3):
        self.stages = stages
        self._r = np.zeros(stages)  # residuos de cada etapa

    def step(self, frac: float) -> int:
        y = 0
        u = frac
        for j in range(self.stages):
            self._r[j] += u
            c = int(np.floor(self._r[j]))
            self._r[j] -= c          # residuo en [0, 1)
            y += c
            u = u - c                # error de cuantización alimenta la etapa siguiente
        return y


def simulate(kp: float = KP, ki: float = KI, seed: int = 0):
    """Ejecuta la simulación temporal del lazo.

    Retorna
    -------
    e     : error de fase del detector [ciclos de reloj dividido]
    fdco  : frecuencia instantánea del DCO [Hz]
    mod   : módulo del divisor aplicado en cada periodo
    """
    rng = np.random.default_rng(seed)
    tref = 1.0 / FREF
    mash = MashDeltaSigma()

    e    = np.empty(NS)
    fdco = np.empty(NS)
    mod  = np.empty(NS, dtype=int)

    integ   = 0.0                # estado del integrador del PI
    phi_div = 0                  # flancos generados por el divisor
    acc     = 0.0               # ciclos del DCO pendientes en el divisor
    modulus = N_INT + mash.step(FRAC)   # módulo actual (carga inicial)

    for k in range(NS):
        # ---- Detector de fase digital ---------------------------------
        # La referencia avanza 1 ciclo (dividido) por Tref. El error es
        # la diferencia entre la fase ideal y los flancos ya emitidos.
        ek = k - phi_div
        e[k] = ek

        # ---- Filtro de lazo PI digital --------------------------------
        integ += ki * ek
        u = kp * ek + integ

        # ---- DCO -------------------------------------------------------
        f = FOUT_NOM + DCO_OFFSET + KDCO * u + rng.normal(0.0, FREQ_NOISE)
        fdco[k] = f
        mod[k] = modulus

        # ---- Divisor fraccional-N --------------------------------------
        # Durante este periodo el DCO genera 'cycles' ciclos; el divisor
        # emite un flanco cada vez que su contador alcanza el módulo
        # y recarga un módulo nuevo del MASH.
        cycles = f * tref                       # ciclos disponibles
        acc_cap = modulus - acc                 # ciclos hasta el flanco
        while cycles >= acc_cap:
            cycles -= acc_cap
            phi_div += 1
            acc = 0.0
            modulus = N_INT + mash.step(FRAC)   # nuevo módulo por flanco
            acc_cap = modulus
        acc += cycles                           # resto no consumido

    return e, fdco, mod


def analyze(e, fdco, mod):
    """Métricas de régimen permanente."""
    sl = slice(LOCK_SKIP, NS)
    e_lk = e[sl] - np.mean(e[sl])
    f_err = fdco[sl] - FOUT_NOM

    # Tiempo de enclavamiento: error de frecuencia < 0.01 % sostenido
    tol = abs(FOUT_NOM) * 1e-4
    locked = np.abs(fdco - FOUT_NOM) < tol
    k_lock = NS
    for k in range(NS - 200):
        if locked[k:k + 200].all():
            k_lock = k
            break

    return {
        "e_rms_ciclos":  float(np.std(e_lk)),
        "e_pk_ciclos":   float(np.max(np.abs(e_lk))),
        "jit_pd_ps":     float(np.std(e_lk) / FREF * 1e12),  # en la salida del divisor
        "ferr_rms_hz":   float(np.std(f_err)),
        "ferr_ppm":      float(np.std(f_err) / FOUT_NOM * 1e6),
        "k_lock":        k_lock,
        "mod_range":     (int(mod.min()), int(mod.max())),
    }


def plot_results(e, fdco, mod, m):
    t = np.arange(NS) / FREF * 1e6   # µs
    k = np.arange(NS)

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("ADPLL con divisor fraccional-N (MASH 1-1-1)")

    # 1. Adquisición de frecuencia
    ax[0, 0].plot(t, fdco / 1e9, lw=0.8)
    ax[0, 0].axhline(FOUT_NOM / 1e9, ls="--", color="gray", label="Nominal")
    ax[0, 0].set_xlabel("Tiempo [µs]")
    ax[0, 0].set_ylabel("f_DCO [GHz]")
    ax[0, 0].set_title("Adquisición del lazo")
    ax[0, 0].legend()

    # 2. Error de fase en régimen
    ax[0, 1].plot(k[LOCK_SKIP:], e[LOCK_SKIP:], lw=0.6)
    ax[0, 1].set_xlabel("Muestra [periodos de referencia]")
    ax[0, 1].set_ylabel("Error de fase [ciclos]")
    ax[0, 1].set_title(f"Detector de fase (rms = {m['e_rms_ciclos']:.3f} ciclos)")

    # 3. Espectro del ruido de frecuencia del DCO
    f_dev = (fdco - FOUT_NOM) / N_AVG   # desviación referida a la referencia [Hz]
    fp, psd = signal.welch(f_dev, fs=FREF, nperseg=2048)
    ax[1, 0].semilogx(fp[1:], 10 * np.log10(psd[1:]), lw=0.9)
    ax[1, 0].set_xlabel("Frecuencia de offset [Hz]")
    ax[1, 0].set_ylabel("PSD de f_dev [dBc-like]")
    ax[1, 0].set_title("Lazo BW + moldeado del ruido del divisor")

    # 4. Histograma del módulo del divisor
    ax[1, 1].hist(mod, bins=np.arange(mod.min() - .5, mod.max() + 1.5),
                  edgecolor="black", align="mid")
    ax[1, 1].axvline(N_AVG, ls="--", color="red", label=f"Media = {N_AVG}")
    ax[1, 1].set_xlabel("Módulo del divisor")
    ax[1, 1].set_ylabel("Ocurrencias")
    ax[1, 1].set_title("Distribución del dither fraccional")
    ax[1, 1].legend()

    plt.tight_layout()
    plt.show()


def main():
    e, fdco, mod = simulate()
    m = analyze(e, fdco, mod)

    print("=" * 60)
    print(f"Frecuencia nominal de salida : {FOUT_NOM/1e9:.4f} GHz")
    print(f"División media               : {N_AVG}")
    print(f"Módulos usados               : {m['mod_range'][0]} .. {m['mod_range'][1]}")
    print(f"Periodos hasta enclavamiento: {m['k_lock']} ({m['k_lock']/FREF*1e6:.2f} µs)")
    print(f"Error de fase rms (PD)       : {m['e_rms_ciclos']:.4f} ciclos")
    print(f"Jitter equivalente rms       : {m['jit_pd_ps']:.1f} ps")
    print(f"Error de frecuencia residual : {m['ferr_rms_hz']:.1f} Hz "
          f"({m['ferr_ppm']:.3f} ppm)")
    print("=" * 60)

    plot_results(e, fdco, mod, m)


if __name__ == "__main__":
    main()