import time
import serial
import sys
import matplotlib.pyplot as plt
#############################################
# Nota:
# Comentar esta linea si se utiliza el puerto serie
# con la FPGA
#############################################
# ser = serial.serial_for_url('loop://', timeout=1)

#############################################
# Nota:
# Descomentar esta linea si se utiliza el puerto serie
# con la FPGA
#############################################
portUSB = sys.argv[1]
ser = serial.Serial(
    port='/dev/ttyUSB{}'.format(int(portUSB)),	#Configurar con el puerto
    baudrate = 115200,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS
)

ser.isOpen()
ser.timeout=None
ser.flushInput()
ser.flushOutput()
print(ser.timeout)

## Armar trama
# cabecera = 10100001 = 161 = 0xA1
cabecera = b'\xA1'
# dispositivo (FPGA): elijo el valor 254 = 0xfe
dispositivo = b'\xFE'
# fin_de_trama = 01000001 = 65 = 0x41
fin_de_trama = b'\x41'

# Inicio de trama
init = (int.from_bytes(cabecera,byteorder='big') & 0xF0) >> 4

# Este dispositivo (Python)
dispositivo_host = b'\xEF'
dispositivo_host = int.from_bytes(dispositivo_host,byteorder='big')

# Memoria del DSP
LOG_SIZE = 1024

# Mensaje de inicio
print ('--- Comunicación con FPGA:',ser.port,'---\r\n')

# Bucle de envio y recepcion
while 1 :
    char_v = []

    # Mensaje a enviar
    print('Indique leer datos:')
    print('\t1: Leer BER')
    print('\t2: Obtener log de datos')

    data_write = input("<< ")
    data_write_str = str(data_write)

    if data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    print ("Esperando respuesta...")
        
    # Armar y enviar trama
    data_write_int = int(data_write)
    data_write_byte = data_write_int.to_bytes(1, 'big')

    # Reiniciar buffer de recepcion
    ser.reset_input_buffer()
    # Enviar dato
    ser.write(cabecera + dispositivo + data_write_byte + fin_de_trama)
    print(cabecera + dispositivo + data_write_byte + fin_de_trama)

    # Leer BER
    if data_write_int == 1:
        # Esperar y mostrar respuesta del receptor
        time.sleep(2)

        print('Bytes entrantes:', ser.inWaiting())

        # ber_values: valores de error y simbolos totales
        # ber_values[0]: errores I parte alta
        # ber_values[1]: errores I parte baja
        # ber_values[2]: simbolos I parte alta
        # ber_values[3]: simbolos I parte baja
        # ber_values[4]: errores Q parte alta
        # ber_values[5]: errores Q parte baja
        # ber_values[6]: simbolos Q parte alta
        # ber_values[7]: simbolos Q parte baja
        ber_values = []

        while ser.in_waiting > 0:
            # Leer dato
            data_read = ser.read(4)
            # Convertir a entero e imprimir dato recibido
            data_read_int = int.from_bytes(data_read,byteorder='big')
            # print (">>", data_read_int)
            ber_values.append(data_read_int)

        # errores/simbolos = (parte_alta * 2**32 + parte_baja)
        print (">> BER I:", (ber_values[0] * 2**32 + ber_values[1]) / \
                            (ber_values[2] * 2**32 + ber_values[3]))
        print (">> BER Q:", (ber_values[4] * 2**32 + ber_values[5]) / \
                            (ber_values[6] * 2**32 + ber_values[7]))

    elif data_write_int == 2:
        # Esperar y mostrar respuesta del receptor
        # time.sleep(2)

        print('Bytes entrantes:', ser.in_waiting)

        idx_read = 0
        log_i = []
        log_q = []

        while idx_read < 2 * LOG_SIZE:

            data_read = ser.read(1)
            # Convertir a entero signado y guardar en arreglo
            data_read_int = int.from_bytes(data_read,byteorder='big',signed=True)
            
            if idx_read < LOG_SIZE:
                log_i.append(data_read_int)
            else:
                log_q.append(data_read_int)

            print('idx:', idx_read, ' - Bytes entrantes:', ser.in_waiting, '- Dato:', data_read_int)
            
            # time.sleep(0.5)
            idx_read = idx_read + 1
            
        plt.figure(figsize=[14,6])
        plt.plot(log_i, 'ro-' , linewidth=1.5, label='Canal I')
        plt.plot(log_q, 'bo-' , linewidth=1.5, label='Canal Q')

        plt.legend()
        plt.grid(True)
        plt.title('Plot')
        plt.xlabel('Muestras')
        plt.ylabel('Amplitud')

        # Guardar grafico como archivo. Para descargarla en mi PC:
        #   pscp -P 2222 user@186.182.36.47:/home/user/work_dda/rzuniga/scripts/log.png ~/Documentos/Facultad/Disenio_Digital_Fulgor/Introduccion-al-Disenio-Digital/TP6
        plt.savefig('log.png')

        # print(">> Datos I:")
        # for i in range(LOG_SIZE):
        #     print(log_i[i])

        # print(">> Datos Q:")
        # for i in range(LOG_SIZE):
        #     print(log_q[i])

    else:
        print('Comando desconocido.')
