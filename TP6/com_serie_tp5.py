import time
import serial
import sys
import struct
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
# sys.set_int_max_str_digits(10000)

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

# Mensaje de inicio
print ('--- Comunicación con FPGA:',ser.port,'---\r\n')

# Bucle de envio y recepcion
while 1 :
    char_v = []

    # Mensaje a enviar
    print('Indique controlar LED o switches [0/1] o escriba "exit" para salir.')
    data_write = input("<< ")
    data_write_str = str(data_write)

    if data_write_str == '0':
        while data_write_str != 'back':
            print('Indique LED a controlar [0/1/2/3] o escriba "back" para volver.')
            led = input("<< ")
            
            # Dato de 1 byte
            data_write_str = str(led)

            # print(int(data_write))

            if data_write_str != 'back':
                print('Indique el color del LED [RGB]:')
                print('- R: Rojo [0/1]')
                print('- G: Verde [0/1]')
                print('- B: Azul [0/1]')
                color = input('<< ')

                # print(color)

                color_str = str(color)

                match color_str:
                    case '000':
                        data_write = 0
                    case '100':
                        data_write = 1
                    case '010':
                        data_write = 2
                    case '110':
                        data_write = 3
                    case '001':
                        data_write = 4
                    case '101':
                        data_write = 5
                    case '011':
                        data_write = 6
                    case '111':
                        data_write = 7
                    case _:
                        data_write = 0

                data_write = data_write + 8*int(led)
                data_write_str = data_write.to_bytes(1, 'big')

                # print(data_write)
                # print(cabecera + dispositivo + data_write_str + fin_de_trama)

                # Armar y enviar trama
                ser.write(cabecera + dispositivo + data_write_str + fin_de_trama)
                time.sleep(1)

    elif data_write_str == '1':
        print ("Esperando respuesta...")
        
        # Armar y enviar trama
        data_write = 32
        data_write_str = data_write.to_bytes(1, 'big')
        
        # print(cabecera + dispositivo + data_write_str + fin_de_trama)

        # Reiniciar buffer de recepcion
        ser.reset_input_buffer()
        # Enviar dato
        ser.write(cabecera + dispositivo + data_write_str + fin_de_trama)
        # Esperar y mostrar respuesta del receptor
        time.sleep(2)

        # print(ser.inWaiting())

        while ser.in_waiting > 0:
            # Leer cabecera y dispositivo
            data_read = ser.read(2)

            # Separar cabecera, tamaño y dispositivo
            data_read_int = int.from_bytes(data_read,byteorder='big')
            init_read = (data_read_int & 0xF000) >> 12
            size_read = (data_read_int & 0x0F00) >> 8
            device_read = data_read_int & 0x00FF

            # print(data_read, init_read, size_read, device_read)
            # print(init, dispositivo_host)

            # Comparar Cabecera y dispositivo
            if init_read == init and device_read == dispositivo_host:
                # Leer tamaño indicado por la trama
                data_read = ser.read(size_read)
                # Convertir a entero e imprimir dato recibido
                data_read_int = int.from_bytes(data_read,byteorder='big')
                print (">>",data_read_int)

                # print (">>",data_read_int,"(",ser.inWaiting(),")")

                # Leer fin de trama
                data_read = ser.read(1)

                # print(data_read)

    elif data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    else:
        print('Comando desconocido.')