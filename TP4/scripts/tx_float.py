import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
### PARAMETROS 
# -------------------------------------------------------------
## Parametros generales
f_baud = 25e6 # Frecuencia de baudio (f_clk / os)
T_baud = 1/f_baud # Periodo de baudio
N_symb = 10000          # Numero de simbolos
os    = 4
## Parametros de la respuesta en frecuencia
N_freqs = 2048          # Cantidad de frecuencias

## Parametros del filtro de caida cosenoidal
beta   = 0.5 # Roll-Off
N_bauds = 6     # Cantidad de baudios del filtro
## Parametros funcionales
Ts = T_baud/os              # Frecuencia de muestreo

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
(t,rc0) = rcosine(beta, T_baud,os,N_bauds,Norm=False)

print(f'Potencia del RC: {np.sum(rc0**2)}')
print(f'Ganancia del RC: {np.sum(rc0)}')

# -------------------------------------------------------------
### RESP. AL IMPULSO 
# -------------------------------------------------------------
plt.figure(figsize=[14,7])
plt.plot(t*1e9, rc0, 'bo-' , linewidth=1.5, label=r'$\beta=%2.2f$'%beta)

plt.legend()
plt.grid(True)
plt.title(rf'Respuesta al Impulso. $BR = {f_baud/1e6}\, $MBd. $OS = {os}$')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')

# -------------------------------------------------------------
### RESP. EN FRECUENCIA
# -------------------------------------------------------------
def resp_freq_np(filt, Ts, N_freqs):
    """Computo de la respuesta en frecuencia usando numpy"""
    H = np.abs(np.fft.fftshift(np.fft.fft(filt, N_freqs)))
    f = np.fft.fftshift(np.fft.fftfreq(len(H), d=Ts))

    return H, f

### Calculo respuesta en frec
[H0, F0] = resp_freq_np(rc0, Ts, N_freqs)

### Generacion del grafico
plt.figure(figsize=[14,6])
plt.semilogx(F0, 20*np.log10(H0), 'r', linewidth=2.0, label=r'$\beta=%2.2f$'%beta)

plt.axvline(x=(1./T_baud)/2.,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(H0[len(H0)//2]/2),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F0[len(F0)//2+1],F0[len(F0)-1])
plt.title(rf'Respuesta en Frecuencia. $BR = {f_baud/1e6}\, $MBd. $OS = {os}$')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')

plt.show()

# -------------------------------------------------------------
### GENERACION DE SIMBOLOS Y CONVOLUCION
# -------------------------------------------------------------
### Generacion de simbolos. La funcion uniform devuelve num. reales
symb_inI = 2*(np.random.uniform(-1,1,N_symb)>0.0)-1
symb_inQ = 2*(np.random.uniform(-1,1,N_symb)>0.0)-1

### Sobremuestreo de los simbolos
zsymbI = np.zeros(os*N_symb); zsymbI[1:len(zsymbI):int(os)]=symb_inI
zsymbQ = np.zeros(os*N_symb); zsymbQ[1:len(zsymbQ):int(os)]=symb_inQ

### Convolucion
symb_out0I = np.convolve(rc0,zsymbI,'same')
symb_out0Q = np.convolve(rc0,zsymbQ,'same')

### Plots
plt.figure(figsize=[10,6])
plt.subplot(2,1,1)
plt.stem(zsymbI,'o')
plt.plot(symb_out0I,'r-',linewidth=2.0,label=r'$\beta=%2.2f$'%beta)
plt.xlim(0,250)
plt.grid(True)
plt.legend(loc='upper right')
# plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. OS: %d'%int(os))

plt.subplot(2,1,2)
plt.stem(zsymbQ,'o')
plt.plot(symb_out0Q,'r-',linewidth=2.0,label=r'$\beta=%2.2f$'%beta)
plt.xlim(0,250)
plt.grid(True)
plt.legend(loc='upper right')
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.tight_layout()

plt.show()

# -------------------------------------------------------------
### DIAGRAMA DE OJO 
# -------------------------------------------------------------
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
eyediagram(symb_out0I[100:len(symb_out0I)-100],os,5,N_bauds)
plt.title(r'Diagrama de ojo (I)')
plt.subplot(1,2,2)
eyediagram(symb_out0Q[100:len(symb_out0Q)-100],os,5,N_bauds)
plt.title(r'Diagrama de ojo (Q)')

# -------------------------------------------------------------
### CONSTELACIONES 
# -------------------------------------------------------------
offset_v = np.arange(0, os, 1, dtype=int)

plt.figure(figsize=[8,7])
plt.subplots_adjust(left=0.142, bottom=0.085, right=0.903, top=0.922, wspace=0.37, hspace=0.361)

for offset in offset_v:
    # Muestreo y eliminacion del transitorio
    symb_out0I_trim = symb_out0I[100+offset:len(symb_out0I)-(100-offset):int(os)]
    symb_out0Q_trim = symb_out0Q[100+offset:len(symb_out0Q)-(100-offset):int(os)]
    zsymbI_trim = zsymbI[100+1:len(zsymbI)-(100-1):int(os)]
    zsymbQ_trim = zsymbQ[100+1:len(zsymbQ)-(100-1):int(os)]

    # Slicer
    symb_out0I_slicer = np.where(symb_out0I_trim >= 0, 1, -1)
    symb_out0Q_slicer = np.where(symb_out0Q_trim >= 0, 1, -1)
    
    errors_I = np.sum(symb_out0I_slicer != zsymbI_trim)
    errors_Q = np.sum(symb_out0Q_slicer != zsymbQ_trim)
    ber_I = errors_I / len(zsymbI_trim)
    ber_Q = errors_Q / len(zsymbQ_trim)

    print(f'---- Fase {offset} ----')
    print(f'BER (I): {ber_I}')
    print(f'BER (Q): {ber_Q}')

    plt.subplot(int(os/2), int(os/2), offset+1)
    plt.plot(symb_out0I_trim, symb_out0Q_trim, '.',linewidth=2.0, alpha=0.5)
    plt.xlim((-2, 2))
    plt.ylim((-2, 2))
    plt.grid(True)
    plt.title(r'Constelación. Fase: %d/%d'%(offset,os-1))
    plt.xlabel('Real')
    plt.ylabel('Imag')

plt.tight_layout()
plt.show()
