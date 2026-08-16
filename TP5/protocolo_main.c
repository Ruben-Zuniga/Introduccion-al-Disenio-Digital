
#include <stdio.h>
#include <string.h>
#include <sys/_intsup.h>
#include "xparameters.h"
#include "xil_cache.h"
#include "xgpio.h"
#include "platform.h"
#include "xuartlite.h"
//#include "microblaze_sleep.h"

// Fijarse: cada nueva version cambia de nombre los xparameters
// Los dos puertos tienen la misma direccion porque es bidireccional (por control)
#define PORT_IN	 		XPAR_AXI_GPIO_0_BASEADDR //XPAR_AXI_GPIO_0_DEVICE_ID //XPAR_GPIO_0_DEVICE_ID
#define PORT_OUT 		XPAR_AXI_GPIO_0_BASEADDR //XPAR_AXI_GPIO_0_DEVICE_ID //XPAR_GPIO_0_DEVICE_ID

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
	Status = XUartLite_Initialize(&uart_module, 0);
	if(Status!=XST_SUCCESS){
        return XST_FAILURE;
    }

	GPO_Value=0x00000000;
	GPO_Param=0x00000000;
    unsigned int N_bytes = 4;
	unsigned char trama[N_bytes];

	Status=XGpio_Initialize(&GpioInput, PORT_IN);
	if(Status!=XST_SUCCESS){
        return XST_FAILURE;
    }
	Status=XGpio_Initialize(&GpioOutput, PORT_OUT);
	if(Status!=XST_SUCCESS){
		return XST_FAILURE;
	}

    // --Setear puerto de entrada y de salida--
    // Todos de salida
	XGpio_SetDataDirection(&GpioOutput, 1, 0x00000000);
    // Todos de entrada
	XGpio_SetDataDirection(&GpioInput, 1, 0xFFFFFFFF);

    // Datos de la trama
    unsigned char cabecera = (unsigned char)161; // 0xA1
    unsigned char dispositivo = (unsigned char)239; // 0xEF
    unsigned char fin_de_trama = (unsigned char)65; // 0x41

	u32 value;
    unsigned char datos[N_bytes];
    datos[0] = cabecera;
    datos[1] = dispositivo;
    datos[3] = fin_de_trama;

	while(1){
    
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// ACA es donde se escribe toda la funcionalidad
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        // Sobreescribir el primer byte de la trama 'trama' por el byte recibido
        XUartLite_Recv(&uart_module, &trama[0],  1);
        if(trama[0] == (unsigned char)161){
            XUartLite_Recv(&uart_module, &trama[1],  1);
            if(trama[1] == (unsigned char)254){
                XUartLite_Recv(&uart_module, &trama[2],  1);

                // Resetear el buffer del UART                
                // XUartLite_ResetFifos(&uart_module);

                switch(trama[2]){
                case '0':
                    XGpio_DiscreteWrite(&GpioOutput,1, (u32) 0x00000249);
                    break;
                case '1':
                    XGpio_DiscreteWrite(&GpioOutput,1, (u32) 0x00000492);
                    break;
                case '2':
                    XGpio_DiscreteWrite(&GpioOutput,1, (u32) 0x00000924);
                    break;
                case '3':
                    XGpio_DiscreteWrite(&GpioOutput,1, (u32) 0x00000000);
                    break;
                case '4':
                    // Leer los 4 switches
                    value = XGpio_DiscreteRead(&GpioInput, 1);
                    datos[2]=(char)(value & (0x0000000F));
                    // Esperar que deje de transmitir
                    while(XUartLite_IsSending(&uart_module)){}
                    // Enviar por UART el valor leido
                    XUartLite_Send(&uart_module, &datos[0],N_bytes);
                    break;
                }
            }
        }

        // Loopback
        // XUartLite_Recv(&uart_module, &trama[0],  1);
        // XUartLite_Recv(&uart_module, &trama[1],  1);
        // XUartLite_Recv(&uart_module, &trama[2],  1);
        // XUartLite_Recv(&uart_module, &trama[3],  1);
        XUartLite_Recv(&uart_module, &trama[0],  N_bytes);

        if(trama[0] == (unsigned char)161 || trama[1] == (unsigned char)254 || trama[3] == (unsigned char)65){
            datos[0] = trama[0];
            datos[1] = trama[1];
            datos[2] = trama[2];
            datos[3] = trama[3];

            // Esperar que deje de transmitir
            while(XUartLite_IsSending(&uart_module)){}
            // Enviar por UART el valor leido
            // XUartLite_Send(&uart_module, &datos[0],1);
            // XUartLite_Send(&uart_module, &datos[1],1);
            // XUartLite_Send(&uart_module, &datos[2],1);
            // XUartLite_Send(&uart_module, &datos[3],1);
            XUartLite_Send(&uart_module, &datos[0],N_bytes);
        }

        // if (trama[0] == '4') {
        //     datos = (char)trama[0];
            
        //     unsigned char cabecera = (unsigned char)161; // 0xA1
        //     unsigned char dispositivo = (unsigned char)239; // 0xEF
        //     unsigned char fin_de_trama = (unsigned char)65; // 0x41
        //     XGpio_DiscreteWrite(&GpioOutput,1, (u32) 0x00000249);
        //     XUartLite_Send(&uart_module, &cabecera,1);
        //     XUartLite_Send(&uart_module, &dispositivo,1);
        //     XUartLite_Send(&uart_module, &datos,1);
        //     XUartLite_Send(&uart_module, &fin_de_trama,1);
        // }
        
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// FIN de toda la funcionalidad
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    }
	
	cleanup_platform();
	return 0;
}
