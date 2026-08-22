
#include <stdio.h>
#include <string.h>
#include <sys/_intsup.h>
#include "xparameters.h"
#include "xil_cache.h"
#include "xgpio.h"
#include "platform.h"
#include "xuartlite.h"

#define PORT_IN	 		XPAR_AXI_GPIO_0_BASEADDR //XPAR_GPIO_0_DEVICE_ID
#define PORT_OUT 		XPAR_AXI_GPIO_0_BASEADDR //XPAR_GPIO_0_DEVICE_ID

//Device_ID Operaciones
#define def_SOFT_RST            0
#define def_ENABLE_MODULES      1
#define def_LOG_RUN             2
#define def_LOG_READ            3

XGpio GpioOutput;
XGpio GpioParameter;
XGpio GpioInput;
u32 GPO_Value;
u32 GPO_Param;
XUartLite uart_module;

//Funcion para recibir 1 byte bloqueante
//XUartLite_RecvByte((&uart_module)->RegBaseAddress)

int main()
{
    init_platform();
    int Status;
    XUartLite_Initialize(&uart_module, 0);

    GPO_Value=0x00000000;
    GPO_Param=0x00000000;

    Status=XGpio_Initialize(&GpioInput, PORT_IN);
    if(Status!=XST_SUCCESS){
        return XST_FAILURE;
    }
    Status=XGpio_Initialize(&GpioOutput, PORT_OUT);
    if(Status!=XST_SUCCESS){
        return XST_FAILURE;
    }
    XGpio_SetDataDirection(&GpioOutput, 1, 0x00000000);
    XGpio_SetDataDirection(&GpioInput, 1, 0xFFFFFFFF);

    u32 value;
    u32 recv_count = 0;

    u8 trama[4] = {0};
    u8 datos[4];
    u8 led;
    u8 color;
    u8 cabecera = 0xA1;
    u8 dispositivo = 0xEF;
    u8 fin_de_trama = 0x41;

    datos[0] = cabecera;
    datos[1] = dispositivo;
    datos[3] = fin_de_trama;

	while(1){
        // Entrar en bucle hasta leer 4 bytes (el UART a veces recibe con delay)
        while(recv_count != 4){
            recv_count += XUartLite_Recv(&uart_module,
                                         &trama[0] + recv_count,
                                         4 - recv_count);
        }
        recv_count = 0;

        // Comparar cabecera, dispositivo y fin de trama
        if(trama[0] == 0xA1 && trama[1] == 0xFE && trama[3] == 0x41){
            if(trama[2] == 32){
                // Leer switches
                value = XGpio_DiscreteRead(&GpioInput, 1);
                datos[2] = (char)(value & 0x0000000F);

                XUartLite_Send(&uart_module, &datos[0],4);
                while(XUartLite_IsSending(&uart_module)){}
            }
            else{
                // Cambiar LED
                led = trama[2] >> 3;
                color = trama[2] & 0x07;
                XGpio_DiscreteWrite(&GpioOutput,1, (u32)color << (led * 3));
            }
        }


//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// FIN de toda la funcionalidad
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    }
	
	cleanup_platform();
	return 0;
}