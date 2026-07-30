import numpy as np
import matplotlib.pyplot as plt
from tool._fixedInt import *

# -------------------------------------------------------------
### PARAMETROS 
# -------------------------------------------------------------
## Parametros generales
f_baud = 25e6 # Frecuencia de baudio (f_clk / os)
T_baud = 1/f_baud # Periodo de baudio
N_symb = 40000          # Numero de simbolos
os    = 4

## Parametros del filtro de caida cosenoidal
beta   = 0.5 # Roll-Off
N_bauds = 6     # Cantidad de baudios del filtro

## Parametros funcionales
sample_phase = 0 # Fase de muestreo
Ts = T_baud/os              # Frecuencia de muestreo
Nb = 8 # Numero de bits totales
Nbf = Nb - 1 # Numero de bits fraccionales
round_mode = 'round'

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

N_corr = 8

# Filtro
rc = arrayFixedInt(Nb, Nb - 1, rc0, 'S', round_mode, 'saturate')
rc_fvalue = [val.fValue for val in rc]

# Respuesta al impulso
plt.figure(figsize=[14,6])
plt.plot(rc_fvalue, '-or')
plt.title(rf'Respuesta al Impulso. $OS = {os}$')
plt.xlabel('N bauds')
plt.ylabel('Amplitud')
plt.grid()

# Respuesta en frecuencia
Nfreqs = 2048
H = np.abs(np.fft.fftshift(np.fft.fft(rc_fvalue, Nfreqs)))
f = np.fft.fftshift(np.fft.fftfreq(len(H), d=Ts))

plt.figure(figsize=[14,6])
plt.semilogx(f, 20*np.log10(H), 'r', linewidth=2.0, label=r'$H(f)$')

plt.axvline(x=(1./T_baud)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(H[len(H)//2]/2),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.xlim(f[len(f)//2+1],f[len(f)-1])
plt.title(rf'Respuesta en Frecuencia. $BR = {int(f_baud/1e6)}\,$MBd. $OS = {os}$')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')
plt.grid(True)
plt.show()

# Logs para plottear
symb_tx_log = []
out_tx_log = []
dec_rx_log = []
symb_rx_log = []
prbs_rx_log = []

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
neg = DeFixedInt(Nb, Nb - 1, 'S', round_mode, 'saturate')
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
    register_dec = arrayFixedInt(Nb + 3, Nb - 1, [0]*os, 'S', round_mode, 'saturate')
    register_prbs_rx = np.zeros(1024, dtype=int)

    os_count = 0
    error_count = 0
    sync_phase = 0
    total_count = 0
    idx_count = 0
    sync_flag = False

    out_sum = arrayFixedInt(Nb + 3, Nb - 1, [0]*os, 'S', round_mode, 'saturate')
    dec_rx = DeFixedInt(Nb + 3, Nb - 1, 'S', round_mode, 'saturate')
    register_corr = np.zeros(N_corr, dtype=int)

    for n in range(N_symb):
        if os_count == 0:
            # print(prbs_tx, '  ', register_rc, '  ', out_sum)

            ### PRBS9 TX
            symb_tx = prbs_tx[8]
            feedback = symb_tx ^ prbs_tx[4]
            prbs_tx = np.concatenate(([feedback], prbs_tx[0:8]))
            symb_tx_log.append(symb_tx)

            register_rc = np.concatenate(([symb_tx], register_rc[0 : N_bauds-1]))

        ### Filtro RC
        # Estructura combinacional del filtro. "os" estructuras FIR con "N_bauds" multiplicaciones c/u
        for i in range(os):
            out_sum[i].value = 0
            for j in range(N_bauds):
                out_sum[i].assign(out_sum[i] + prod(register_rc[j], coeffs[i][j]))
                # print(n, j, out_sum)

        # out_sum[os_count] =  prod(register_rc[0], coeffs[os_count][0]) \
        #             + prod(register_rc[1], coeffs[os_count][1]) \
        #             + prod(register_rc[2], coeffs[os_count][2]) \
        #             + prod(register_rc[3], coeffs[os_count][3]) \
        #             + prod(register_rc[4], coeffs[os_count][4]) \
        #             + prod(register_rc[5], coeffs[os_count][5])
        # print(out_sum[os_count])

        out_rc = out_sum[os_count]
        out_tx_log.append(out_rc.fValue)

        ### Decimador
        register_dec = np.concatenate(([out_rc], register_dec[0:os]))
        if os_count == 0:
            dec_rx.assign(register_dec[sample_phase])
            dec_rx_log.append(dec_rx.fValue)
                
            # print(dec_rx)

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

            # print(n, symb_rx, register_prbs_rx[sync_phase])
            
            error_count = error_count + (register_prbs_rx[sync_phase] ^ symb_rx)

            # Si no esta sincronizado
            if not sync_flag:
                # Luego de terminar la secuencia del PRBS
                if n % 511 == 0 and n != 0:
                    register_corr[sync_phase] = error_count
                    print(f'Registro de errores: fase {sync_phase}/{N_corr} -> {register_corr[sync_phase]}')
                    sync_phase = sync_phase + 1
                    error_count = 0

                # Luego de terminar de recorrer todas las fases
                if sync_phase >= N_corr:
                    # Encontrar la fase con el error minimo
                    min_corr = 512
                    for i in range(N_corr):
                        if register_corr[i] <= min_corr:
                            sync_phase = i
                            min_corr = register_corr[i]
                    error_count = 0
                    sync_flag = True
                    # Guardar índice para graficar luego
                    idx_count = n+1
            # Si ya sincronizó
            else:
                # Comenzar a contar los simbolos totales para contar BER
                total_count = total_count + 1
            
            # total_count = total_count + 1
            # idx_count = 0

        os_count = (os_count + 1) % os

    return error_count, sync_flag, idx_count//os, total_count, sync_phase

# -------------------------------------------------------------
### LOGS Y GRAFICOS
# -------------------------------------------------------------

prbs_seed_I = np.array([0,1,0,1,0,1,0,1,1]) # 0x1AA al reves [8:0]
prbs_seed_Q = np.array([0,1,1,1,1,1,1,1,1]) # 0x1FE
error_count_I, sync_flag_I, idx_count_I, total_count_I, sync_phase_I = top_model(sample_phase, prbs_seed_I, N_corr)

# Guardar y resetear logs
symb_tx_log_I = symb_tx_log
out_tx_log_I = out_tx_log
dec_rx_log_I = dec_rx_log
symb_rx_log_I = symb_rx_log
prbs_rx_log_I = prbs_rx_log
symb_tx_log = []
out_tx_log = []
dec_rx_log = []
symb_rx_log = []
prbs_rx_log = []

error_count_Q, sync_flag_Q, idx_count_Q, total_count_Q, sync_phase_Q = top_model(sample_phase, prbs_seed_Q, N_corr)

# Guardar logs
symb_tx_log_Q = symb_tx_log
out_tx_log_Q = out_tx_log
dec_rx_log_Q = dec_rx_log
symb_rx_log_Q = symb_rx_log
prbs_rx_log_Q = prbs_rx_log

ber_I = error_count_I / total_count_I
ber_Q = error_count_Q / total_count_Q

print(f'Sincronizacion del RX: I -> {sync_flag_I}; Q -> {sync_flag_Q}')
print(f'Nro. de errores: I -> {error_count_I}; Q -> {error_count_Q}')
print(f'BER (I): {ber_I}')
print(f'BER (Q): {ber_Q}')

out_tx_log_I = np.array(out_tx_log_I)
symb_tx_log_I = np.array(symb_tx_log_I)
symb_tx_log_I = np.concatenate((np.zeros(sync_phase_I-1), symb_tx_log_I[:-sync_phase_I+1]))
dec_rx_log_I = np.array(dec_rx_log_I)
symb_rx_log_I = np.array(symb_rx_log_I)

out_tx_log_Q = np.array(out_tx_log_Q)
symb_tx_log_Q = np.array(symb_tx_log_Q)
symb_tx_log_Q = np.concatenate((np.zeros(sync_phase_Q-1), symb_tx_log_Q[:-sync_phase_Q+1]))
dec_rx_log_Q = np.array(dec_rx_log_Q)
symb_rx_log_Q = np.array(symb_rx_log_Q)

N_points = 100

# Canal I
plt.figure(figsize=[14,6])

plt.subplot(2,1,1)
plt.stem(range(0, N_points, os), -(symb_tx_log_I[:N_points//os]*2-1), '-o', linefmt='blue', label='Símbolos Tx')
plt.plot(range(N_points), out_tx_log_I[:N_points], '-o', color='red', label='Salida Tx')
plt.title('Transmisor (I)')
plt.ylabel('Amplitud')
plt.legend(loc='upper right')
plt.xlim((-1, N_points+1))
plt.grid()

plt.subplot(2,1,2)
plt.stem(range(0, N_points, os), -(symb_rx_log_I[:N_points//os]*2-1), '-o', linefmt='blue', label='Símbolos Rx')
plt.plot(range(0, N_points, os), dec_rx_log_I[:N_points//os], '-o', color='red', label='Entrada Rx decimada')
plt.title('Receptor (I)')
plt.xlabel('N símbolos')
plt.ylabel('Amplitud')
plt.legend(loc='upper right')
plt.xlim((-1, N_points+1))
plt.grid()
plt.tight_layout()

# Canal Q
plt.figure(figsize=[14,6])

plt.subplot(2,1,1)
plt.stem(range(0, N_points, os), -(symb_tx_log_Q[:N_points//os]*2-1), '-o', linefmt='blue', label='Símbolos Tx')
plt.plot(range(N_points), out_tx_log_Q[:N_points], '-o', color='red', label='Salida Tx')
plt.title('Transmisor (Q)')
plt.ylabel('Amplitud')
plt.legend(loc='upper right')
plt.xlim((-1, N_points+1))
plt.grid()

plt.subplot(2,1,2)
plt.stem(range(0, N_points, os), -(symb_rx_log_Q[:N_points//os]*2-1), '-o', linefmt='blue', label='Símbolos Rx')
plt.plot(range(0, N_points, os), dec_rx_log_Q[:N_points//os], '-o', color='red', label='Entrada Rx decimada')
plt.title('Receptor (Q)')
plt.xlabel('N símbolos')
plt.ylabel('Amplitud')
plt.legend(loc='upper right')
plt.xlim((-1, N_points+1))
plt.grid()
plt.tight_layout()
plt.show()

def eyediagram(data, n, offset, period):
    span     = 2*n
    segments = int(len(data)/span)
    xmax     = (n-1)*period
    xmin     = -(n-1)*period
    x        = list(np.arange(-n,n,)*period)
    xoff     = offset

    for i in range(0,segments-1):
        plt.plot(x, data[(i*span+xoff):((i+1)*span+xoff)],'b')       
    plt.grid(True)
    plt.xlim(xmin, xmax)

plt.figure(figsize=[14,6])
plt.subplot(1,2,1)
eyediagram(out_tx_log_I,os,0,N_bauds)
plt.title(r'Diagrama de ojo (I)')
plt.subplot(1,2,2)
eyediagram(out_tx_log_Q,os,0,N_bauds)
plt.title(r'Diagrama de ojo (Q)')
plt.show()

plt.figure(figsize=[6,5])
plt.subplots_adjust(left=0.142, bottom=0.085, right=0.903, top=0.922, wspace=0.37, hspace=0.361)

# Recortar desde cuando se comienza a contar BER
symb_rx_trimm_I = dec_rx_log_I[idx_count_I:-1]
symb_rx_trimm_Q = dec_rx_log_Q[idx_count_Q:-1]

plt.plot(symb_rx_trimm_I, symb_rx_trimm_Q, '.',linewidth=2.0, alpha=0.5)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación. Fase: %d/%d'%(sample_phase,os-1))
plt.xlabel('Real')
plt.ylabel('Imag')

# plt.tight_layout()
plt.show()
