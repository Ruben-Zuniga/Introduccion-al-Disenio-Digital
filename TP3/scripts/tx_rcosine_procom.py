import numpy as np
import matplotlib.pyplot as plt
from tool._fixedInt import *

##  ipython nbconvert --to latex --post PDF <Name.ipynb>

## Parametros generales
Fbaud = 1e9 # Frecuencia de baudio
T     = 1/Fbaud # Periodo de baudio
Nsymb = 1000          # Numero de simbolos
os    = 8
## Parametros de la respuesta en frecuencia
Nfreqs = 2048          # Cantidad de frecuencias

## Parametros del filtro de caida cosenoidal
beta   = [0.0,0.5,0.99] # Roll-Off
Nbauds = 16     # Cantidad de baudios del filtro
## Parametros funcionales
Ts = T/os              # Frecuencia de muestreo

def rcosine(beta, Tbaud, oversampling, Nbauds, Norm):
    """ Respuesta al impulso del pulso de caida cosenoidal """
    t_vect = np.arange(-0.5*Nbauds*Tbaud, 0.5*Nbauds*Tbaud, 
                       float(Tbaud)/oversampling)

    y_vect = []
    for t in t_vect:
        y_vect.append(np.sinc(t/Tbaud)*(np.cos(np.pi*beta*t/Tbaud)/
                                        (1-(4.0*beta*beta*t*t/
                                            (Tbaud*Tbaud)))))

    y_vect = np.array(y_vect)

    if(Norm):
        # return (t_vect, y_vect/np.sqrt(np.sum(y_vect**2)))
        return (t_vect, y_vect/y_vect.sum())
    else:
        return (t_vect,y_vect)

### Calculo de tres pulsos con diferente roll-off
(t,rc0) = rcosine(beta[0], T,os,Nbauds,Norm=False)
(t,rc1) = rcosine(beta[1], T,os,Nbauds,Norm=False)
(t,rc2) = rcosine(beta[2], T,os,Nbauds,Norm=False)

print (np.sum(rc0**2),np.sum(rc1**2),np.sum(rc2**2))
print (np.sum(rc0),np.sum(rc1),np.sum(rc2))

### Conversion a punto fijo
# Beta = 0
rc0_s87 = arrayFixedInt(8, 7, rc0, 'S', 'round', 'saturate')
rc0_s64 = arrayFixedInt(6, 4, rc0, 'S', 'round', 'saturate')
rc0_s32 = arrayFixedInt(3, 2, rc0, 'S', 'round', 'saturate')

rc0_s87_fvalue = np.array([val.fValue for val in rc0_s87])
rc0_s64_fvalue = np.array([val.fValue for val in rc0_s64])
rc0_s32_fvalue = np.array([val.fValue for val in rc0_s32])

# Beta = 0.5
rc1_s87 = arrayFixedInt(8, 7, rc1, 'S', 'round', 'saturate')
rc1_s64 = arrayFixedInt(6, 4, rc1, 'S', 'round', 'saturate')
rc1_s32 = arrayFixedInt(3, 2, rc1, 'S', 'round', 'saturate')

rc1_s87_fvalue = np.array([val.fValue for val in rc1_s87])
rc1_s64_fvalue = np.array([val.fValue for val in rc1_s64])
rc1_s32_fvalue = np.array([val.fValue for val in rc1_s32])

# Beta = 0.99
rc2_s87 = arrayFixedInt(8, 7, rc2, 'S', 'round', 'saturate')
rc2_s64 = arrayFixedInt(6, 4, rc2, 'S', 'round', 'saturate')
rc2_s32 = arrayFixedInt(3, 2, rc2, 'S', 'round', 'saturate')

rc2_s87_fvalue = np.array([val.fValue for val in rc2_s87])
rc2_s64_fvalue = np.array([val.fValue for val in rc2_s64])
rc2_s32_fvalue = np.array([val.fValue for val in rc2_s32])

### Generacion de las graficas
# Filtro flotante
plt.figure(figsize=[14,7])
plt.plot(t*1e9, rc0, 'bo-' , linewidth=1.5, label=r'$\beta=0.0$')
plt.plot(t*1e9, rc1, 'rs-' , linewidth=1.5, label=r'$\beta=0.5$')
plt.plot(t*1e9, rc2, 'g^-' , linewidth=1.5, label=r'$\beta=1.0$')

plt.legend()
plt.grid(True)
plt.title(r'Respuesta al Impulso (Punto Flotante). $BR = 1\, $GBd. $OS = 8$')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')


# Filtro cuantizado
plt.figure(figsize=[14,7])
plt.plot(t, rc0           , 'b-' , linewidth=1.0, label=r'Float')
plt.plot(t, rc0_s87_fvalue, 'ro-', linewidth=2.0, label=r'S(8,7)')
plt.plot(t, rc0_s64_fvalue, 'gs-', linewidth=2.0, label=r'S(6,4)')
plt.plot(t, rc0_s32_fvalue, 'k^-', linewidth=2.0, label=r'S(3,2)')

plt.legend()
plt.grid(True)
plt.xlabel('Tiempo [s]')
plt.ylabel('Magnitud')

symb00    = np.zeros(int(os)*3+1);symb00[os:len(symb00)-1:int(os)] = 1.0
rc0Symb00 = np.convolve(rc0,symb00);
rc1Symb00 = np.convolve(rc1,symb00);
rc2Symb00 = np.convolve(rc2,symb00);

offsetPot = os*((Nbauds//2)-1) + int(os/2)*(Nbauds%2) + 0.5*(os%2 and Nbauds%2)

plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0)),rc0,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0)+os),rc0,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
#plt.xlim(0,35)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. OS: %d'%int(os))

#plt.figure()
plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1)),rc1,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1)+os),rc1,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
#plt.xlim(0,35)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
#plt.title('Rcosine - OS: %d'%int(os))

#plt.figure()
plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2)),rc2,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2)+os),rc2,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
#plt.xlim(0,35)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
#plt.title('Rcosine - OS: %d'%int(os))

plt.show()


def resp_freq(filt, Ts, Nfreqs):
    """Computo de la respuesta en frecuencia de cualquier filtro FIR"""
    H = [] # Lista de salida de la magnitud
    A = [] # Lista de salida de la fase
    filt_len = len(filt)

    #### Genero el vector de frecuencias
    freqs = np.matrix(np.linspace(0,1.0/(2.0*Ts),Nfreqs))
    #### Calculo cuantas muestras necesito para 20 ciclo de
    #### la mas baja frec diferente de cero
    Lseq = 20.0/(freqs[0,1]*Ts)

    #### Genero el vector tiempo
    t = np.matrix(np.arange(0,Lseq))*Ts

    #### Genero la matriz de 2pifTn
    Omega = 2.0j*np.pi*(t.transpose()*freqs)

    #### Valuacion de la exponencial compleja en todo el
    #### rango de frecuencias
    fin = np.exp(Omega)

    #### Suma de convolucion con cada una de las exponenciales complejas
    for i in range(0,np.size(fin,1)):
        fout = np.convolve(np.squeeze(np.array(fin[:,i].transpose())),filt)
        mfout = abs(fout[filt_len:len(fout)-filt_len])
        afout = np.angle(fout[filt_len:len(fout)-filt_len])
        H.append(mfout.sum()/len(mfout))
        A.append(afout.sum()/len(afout))

    return [H,list(np.squeeze(np.array(freqs)))]

def resp_freq_np(filt, Ts, Nfreqs):
    """Computo de la respuesta en frecuencia usando numpy"""
    H = np.abs(np.fft.fftshift(np.fft.fft(filt, Nfreqs)))
    f = np.fft.fftshift(np.fft.fftfreq(len(H), d=Ts))

    return H, f


### Calculo respuesta en frec para los tres pulsos
# Beta = 0
[H0,F0]         = resp_freq_np(rc0           , Ts, Nfreqs)
[H0_s87,F0_s87] = resp_freq_np(rc0_s87_fvalue, Ts, Nfreqs)
[H0_s64,F0_s64] = resp_freq_np(rc0_s64_fvalue, Ts, Nfreqs)
[H0_s32,F0_s32] = resp_freq_np(rc0_s32_fvalue, Ts, Nfreqs)

# Beta = 0.5
[H1,F1]         = resp_freq_np(rc1           , Ts, Nfreqs)
[H1_s87,F1_s87] = resp_freq_np(rc1_s87_fvalue, Ts, Nfreqs)
[H1_s64,F1_s64] = resp_freq_np(rc1_s64_fvalue, Ts, Nfreqs)
[H1_s32,F1_s32] = resp_freq_np(rc1_s32_fvalue, Ts, Nfreqs)

# Beta = 0.99
[H2,F2]         = resp_freq_np(rc2           , Ts, Nfreqs)
[H2_s87,F2_s87] = resp_freq_np(rc2_s87_fvalue, Ts, Nfreqs)
[H2_s64,F2_s64] = resp_freq_np(rc2_s64_fvalue, Ts, Nfreqs)
[H2_s32,F2_s32] = resp_freq_np(rc2_s32_fvalue, Ts, Nfreqs)

### Generacion de los graficos
# Float
plt.figure(figsize=[14,6])
plt.semilogx(F0, 20*np.log10(H0), 'r', linewidth=2.0, label=r'$\beta=0.0$')
plt.semilogx(F1, 20*np.log10(H1), 'g', linewidth=2.0, label=r'$\beta=0.5$')
plt.semilogx(F2, 20*np.log10(H2), 'b', linewidth=2.0, label=r'$\beta=1.0$')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(0.5),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F2[1],F2[len(F2)-1])
plt.title(r'Respuesta en Frecuencia (Punto Flotante). $BR = 1\,$GBd. $OS = 8$')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')

# Fixed
plt.figure(figsize=[14,6])
plt.semilogx(F0_s87, 20*np.log10(H0_s87), 'r', linewidth=2.0, label=r'S(8,7)')
plt.semilogx(F0_s64, 20*np.log10(H0_s64), 'g', linewidth=2.0, label=r'S(6,4)')
plt.semilogx(F0_s32, 20*np.log10(H0_s32), 'b', linewidth=2.0, label=r'S(3,2)')
plt.semilogx(F0, 20*np.log10(H0), 'k', linewidth=1.0, label=r'Float')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(0.5),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F0_s32[1],F0_s32[len(F0_s32)-1])
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')
plt.show()


### Generacion de simbolos. La funcion devuelve num. reales
symbolsI = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;
symbolsQ = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;

### Sobremuestreo de los simbolos
zsymbI = np.zeros(os*Nsymb); zsymbI[1:len(zsymbI):int(os)]=symbolsI
zsymbQ = np.zeros(os*Nsymb); zsymbQ[1:len(zsymbQ):int(os)]=symbolsQ

### Convolucion
# Beta = 0
symb_out0I = np.convolve(rc0,zsymbI,'same'); symb_out0Q = np.convolve(rc0,zsymbQ,'same')

# Beta = 0.5
symb_out1I = np.convolve(rc1,zsymbI,'same'); symb_out1Q = np.convolve(rc1,zsymbQ,'same')

# Beta = 0.99
symb_out2I = np.convolve(rc2,zsymbI,'same'); symb_out2Q = np.convolve(rc2,zsymbQ,'same')

### Diagrama de ojo
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

# Beta = 0
plt.figure(figsize=[14,6])
plt.subplot(1,2,1)
eyediagram(symb_out0I[100:len(symb_out0I)-100],os,5,Nbauds)
plt.subplot(1,2,2)
eyediagram(symb_out0Q[100:len(symb_out0Q)-100],os,5,Nbauds)

# Beta = 0.5
plt.figure(figsize=[14,6])
plt.subplot(1,2,1)
eyediagram(symb_out1I[100:len(symb_out1I)-100],os,5,Nbauds)
plt.subplot(1,2,2)
eyediagram(symb_out1Q[100:len(symb_out1Q)-100],os,5,Nbauds)

# Beta = 0.99
plt.figure(figsize=[14,6])
plt.subplot(1,2,1)
eyediagram(symb_out2I[100:len(symb_out2I)-100],os,5,Nbauds)
plt.subplot(1,2,2)
eyediagram(symb_out2Q[100:len(symb_out2Q)-100],os,5,Nbauds)

plt.show()

### Constelaciones
offset = 6
plt.figure(figsize=[14,6])

plt.subplots_adjust(left=0.057, bottom=0.128, right=0.97, top=0.846, wspace=0.292, hspace=0.2)

# Beta = 0
plt.subplot(1,3,1)
plt.plot(symb_out0I[100+offset:len(symb_out0I)-(100-offset):int(os)],
         symb_out0Q[100+offset:len(symb_out0Q)-(100-offset):int(os)],
             '.',linewidth=2.0)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación (Punto Flotante). $\beta=0.0$')
plt.xlabel('Real')
plt.ylabel('Imag')

# Beta = 0.5
plt.subplot(1,3,2)
plt.plot(symb_out1I[100+offset:len(symb_out1I)-(100-offset):int(os)],
         symb_out1Q[100+offset:len(symb_out1Q)-(100-offset):int(os)],
             '.',linewidth=2.0)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación (Punto Flotante). $\beta=0.5$')
plt.xlabel('Real')
plt.ylabel('Imag')

# Beta = 0.99
plt.subplot(1,3,3)
plt.plot(symb_out2I[100+offset:len(symb_out2I)-(100-offset):int(os)],
         symb_out2Q[100+offset:len(symb_out2Q)-(100-offset):int(os)],
             '.',linewidth=2.0)
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación (Punto Flotante). $\beta=1.0$')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.show()





