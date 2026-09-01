module top 
#(
    // Placa
    parameter NB_SWITCH = 4,
    parameter NB_LED    = 4,
    parameter NB_RGB    = 3,
    // GPIO
    parameter NB_DATA_RF = 23,
    parameter NB_COMMAND = 8 ,
    parameter NB_GPIO    = NB_DATA_RF + NB_COMMAND + 1, // 32
    // PRBS9
    parameter NB_PRBS     = 9     ,
    parameter SEED_PRBS_I = 9'h1AA,
    parameter SEED_PRBS_Q = 9'h1FE,
    // Filtro
    parameter OS         = 4         ,
    parameter NB_COUNTER = $clog2(OS), // 2
    parameter N_BAUD     = 6         ,
    parameter NB_DATA    = 8         ,
    parameter NBF_DATA   = 7         ,
    parameter NB_COEFF   = 8         ,
    parameter NBF_COEFF  = 7         ,
    // BER
    parameter SYNC_PHASES   = 512 ,
    parameter NB_BER        = 64  ,
    // Memoria
    parameter SIZE      = 1024          ,
    parameter NB_SIZE   = $clog2(SIZE)  , // 10
    parameter NB_LOG    = 32
)
(
    // output wire [NB_GPIO   -1 : 0]      o_gpio          , // Comentar al sintetizar
    // input  wire [NB_GPIO   -1 : 0]      i_gpio          , // Comentar al sintetizar
    output wire [NB_LED    -1 : 0]      o_led           ,
    output wire [NB_RGB    -1 : 0]      o_led_rgb_0     ,
    output wire [NB_RGB    -1 : 0]      o_led_rgb_1     ,
    output wire                         o_tx_uart       ,
    input  wire                         clk             ,
    input  wire                         i_rst_n         ,
    input  wire                         i_rx_uart       
);

// Module Connections
wire                            prbs_tx_i    ;
wire                            prbs_tx_q    ;
wire                            bits_rx_i    ;
wire                            bits_rx_q    ;
wire signed [NB_DATA    -1 : 0] data_i       ;
wire signed [NB_DATA    -1 : 0] data_q       ;
wire signed [NB_DATA    -1 : 0] decimated_i  ;
wire signed [NB_DATA    -1 : 0] decimated_q  ;
wire        [NB_BER     -1 : 0] symb_count_i ;
wire        [NB_BER     -1 : 0] symb_count_q ;
wire        [NB_BER     -1 : 0] error_count_i;
wire        [NB_BER     -1 : 0] error_count_q;
wire                            led_i        ;
wire                            led_q        ;
wire                            valid        ;
wire        [NB_COUNTER -1 : 0] count        ;
wire                            ber_0        ;
wire                            run_log      ;
wire                            read_log     ;
wire        [NB_SIZE    -1 : 0] address      ;
wire        [NB_LOG     -1 : 0] data_log     ;
wire                            full_mem     ;
wire                            rst_dsp_n    ;
wire        [NB_SWITCH  -1 : 0] switch       ;
wire        [NB_GPIO    -1 : 0] from_gpio    ;
wire        [NB_GPIO    -1 : 0] to_gpio      ;
wire                            clk_micro    ;
wire                            lock_clk     ;

// // VIO Connections
// wire                     connect_reset  ;
// wire [NB_SWITCH - 1 : 0] connect_switch ;
// wire [NB_SWITCH - 1 : 0] switch_from_VIO;
// wire                     reset_from_VIO ;
// wire                     select_VIO     ;

// // Reverse Reset
// assign connect_switch = (select_VIO) ? switch_from_VIO : i_switch;
// assign connect_reset  = (select_VIO) ? reset_from_VIO  : i_rst_n ;

// assign select_VIO = 1'b0;        // Comentar al sintetizar
// assign reset_from_VIO = 1'b0;    // Comentar al sintetizar
// assign switch_from_VIO = 4'b0;   // Comentar al sintetizar

// Modulo DSP
dsp #(
    .NB_SWITCH      (NB_SWITCH  ),
    .NB_LED         (NB_LED     ),
    .NB_RGB         (NB_RGB     ),
    .NB_PRBS        (NB_PRBS    ),
    .SEED_PRBS_I    (SEED_PRBS_I),
    .SEED_PRBS_Q    (SEED_PRBS_Q),
    .OS             (OS         ),
    .NB_COUNTER     (NB_COUNTER ),
    .N_BAUD         (N_BAUD     ),
    .NB_DATA        (NB_DATA    ),
    .NBF_DATA       (NBF_DATA   ),
    .NB_COEFF       (NB_COEFF   ),
    .NBF_COEFF      (NBF_COEFF  ),
    .SYNC_PHASES    (SYNC_PHASES),
    .NB_BER         (NB_BER     ),
    .SIZE           (SIZE       ),
    .NB_SIZE        (NB_SIZE    ),
    .NB_LOG         (NB_LOG     )
)
u_dsp (
    .clk            (clk_micro            ), // Descomentar al sintetizar
    // .clk            (clk            ), // Comentar al sintetizar
    .o_led          (ber_0          ),
    .o_symb_count_i (symb_count_i   ),
    .o_symb_count_q (symb_count_q   ),
    .o_error_count_i(error_count_i  ),
    .o_error_count_q(error_count_q  ),
    .o_data_log     (data_log       ),
    .o_full_mem     (full_mem       ),
    .i_rst_n        (rst_dsp_n      ),
    .i_switch       (switch       ),
    .i_run_log      (run_log        ),
    .i_read_log     (read_log       ),
    .i_address      (address        )
);

// Register File
reg_file #(
    .NB_SWITCH  (NB_SWITCH  ),
    .NB_DATA_RF (NB_DATA_RF ),
    .NB_COMMAND (NB_COMMAND ),
    .NB_GPIO    (NB_GPIO    ),
    .OS         (OS         ),
    .NB_COUNTER (NB_COUNTER ),
    .NB_BER     (NB_BER     ),
    .SIZE       (SIZE       ),
    .NB_SIZE    (NB_SIZE    ),
    .NB_LOG     (NB_LOG     )
)
u_reg_file (
    .o_gpio         (to_gpio      ), // Descomentar al sintetizar
    .i_gpio         (from_gpio    ), // Descomentar al sintetizar
    .clk            (clk_micro          ), // Descomentar al sintetizar
    // .o_gpio         (o_gpio      ), // Comentar al sintetizar
    // .i_gpio         (i_gpio    ), // Comentar al sintetizar
    // .clk            (clk          ), // Comentar al sintetizar
    .o_rst_dsp_n    (rst_dsp_n    ),
    .o_switch       (switch       ),
    .o_run_log      (run_log      ),
    .o_read_log     (read_log     ),
    .o_address      (address      ),
    .i_symb_count_i (symb_count_i ),
    .i_symb_count_q (symb_count_q ),
    .i_error_count_i(error_count_i),
    .i_error_count_q(error_count_q),
    .i_data_log     (data_log     ),
    .i_full_mem     (full_mem     ),
    .i_rst_n        (i_rst_n      )
);

micro_gpio #()                   // Descomentar al sintetizar
u_micro_gpio(
    .clk              (clk_micro),  // Clock aplicacion
    .gpio_rtl_tri_o   (from_gpio),  // GPIO
    .gpio_rtl_tri_i   (to_gpio  ),  // GPIO
    .reset            (i_rst_n  ),  // Hard Reset
    .sys_clock        (clk      ),  // Clock de FPGA
    .o_lock_clk       (lock_clk ),  // Senal Lock Clock
    .usb_uart_rxd     (i_rx_uart),  // UART
    .usb_uart_txd     (o_tx_uart)   // UART
);

// // VIO instance
// vio #()                                  // Descomentar al sintetizar
//     u_vio
//     (
//         .clk_0       (clk_micro            ),
//         .probe_in0_0 (o_led          ),
//         .probe_in1_0 (o_led_rgb_0    ),
//         .probe_in2_0 (o_led_rgb_1    ),
//         .probe_out0_0(select_VIO     ),
//         .probe_out1_0(reset_from_VIO ),
//         .probe_out2_0(switch_from_VIO),
//         .probe_out3_0(run_log        ),
//         .probe_out4_0(read_log       ),
//         .probe_out5_0(address        )
//     );

// // ILA Instance
// ila #()
//     u_ila
//     (
//         .clk_0   (clk_micro),
//         .probe0_0(full_mem),
//         .probe1_0(data_log[7:0]),
//         .probe2_0(data_log[23:16])
//     );

assign o_led[0] = ber_0;
assign o_led[1] = i_rst_n    ;
assign o_led[2] = switch[0];
assign o_led[3] = switch[1];

assign o_led_rgb_0[0] = full_mem;
assign o_led_rgb_0[1] = read_log;
assign o_led_rgb_0[2] = run_log;
assign o_led_rgb_1 = switch[3:2] + 1'b1;
    
endmodule