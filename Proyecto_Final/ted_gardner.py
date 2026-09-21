import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy import signal

# Parametros 
BR = 25e6      # Bd
L = 10000      # Simulation Length
N = 4          # Oversampling rate
fs = N*BR      # Sampling rate to emulate analog domain
T = 1/BR       # Time interval between two consecutive symbols
Ts = 1/fs      # Time between 2 conseutive samples at Tx output
rolloff = 0.5  # Pulse shaping rolloff 
N_bauds = 10   # Filter bauds
M=16            # M-QAM
k=np.log2(M)

# PARAMETROS DEL CLOCK
clk_phase = 0 # Son fracciones de T: si clk_phase = 0.5 -> t0 =0.5*T=0.5/BR
clk_ppm =  100  # fs_tx=fs. Relacion fs_rx = fs*(1+ppm*1e-6)
clk_jitter_amp = 0*0.1 # Amplitud de jitter deterministico
clk_jitter_freq = 40e3 # Frecuencia de jitter deterministico 
clk_jitter_std = 0e-12 # Desviacion estandar de jitter random

# clk_phase = 0.09 # Son fracciones de T: si clk_phase = 0.5 -> t0 =0.5*T=0.5/BR
# clk_ppm =  50  # fs_tx=fs. Relacion fs_rx = fs*(1+ppm*1e-6)
# clk_jitter_amp = 1*0.1 # Amplitud de jitter deterministico
# clk_jitter_freq = 40e3 # Frecuencia de jitter deterministico 
# # clk_jitter_std = 2e-12 # Desviacion estandar de jitter random

## Two symbols generation (+1,-1)
# decsymbs = np.randi([0 M-1], L,1)
# x=qammod(decsymbs, M)
x_i = 2 * (np.random.uniform(-1,1,L) > 0.0) - 1
x_q = 2 * (np.random.uniform(-1,1,L) > 0.0) - 1

## Upsampling to change sampling rate
# xup = upsample(x,N)
xup_i = np.zeros(N*L) 
xup_q = np.zeros(N*L) 

xup_i[1:len(xup_i):int(N)] = x_i
xup_q[1:len(xup_q):int(N)] = x_q

## Filter to interpolate the signal
# h = rcosdesign(rolloff, N_bauds, N, 'sqrt')
# yup = filter(h, 1, xup)
def root_rcosine(beta, Tbaud, oversampling, N_bauds, Norm, type):
    """ Respuesta al impulso del pulso de caida cosenoidal """
    t_vect = np.arange(-0.5*N_bauds*Tbaud, 0.5*N_bauds*Tbaud, 
                       float(Tbaud)/oversampling)

    if len(t_vect) % 2 == 0:
        t_vect = np.append(t_vect, 0.5*N_bauds*Tbaud)

    y_vect = np.zeros_like(t_vect)

    if type == 'rc':
        for i in range(len(t_vect)):
            ti = t_vect[i]
            y_vect[i] = np.sinc(ti/Tbaud)*(np.cos(np.pi*beta*ti/Tbaud)/
                                            (1-(4.0*beta*beta*ti*ti/
                                                (Tbaud*Tbaud))))
    elif type == 'rrc':
        for i in range(len(t_vect)):
            ti = t_vect[i]
            if abs(ti) < 1e-10:
                y_vect[i] = 1.0 + beta * (4 / np.pi - 1)
            elif abs(abs(ti) - Tbaud / (4 * beta)) < 1e-10:
                y_vect[i] = (beta / np.sqrt(2)) * (
                    ((1 + 2/np.pi) * (np.sin(np.pi/(4*beta)))) +
                    ((1 - 2/np.pi) * (np.cos(np.pi/(4*beta))))
                )
            else:
                y_vect[i] = (np.sin(np.pi * ti/Tbaud * (1 - beta)) +
                        4 * beta * ti/Tbaud *
                        np.cos(np.pi * ti/Tbaud * (1 + beta))) / \
                        (np.pi * ti/Tbaud * (1 - (4 * beta * ti/Tbaud) ** 2))

    if(Norm):
        return (t_vect, y_vect/np.sqrt(np.sum(y_vect**2)))
        # return (t_vect, y_vect/y_vect.sum())
    else:
        return (t_vect,y_vect)
    
(t,h) = root_rcosine(rolloff, T, N, N_bauds, Norm=True, type='rrc')

# plt.figure()
# plt.plot(t, h, '-o')
# plt.grid()
# plt.show()

yup_i = np.convolve(h, xup_i, 'same')
yup_q = np.convolve(h, xup_q, 'same')

## Errores de timing
# Lyup = length(yup)
# line = (0:Lyup-1).'
Lyup = len(yup_i) 
line = np.arange(0, Lyup)

# Tiempo ideal
time_ideal =  line * Ts 

# Modelo ppm
fs_real = fs * (1 + clk_ppm*1e-6) 
Ts_real = 1 / fs_real 

# Modelo jitter deterministico
Ts_jitter_det = clk_jitter_amp*1/BR * np.sin(2*np.pi*clk_jitter_freq * time_ideal)

# Modelo jitter random
Ts_jitter_rand = clk_jitter_std * np.random.randn(Lyup) 

# Fenomenos completo
time_real = clk_phase*1/BR + line*Ts_real + Ts_jitter_det + Ts_jitter_rand

# Aplico los fenomenos resampleando 
# yrs = interp1(time_ideal,yup,time_real, 'spline', 0);
cs = interpolate.CubicSpline(time_ideal, yup_i, extrapolate=False)
yrs_i = cs(time_real)
cs = interpolate.CubicSpline(time_ideal, yup_q, extrapolate=False)
yrs_q = cs(time_real)
# yrs[np.isnan(yrs)] = 0  # Reemplaza NaN con 0 para extrapolación

# print(cs)
# plt.figure()
# plt.plot(time_ideal[:100], yup_i[:100])
# plt.grid()
# plt.figure()
# plt.plot(time_real[:100], yrs[:100])
# plt.grid()
# plt.show()

## RECEPTOR
# MF
# yrx = filter(h,1,yup);
# yrx_rs = filter(h,1,yrs);
yrx_i = np.convolve(h, yup_i, 'same')
yrx_q = np.convolve(h, yup_q, 'same')
yrx_rs_i = np.convolve(h, yrs_i, 'same')
yrx_rs_q = np.convolve(h, yrs_q, 'same')

## Calcular retardo introducido por el filtro
delay = int((len(h)-1) / 2)

## Downsampling
# start_idx = delay + 1
# ybd = downsample(yrx(start_idx:end),N)
# ybd_rs = downsample(yrx_rs(start_idx:end),N)
offset = delay + 1

print(len(yrx_i))
eye_length = int(5e3)

ybd_i = yrx_i[100+offset : eye_length-(100-offset) : int(N)]
ybd_q = yrx_q[100+offset : eye_length-(100-offset) : int(N)]
ybd_rs_i = yrx_rs_i[100+offset : eye_length-(100-offset) : int(N)]
ybd_rs_q = yrx_rs_q[100+offset : eye_length-(100-offset) : int(N)]

## PLOTS
# eyediagram(yrx(L*N/2:end-1000),2*N)
# title('Diagrama de ojo sin ppm')
# eyediagram(yrx_rs(L*N/2:end-1000),2*N)
# title('Diagrama de ojo con ppm')
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
eyediagram(yrx_i[100:len(yrx_i)-100],N,5,N_bauds)
plt.title(r'Diagrama de ojo sin errores')
plt.subplot(1,2,2)
eyediagram(yrx_rs_i[100:len(yrx_rs_i)-100],N,5,N_bauds)
plt.title(r'Diagrama de ojo con errores')

plt.figure()
plt.subplot(1,2,1)
plt.plot(ybd_i, ybd_q, '.',linewidth=2.0)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación sin errores')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.subplot(1,2,2)
plt.plot(ybd_rs_i, ybd_rs_q, '.',linewidth=2.0)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación con errores')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.figure()
plt.subplot(1,2,1)
plt.plot(ybd_i[1:L//2].real, '.')
plt.grid()
plt.title('Simbolos recibidos sin errores')

plt.subplot(1,2,2)
plt.plot(ybd_rs_i[1:L//2].real, '.')
plt.grid()
plt.title('Simbolos recibidos con errores')

plt.figure()
plt.subplot(1,2,1)
plt.plot(time_ideal, 'r', linewidth=2, label='Tiempo ideal')
plt.plot(time_real, '--b', linewidth=2, label='Tiempo real')
plt.legend()
plt.grid()
plt.title('Tiempo Real vs Ideal')
    
plt.subplot(1,2,2)
plt.plot(time_ideal-time_real, '-k', linewidth=2)
plt.grid()
plt.title('Diferencia')

plt.show()