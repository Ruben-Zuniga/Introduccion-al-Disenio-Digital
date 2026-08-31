// BER I = 0,25048
// BER Q = 0,25050

`timescale 1ns/100ps

module tb_top ();

// Placa
parameter NB_SWITCH = 4;
parameter NB_LED    = 4;
parameter NB_RGB    = 3;
// PRBS9
parameter NB_PRBS     = 9     ;
parameter SEED_PRBS_I = 9'h1AA;
parameter SEED_PRBS_Q = 9'h1FE;
// Filtro
parameter OS         = 4         ;
parameter NB_COUNTER = $clog2(OS); // 2
parameter N_BAUD     = 6         ;
parameter NB_DATA    = 8         ;
parameter NBF_DATA   = 7         ;
parameter NB_COEFF   = 8         ;
parameter NBF_COEFF  = 7         ;
// BER
parameter SYNC_PHASES = 16;
parameter NB_BER      = 64;
// Memoria
parameter SIZE      = 1024        ;
parameter NB_SIZE   = $clog2(SIZE); // 10
parameter NB_LOG    = 32          ;

wire                           prbs_tx        ;
wire                           bits_rx        ;
wire signed [NB_DATA   -1 : 0] data           ;
wire        [NB_LED    -1 : 0] o_led          ;
wire        [NB_RGB    -1 : 0] o_led_rgb_0    ;
wire        [NB_RGB    -1 : 0] o_led_rgb_1    ;
wire        [NB_BER    -1 : 0] o_symb_count_i ;
wire        [NB_BER    -1 : 0] o_symb_count_q ;
wire        [NB_BER    -1 : 0] o_error_count_i;
wire        [NB_BER    -1 : 0] o_error_count_q;
wire        [NB_LOG    -1 : 0] o_data_log     ;
wire                           o_full_mem     ;
reg                            clk            ;
reg                            i_rst_n        ;
reg         [NB_SWITCH -1 : 0] i_switch       ;
reg                            i_run_log      ;
reg                            i_read_log     ;
reg         [NB_SIZE   -1 : 0] i_address      ;

wire        [NB_DATA   -1 : 0] data_log_8bit  ;
assign data_log_8bit = o_data_log[7:0];

// Vector Matching
integer vm_data_errors;
integer vm_prbs_tx_errors;
integer vm_bits_rx_errors;
integer i;
localparam N_LOG = 40000;
reg [NB_DATA-1 : 0] data_log [N_LOG-1 : 0];
reg [NB_DATA-1 : 0] prbs_tx_log [N_LOG/OS - 1 : 0];
reg [NB_DATA-1 : 0] bits_rx_log [N_LOG/OS - 1 : 0];

// Reloj 100 MHz
always #5 clk = ~clk;

// Señales internas
assign prbs_tx = dut.prbs_tx_i;
assign bits_rx = dut.bits_rx_i;
assign data = dut.data_i;

initial begin
    clk = 1'b0;
    i_rst_n = 1'b0;
    i_switch = {NB_SWITCH{1'b0}};
    i_run_log = 1'b0;
    i_read_log = 1'b0;
    i_address = 'd0;

    vm_data_errors = 0;
    vm_prbs_tx_errors = 0;
    vm_bits_rx_errors = 0;
    $readmemh("out_tx_log.mem", data_log);
    $readmemh("symb_tx_log.mem", prbs_tx_log);
    $readmemh("symb_rx_log.mem", bits_rx_log);

    #1000;
    @(posedge clk);
    i_rst_n = 1'b1;

    // -- Simulacion corta (SYNC_PHASES = 16) --
    // `include "tb_include/tb_sync_16.v"

    // -- Simulacion larga para probar el correlador de 1024 (SYNC_PHASES = 1024) --
    // `include "tb_include/tb_sync_1024.v"
    
    #10000;
    @(posedge clk);
    i_rst_n = 1'b0;
    
    // -- Contar BER --

    // #10000;
    // @(posedge clk);
    // i_rst_n = 1'b1;
    // i_switch = 4'b0011;

    // repeat(511*SYNC_PHASES*OS + 40000 + 200000)
    //     @(posedge clk);

    // -- Probar memoria --
    `include "tb_include/tb_mem.v"

    #10000;
    $display("---------------------------------------");
    $display("Errores en los bits del TX:  %d" , vm_prbs_tx_errors);
    $display("Errores en la salida del TX: %d" , vm_data_errors   );
    $display("Errores en los bits del RX:  %d" , vm_bits_rx_errors);
    $finish;
end

top
#(
    .NB_SWITCH  (NB_SWITCH  ),
    .NB_LED     (NB_LED     ),
    .NB_PRBS    (NB_PRBS    ),
    .SEED_PRBS_I(SEED_PRBS_I),
    .SEED_PRBS_Q(SEED_PRBS_Q),
    .OS         (OS         ),
    .NB_COUNTER (NB_COUNTER ),
    .N_BAUD     (N_BAUD     ),
    .NB_DATA    (NB_DATA    ),
    .NBF_DATA   (NBF_DATA   ),
    .NB_COEFF   (NB_COEFF   ),
    .NBF_COEFF  (NBF_COEFF  ),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_BER     (NB_BER     )
)
dut
(
    .o_led          (o_led          ),
    .o_led_rgb_0    (o_led_rgb_0    ),
    .o_led_rgb_1    (o_led_rgb_1    ),
    .o_symb_count_i (o_symb_count_i ),
    .o_symb_count_q (o_symb_count_q ),
    .o_error_count_i(o_error_count_i),
    .o_error_count_q(o_error_count_q),
    .o_data_log     (o_data_log     ),
    .o_full_mem     (o_full_mem     ),
    .clk            (clk            ),
    .i_rst_n        (i_rst_n        ),
    .i_switch       (i_switch       ),
    .i_run_log      (i_run_log      ),
    .i_read_log     (i_read_log     ),
    .i_address      (i_address      )
);

endmodule