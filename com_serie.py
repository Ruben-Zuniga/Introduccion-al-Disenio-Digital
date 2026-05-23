import time
import serial

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
ser = serial.Serial(
    # port     = '/dev/ttyUSB1', #COM3
    port     = '/dev/pts/3', #Filtro. CAMBIAR segun el puerto que se abra
    baudrate = 9600,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS
)

ser.isOpen()
ser.timeout=None
ser.flushInput()
ser.flushOutput()

# Mensaje de inicio
print('Ingrese parametros en formato "[alfa],[span],[sps],[rrc]".')
print('rrc=1 para RRC, rrc=0 para RC:')

# Bucle de envio y recepcion
while 1 :
    char_v = []

    # Mensaje a enviar
    data = input("ToSent: ")
    if data == 'exit':
        if ser.isOpen():
            ser.close()
        break
    else:
        # Armar el vector a transmitir
        for ptr in range(len(data)):
            char_v.append(data[ptr])
        print(char_v)
        
        for ptr in range(len(char_v)):
            ser.write(char_v[ptr].encode())

        # Caracter de seguridad al final
        ser.write('$'.encode())
        
        # Esperar y mostrar respuesta del receptor
        time.sleep(1)
        out = ''
        while ser.in_waiting > 0:
            out += ser.read(1).decode()

        if out != '':
            print(">> " + out)
