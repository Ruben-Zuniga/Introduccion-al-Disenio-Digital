module dsp
#(
    // Placa
    parameter NB_SWITCH = 4,
    parameter NB_LED    = 4,
    parameter NB_RGB    = 3,
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
    output wire                         o_led           ,
    output wire [NB_BER    -1 : 0]      o_symb_count_i  , // Comentar al sintetizar
    output wire [NB_BER    -1 : 0]      o_symb_count_q  , // Comentar al sintetizar
    output wire [NB_BER    -1 : 0]      o_error_count_i , // Comentar al sintetizar
    output wire [NB_BER    -1 : 0]      o_error_count_q , // Comentar al sintetizar
    output wire [NB_LOG    -1 : 0]      o_data_log      , // Comentar al sintetizar
    output wire                         o_full_mem      , // Comentar al sintetizar
    input  wire                         clk             ,
    input  wire                         i_rst_n         ,
    input  wire [NB_SWITCH -1 : 0]      i_switch        ,
    input  wire                         i_run_log       , // Comentar al sintetizar
    input  wire                         i_read_log      , // Comentar al sintetizar
    input  wire [NB_SIZE   -1 : 0]      i_address         // Comentar al sintetizar
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
wire        [NB_BER-1  : 0] symb_count_i ;
wire        [NB_BER-1  : 0] symb_count_q ;
wire        [NB_BER-1  : 0] error_count_i;
wire        [NB_BER-1  : 0] error_count_q;
wire                           led_i        ;
wire                           led_q        ;
wire                           valid        ;
wire        [NB_COUNTER-1 : 0] count        ;

// Control: Contador
counter #(
    .OS        (OS        ),
    .NB_COUNTER(NB_COUNTER)
)
u_counter
(
    .o_valid(valid        ),
    .o_count(count        ),
    .clk    (clk          ),
    .i_rst_n(i_rst_n)
);

// Transmisor: PRBS + Filtro (Canal I)
tx #(
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
    .i_rst_n  (i_rst_n    ),
    .i_enable (i_switch[0]),
    .i_valid  (valid            ),
    .i_count  (count            )
);

// Receptor: Decimador + BER (Canal I)
rx #(
    .NB_PRBS    (NB_PRBS    ),
    .SEED_PRBS  (SEED_PRBS_I),
    .OS         (OS         ),
    .NB_COUNTER (NB_COUNTER ),
    .NB_DATA    (NB_DATA    ),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_BER     (NB_BER     )
)
u_rx_i
(
    .o_led        (led_i              ),
    .o_symb_count (symb_count_i       ),
    .o_error_count(error_count_i      ),
    .o_bits_rx    (bits_rx_i          ),
    .o_decimated  (decimated_i        ),
    .clk          (clk                ),
    .i_rst_n      (i_rst_n      ),
    .i_enable     (i_switch[1]  ),
    .i_valid      (valid              ),
    .i_phase      (i_switch[3:2]),
    .i_data       (data_i             )
);

// Transmisor: PRBS + Filtro (Canal Q)
tx #(
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
    .i_rst_n  (i_rst_n    ),
    .i_enable (i_switch[0]),
    .i_valid  (valid            ),
    .i_count  (count            )
);

// Receptor: Decimador + BER (Canal Q)
rx #(
    .NB_PRBS    (NB_PRBS    ),
    .SEED_PRBS  (SEED_PRBS_Q),
    .OS         (OS         ),
    .NB_COUNTER (NB_COUNTER ),
    .NB_DATA    (NB_DATA    ),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_BER     (NB_BER     )
)
u_rx_q
(
    .o_led        (led_q              ),
    .o_symb_count (symb_count_q       ),
    .o_error_count(error_count_q      ),
    .o_bits_rx    (bits_rx_q          ),
    .o_decimated  (decimated_q        ),
    .clk          (clk                ),
    .i_rst_n      (i_rst_n      ),
    .i_enable     (i_switch[1]  ),
    .i_valid      (valid              ),
    .i_phase      (i_switch[3:2]),
    .i_data       (data_q             )
);

// Memoria
mem_log #(
    .SIZE   (SIZE   ),
    .NB_SIZE(NB_SIZE),
    .NB_LOG (NB_LOG ),
    .NB_DATA(NB_DATA)
)
u_mem_log
(
    .clk        (clk          ),
    .i_rst_n    (i_rst_n),
    .i_data_tx_i(data_i       ),
    .i_data_tx_q(data_q       ),
    .i_run_log  (i_run_log    ),
    .i_read_log (i_read_log   ),
    .i_address  (i_address    ),
    .o_data_log (o_data_log   ),
    .o_full_mem (o_full_mem   )
);

assign o_led = led_i & led_q;
assign o_symb_count_i = symb_count_i;
assign o_symb_count_q = symb_count_q;
assign o_error_count_i = error_count_i;
assign o_error_count_q = error_count_q;
    
endmodule