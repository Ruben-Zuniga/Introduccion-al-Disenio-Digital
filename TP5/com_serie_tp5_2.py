import time
import serial
import sys

#############################################
# Nota:
# Comentar esta linea si se utiliza el puerto serie
# con la FPGA
#############################################
ser = serial.serial_for_url('loop://', timeout=1)

#############################################
# Nota:
# Descomentar esta linea si se utiliza el puerto serie
# con la FPGA
#############################################
# portUSB = sys.argv[1]
# ser = serial.Serial(
#     port='/dev/ttyUSB{}'.format(int(portUSB)),	#Configurar con el puerto
#     baudrate = 9600,
#     parity   = serial.PARITY_NONE,
#     stopbits = serial.STOPBITS_ONE,
#     bytesize = serial.EIGHTBITS
# )

ser.isOpen()
ser.timeout=None
ser.flushInput()
ser.flushOutput()
print(ser.timeout)

## Armar trama
# cabecera = 10100001 = 161
cabecera = chr(161)
# dispositivo: elijo el valor
dispositivo = chr(233)
# fin_de_trama = 01000001 = 65
fin_de_trama = chr(65)

# Mensaje de inicio
print ('--- Comunicación con FPGA:',ser.port,' ---\r\n')

# Bucle de envio y recepcion
while 1 :
    char_v = []

    # Mensaje a enviar
    print('Indique controlar LED o switches [l/s] o escriba "exit" para salir.')
    data_write = input("<< ")
    data_write_str = str(data_write)

    if data_write_str == 'l':
        print('Indique LED a controlar [0/1/2/3]')
        data_write = input("<< ")
        
        # Dato de 1 byte
        data_write_str = str(data_write)
        # Armar y enviar trama
        trama = cabecera + dispositivo + data_write_str[0] + fin_de_trama
        ser.write(trama.encode())
        time.sleep(1)

    elif data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    elif data_write_str == 's':
        # Enviar dato
        print ("Wait Input Data")
        trama = cabecera + dispositivo + data_write_str + fin_de_trama
        ser.write(trama.encode())

        # Esperar y mostrar respuesta del receptor
        time.sleep(2)
        data_read = ser.read(1)
        data_read_str = str(int.from_bytes(data_read,byteorder='big'))
        print(ser.inWaiting())
        if data_read_str != '':
            print (">>" + data_read_str)

    else:
        # Data de 1 byte
        # cabecera = 10100001 = 161
        cabecera = chr(161)
        # dispositivo: elijo el valor
        dispositivo = chr(233)
        # fin_de_trama = 01000001 = 65
        fin_de_trama = chr(65)

        trama = cabecera + dispositivo + data_write_str[0] + fin_de_trama
        print(trama)
        ser.write(trama.encode())
        time.sleep(1)

    # else:
    #     # Armar el vector a transmitir
    #     for ptr in range(len(data_write_str)):
    #         char_v.append(data_write_str[ptr])
    #     print(char_v)
        
    #     for ptr in range(len(char_v)):
    #         ser.write(char_v[ptr].encode())

    #     # Caracter de seguridad al final
    #     ser.write('$'.encode())
        
    #     # Esperar y mostrar respuesta del receptor
    #     time.sleep(1)
    #     data_read_str = ''
    #     while ser.in_waiting > 0:
    #         data_read_str += ser.read(1).decode()

    #     if data_read_str != '':
    #         print(">> " + data_read_str)
