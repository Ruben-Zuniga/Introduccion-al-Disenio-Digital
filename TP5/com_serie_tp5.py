import time
import serial
import sys

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
    baudrate = 9600,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS
)

ser.isOpen()
ser.timeout=None
ser.flushInput()
ser.flushOutput()
print(ser.timeout)

# Mensaje de inicio
print ('Ingrese un comando:[0,1,2,3]\r\n')

# Bucle de envio y recepcion
while 1 :
    char_v = []

    # Mensaje a enviar
    data_write = input("<< ")
    data_write_str = str(data_write)

    if data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    elif data_write_str == '3':
        # Enviar dato
        print ("Wait Input Data")
        ser.write(data_write_str.encode())

        # Esperar y mostrar respuesta del receptor
        time.sleep(2)
        data_read = ser.read(1)
        data_read_str = str(int.from_bytes(data_read,byteorder='big'))
        print(ser.inWaiting())
        if data_read_str != '':
            print (">>" + data_read_str)

    else:
        ser.write(data_write_str.encode())
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
