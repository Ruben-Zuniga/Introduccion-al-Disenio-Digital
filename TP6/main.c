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

// Tramas del UART
u8 frame_in[4] = {0};
u8 frame_out[4] = {0};

//Funcion para recibir 1 byte bloqueante
//XUartLite_RecvByte((&uart_module)->RegBaseAddress)

u32 get_gpio(u32 input)
{
    XGpio_DiscreteWrite(&GpioOutput, 1, input);
    XGpio_DiscreteWrite(&GpioOutput, 1, input | (u32)(1 << 23));
    XGpio_DiscreteWrite(&GpioOutput, 1, input);

    return XGpio_DiscreteRead(&GpioOutput, 1);
}

void send_frame(u32 input)
{
    frame_out[0] = (input >> 24) & 0x000000FF;
    frame_out[1] = (input >> 16) & 0x000000FF;
    frame_out[2] = (input >>  8) & 0x000000FF;
    frame_out[3] = (input >>  0) & 0x000000FF;

    XUartLite_Send(&uart_module, &frame_out[0], 4);
    while(XUartLite_IsSending(&uart_module)){}
}

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

        // Extraer BER - no se latchean los registros al mismo tiempo -> hay una diferencia de 207
        //  simbolos entre Q e I
        error_i_high = get_gpio(0x40000000);
        error_i_low = get_gpio(0x40000001);
        symb_i_high = get_gpio(0x40000002);
        symb_i_low = get_gpio(0x40000003);
        error_q_high = get_gpio(0x40000004);
        error_q_low = get_gpio(0x40000005);
        symb_q_high = get_gpio(0x40000006);
        symb_q_low = get_gpio(0x40000007);

        // Enviar todas las tramas
        send_frame(error_i_high);
        send_frame(error_i_low);
        send_frame(symb_i_high);
        send_frame(symb_i_low);
        send_frame(error_q_high);
        send_frame(error_q_low);
        send_frame(symb_q_high);
        send_frame(symb_q_low);

        
    }
	
	cleanup_platform();
	return 0;
}