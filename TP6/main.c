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

// Memoria del log del DSP
#define LOG_SIZE 1024

XGpio GpioOutput;
XGpio GpioParameter;
XGpio GpioInput;
u32 GPO_Value;
u32 GPO_Param;
XUartLite uart_module;

// Tramas del UART
u8 frame_in[4] = {0};
u8 frame_out_ber[4] = {0};
u8 frame_out_log[2 * LOG_SIZE] = {0};

// Log del DSP
u32 log_mem_temp = 0;
u8 log_mem_i[LOG_SIZE] = {0};
u8 log_mem_q[LOG_SIZE] = {0};

//Funcion para recibir 1 byte bloqueante
//XUartLite_RecvByte((&uart_module)->RegBaseAddress)

u32 write_and_read_gpio(u32 input)
{
    XGpio_DiscreteWrite(&GpioOutput, 1, input);
    XGpio_DiscreteWrite(&GpioOutput, 1, input | (u32)(1 << 23));
    XGpio_DiscreteWrite(&GpioOutput, 1, input);

    return XGpio_DiscreteRead(&GpioOutput, 1);
}

u32 write_gpio(u32 input)
{
    XGpio_DiscreteWrite(&GpioOutput, 1, input);
    XGpio_DiscreteWrite(&GpioOutput, 1, input | (u32)(1 << 23));
    XGpio_DiscreteWrite(&GpioOutput, 1, input);
}

void send_frame_ber(u32 input)
{
    frame_out_ber[0] = (input >> 24) & 0x000000FF;
    frame_out_ber[1] = (input >> 16) & 0x000000FF;
    frame_out_ber[2] = (input >>  8) & 0x000000FF;
    frame_out_ber[3] = (input >>  0) & 0x000000FF;

    XUartLite_Send(&uart_module, &frame_out_ber[0], 4);
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
    XGpio_DiscreteWrite(&GpioOutput, 1, 0x0E000002);
    XGpio_DiscreteWrite(&GpioOutput, 1, 0x0E800002);
    XGpio_DiscreteWrite(&GpioOutput, 1, 0x0E000002);

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

        // Comparar cabecera, dispositivo y fin de trama
        if(frame_in[0] == 0xA1 && frame_in[1] == 0xFE && frame_in[3] == 0x41){
            
            if(frame_in[2] == 1){

                // Extraer BER - no se latchean los registros al mismo tiempo -> hay una diferencia de 207
                //  simbolos entre Q e I
                error_i_high = write_and_read_gpio(0x40000000);
                error_i_low  = write_and_read_gpio(0x40000001);
                symb_i_high  = write_and_read_gpio(0x40000002);
                symb_i_low   = write_and_read_gpio(0x40000003);
                error_q_high = write_and_read_gpio(0x40000004);
                error_q_low  = write_and_read_gpio(0x40000005);
                symb_q_high  = write_and_read_gpio(0x40000006);
                symb_q_low   = write_and_read_gpio(0x40000007);

                // Enviar todas las tramas
                send_frame_ber(error_i_high);
                send_frame_ber(error_i_low );
                send_frame_ber(symb_i_high );
                send_frame_ber(symb_i_low  );
                send_frame_ber(error_q_high);
                send_frame_ber(error_q_low );
                send_frame_ber(symb_q_high );
                send_frame_ber(symb_q_low  );
            }
            else if (frame_in[2] == 2){

                // Comenzar logueo
                write_gpio(0x10000000);
                // Esperar si el MSB de la respuesta (bit de memoria llena) esta en 0
                while (!(write_and_read_gpio(0x20000000) & 0x80000000)) {}
                // Guardar datos
                for (u32 i = 0; i < LOG_SIZE; i = i + 1) {
                    log_mem_temp = write_and_read_gpio(0x20000000 | i);
                    log_mem_i[i] = log_mem_temp & 0x000000FF;
                    log_mem_q[i] = (log_mem_temp >> 16) & 0x000000FF;
                }
                // Enviar datos
                for (u32 i = 0; i < LOG_SIZE; i = i + 1) {
                    frame_out_log[i] = log_mem_i[i];
                }
                for (u32 i = 0; i < LOG_SIZE; i = i + 1) {
                    frame_out_log[i + LOG_SIZE] = log_mem_q[i];
                }
                for (u32 i = 0; i < 2*LOG_SIZE / 32; i = i + 1) {
                    XUartLite_Send(&uart_module, &frame_out_log[i], 32);
                    while(XUartLite_IsSending(&uart_module)){}
                    // Tiempo de espera para no sobrecargar el buffer
                    for (u32 j = 0; j < 20000; j = j + 1) {}
                }
            }
        }


        // // Loopback
        // for (int i = 0; i < 4; i++) {
        //     frame_out[i] = frame_in[i];
        // }
        // XUartLite_Send(&uart_module, &frame_out[0], 4);
        // while(XUartLite_IsSending(&uart_module)){}

    }
	
	cleanup_platform();
	return 0;
}