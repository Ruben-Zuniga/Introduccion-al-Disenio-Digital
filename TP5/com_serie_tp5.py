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
cabecera = b'\xA1'
# dispositivo: elijo el valor 254 = 0xfe
dispositivo = b'\xFE'
# fin_de_trama = 01000001 = 65 = 0x41
fin_de_trama = b'\x41'

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
                # Armar y enviar trama
                trama = [cabecera, dispositivo, data_write_str.encode(), fin_de_trama]
                print(trama)
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
        trama = [cabecera, dispositivo, data_write_str.encode(), fin_de_trama]
        print(trama)
        ser.write(cabecera)
        ser.write(dispositivo)
        ser.write(data_write_str.encode())
        ser.write(fin_de_trama)

        # Esperar y mostrar respuesta del receptor
        time.sleep(2)
        while ser.in_waiting > 0:
            data_read = ser.read(1)
            data_read_str = str(int.from_bytes(data_read,byteorder='big'))
            print(ser.inWaiting())
            if data_read_str != '':
                print (">>",data_read_str,"|",data_read)

    elif data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    else:
        print('Comando desconocido.')