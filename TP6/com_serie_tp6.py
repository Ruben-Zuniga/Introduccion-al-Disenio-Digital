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
    print('Envíe algo.')
    data_write = input("<< ")
    data_write_str = str(data_write)

    if data_write_str == 'exit':
        if ser.isOpen():
            ser.close()
        break

    print ("Esperando respuesta...")
        
    # Armar y enviar trama
    data_write = int(data_write)
    data_write_byte = data_write.to_bytes(1, 'big')

    # Reiniciar buffer de recepcion
    ser.reset_input_buffer()
    # Enviar dato
    ser.write(cabecera + dispositivo + data_write_byte + fin_de_trama)
    print(cabecera + dispositivo + data_write_byte + fin_de_trama)
    # Esperar y mostrar respuesta del receptor
    time.sleep(2)

    print('Esperando:', ser.inWaiting())

    while ser.in_waiting > 0:
        data_read = ser.read(4)
        # Convertir a entero e imprimir dato recibido
        data_read_int = int.from_bytes(data_read,byteorder='big')
        print (">>",data_read, data_read_int)