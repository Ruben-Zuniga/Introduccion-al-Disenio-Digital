import numpy as np
import matplotlib.pyplot as plt
import serial
import time

ser = serial.Serial(
    # port     = '/dev/ttyUSB1', #COM3
    port     = '/dev/pts/4', #Filtro. CAMBIAR segun el puerto que se abra
    baudrate = 9600,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS
)

# Clase Filtro
class RaisedCosineFilter:
    def __init__(self, alpha=0.25, span=6, sps=8, rrc=True):
        """
        Filtro de coseno realzado o raíz de coseno realzado.
        
        Parámetros:
        - alpha: Factor de roll-off (0 <= alpha <= 1)
        - span: Duración total del filtro en símbolos
        - sps: Muestras por símbolo
        - rrc: Si True, genera raíz de coseno realzado; si False, coseno realzado
        """
        self.alpha = []
        self.span = []
        self.sps = []
        self.rrc = []
        self.taps = []

        self.generate_filter(alpha=alpha, span=span, sps=sps, rrc=rrc)

    # Generar los taps
    def generate_filter(self, alpha=0.25, span=6, sps=8, rrc=True):

        self.alpha.append(alpha)
        self.span.append(span)
        self.sps.append(sps)
        self.rrc.append(rrc)

        T = 1  # Duración del símbolo (normalizado)
        N = self.span[-1] * self.sps[-1] # Cantidad de taps
        t = np.arange(-N//2, N//2 + 1) / self.sps[-1]

        # print(t)
        # print(t[0], t[-1])
        # print(len(t))
        # print(N//2+1)

        if self.rrc[-1]:
            # Filtro Root Raised Cosine
            h = np.zeros_like(t)
            for i in range(len(t)):
                ti = t[i]
                if ti == 0.0:
                    h[i] = 1.0 - self.alpha[-1] + (4 * self.alpha[-1] / np.pi)
                elif abs(ti) == T / (4 * self.alpha[-1]):
                    h[i] = (self.alpha[-1] / np.sqrt(2)) * (
                        ((1 + 2/np.pi) * (np.sin(np.pi/(4*self.alpha[-1])))) +
                        ((1 - 2/np.pi) * (np.cos(np.pi/(4*self.alpha[-1]))))
                    )
                else:
                    h[i] = (np.sin(np.pi * ti * (1 - self.alpha[-1]) / T) +
                            4 * self.alpha[-1] * ti / T *
                            np.cos(np.pi * ti * (1 + self.alpha[-1]) / T)) / \
                           (np.pi * ti * (1 - (4 * self.alpha[-1] * ti / T) ** 2))
        else:
            # Filtro Raised Cosine clásico
            h = np.zeros_like(t)
            for i in range(len(t)):
                ti = t[i]
                if ti == 0.0:
                    h[i] = 1.0
                elif abs(ti) == T / (2 * self.alpha[-1]):
                    h[i] = (np.pi / 4) * np.sinc(1 / (2 * self.alpha[-1]))
                else:
                    h[i] = np.sinc(ti / T) * \
                           np.cos(np.pi * self.alpha[-1] * ti / T) / \
                           (1 - (2 * self.alpha[-1] * ti / T) ** 2)
                    
        # print(len(h))

        self.taps.append(h)

    def plot(self, time_domain=True, freq_domain=False):

        # print(self.span)
        # print(len(self.alpha))

        # Un N y un vector de tiempo para cada filtro
        N = [0]*len(self.alpha)
        t = [0]*len(self.alpha)

        for i in range(len(self.alpha)):
            N[i] = self.span[i] * self.sps[i]
            t[i] = np.arange(-N[i]//2, N[i]//2 + 1) / self.sps[i]

        # print(N)
        # print(t)
        # print(len(self.taps)//2)
        # print(len(t))
        # print(self.taps)

        # Arreglo de colores para los graficos
        color = ['b','g','r','c','m']

        if time_domain:

            # Si se muestra en tiempo y frecuencia, hacer dos subplots, sino hacer uno solo
            if time_domain and freq_domain:
                plt.figure(figsize=(10, 8))
                plt.subplot(2,1,1)
            else:
                plt.figure(figsize=(10, 4))

            for i in range(len(self.alpha)):
                
                plt.stem(t[i], self.taps[i], color[i], label=f"{self.alpha[i]}")
                # plt.plot(t[i], self.taps[i], color[i], '--', linewidth=0.5)

            plt.title("Raised Cosine Filter (Time Domain)")
            plt.xlabel("Time [symbol periods]")
            plt.ylabel("Amplitude")
            plt.grid(True)
            plt.legend(title='Rolloff')
            plt.tight_layout()
            
            # Mostrar ahora si no se grafica frecuencia
            if not (time_domain and freq_domain):
                plt.show()

        if freq_domain:
            # Si se muestra en tiempo y frecuencia, cambiar al otro subplot, sino hacer uno solo
            if time_domain and freq_domain:
                plt.subplot(2,1,2)
            else:
                plt.figure(figsize=(10, 4))

            H = [0]*len(self.alpha)
            f = [0]*len(self.alpha)

            for i in range(len(self.alpha)):
                H[i] = np.fft.fftshift(np.fft.fft(self.taps[i], 1024))
                f[i] = np.linspace(-1, 1, len(H[i]), endpoint=False)

            for i in range(len(self.alpha)):
                plt.plot(f[i], 20 * np.log10(np.abs(H[i])), color[i], label=f"{self.alpha[i]}") # aca sumaba el abs por 1e-6

            plt.title("Raised Cosine Filter (Frequency Domain)")
            plt.xlabel("Normalized Frequency [×π rad/sample]")
            plt.ylabel("Magnitude [dB]")
            plt.grid(True)
            plt.legend(title='Rolloff')
            plt.tight_layout()
            plt.show()

    # Devolver coeficientes del ultimo filtro generado
    def get_coefficients(self):
        return self.taps[-1]
    
# Recibir datos
def serial_read():
    data = ''
    while 1 :
        
        time.sleep(1)
        while ser.in_waiting > 0:
            data += ser.read(1).decode()

        if data != '':
            # Chequear si el caracter de seguridad esta al final. Detecta si el mensaje esta completo, si no, lee lo que queda del buffer
            if data[-1] == '$':
                # Remover caracter de seguridad
                data = data[:len(data)-1]
                
                print(">> " + data)
                return data
            else:
                continue

# Enviar datos
def serial_write(data):
    char_v = []
    for ptr in range(len(data)):
        char_v.append(data[ptr])
        
    for ptr in range(len(char_v)):
        ser.write(char_v[ptr].encode())

# Recibir parametros
def serial_read_params():
    while 1:
        params = serial_read()
        # Separar string recibido y formar un arreglo
        params = params.split(',')

        # Si no se enviaron todos los parametros o se mandaron de más
        if len(params) != 4:
            serial_write('Formato invalido. Intente nuevamente...')

        else:
            # Asignar parametros
            try:
                alpha = float(params[0])
                span = int(params[1])
                sps = int(params[2])
            except ValueError:
                serial_write('Los campos deben ser numeros. Intente nuevamente...')
                continue

            # Si rrc no es 1 o 0
            if params[3] != '1' and params[3] != '0':
                serial_write('rrc debe ser 1 para RRC o 0 para RC. Intente nuevamente...')
            else:
                break

    if params[3] == '1':
        rrc = True
    if params[3] == '0':
        rrc = False

    serial_write('Filtro generado. Puede ingresar los siguientes comandos:\n \
                 "1": Imprime los coeficientes del filtro.\n \
                 "2": Genera el plot de la respuesta al impulso y la ganancia en frecuencia.\n \
                 "3": Genera y almacena un nuevo filtro.')
    
    # Si se acaba de iniciar el script, generar la clase.
    if first_filter_flag:
        return RaisedCosineFilter(alpha=alpha, span=span, sps=sps, rrc=rrc)
    # Sino, usar la funcion de generar un filtro sin borrar los anteriores
    else:
        filtro.generate_filter(alpha=alpha, span=span, sps=sps, rrc=rrc)
        return filtro

first_filter_flag = True
filtro = serial_read_params()
first_filter_flag = False

while 1:
    # Leer comando
    command = serial_read()

    if command == '1':
        serial_write(str(filtro.get_coefficients()))

    elif command == '2':
        serial_write('Graficar respuesta en el tiempo? [S/n]:')

        command = serial_read()
        if command == 'n':
            time_domain = False
        else:
            time_domain = True

        serial_write('Graficar respuesta en frecuencia? [S/n]:')

        command = serial_read()
        if command == 'n':
            freq_domain = False
        else:
            freq_domain = True

        serial_write('Plot en pantalla.')
        filtro.plot(time_domain=time_domain, freq_domain=freq_domain)
        
    elif command == '3':
        serial_write('Ingrese parametros en formato "[alfa],[span],[sps],[rrc]".')
        serial_write('rrc=1 para RRC, rrc=0 para RC:')
        filtro = serial_read_params()

    else:
        serial_write('Comando invalido. Intente nuevamente...')

