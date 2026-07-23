import numpy as np
import matplotlib.pyplot as plt
from tool._fixedInt import *

# -------------------------------------------------------------
### PARAMETROS 
# -------------------------------------------------------------
## Parametros generales
f_baud = 25e6 # Frecuencia de baudio (f_clk / os)
T_baud = 1/f_baud # Periodo de baudio
N_symb = 100          # Numero de simbolos
os    = 4

## Parametros del filtro de caida cosenoidal
beta   = 0.5 # Roll-Off
N_bauds = 6     # Cantidad de baudios del filtro

## Parametros funcionales
phase = 0 # Fase de muestreo
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

### Calculo de tres pulsos con diferente roll-off
(t,rc0) = rcosine(beta, T_baud,os,N_bauds,Norm=True)

print(f'Potencia del RC: {np.sum(rc0**2)}')
print(f'Ganancia del RC: {np.sum(rc0)}')

# rc0_sq = np.sum(rc0 ** 2)

# nbf_v = np.arange(2, 17)
# rc0_fix = []
# rc0_fix_sq = []
# error_sq = []
# for nb in nbf_v:
#     rc0_fix_aux = arrayFixedInt(nb, nb-1, rc0, 'S', 'trunc', 'saturate')
#     rc0_fix_aux = np.array([val.fValue for val in rc0_fix_aux])
#     rc0_fix.append(rc0_fix_aux)
#     error_sq.append(np.sum((rc0 - rc0_fix_aux) ** 2))

# rc0_fix_sq = np.array(rc0_fix_sq)
# error_sq = np.array(error_sq)
# ser = rc0_sq / error_sq

# plt.figure()
# plt.plot(nbf_v, 10*np.log10(ser), '-o')
# plt.title('Relación Señal-Error para Máx. Resolución')
# plt.xlabel('N° Bits Totales')
# plt.ylabel('SER [dB]')
# plt.grid()
# plt.show()

rc = arrayFixedInt(Nb, Nb - 1, rc0, 'S', 'trunc', 'saturate')
rc_fvalue = np.array([val.fValue for val in rc])
rc_int = np.array([val.value for val in rc])

prbs_tx = np.array([0,1,0,1,0,1,0,1,1]) # 0x1AA al reves [8:0]
prbs_rx = prbs_tx
register_rc = np.zeros(N_bauds)
out_sum = arrayFixedInt(Nb + 3, Nb - 1, [0]*os, 'S', 'trunc', 'saturate')
register_dec = arrayFixedInt(Nb + 3, Nb - 1, [0]*os, 'S', 'trunc', 'saturate')
dec_rx = DeFixedInt(Nb + 3, Nb - 1, 'S', 'trunc', 'saturate')

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
            dec_rx.assign(register_dec[phase])
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
    feedback = prbs_rx[8] ^ prbs_rx[4]
    prbs_rx = np.concatenate(([feedback], prbs_rx[0:8]))
    prbs_rx_log.append(prbs_rx[8])


    

out_tx_log = np.array(out_tx_log)
symb_tx_log = np.array(symb_tx_log)
symb_tx_log = np.concatenate((np.zeros(N_bauds // 2 + 1), symb_tx_log[0:-N_bauds // 2 - 1]))
signal_rx_log = np.array(signal_rx_log)
symb_rx_log = np.array(symb_rx_log)
# signal_rx_log = np.concatenate((signal_rx_log[phase:], np.zeros(phase)))

plt.figure()
plt.plot(range(0, N_symb*os, os), -(symb_tx_log*2-1), '-o', label='Tx symbols')
plt.plot(range(N_symb*os), out_tx_log, '-o', label='Tx output')
plt.plot(range(0, N_symb*os, os), signal_rx_log, '-o', label='Rx decimated')
plt.plot(range(0, N_symb*os, os), -(symb_rx_log*2-1), '-o', label='Rx symbols')
plt.title('Salida')
plt.xlabel('N symbs')
plt.ylabel('Amplitud')
plt.legend(loc='upper right')
plt.grid()
plt.show()