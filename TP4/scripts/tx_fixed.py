import numpy as np
import matplotlib.pyplot as plt
from tool._fixedInt import *

# -------------------------------------------------------------
### PARAMETROS 
# -------------------------------------------------------------
## Parametros generales
f_baud = 25e6 # Frecuencia de baudio (f_clk / os)
T_baud = 1/f_baud # Periodo de baudio
N_symb = 50000          # Numero de simbolos
os    = 4

## Parametros del filtro de caida cosenoidal
beta   = 0.5 # Roll-Off
N_bauds = 6     # Cantidad de baudios del filtro

## Parametros funcionales
sample_phase = 2 # Fase de muestreo
Ts = T_baud/os              # Frecuencia de muestreo
Nb = 8 # Numero de bits totales
Nbf = Nb - 1 # Numero de bits fraccionales

# -------------------------------------------------------------
### GENERACION COSENO REALZADO 
# -------------------------------------------------------------

def rcosine(beta, Tbaud, oversampling, N_bauds, Norm):
    """ Respuesta al impulso del pulso de caida cosenoidal """
    t_vect = np.arange(-0.5*N_bauds*Tbaud, 0.5*N_bauds*Tbaud, 
                       float(Tbaud)/oversampling)

    y_vect = []
    for t in t_vect:
        y_vect.append(np.sinc(t/Tbaud)*(np.cos(np.pi*beta*t/Tbaud)/
                                        (1-(4.0*beta*beta*t*t/
                                            (Tbaud*Tbaud)))))

    y_vect = np.array(y_vect)

    if(Norm):
        return (t_vect, y_vect/np.sqrt(np.sum(y_vect**2)))
        # return (t_vect, y_vect/y_vect.sum())
    else:
        return (t_vect,y_vect)

(t,rc0) = rcosine(beta, T_baud,os,N_bauds,Norm=True)

print(f'Potencia del RC: {np.sum(rc0**2)}')
print(f'Ganancia del RC: {np.sum(rc0)}')

# -------------------------------------------------------------
### VARIABLES 
# -------------------------------------------------------------

rc = arrayFixedInt(Nb, Nb - 1, rc0, 'S', 'trunc', 'saturate')
N_corr = 32

# Logs para plottear
symb_tx_log = []
out_tx_log = []
signal_rx_log = []
symb_rx_log = []
prbs_rx_log = []

# plt.figure()
# plt.plot(rc_fvalue, '-o')
# plt.title('Filtro RC')
# plt.xlabel('N bauds')
# plt.ylabel('Amplitud')
# plt.grid()
# plt.show()

## Matriz de coeficientes del filtro
coeffs = [[0]*N_bauds]*os
coeffs = [0]*os
for i in range(os):
    # print(np.arange(i, N_bauds*os + i, os))

    coeffs[i] = rc[i:i-(os):os]

# print(rc)
# print(np.array(coeffs))

## Producto
# Valor -1 en punto fijo para multiplicar por los demas valores
neg = DeFixedInt(Nb, Nb - 1, 'S', 'trunc', 'saturate')
neg.value = -1.

def prod(x, h):
    if x: return neg*h
    else: return h
    
# -------------------------------------------------------------
### SIMULADOR DEL HARDWARE 
# -------------------------------------------------------------

def top_model(sample_phase, prbs_seed ,N_corr):
    prbs_tx = prbs_seed
    prbs_rx = prbs_tx
    register_rc = np.zeros(N_bauds)
    register_dec = arrayFixedInt(Nb + 3, Nb - 1, [0]*os, 'S', 'trunc', 'saturate')
    register_prbs_rx = np.zeros(1024, dtype=int)

    errors = 0
    ber_phase = 0
    ber_count = 0
    min_found = False

    out_sum = arrayFixedInt(Nb + 3, Nb - 1, [0]*os, 'S', 'trunc', 'saturate')
    dec_rx = DeFixedInt(Nb + 3, Nb - 1, 'S', 'trunc', 'saturate')
    register_corr = np.zeros(N_corr, dtype=int)

    for n in range(N_symb):

        # print(prbs_tx, '  ', register_rc, '  ', out_sum)

        ### PRBS9 TX
        symb_tx = prbs_tx[8]
        feedback = symb_tx ^ prbs_tx[4]
        prbs_tx = np.concatenate(([feedback], prbs_tx[0:8]))
        symb_tx_log.append(symb_tx)

        ### Filtro RC
        for m in range(os):

            out_sum[m].value = 0
            for i in range(N_bauds):
                out_sum[m].assign(out_sum[m] + prod(register_rc[i], coeffs[m][i]))

            # out_sum[m] =  prod(register_rc[0], coeffs[m][0]) \
            #             + prod(register_rc[1], coeffs[m][1]) \
            #             + prod(register_rc[2], coeffs[m][2]) \
            #             + prod(register_rc[3], coeffs[m][3]) \
            #             + prod(register_rc[4], coeffs[m][4]) \
            #             + prod(register_rc[5], coeffs[m][5])
            # print(out_sum[m])

            out_rc = out_sum[m]
            out_tx_log.append(out_rc.fValue)

            ### Decimador
            register_dec = np.concatenate(([out_rc], register_dec[0:os]))
            if m == 0:
                dec_rx.assign(register_dec[sample_phase])
                signal_rx_log.append(dec_rx.fValue)
            
        # print(dec_rx)

        register_rc = np.concatenate(([symb_tx], register_rc[0 : N_bauds-1]))

        ### Decimador (cont.)
        if dec_rx.fValue >= 0:
            symb_rx = 0
        else:
            symb_rx = 1
        symb_rx_log.append(symb_rx)

        ### BER
        # PRBS Rx
        feedback = prbs_rx[8] ^ prbs_rx[4]
        prbs_rx = np.concatenate(([feedback], prbs_rx[0:8]))
        register_prbs_rx = np.concatenate(([prbs_rx[8]], register_prbs_rx[0:1023]))
        prbs_rx_log.append(prbs_rx[8])

        # print(n, symb_rx, register_prbs_rx[ber_phase])
        
        errors = errors + (register_prbs_rx[ber_phase] ^ symb_rx)

        # Si no esta sincronizado
        if not min_found:
            # Luego de terminar la secuencia del PRBS
            if n % 511 == 0 and n != 0:
                register_corr[ber_phase] = errors
                print(f'Registro de errores: fase {ber_phase}/{N_corr} -> {register_corr[ber_phase]}')
                ber_phase = ber_phase + 1
                errors = 0

            # Luego de terminar de recorrer todas las fases
            if ber_phase >= N_corr:
                # Encontrar la fase con el error minimo
                min_corr = 512
                for i in range(N_corr):
                    if register_corr[i] < min_corr:
                        ber_phase = i
                        min_corr = register_corr[i]
                errors = 0
                min_found = True
                # Guardar índice para graficar luego
                idx_count = n+1
        # Si ya sincronizó
        else:
            # Comenzar a contar los simbolos totales para contar BER
            ber_count = ber_count + 1

    return errors, min_found, idx_count, ber_count

# -------------------------------------------------------------
### LOGS Y GRAFICOS
# -------------------------------------------------------------

prbs_seed_I = np.array([0,1,0,1,0,1,0,1,1]) # 0x1AA al reves [8:0]
prbs_seed_Q = np.array([0,1,1,1,1,1,1,1,1]) # 0x1FE
errors_I, min_found_I, idx_count_I, ber_count_I = top_model(sample_phase, prbs_seed_I, N_corr)

# Guardar y resetear logs
symb_tx_log_I = symb_tx_log
out_tx_log_I = out_tx_log
signal_rx_log_I = signal_rx_log
symb_rx_log_I = symb_rx_log
prbs_rx_log_I = prbs_rx_log
symb_tx_log = []
out_tx_log = []
signal_rx_log = []
symb_rx_log = []
prbs_rx_log = []

errors_Q, min_found_Q, idx_count_Q, ber_count_Q = top_model(sample_phase, prbs_seed_Q, N_corr)

# Guardar logs
symb_tx_log_Q = symb_tx_log
out_tx_log_Q = out_tx_log
signal_rx_log_Q = signal_rx_log
symb_rx_log_Q = symb_rx_log
prbs_rx_log_Q = prbs_rx_log

ber_I = errors_I / ber_count_I
ber_Q = errors_Q / ber_count_Q

print(f'Sincronizacion del RX: {min_found_I}, {min_found_Q}')
print(f'Nro. de errores: {errors_I}, {errors_Q}')
print(f'BER (I): {ber_I}')
print(f'BER (Q): {ber_Q}')

out_tx_log_I = np.array(out_tx_log_I)
symb_tx_log_I = np.array(symb_tx_log_I)
symb_tx_log_I = np.concatenate((np.zeros(N_bauds // 2 + 1), symb_tx_log_I[0:-N_bauds // 2 - 1]))
signal_rx_log_I = np.array(signal_rx_log_I)
symb_rx_log_I = np.array(symb_rx_log_I)

plt.figure()
plt.plot(range(0, N_symb*os, os), -(symb_tx_log_I*2-1), '-o', label='Tx symbols')
plt.plot(range(N_symb*os), out_tx_log_I, '-o', label='Tx output')
plt.plot(range(0, N_symb*os, os), signal_rx_log_I, '-o', label='Rx decimated')
plt.plot(range(0, N_symb*os, os), -(symb_rx_log_I*2-1), '-o', label='Rx symbols')
plt.title('Salida')
plt.xlabel('N symbs')
plt.ylabel('Amplitud')
plt.legend(loc='upper right')
plt.grid()
plt.show()

plt.figure(figsize=[8,7])
plt.subplots_adjust(left=0.142, bottom=0.085, right=0.903, top=0.922, wspace=0.37, hspace=0.361)

# Recortar desde cuando se comienza a contar BER
symb_rx_trimm_I = signal_rx_log_I[idx_count_I:N_symb]
symb_rx_trimm_Q = signal_rx_log_Q[idx_count_I:N_symb]

plt.plot(symb_rx_trimm_I, symb_rx_trimm_Q, '.',linewidth=2.0, alpha=0.5)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación. Fase: %d/%d'%(sample_phase,os-1))
plt.xlabel('Real')
plt.ylabel('Imag')

# plt.tight_layout()
plt.show()
