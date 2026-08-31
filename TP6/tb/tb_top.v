// BER I = 0,25048
// BER Q = 0,25050

`timescale 1ns/100ps

module tb_top ();

// Placa
parameter NB_SWITCH = 4;
parameter NB_LED    = 4;
parameter NB_RGB    = 3;
// GPIO
parameter NB_DATA_RF = 23;
parameter NB_COMMAND = 8 ;
parameter NB_GPIO    = NB_DATA_RF + NB_COMMAND + 1; // 32
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

// Comandos desde el GPIO - posicion de cada bit
localparam ENABLE_BIT       = NB_DATA_RF          ;
localparam RST_BIT          = 0 + (NB_DATA_RF + 1);
localparam TOGGLE_TX_RX_BIT = 1 + (NB_DATA_RF + 1);
localparam TX_BIT           = 2 + (NB_DATA_RF + 1);
localparam RX_BIT           = 3 + (NB_DATA_RF + 1);
localparam RUN_LOG_BIT      = 4 + (NB_DATA_RF + 1);
localparam READ_ADDRESS_BIT = 5 + (NB_DATA_RF + 1);
localparam READ_BER_BIT     = 6 + (NB_DATA_RF + 1);

wire [NB_LED    -1 : 0]      o_led           ;
wire [NB_RGB    -1 : 0]      o_led_rgb_0     ;
wire [NB_RGB    -1 : 0]      o_led_rgb_1     ;
wire [NB_GPIO   -1 : 0]      o_gpio          ;
reg                         clk             ;
reg                         i_rst_n         ;
reg [NB_GPIO   -1 : 0]      i_gpio          ;

// Señales internas
wire                           prbs_tx        ;
wire                           bits_rx        ;
wire signed [NB_DATA   -1 : 0] data           ;
wire        [NB_BER    -1 : 0] o_symb_count_i ;
wire        [NB_BER    -1 : 0] o_symb_count_q ;
wire        [NB_BER    -1 : 0] o_error_count_i;
wire        [NB_BER    -1 : 0] o_error_count_q;
wire        [NB_LOG    -1 : 0] o_data_log     ;
wire                           o_full_mem     ;
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
    i_gpio = 32'h0;

    #1000;
    @(posedge clk);
    i_rst_n = 1'b1;

    // Reset con gpio
    #1000;
    @(posedge clk);
    i_gpio = 1'b1 << RST_BIT;
    @(posedge clk);
    i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    @(posedge clk);
    i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);
    
    // Encender TX y RX con fase 2
    #10000;
    @(posedge clk);
    i_gpio = 1'b1 << RX_BIT | 1'b1 << TX_BIT | 1'b1 << TOGGLE_TX_RX_BIT | 1'b0 << RST_BIT | 2'h2;
    @(posedge clk);
    i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    @(posedge clk);
    i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);

    // // Leer BER (parte baja)
    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h1;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h3;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h5;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h7;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);
    
    // // Reiniciar RX con fase 0
    // #10000;
    // @(posedge clk);
    // i_gpio = 1'b1 << TOGGLE_TX_RX_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);
    // @(posedge clk);
    // i_gpio = (i_gpio | 1'b1 << RX_BIT | 1'b1 << TX_BIT) & ~2'h0;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // repeat(511*SYNC_PHASES*OS + 120000)
    //     @(posedge clk);

    // // Leer BER
    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h1;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h3;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h5;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // @(posedge clk);
    // i_gpio = 1'b1 << READ_BER_BIT | 3'h7;
    // @(posedge clk);
    // i_gpio = i_gpio | 1'b1 << ENABLE_BIT;
    // @(posedge clk);
    // i_gpio = i_gpio & ~(1'b1 << ENABLE_BIT);

    // Leer memoria
    i_gpio = {8'h10, 1'b0, 23'h0};
    @(posedge clk);
    i_gpio = {8'h10, 1'b1, 23'h0};
    @(posedge clk);
    i_gpio = {8'h10, 1'b0, 23'h0};
    @(posedge clk);
    i_gpio = {8'h00, 1'b0, 23'h0};
    @(posedge clk);
    i_gpio = {8'h00, 1'b1, 23'h0};
    @(posedge clk);
    i_gpio = {8'h00, 1'b0, 23'h0};

    repeat(SIZE + 4000)
        @(posedge clk);

    i_gpio = {8'h20, 1'b0, 23'h0};
    for (i = 23'h0; i < SIZE; i = i + 1'b1) begin
        i_gpio[NB_SIZE-1 : 0] = i;
        @(posedge clk);
        i_gpio[ENABLE_BIT] = 1'b1;
        @(posedge clk);
        i_gpio[ENABLE_BIT] = 1'b0;
        @(posedge clk);
    end
    

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
    .NB_RGB     (NB_RGB     ),
    .NB_DATA_RF (NB_DATA_RF ),
    .NB_COMMAND (NB_COMMAND ),
    .NB_GPIO    (NB_GPIO    ),
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
    .NB_BER     (NB_BER     ),
    .SIZE       (SIZE       ),
    .NB_SIZE    (NB_SIZE    ),
    .NB_LOG     (NB_LOG     )
)
dut
(
    .o_led       (o_led      ),
    .o_led_rgb_0 (o_led_rgb_0),
    .o_led_rgb_1 (o_led_rgb_1),
    .o_gpio      (o_gpio     ),
    .clk         (clk        ),
    .i_rst_n     (i_rst_n    ),
    .i_gpio      (i_gpio     )
);

endmodule