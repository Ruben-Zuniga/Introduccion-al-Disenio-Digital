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
// BER
u32 error_i_high = 0;
u32 error_i_low = 0;
u32 symb_i_high = 0;
u32 symb_i_low = 0;
u32 error_q_high = 0;
u32 error_q_low = 0;
u32 symb_q_high = 0;
u32 symb_q_low = 0;
// Contador de bytes recibidos
u32 recv_count = 0;
// Auxiliar
u8 state;
// Estados del TX y RX
u32 tx_state = 0;
u32 rx_state = 0;
u32 phase = 0;

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

	while(1){
        // Entrar en bucle hasta leer 4 bytes (el UART a veces recibe con delay)
        while(recv_count != 4){
            recv_count += XUartLite_Recv(&uart_module,
                                         &frame_in[0] + recv_count,
                                         4 - recv_count);
        }
        recv_count = 0;
        state = 0;

        // Comparar cabecera, dispositivo y fin de trama
        if(frame_in[0] == 0xA1 && frame_in[1] == 0xFE && frame_in[3] == 0x41){

            if(frame_in[2] == 1){
                // Levantar y bajar reset
                write_gpio(1 << 24);
                write_gpio(0);
                // Enviar estado ok
                state = 1;
                XUartLite_Send(&uart_module, &state, 1);
                while(XUartLite_IsSending(&uart_module)){}
            }
            else if(frame_in[2] == 2){
                // Togglear TX
                tx_state = (tx_state == (1 << 26)) ? 0 : 1 << 26;
                write_gpio(rx_state | tx_state | (1 << 25) | phase);
                // Enviar estado del TX
                state = (u8)(tx_state >> 26);
                XUartLite_Send(&uart_module, &(state), 1);
                while(XUartLite_IsSending(&uart_module)){}
            }
            else if(frame_in[2] / 10 == 3){
                // Togglear RX junto con la fase
                rx_state = (rx_state == (1 << 27)) ? 0 : 1 << 27;
                phase = (u32)(frame_in[2] % 30);
                write_gpio(rx_state | tx_state | (1 << 25) | phase);
                // Enviar estado del RX
                state = (u8)(rx_state >> 27);
                XUartLite_Send(&uart_module, &state, 1);
                while(XUartLite_IsSending(&uart_module)){}
            }
            else if(frame_in[2] == 4){
                // Extraer BER - no se latchean los registros al mismo tiempo -> hay una diferencia de 207
                //  simbolos entre Q e I
                error_i_high = write_and_read_gpio((1 << 30) | 0);
                error_i_low  = write_and_read_gpio((1 << 30) | 1);
                symb_i_high  = write_and_read_gpio((1 << 30) | 2);
                symb_i_low   = write_and_read_gpio((1 << 30) | 3);
                error_q_high = write_and_read_gpio((1 << 30) | 4);
                error_q_low  = write_and_read_gpio((1 << 30) | 5);
                symb_q_high  = write_and_read_gpio((1 << 30) | 6);
                symb_q_low   = write_and_read_gpio((1 << 30) | 7);

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
            else if(frame_in[2] == 5){
                // Comenzar logueo
                write_gpio(1 << 28);

                while ((write_and_read_gpio((u32)(1 << 29)) & (1 << 31)) != (u32)(1 << 31)) {}
                // Guardar datos
                for (u32 i = 0; i < LOG_SIZE; i = i + 1) {
                    log_mem_temp = write_and_read_gpio((1 << 29) | i);
                    log_mem_i[i] = log_mem_temp & 0x000000FF;
                    log_mem_q[i] = (log_mem_temp >> 16) & 0x000000FF;
                }
                // Enviar datos
                for (u32 i = 0; i < LOG_SIZE; i = i + 1) {
                    frame_out_log[i] = log_mem_i[i];
                    // frame_out_log[i] = i;
                }
                for (u32 i = 0; i < LOG_SIZE; i = i + 1) {
                    frame_out_log[i + LOG_SIZE] = log_mem_q[i];
                    // frame_out_log[i + LOG_SIZE] = i;
                }
                for (u32 i = 0; i < 2 * LOG_SIZE; i = i + 16) {
                    XUartLite_Send(&uart_module, &frame_out_log[i], 32);
                    while(XUartLite_IsSending(&uart_module)){}
                }
            }
        }


        // // Loopback
        // for (int i = 0; i < 4; i++) {
        //     frame_out_ber[i] = frame_in[i];
        // }
        // XUartLite_Send(&uart_module, &frame_out_ber[0], 4);
        // while(XUartLite_IsSending(&uart_module)){}

    }
	
	cleanup_platform();
	return 0;
}