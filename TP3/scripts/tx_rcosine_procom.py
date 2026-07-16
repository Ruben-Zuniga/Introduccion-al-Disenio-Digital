import numpy as np
import matplotlib.pyplot as plt
from tool._fixedInt import *

# -------------------------------------------------------------
### PARAMETROS 
# -------------------------------------------------------------
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

# -------------------------------------------------------------
### GENERACION COSENO REALZADO 
# -------------------------------------------------------------

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

print(np.sum(rc0**2),np.sum(rc1**2),np.sum(rc2**2))
print(np.sum(rc0),np.sum(rc1),np.sum(rc2))

# -------------------------------------------------------------
### CONVERSION A PUNTO FIJO 
# -------------------------------------------------------------
## Beta = 0
# Truncado
rc0_s87_trunc = arrayFixedInt(8, 7, rc0, 'S', 'trunc', 'saturate')
rc0_s64_trunc = arrayFixedInt(6, 4, rc0, 'S', 'trunc', 'saturate')
rc0_s32_trunc = arrayFixedInt(3, 2, rc0, 'S', 'trunc', 'saturate')

rc0_s87_trunc_fvalue = np.array([val.fValue for val in rc0_s87_trunc])
rc0_s64_trunc_fvalue = np.array([val.fValue for val in rc0_s64_trunc])
rc0_s32_trunc_fvalue = np.array([val.fValue for val in rc0_s32_trunc])

# Redondeo
rc0_s87_round = arrayFixedInt(8, 7, rc0, 'S', 'round', 'saturate')
rc0_s64_round = arrayFixedInt(6, 4, rc0, 'S', 'round', 'saturate')
rc0_s32_round = arrayFixedInt(3, 2, rc0, 'S', 'round', 'saturate')

rc0_s87_round_fvalue = np.array([val.fValue for val in rc0_s87_round])
rc0_s64_round_fvalue = np.array([val.fValue for val in rc0_s64_round])
rc0_s32_round_fvalue = np.array([val.fValue for val in rc0_s32_round])

## Beta = 0.5
# Truncado
rc1_s87_trunc = arrayFixedInt(8, 7, rc1, 'S', 'trunc', 'saturate')
rc1_s64_trunc = arrayFixedInt(6, 4, rc1, 'S', 'trunc', 'saturate')
rc1_s32_trunc = arrayFixedInt(3, 2, rc1, 'S', 'trunc', 'saturate')

rc1_s87_trunc_fvalue = np.array([val.fValue for val in rc1_s87_trunc])
rc1_s64_trunc_fvalue = np.array([val.fValue for val in rc1_s64_trunc])
rc1_s32_trunc_fvalue = np.array([val.fValue for val in rc1_s32_trunc])

# Redondeo
rc1_s87_round = arrayFixedInt(8, 7, rc1, 'S', 'round', 'saturate')
rc1_s64_round = arrayFixedInt(6, 4, rc1, 'S', 'round', 'saturate')
rc1_s32_round = arrayFixedInt(3, 2, rc1, 'S', 'round', 'saturate')

rc1_s87_round_fvalue = np.array([val.fValue for val in rc1_s87_round])
rc1_s64_round_fvalue = np.array([val.fValue for val in rc1_s64_round])
rc1_s32_round_fvalue = np.array([val.fValue for val in rc1_s32_round])

## Beta = 0.99
# Truncado
rc2_s87_trunc = arrayFixedInt(8, 7, rc2, 'S', 'trunc', 'saturate')
rc2_s64_trunc = arrayFixedInt(6, 4, rc2, 'S', 'trunc', 'saturate')
rc2_s32_trunc = arrayFixedInt(3, 2, rc2, 'S', 'trunc', 'saturate')

rc2_s87_trunc_fvalue = np.array([val.fValue for val in rc2_s87_trunc])
rc2_s64_trunc_fvalue = np.array([val.fValue for val in rc2_s64_trunc])
rc2_s32_trunc_fvalue = np.array([val.fValue for val in rc2_s32_trunc])

# Redondeo
rc2_s87_round = arrayFixedInt(8, 7, rc2, 'S', 'round', 'saturate')
rc2_s64_round = arrayFixedInt(6, 4, rc2, 'S', 'round', 'saturate')
rc2_s32_round = arrayFixedInt(3, 2, rc2, 'S', 'round', 'saturate')

rc2_s87_round_fvalue = np.array([val.fValue for val in rc2_s87_round])
rc2_s64_round_fvalue = np.array([val.fValue for val in rc2_s64_round])
rc2_s32_round_fvalue = np.array([val.fValue for val in rc2_s32_round])

# print(rc0_s87_round[0].showRange())
# print(rc0_s64_round[0].showRange())
# print(rc0_s32_round[0].showRange())

# -------------------------------------------------------------
### RESP. AL IMPULSO 
# -------------------------------------------------------------
## Filtro flotante
plt.figure(figsize=[14,7])
plt.plot(t*1e9, rc0, 'bo-' , linewidth=1.5, label=r'$\beta=0.0$')
plt.plot(t*1e9, rc1, 'rs-' , linewidth=1.5, label=r'$\beta=0.5$')
plt.plot(t*1e9, rc2, 'g^-' , linewidth=1.5, label=r'$\beta=1.0$')

plt.legend()
plt.grid(True)
plt.title(r'Respuesta al Impulso (Punto Flotante). $BR = 1\, $GBd. $OS = 8$')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')

## Filtro cuantizado
# Formato variable
plt.figure(figsize=[14,7])
plt.plot(t*1e9, rc1_s32_trunc_fvalue, 'b^-', linewidth=2.0, label=r'S(3,2) Trunc.')
plt.plot(t*1e9, rc1_s64_trunc_fvalue, 'gs-', linewidth=2.0, label=r'S(6,4) Trunc.')
plt.plot(t*1e9, rc1_s87_trunc_fvalue, 'ro-', linewidth=2.0, label=r'S(8,7) Trunc.')

plt.legend()
plt.grid(True)
plt.title(r'Respuesta al Impulso. $\beta=0.5$')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')

# Beta variable
plt.figure(figsize=[14,7])
plt.plot(t*1e9, rc0_s64_trunc_fvalue, 'ro-', linewidth=2.0, label=r'$\beta=0.0$')
plt.plot(t*1e9, rc1_s64_trunc_fvalue, 'gs-', linewidth=2.0, label=r'$\beta=0.5$')
plt.plot(t*1e9, rc2_s64_trunc_fvalue, 'b^-', linewidth=2.0, label=r'$\beta=1.0$')

plt.legend()
plt.grid(True)
plt.title(r'Respuesta al Impulso. Formato: S(6,4) Truncado.')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')

# Truncado y redondeo
plt.figure(figsize=[14,7])
plt.plot(t*1e9, rc2                 , 'k-' , linewidth=1.0, label=r'Float')
plt.plot(t*1e9, rc2_s64_trunc_fvalue, 'ro-', linewidth=2.0, label=r'S(6,4) Trunc.')
plt.plot(t*1e9, rc2_s64_round_fvalue, 'gs-', linewidth=2.0, label=r'S(6,4) Red.')

plt.legend()
plt.grid(True)
plt.title(r'Respuesta al Impulso. $\beta=1$. Formato: S(6,4)')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')

# Formato variable con redondeo
plt.figure(figsize=[14,7])
# plt.plot(t, rc1                 , 'b-' , linewidth=1.0, label=r'Float')
plt.plot(t*1e9, rc1_s32_round_fvalue, 'b^-', linewidth=2.0, label=r'S(3,2) Red.')
plt.plot(t*1e9, rc1_s64_round_fvalue, 'gs-', linewidth=2.0, label=r'S(6,4) Red.')
plt.plot(t*1e9, rc1_s87_round_fvalue, 'ro-', linewidth=2.0, label=r'S(8,7) Red.')

plt.legend()
plt.grid(True)
plt.title(r'Respuesta al Impulso. $\beta=0.5$')
plt.xlabel('Tiempo [períodos de símbolo T]')
plt.ylabel('Magnitud')
plt.show()

# -------------------------------------------------------------
### CONVOLUCION CON SIMBOLOS 
# -------------------------------------------------------------
symb00    = np.zeros(int(os)*3+1);symb00[os:len(symb00)-1:int(os)] = 1.0

## Float
rc0Symb00 = np.convolve(rc0,symb00)
rc1Symb00 = np.convolve(rc1,symb00)
rc2Symb00 = np.convolve(rc2,symb00)
## S(8,7) trunc
rc0Symb00_s87_trunc = np.convolve(rc0_s87_trunc_fvalue,symb00)
rc1Symb00_s87_trunc = np.convolve(rc1_s87_trunc_fvalue,symb00)
rc2Symb00_s87_trunc = np.convolve(rc2_s87_trunc_fvalue,symb00)
## S(8,7) round
rc0Symb00_s87_round = np.convolve(rc0_s87_round_fvalue,symb00)
rc1Symb00_s87_round = np.convolve(rc1_s87_round_fvalue,symb00)
rc2Symb00_s87_round = np.convolve(rc2_s87_round_fvalue,symb00)
## S(6,4) trunc
rc0Symb00_s64_trunc = np.convolve(rc0_s64_trunc_fvalue,symb00)
rc1Symb00_s64_trunc = np.convolve(rc1_s64_trunc_fvalue,symb00)
rc2Symb00_s64_trunc = np.convolve(rc2_s64_trunc_fvalue,symb00)
## S(6,4) round
rc0Symb00_s64_round = np.convolve(rc0_s64_round_fvalue,symb00)
rc1Symb00_s64_round = np.convolve(rc1_s64_round_fvalue,symb00)
rc2Symb00_s64_round = np.convolve(rc2_s64_round_fvalue,symb00)
## S(3,2) trunc
rc0Symb00_s32_trunc = np.convolve(rc0_s32_trunc_fvalue,symb00)
rc1Symb00_s32_trunc = np.convolve(rc1_s32_trunc_fvalue,symb00)
rc2Symb00_s32_trunc = np.convolve(rc2_s32_trunc_fvalue,symb00)
## S(3,2) round
rc0Symb00_s32_round = np.convolve(rc0_s32_round_fvalue,symb00)
rc1Symb00_s32_round = np.convolve(rc1_s32_round_fvalue,symb00)
rc2Symb00_s32_round = np.convolve(rc2_s32_round_fvalue,symb00)

offsetPot = os*((Nbauds//2)-1) + int(os/2)*(Nbauds%2) + 0.5*(os%2 and Nbauds%2)

## Float
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0)),rc0,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0)+os),rc0,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1)),rc1,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1)+os),rc1,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2)),rc2,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2)+os),rc2,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

## Con truncado
# S(8,7)
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0_s87_trunc_fvalue)),rc0_s87_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0_s87_trunc_fvalue)+os),rc0_s87_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00_s87_trunc[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. Formato: S(8,7) trunc. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1_s87_trunc_fvalue)),rc1_s87_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1_s87_trunc_fvalue)+os),rc1_s87_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00_s87_trunc[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2_s87_trunc_fvalue)),rc2_s87_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2_s87_trunc_fvalue)+os),rc2_s87_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00_s87_trunc[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

## S(6,4)
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0_s64_trunc_fvalue)),rc0_s64_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0_s64_trunc_fvalue)+os),rc0_s64_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00_s64_trunc[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. Formato: S(6,4) trunc. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1_s64_trunc_fvalue)),rc1_s64_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1_s64_trunc_fvalue)+os),rc1_s64_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00_s64_trunc[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2_s64_trunc_fvalue)),rc2_s64_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2_s64_trunc_fvalue)+os),rc2_s64_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00_s64_trunc[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

## S(3,2)
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0_s32_trunc_fvalue)),rc0_s32_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0_s32_trunc_fvalue)+os),rc0_s32_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00_s32_trunc[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. Formato: S(3,2) trunc. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1_s32_trunc_fvalue)),rc1_s32_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1_s32_trunc_fvalue)+os),rc1_s32_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00_s32_trunc[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2_s32_trunc_fvalue)),rc2_s32_trunc_fvalue,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2_s32_trunc_fvalue)+os),rc2_s32_trunc_fvalue,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00_s32_trunc[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')


## Con redondeo
# S(8,7)
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0_s87_round_fvalue)),rc0_s87_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0_s87_round_fvalue)+os),rc0_s87_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00_s87_round[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. Formato: S(8,7) red. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1_s87_round_fvalue)),rc1_s87_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1_s87_round_fvalue)+os),rc1_s87_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00_s87_round[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2_s87_round_fvalue)),rc2_s87_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2_s87_round_fvalue)+os),rc2_s87_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00_s87_round[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

## S(6,4)
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0_s64_round_fvalue)),rc0_s64_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0_s64_round_fvalue)+os),rc0_s64_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00_s64_round[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. Formato: S(6,4) red. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1_s64_round_fvalue)),rc1_s64_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1_s64_round_fvalue)+os),rc1_s64_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00_s64_round[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2_s64_round_fvalue)),rc2_s64_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2_s64_round_fvalue)+os),rc2_s64_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00_s64_round[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

## S(3,2)
plt.figure(figsize=[14,7])
plt.subplot(3,1,1)
plt.plot(np.arange(0,len(rc0_s32_round_fvalue)),rc0_s32_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.plot(np.arange(os,len(rc0_s32_round_fvalue)+os),rc0_s32_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc0Symb00_s32_round[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')
plt.title('Convolución del RC con símbolos. Formato: S(3,2) red. OS: %d'%int(os))

plt.subplot(3,1,2)
plt.plot(np.arange(0,len(rc1_s32_round_fvalue)),rc1_s32_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.plot(np.arange(os,len(rc1_s32_round_fvalue)+os),rc1_s32_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=0.5$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc1Symb00_s32_round[os::],'--',linewidth=2.0,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.subplot(3,1,3)
plt.plot(np.arange(0,len(rc2_s32_round_fvalue)),rc2_s32_round_fvalue,'r.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.plot(np.arange(os,len(rc2_s32_round_fvalue)+os),rc2_s32_round_fvalue,'k.-',linewidth=1.0,label=r'$\beta=1.0$')
plt.stem(np.arange(offsetPot,len(symb00)+offsetPot),symb00,label='Símbolos')
plt.plot(rc2Symb00_s32_round[os::],'--',linewidth=2,label='Convolución')
plt.legend()
plt.grid(True)
plt.xlim(40,100)
plt.ylim(-0.2,1.4)
plt.xlabel('Muestras')
plt.ylabel('Magnitud')

plt.show()

# -------------------------------------------------------------
### RESP. EN FRECUENCIA
# -------------------------------------------------------------
def resp_freq_np(filt, Ts, Nfreqs):
    """Computo de la respuesta en frecuencia usando numpy"""
    H = np.abs(np.fft.fftshift(np.fft.fft(filt, Nfreqs)))
    f = np.fft.fftshift(np.fft.fftfreq(len(H), d=Ts))

    return H, f

### Calculo respuesta en frec para los tres pulsos
## Beta = 0
[H0          , F0          ] = resp_freq_np(rc0                 , Ts, Nfreqs)

# Truncado
[H0_s87_trunc, F0_s87_trunc] = resp_freq_np(rc0_s87_trunc_fvalue, Ts, Nfreqs)
[H0_s64_trunc, F0_s64_trunc] = resp_freq_np(rc0_s64_trunc_fvalue, Ts, Nfreqs)
[H0_s32_trunc, F0_s32_trunc] = resp_freq_np(rc0_s32_trunc_fvalue, Ts, Nfreqs)

# Redondeo
[H0_s87_round, F0_s87_round] = resp_freq_np(rc0_s87_round_fvalue, Ts, Nfreqs)
[H0_s64_round, F0_s64_round] = resp_freq_np(rc0_s64_round_fvalue, Ts, Nfreqs)
[H0_s32_round, F0_s32_round] = resp_freq_np(rc0_s32_round_fvalue, Ts, Nfreqs)

## Beta = 0.5
[H1          , F1          ] = resp_freq_np(rc1                 , Ts, Nfreqs)

# Truncado
[H1_s87_trunc, F1_s87_trunc] = resp_freq_np(rc1_s87_trunc_fvalue, Ts, Nfreqs)
[H1_s64_trunc, F1_s64_trunc] = resp_freq_np(rc1_s64_trunc_fvalue, Ts, Nfreqs)
[H1_s32_trunc, F1_s32_trunc] = resp_freq_np(rc1_s32_trunc_fvalue, Ts, Nfreqs)

# Redondeo
[H1_s87_round, F1_s87_round] = resp_freq_np(rc1_s87_round_fvalue, Ts, Nfreqs)
[H1_s64_round, F1_s64_round] = resp_freq_np(rc1_s64_round_fvalue, Ts, Nfreqs)
[H1_s32_round, F1_s32_round] = resp_freq_np(rc1_s32_round_fvalue, Ts, Nfreqs)

## Beta = 0.99
[H2          , F2          ] = resp_freq_np(rc2                 , Ts, Nfreqs)

# Truncado
[H2_s87_trunc, F2_s87_trunc] = resp_freq_np(rc2_s87_trunc_fvalue, Ts, Nfreqs)
[H2_s64_trunc, F2_s64_trunc] = resp_freq_np(rc2_s64_trunc_fvalue, Ts, Nfreqs)
[H2_s32_trunc, F2_s32_trunc] = resp_freq_np(rc2_s32_trunc_fvalue, Ts, Nfreqs)

# Redondeo
[H2_s87_round, F2_s87_round] = resp_freq_np(rc2_s87_round_fvalue, Ts, Nfreqs)
[H2_s64_round, F2_s64_round] = resp_freq_np(rc2_s64_round_fvalue, Ts, Nfreqs)
[H2_s32_round, F2_s32_round] = resp_freq_np(rc2_s32_round_fvalue, Ts, Nfreqs)

### Generacion de los graficos
## Float
plt.figure(figsize=[14,6])
plt.semilogx(F0, 20*np.log10(H0), 'r', linewidth=2.0, label=r'$\beta=0.0$')
plt.semilogx(F1, 20*np.log10(H1), 'g', linewidth=2.0, label=r'$\beta=0.5$')
plt.semilogx(F2, 20*np.log10(H2), 'b', linewidth=2.0, label=r'$\beta=1.0$')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(0.5),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F2[len(F2)//2+1],F2[len(F2)-1])
plt.title(r'Respuesta en Frecuencia (Punto Flotante). $BR = 1\,$GBd. $OS = 8$')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')

## Fixed
# Beta fijo
plt.figure(figsize=[14,6])
plt.semilogx(F1_s32_trunc, 20*np.log10(H1_s32_trunc), 'b', linewidth=2.0, label=r'S(3,2) Trunc.')
plt.semilogx(F1_s64_trunc, 20*np.log10(H1_s64_trunc), 'g', linewidth=2.0, label=r'S(6,4) Trunc.')
plt.semilogx(F1_s87_trunc, 20*np.log10(H1_s87_trunc), 'r', linewidth=2.0, label=r'S(8,7) Trunc.')
plt.semilogx(F1          , 20*np.log10(H1          ), 'k', linewidth=0.8, label=r'Float')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(H1[len(H1)//2]/2),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F1_s32_trunc[len(F1_s32_trunc)//2+1],F1_s32_trunc[len(F1_s32_trunc)-1])
plt.title(r'Respuesta en Frecuencia. $\beta=0.5$')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')

# Formato fijo
plt.figure(figsize=[14,6])
plt.semilogx(F0_s64_trunc, 20*np.log10(H0_s64_trunc), 'r', linewidth=2.0, label=r'$\beta=0.0$')
plt.semilogx(F1_s64_trunc, 20*np.log10(H1_s64_trunc), 'g', linewidth=2.0, label=r'$\beta=0.5$')
plt.semilogx(F2_s64_trunc, 20*np.log10(H2_s64_trunc), 'b', linewidth=2.0, label=r'$\beta=1.0$')
# plt.semilogx(F0          , 20*np.log10(H0          ), 'k', linewidth=0.8, label=r'Float')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(H0_s64_trunc[len(H0_s64_trunc)//2]/2),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F0[len(F0)//2+1],F0[len(F0)-1])
plt.title(r'Respuesta en Frecuencia. Formato: S(6,4) Truncado')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')

# Beta y formato fijos
plt.figure(figsize=[14,6])
plt.semilogx(F2_s64_trunc, 20*np.log10(H2_s64_trunc), 'r', linewidth=2.0, label=r'S(6,4) Trunc.')
plt.semilogx(F2_s64_round, 20*np.log10(H2_s64_round), 'g', linewidth=2.0, label=r'S(6,4) Red.')
plt.semilogx(F2          , 20*np.log10(H2          ), 'k', linewidth=0.8, label=r'Float')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(H2[len(H2)//2]/2),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F2[len(F2)//2+1],F2[len(F2)-1])
plt.title(r'Respuesta en Frecuencia. $\beta=1$. Formato: S(6,4)')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')

# Beta fijo con redondeo
plt.figure(figsize=[14,6])
plt.semilogx(F1_s32_round, 20*np.log10(H1_s32_round), 'b', linewidth=2.0, label=r'S(3,2) Red.')
plt.semilogx(F1_s64_round, 20*np.log10(H1_s64_round), 'g', linewidth=2.0, label=r'S(6,4) Red.')
plt.semilogx(F1_s87_round, 20*np.log10(H1_s87_round), 'r', linewidth=2.0, label=r'S(8,7) Red.')
plt.semilogx(F1          , 20*np.log10(H1          ), 'k', linewidth=0.8, label=r'Float')

plt.axvline(x=(1./T)/2.       ,color='k',linestyle='dotted',linewidth=1.5, label=r'BR/2')
plt.axhline(y=20*np.log10(H1[len(H1)//2]/2),color='k',linestyle='dashed',linewidth=1.5, label=r'$-6\,$dB')
plt.legend(loc=3)
plt.grid(True)
plt.xlim(F1_s32_round[len(F1_s32_round)//2+1],F1_s32_round[len(F1_s32_round)-1])
plt.title(r'Respuesta en Frecuencia. $\beta=0.5$')
plt.xlabel('Frequencia [Hz]')
plt.ylabel('Magnitud [dB]')
plt.show()

# -------------------------------------------------------------
### GENERACION DE SIMBOLOS Y CONVOLUCION
# -------------------------------------------------------------
### Generacion de simbolos. La funcion devuelve num. reales
symbolsI = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;
symbolsQ = 2*(np.random.uniform(-1,1,Nsymb)>0.0)-1;

### Sobremuestreo de los simbolos
zsymbI = np.zeros(os*Nsymb); zsymbI[1:len(zsymbI):int(os)]=symbolsI
zsymbQ = np.zeros(os*Nsymb); zsymbQ[1:len(zsymbQ):int(os)]=symbolsQ

### Convolucion
## Float
# Beta = 0
symb_out0I = np.convolve(rc0,zsymbI,'same'); symb_out0Q = np.convolve(rc0,zsymbQ,'same')
# Beta = 0.5
symb_out1I = np.convolve(rc1,zsymbI,'same'); symb_out1Q = np.convolve(rc1,zsymbQ,'same')
# Beta = 1
symb_out2I = np.convolve(rc2,zsymbI,'same'); symb_out2Q = np.convolve(rc2,zsymbQ,'same')

## S(8,7) trunc
symb_out0I_s87_trunc = np.convolve(rc0_s87_trunc_fvalue,zsymbI,'same')
symb_out0Q_s87_trunc = np.convolve(rc0_s87_trunc_fvalue,zsymbQ,'same')
symb_out1I_s87_trunc = np.convolve(rc1_s87_trunc_fvalue,zsymbI,'same')
symb_out1Q_s87_trunc = np.convolve(rc1_s87_trunc_fvalue,zsymbQ,'same')
symb_out2I_s87_trunc = np.convolve(rc2_s87_trunc_fvalue,zsymbI,'same')
symb_out2Q_s87_trunc = np.convolve(rc2_s87_trunc_fvalue,zsymbQ,'same')

## S(8,7) round
symb_out0I_s87_round = np.convolve(rc0_s87_round_fvalue,zsymbI,'same')
symb_out0Q_s87_round = np.convolve(rc0_s87_round_fvalue,zsymbQ,'same')
symb_out1I_s87_round = np.convolve(rc1_s87_round_fvalue,zsymbI,'same')
symb_out1Q_s87_round = np.convolve(rc1_s87_round_fvalue,zsymbQ,'same')
symb_out2I_s87_round = np.convolve(rc2_s87_round_fvalue,zsymbI,'same')
symb_out2Q_s87_round = np.convolve(rc2_s87_round_fvalue,zsymbQ,'same')

## S(6,4) trunc
symb_out0I_s64_trunc = np.convolve(rc0_s64_trunc_fvalue,zsymbI,'same')
symb_out0Q_s64_trunc = np.convolve(rc0_s64_trunc_fvalue,zsymbQ,'same')
symb_out1I_s64_trunc = np.convolve(rc1_s64_trunc_fvalue,zsymbI,'same')
symb_out1Q_s64_trunc = np.convolve(rc1_s64_trunc_fvalue,zsymbQ,'same')
symb_out2I_s64_trunc = np.convolve(rc2_s64_trunc_fvalue,zsymbI,'same')
symb_out2Q_s64_trunc = np.convolve(rc2_s64_trunc_fvalue,zsymbQ,'same')

## S(6,4) round
symb_out0I_s64_round = np.convolve(rc0_s64_round_fvalue,zsymbI,'same')
symb_out0Q_s64_round = np.convolve(rc0_s64_round_fvalue,zsymbQ,'same')
symb_out1I_s64_round = np.convolve(rc1_s64_round_fvalue,zsymbI,'same')
symb_out1Q_s64_round = np.convolve(rc1_s64_round_fvalue,zsymbQ,'same')
symb_out2I_s64_round = np.convolve(rc2_s64_round_fvalue,zsymbI,'same')
symb_out2Q_s64_round = np.convolve(rc2_s64_round_fvalue,zsymbQ,'same')

## S(3,2) trunc
symb_out0I_s32_trunc = np.convolve(rc0_s32_trunc_fvalue,zsymbI,'same')
symb_out0Q_s32_trunc = np.convolve(rc0_s32_trunc_fvalue,zsymbQ,'same')
symb_out1I_s32_trunc = np.convolve(rc1_s32_trunc_fvalue,zsymbI,'same')
symb_out1Q_s32_trunc = np.convolve(rc1_s32_trunc_fvalue,zsymbQ,'same')
symb_out2I_s32_trunc = np.convolve(rc2_s32_trunc_fvalue,zsymbI,'same')
symb_out2Q_s32_trunc = np.convolve(rc2_s32_trunc_fvalue,zsymbQ,'same')

## S(3,2) round
symb_out0I_s32_round = np.convolve(rc0_s32_round_fvalue,zsymbI,'same')
symb_out0Q_s32_round = np.convolve(rc0_s32_round_fvalue,zsymbQ,'same')
symb_out1I_s32_round = np.convolve(rc1_s32_round_fvalue,zsymbI,'same')
symb_out1Q_s32_round = np.convolve(rc1_s32_round_fvalue,zsymbQ,'same')
symb_out2I_s32_round = np.convolve(rc2_s32_round_fvalue,zsymbI,'same')
symb_out2Q_s32_round = np.convolve(rc2_s32_round_fvalue,zsymbQ,'same')

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

# -------------------------------------------------------------
### CONSTELACIONES 
# -------------------------------------------------------------
plt.figure(figsize=[14,6])
plt.subplots_adjust(left=0.057, bottom=0.128, right=0.97, top=0.846, wspace=0.292, hspace=0.2)

## Float
offset = 6
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


## Fijo truncado
plt.figure(figsize=[14,6])
plt.subplots_adjust(left=0.057, bottom=0.128, right=0.97, top=0.846, wspace=0.292, hspace=0.2)
offset = 6

plt.subplot(1,3,1)
plt.plot(symb_out0I_s32_trunc[100+offset:len(symb_out0I_s32_trunc)-(100-offset):int(os)],
         symb_out0Q_s32_trunc[100+offset:len(symb_out0Q_s32_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(3,2)')
plt.plot(symb_out0I_s64_trunc[100+offset:len(symb_out0I_s64_trunc)-(100-offset):int(os)],
         symb_out0Q_s64_trunc[100+offset:len(symb_out0Q_s64_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(6,4)')
plt.plot(symb_out0I_s87_trunc[100+offset:len(symb_out0I_s87_trunc)-(100-offset):int(os)],
         symb_out0Q_s87_trunc[100+offset:len(symb_out0Q_s87_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(8,7)')
plt.xlim((-3.5, 3.5))
plt.ylim((-3.5, 3.5))
plt.grid(True)
plt.title(r'Constelación (Punto Fijo Truncado). $\beta=0.0$')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.subplot(1,3,2)
plt.plot(symb_out0I_s32_trunc[100+offset:len(symb_out0I_s32_trunc)-(100-offset):int(os)],
         symb_out0Q_s32_trunc[100+offset:len(symb_out0Q_s32_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(3,2)')
plt.plot(symb_out0I_s64_trunc[100+offset:len(symb_out0I_s64_trunc)-(100-offset):int(os)],
         symb_out0Q_s64_trunc[100+offset:len(symb_out0Q_s64_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(6,4)')
plt.plot(symb_out1I_s87_trunc[100+offset:len(symb_out1I_s87_trunc)-(100-offset):int(os)],
         symb_out1Q_s87_trunc[100+offset:len(symb_out1Q_s87_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(8,7)')
plt.xlim((-3.5, 3.5))
plt.ylim((-3.5, 3.5))
plt.grid(True)
plt.title(r'Constelación (Punto Fijo Truncado). $\beta=0.5$')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.subplot(1,3,3)
plt.plot(symb_out0I_s32_trunc[100+offset:len(symb_out0I_s32_trunc)-(100-offset):int(os)],
         symb_out0Q_s32_trunc[100+offset:len(symb_out0Q_s32_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(3,2)')
plt.plot(symb_out0I_s64_trunc[100+offset:len(symb_out0I_s64_trunc)-(100-offset):int(os)],
         symb_out0Q_s64_trunc[100+offset:len(symb_out0Q_s64_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(6,4)')
plt.plot(symb_out2I_s87_trunc[100+offset:len(symb_out2I_s87_trunc)-(100-offset):int(os)],
         symb_out2Q_s87_trunc[100+offset:len(symb_out2Q_s87_trunc)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(8,7)')
plt.xlim((-3.5, 3.5))
plt.ylim((-3.5, 3.5))
plt.grid(True)
plt.legend(loc='upper right')
plt.title(r'Constelación (Punto Fijo Truncado). $\beta=1.0$')
plt.xlabel('Real')
plt.ylabel('Imag')

## Fijo redondeado
plt.figure(figsize=[14,6])
plt.subplots_adjust(left=0.057, bottom=0.128, right=0.97, top=0.846, wspace=0.292, hspace=0.2)
offset = 6

plt.subplot(1,3,1)
plt.plot(symb_out0I_s32_round[100+offset:len(symb_out0I_s32_round)-(100-offset):int(os)],
         symb_out0Q_s32_round[100+offset:len(symb_out0Q_s32_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(3,2)')
plt.plot(symb_out0I_s64_round[100+offset:len(symb_out0I_s64_round)-(100-offset):int(os)],
         symb_out0Q_s64_round[100+offset:len(symb_out0Q_s64_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(6,4)')
plt.plot(symb_out0I_s87_round[100+offset:len(symb_out0I_s87_round)-(100-offset):int(os)],
         symb_out0Q_s87_round[100+offset:len(symb_out0Q_s87_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(8,7)')
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación (Punto Fijo Redondeado). $\beta=0.0$')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.subplot(1,3,2)
plt.plot(symb_out0I_s32_round[100+offset:len(symb_out0I_s32_round)-(100-offset):int(os)],
         symb_out0Q_s32_round[100+offset:len(symb_out0Q_s32_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(3,2)')
plt.plot(symb_out0I_s64_round[100+offset:len(symb_out0I_s64_round)-(100-offset):int(os)],
         symb_out0Q_s64_round[100+offset:len(symb_out0Q_s64_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(6,4)')
plt.plot(symb_out1I_s87_round[100+offset:len(symb_out1I_s87_round)-(100-offset):int(os)],
         symb_out1Q_s87_round[100+offset:len(symb_out1Q_s87_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(8,7)')
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.title(r'Constelación (Punto Fijo Redondeado). $\beta=0.5$')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.subplot(1,3,3)
plt.plot(symb_out0I_s32_round[100+offset:len(symb_out0I_s32_round)-(100-offset):int(os)],
         symb_out0Q_s32_round[100+offset:len(symb_out0Q_s32_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(3,2)')
plt.plot(symb_out0I_s64_round[100+offset:len(symb_out0I_s64_round)-(100-offset):int(os)],
         symb_out0Q_s64_round[100+offset:len(symb_out0Q_s64_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(6,4)')
plt.plot(symb_out2I_s87_round[100+offset:len(symb_out2I_s87_round)-(100-offset):int(os)],
         symb_out2Q_s87_round[100+offset:len(symb_out2Q_s87_round)-(100-offset):int(os)],
             '.',linewidth=2.0,label='S(8,7)')
plt.xlim((-2, 2))
plt.ylim((-2, 2))
plt.grid(True)
plt.legend(loc='upper right')
plt.title(r'Constelación (Punto Fijo Redondeado). $\beta=1.0$')
plt.xlabel('Real')
plt.ylabel('Imag')

plt.show()
