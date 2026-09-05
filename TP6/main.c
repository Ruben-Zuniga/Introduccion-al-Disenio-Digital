#include <stdio.h>
#include <string.h>
#include <sys/_intsup.h>
#include "xparameters.h"
#include "xil_cache.h"
#include "xgpio.h"
#include "platform.h"
#include "xuartlite.h"

#define PORT_IN	 		XPAR_AXI_GPIO_0_BASEADDR
#define PORT_OUT 		XPAR_AXI_GPIO_0_BASEADDR

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
    
    // Prender transceptor
    XGpio_DiscreteWrite(&GpioOutput, 1, 0x0E000000);
    XGpio_DiscreteWrite(&GpioOutput, 1, 0x0E800000);
    XGpio_DiscreteWrite(&GpioOutput, 1, 0x0E000000);

    u32 error_i_high = 0;
    u32 error_i_low = 0;
    u32 symb_i_high = 0;
    u32 symb_i_low = 0;
    u32 error_q_high = 0;
    u32 error_q_low = 0;
    u32 symb_q_high = 0;
    u32 symb_q_low = 0;

    u32 recv_count = 0;
    u8 frame_in[4] = {0};
    u8 frame_out[4] = {0};
    u8 i = 0;
	while(1){
        // Entrar en bucle hasta leer 4 bytes (el UART a veces recibe con delay)
        while(recv_count != 4){
            recv_count += XUartLite_Recv(&uart_module,
                                         &frame_in[0] + recv_count,
                                         4 - recv_count);
        }
        recv_count = 0;

        // // Loopback
        // for (int i = 0; i < 4; i++) {
        //     frame_out[i] = frame_in[i];
        // }
        // XUartLite_Send(&uart_module, &frame_out[0], 4);
        // while(XUartLite_IsSending(&uart_module)){}

        XGpio_DiscreteWrite(&GpioOutput, 1, 0x40000000);
        XGpio_DiscreteWrite(&GpioOutput, 1, 0x40800000);
        XGpio_DiscreteWrite(&GpioOutput, 1, 0x40000000);
        error_i_high = XGpio_DiscreteRead(&GpioOutput, 1);

        XGpio_DiscreteWrite(&GpioOutput, 1, 0x40000001);
        XGpio_DiscreteWrite(&GpioOutput, 1, 0x40800001);
        XGpio_DiscreteWrite(&GpioOutput, 1, 0x40000001);
        error_i_low = XGpio_DiscreteRead(&GpioOutput, 1);

        frame_out[0] = (error_i_high >> 24) & 0x000000FF;
        frame_out[1] = (error_i_high >> 16) & 0x000000FF;
        frame_out[2] = (error_i_high >>  8) & 0x000000FF;
        frame_out[3] = (error_i_high >>  0) & 0x000000FF;
        XUartLite_Send(&uart_module, &frame_out[0], 4);
        while(XUartLite_IsSending(&uart_module)){}

        frame_out[0] = (error_i_low >> 24) & 0x000000FF;
        frame_out[1] = (error_i_low >> 16) & 0x000000FF;
        frame_out[2] = (error_i_low >>  8) & 0x000000FF;
        frame_out[3] = (error_i_low >>  0) & 0x000000FF;
        XUartLite_Send(&uart_module, &frame_out[0], 4);
        while(XUartLite_IsSending(&uart_module)){}
    }
	
	cleanup_platform();
	return 0;
}