import numpy as np
import matplotlib.pyplot as plt
from tool._fixedInt import *

# -------------------------------------------------------------
### PARAMETROS 
# -------------------------------------------------------------
## Parametros generales
f_baud = 25e6 # Frecuencia de baudio (f_clk / os)
T_baud = 1/f_baud # Periodo de baudio
os    = 4

## Parametros del filtro de caida cosenoidal
beta   = 0.5 # Roll-Off
N_bauds = 6     # Cantidad de baudios del filtro

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

# Potencia de señal
rc0_sq = np.sum(rc0 ** 2)

# -------------------------------------------------------------
### CONVERSION A VARIOS BITS
# -------------------------------------------------------------

nb_v = np.arange(2, 17)

rc0_fix_sq_t = []
error_sq_t = []

rc0_fix_sq_r = []
error_sq_r = []

for nb in nb_v:
    rc0_fix_t_aux = arrayFixedInt(nb, nb-1, rc0, 'S', 'trunc', 'saturate')
    rc0_fix_t_aux = np.array([val.fValue for val in rc0_fix_t_aux])
    rc0_fix_sq_t.append(np.sum(rc0_fix_t_aux ** 2))

    rc0_fix_r_aux = arrayFixedInt(nb, nb-1, rc0, 'S', 'round', 'saturate')
    rc0_fix_r_aux = np.array([val.fValue for val in rc0_fix_r_aux])
    rc0_fix_sq_r.append(np.sum(rc0_fix_r_aux ** 2))

    # Potencia del error
    error_sq_t.append(np.sum((rc0_fix_t_aux - rc0) ** 2))
    error_sq_r.append(np.sum((rc0_fix_r_aux - rc0) ** 2))

error_sq_t = np.array(error_sq_t)
error_sq_r = np.array(error_sq_r)
# Relacion señal-error
ser_t = rc0_fix_sq_t / error_sq_t
ser_r = rc0_fix_sq_r / error_sq_r

plt.figure()
plt.plot(nb_v, 10*np.log10(ser_t), '-o', label='Truncado')
plt.plot(nb_v, 10*np.log10(ser_r), '-o', label='Redondeo')
plt.title('Relación Señal-Error para Máx. Resolución')
plt.xlabel('N° Bits Totales')
plt.ylabel('SER [dB]')
plt.legend(loc='lower right')
plt.grid()
plt.show()