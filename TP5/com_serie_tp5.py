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
sys.set_int_max_str_digits(10000)

## Armar trama
# cabecera = 10100001 = 161 = 0xA1
cabecera = 0xA1
# dispositivo: elijo el valor 254 = 0xfe
dispositivo = 0xFE
# fin_de_trama = 01000001 = 65 = 0x41
fin_de_trama = 0x41

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
            data_write = input("<< ")
            
            # Dato de 1 byte
            data_write_str = str(data_write)

            if data_write_str != 'back':
                # # Limpiar buffer
                # data_read = ser.read(ser.in_waiting)
                # Armar y enviar trama
                trama = [cabecera, dispositivo, data_write_str.encode(), fin_de_trama]
                print(trama)
                # for i in range(10):
                ser.write(cabecera)
                ser.write(dispositivo)
                ser.write(data_write_str.encode())
                ser.write(fin_de_trama)

                time.sleep(1)

    elif data_write_str == '1':
        print ("Wait Input Data")

        # # Limpiar buffer
        # data_read = ser.read(ser.in_waiting)
        
        # Armar y enviar trama
        data_write_str = '4'
        data_write = 4
        # trama = [cabecera, dispositivo, data_write_str.encode(), fin_de_trama]
        print(cabecera, dispositivo, data_write_str.encode(), fin_de_trama)
        # for i in range(10):
        ser.reset_input_buffer()
        # ser.write(cabecera)
        # ser.write(dispositivo)
        # ser.write(data_write_str.encode())
        # ser.write(fin_de_trama)
        # ser.write(struct.pack('BBBB', cabecera, dispositivo, data_write, fin_de_trama))
        ser.write(bytearray([cabecera, dispositivo, data_write, fin_de_trama]))

        # Esperar y mostrar respuesta del receptor
        time.sleep(1)
        while ser.in_waiting > 0:
            data_read = ser.read(4)
            # print(data_read)
            print(data_read[0], data_read[1], data_read[2], data_read[3])
            # if data_read[0] == 161 and data_read[1] == 239 and data_read[3] == 65:
            #     print (">>",data_read[2])
            #     break
            # time.sleep(0.5)

    elif data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    else:
        print('Comando desconocido.')