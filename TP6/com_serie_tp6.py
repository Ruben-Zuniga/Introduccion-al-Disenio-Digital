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
# Inicio de trama
init = 0x5 # primeros 3 bits '101'
# cabecera = 10100001 = 161 = 0xA1
cabecera = b'\xA1'
# dispositivo (FPGA): elijo el valor 254 = 0xfe
dispositivo = b'\xFE'
# fin_de_trama = 01000001 = 65 = 0x41
fin_de_trama = b'\x41'
end = 0x2 # primeros 3 bits '010'

# Este dispositivo (Python)
dispositivo_host = b'\xEF'
# dispositivo_host = int.from_bytes(dispositivo_host,byteorder='big')

# Memoria del DSP
LOG_SIZE = 8192

# Estado del RX
rx_state = False

def read_frame():
    # Leer cabecera y tamaño
    data_read = ser.read(1)

    # Separar cabecera y tamaño
    data_read_int = int.from_bytes(data_read,byteorder='big')
    init_read = (data_read_int & 0xE0) >> 5
    size_bit_read = (data_read_int & 0x10) >> 4

    print('data read',data_read)
    print('init read',init_read)
    print('size_bit_read',size_bit_read)

    if init_read == init:
        # Tamaño corto
        if size_bit_read == 0:
            size_read = data_read_int & 0x0F
        # Tamaño largo
        else:
            data_read = ser.read(2)
            size_read = int.from_bytes(data_read,byteorder='big')

        print('size_read',size_read)

        # Leer dispositivo
        data_read = ser.read(1)

        print('data_read',data_read)

        if data_read == dispositivo_host:

            # Leer tamaño indicado por la trama
            idx_read = 0
            payload_uint = []
            payload_int = []
            while idx_read < size_read:
                data_read = ser.read(1)
                # Convertir a entero y guardar dato recibido en arreglo
                payload_uint.append(int.from_bytes(data_read,byteorder='big'))
                payload_int.append(int.from_bytes(data_read,byteorder='big', signed=True))
                print (">>", idx_read, payload_uint[idx_read])
                idx_read = idx_read + 1

            payload = bytearray(payload_uint)

            # Comprobar fin de trama
            data_read = ser.read(1)
            print('data_read',data_read)
            data_read_int = int.from_bytes(data_read,byteorder='big')
            end_read = (data_read_int & 0xE0) >> 5
            size_bit_check = (data_read_int & 0x10) >> 4
            size_check = data_read_int & 0x0F

            print('end_read',end_read)
            print('size_bit_check',size_bit_check)

            if end_read != end or size_bit_check != size_bit_read:
                print('Advertencia: es posible que la trama este corrupta (end byte or size bit).')
            elif size_bit_check == 0 and size_check != size_read:
                print('Advertencia: es posible que la trama este corrupta (size byte).')
            elif size_bit_check == 1 and size_check != 0:
                print('Advertencia: es posible que la trama este corrupta (size byte).')

    return payload_uint, payload_int, payload

# Mensaje de inicio
print ('--- Comunicación con FPGA:',ser.port,'---\r\n')
print ('Aviso: TX y RX apagados.')
print ()

# Bucle de envio y recepcion
while 1 :
    char_v = []

    # Mensaje a enviar
    print('Indique una de las siguientes opciones:')
    print('\t1: Reiniciar DSP')
    print('\t2: Togglear TX')
    print('\t3: Togglear RX')
    print('\t4: Leer BER')
    print('\t5: Obtener log de datos')

    data_write = input("<< ")
    data_write_str = str(data_write)
    print(data_write_str)

    # Convertir a entero si no es una entrada vacia
    if data_write_str != '':
        data_write_int = int(data_write)
    else:
        data_write_int = 0

    # Salir del script
    if data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break
    
    # Encender RX preguntando por la fase
    if data_write_int == 3:
        if rx_state:
            data_write = '30'
        else:
            print('Indicar fase:')
            data_write = input("<< ")
            # enviar el valor "{3,fase}"
            data_write = '3' + str(data_write)
        data_write_int = int(data_write)
        rx_state = not rx_state

    # Armar y enviar trama
    data_write_byte = data_write_int.to_bytes(1, 'big')

    # Reiniciar buffer de recepcion
    ser.reset_input_buffer()
    # Enviar dato
    ser.write(cabecera + dispositivo + data_write_byte + fin_de_trama)
    print(cabecera + dispositivo + data_write_byte + fin_de_trama)

    # Resetear
    if data_write_int == 1:

        # Leer dato
        data_read_int,_,_ = read_frame()
            
        if data_read_int[0] != 0:
            print('>> DSP reiniciado con exito.')
        else:
            print('>> Error: El DSP no se reinicio.')

    # Togglear TX
    elif data_write_int == 2:

        # Leer dato
        data_read_int,_,_ = read_frame()

        if data_read_int[0] != 0:
            print('>> TX encendido.')
        else:
            print('>> TX apagado.')

    # Togglear RX
    elif data_write_int // 10 == 3:
        
        # Leer dato
        data_read_int,_,_ = read_frame()
        
        if data_read_int[0] != 0:
            print('>> RX encendido con fase', data_write_int % 3)
        else:
            print('>> RX apagado.')
    
    # Leer BER
    elif data_write_int == 4:
        # Esperar y mostrar respuesta del receptor
        # time.sleep(2)

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

        # Leer dato
        _,_,data_read = read_frame()

        for i in range(0,8):
            ber_values.append(int.from_bytes(data_read[4*i : 4*i + 4],byteorder='big'))

        # errores/simbolos = (parte_alta * 2**32 + parte_baja)
        errors_i = ber_values[0] * 2**32 + ber_values[1]
        symb_i   = ber_values[2] * 2**32 + ber_values[3]
        errors_q = ber_values[4] * 2**32 + ber_values[5]
        symb_q   = ber_values[6] * 2**32 + ber_values[7]

        if symb_i == 0 or symb_q == 0:
            print(">> Error: el receptor no capturo ningun simbolo.")
        else:
            print (">> Errores / Simbolos I:", errors_i, "/", symb_i)
            print ("   Errores / Simbolos Q:", errors_q, "/", symb_q)
            print ("   BER I:", errors_i / symb_i)
            print ("   BER Q:", errors_q / symb_q)
        print ()

    # Leer memoria
    elif data_write_int == 5:

        idx_read = 0
        log_i = []
        log_q = []
        log_i_hex = []
        log_q_hex = []

        # Leer dato
        data_read_hex, data_read_int,_ = read_frame()

        while idx_read < LOG_SIZE:

            log_i.append(data_read_int[idx_read])
            log_i_hex.append(data_read_hex[idx_read])
            
            log_q.append(data_read_int[idx_read + LOG_SIZE])
            log_q_hex.append(data_read_hex[idx_read + LOG_SIZE])

            # print('idx:', idx_read, '- Dato:', data_read_int[idx_read])
            print('Leyendo memoria:', idx_read, '/', LOG_SIZE, end='\r')

            idx_read = idx_read + 1

        print('Leyendo memoria:', idx_read, '/', LOG_SIZE)
        # Crear archivo de datos en I y Q, luego crear el grafico.
        # Para descargar en mi PC:
        #   pscp -P 2222 user@186.182.36.47:/home/user/work_dda/rzuniga/scripts/logs ~/Documentos/Facultad/Disenio_Digital_Fulgor/Introduccion-al-Disenio-Digital/TP6
        with open('logs/log_i.hex', 'w') as file:
            for value in log_i_hex:
                file.write(f'{value:02X}\n')
        with open('logs/log_q.hex', 'w') as file:
            for value in log_q_hex:
                file.write(f'{value:02X}\n')
            
        plt.figure(figsize=[14,6])
        plt.plot(log_i, 'r-' , linewidth=1.5, label='Canal I')
        plt.plot(log_q, 'b-' , linewidth=1.5, label='Canal Q')

        plt.legend()
        plt.grid(True)
        plt.title('Salida del TX')
        plt.xlabel('Muestras')
        plt.ylabel('Amplitud')

        # Guardar grafico completo como archivo
        plt.savefig('logs/log.png')
        # Guardar una porcion
        plt.xlim([0,100])
        plt.savefig('logs/log_zoom.png')

        print('Archivos generados.')
        print()

    else:
        print('Comando desconocido.')
