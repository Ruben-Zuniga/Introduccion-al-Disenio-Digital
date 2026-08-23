module top 
#(
    // Placa
    parameter NB_SWITCH = 4,
    parameter NB_LED    = 4,
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
    parameter SYNC_PHASES = 512,
    parameter NB_ERRORS   = 64
)
(
    output wire        [NB_LED-1    : 0] o_led    ,
    input  wire                          clk      ,
    input  wire                          i_rst_n  ,
    input  wire        [NB_SWITCH-1 : 0] i_switch
);

// Module Connections
wire                           prbs_tx_i    ;
wire                           prbs_tx_q    ;
wire                           bits_rx_i    ;
wire                           bits_rx_q    ;
wire signed [NB_DATA-1    : 0] data_i       ;
wire signed [NB_DATA-1    : 0] data_q       ;
wire signed [NB_DATA-1    : 0] decimated_i  ;
wire signed [NB_DATA-1    : 0] decimated_q  ;
wire        [NB_ERRORS-1  : 0] symb_count_i ;
wire        [NB_ERRORS-1  : 0] symb_count_q ;
wire        [NB_ERRORS-1  : 0] error_count_i;
wire        [NB_ERRORS-1  : 0] error_count_q;
wire                           led_i        ;
wire                           led_q        ;
wire                           valid        ;
wire        [NB_COUNTER-1 : 0] count        ;

// VIO Connections
wire                     connect_reset  ;
wire [NB_SWITCH - 1 : 0] connect_switch ;
wire [NB_SWITCH - 1 : 0] switch_from_VIO;
wire                     reset_from_VIO ;
wire                     select_VIO     ;

// Reverse Reset
assign connect_switch = (select_VIO) ? switch_from_VIO : i_switch;
assign connect_reset  = (select_VIO) ? reset_from_VIO  : i_rst_n ;

// Control: Contador
counter
#(
    .OS        (OS        ),
    .NB_COUNTER(NB_COUNTER)
)
u_counter
(
    .o_valid(valid        ),
    .o_count(count        ),
    .clk    (clk          ),
    .i_rst_n(connect_reset)
);

// Transmisor: PRBS + Filtro (Canal I)
tx
#(
    .NB_PRBS   (NB_PRBS    ),
    .SEED_PRBS (SEED_PRBS_I),
    .OS        (OS         ),
    .NB_COUNTER(NB_COUNTER ),
    .N_BAUD    (N_BAUD     ),
    .NB_DATA   (NB_DATA    ),
    .NBF_DATA  (NBF_DATA   ),
    .NB_COEFF  (NB_COEFF   ),
    .NBF_COEFF (NBF_COEFF  )
)
u_tx_i
(
    .o_prbs_tx(prbs_tx_i        ),
    .o_data   (data_i           ),
    .clk      (clk              ),
    .i_rst_n  (connect_reset    ),
    .i_enable (connect_switch[0]),
    .i_valid  (valid            ),
    .i_count  (count            )
);

// Receptor: Decimador + BER (Canal I)
rx
#(
    .NB_PRBS    (NB_PRBS    ),
    .SEED_PRBS  (SEED_PRBS_I),
    .OS         (OS         ),
    .NB_COUNTER (NB_COUNTER ),
    .NB_DATA    (NB_DATA    ),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_ERRORS  (NB_ERRORS  )
)
u_rx_i
(
    .o_led        (led_i              ),
    .o_symb_count (symb_count_i       ),
    .o_error_count(error_count_i      ),
    .o_bits_rx    (bits_rx_i          ),
    .o_decimated  (decimated_i        ),
    .clk          (clk                ),
    .i_rst_n      (connect_reset      ),
    .i_enable     (connect_switch[1]  ),
    .i_valid      (valid              ),
    .i_phase      (connect_switch[3:2]),
    .i_data       (data_i             )
);

// Transmisor: PRBS + Filtro (Canal Q)
tx
#(
    .NB_PRBS   (NB_PRBS    ),
    .SEED_PRBS (SEED_PRBS_Q),
    .OS        (OS         ),
    .NB_COUNTER(NB_COUNTER ),
    .N_BAUD    (N_BAUD     ),
    .NB_DATA   (NB_DATA    ),
    .NBF_DATA  (NBF_DATA   ),
    .NB_COEFF  (NB_COEFF   ),
    .NBF_COEFF (NBF_COEFF  )
)
u_tx_q
(
    .o_prbs_tx(prbs_tx_q        ),
    .o_data   (data_q           ),
    .clk      (clk              ),
    .i_rst_n  (connect_reset    ),
    .i_enable (connect_switch[0]),
    .i_valid  (valid            ),
    .i_count  (count            )
);

// Receptor: Decimador + BER (Canal Q)
rx
#(
    .NB_PRBS    (NB_PRBS    ),
    .SEED_PRBS  (SEED_PRBS_Q),
    .OS         (OS         ),
    .NB_COUNTER (NB_COUNTER ),
    .NB_DATA    (NB_DATA    ),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_ERRORS  (NB_ERRORS  )
)
u_rx_q
(
    .o_led        (led_q              ),
    .o_symb_count (symb_count_q       ),
    .o_error_count(error_count_q      ),
    .o_bits_rx    (bits_rx_q          ),
    .o_decimated  (decimated_q        ),
    .clk          (clk                ),
    .i_rst_n      (connect_reset      ),
    .i_enable     (connect_switch[1]  ),
    .i_valid      (valid              ),
    .i_phase      (connect_switch[3:2]),
    .i_data       (data_q             )
);

// VIO instance
vio
    u_vio
    (
        .clk_0       (clk            ),
        .probe_in0_0 (o_led          ),
        .probe_in1_0 (prbs_tx_i      ),
        .probe_in2_0 (bits_rx_i      ),
        .probe_out0_0(select_VIO     ),
        .probe_out1_0(reset_from_VIO ),
        .probe_out2_0(switch_from_VIO)
    );

// ILA Instance
ila
    u_ila
    (
        .clk_0   (clk      ),
        .probe0_0(decimated_i), // Se puede intercambiar por data_i
        .probe1_0(decimated_q), // Se puede intercambiar por data_q
        .probe2_0(led_i),
        .probe3_0(led_q)
    );
// ila
//     u_ila
//     (
//         .clk_0   (clk),
//         .probe0_0(o_led),
//         .probe1_0(error_count_i),
//         .probe2_0(symb_count_i)
//     );

assign o_led[0] = connect_reset    ;
assign o_led[1] = connect_switch[0];
assign o_led[2] = connect_switch[1];
assign o_led[3] = led_i & led_q    ;
    
endmodule