`timescale 1ns/100ps

module tb_top ();

// Placa
parameter NB_ENABLE = 2;
parameter NB_LED    = 4;
parameter NB_RGB    = 3;
parameter N_RGB_LEDS = 2;
// PRBS9
parameter NB_PRBS   = 9;
parameter SEED_PRBS_I = 9'h1AA;
parameter SEED_PRBS_Q = 9'h1FE;
// Filtro
parameter OS         = 4         ;
parameter NB_COUNTER = $clog2(OS); // 2
parameter N_BAUD     = 6         ;
parameter NB_DATA  = 8         ;
parameter NBF_DATA = 7         ;
parameter NB_COEFF   = 8         ;
parameter NBF_COEFF  = 7         ;
// BER
parameter SYNC_PHASES = 16;
parameter NB_BER = 64;

wire prbs_tx;
wire bits_rx;
wire signed [NB_DATA-1 : 0] data;
wire [NB_LED-1 : 0] o_led;
wire [NB_RGB-1 : 0] o_led_rgb [N_RGB_LEDS-1 : 0];
wire [NB_BER-1  : 0] o_sample_count_i;
wire [NB_BER-1  : 0] o_sample_count_q;
wire [NB_BER-1  : 0] o_error_count_i;
wire [NB_BER-1  : 0] o_error_count_q;
wire [NB_ENABLE-1 : 0] i_enable;
wire [NB_COUNTER-1 : 0] i_phase_sel;
reg  clk;
reg  i_rst_n;

wire [NB_ENABLE + NB_COUNTER - 1 : 0] switch;
assign switch = {i_phase_sel, i_enable};

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
    switch = {NB_SWITCH{1'b0}};

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

    #10000;
    @(posedge clk);
    switch = 4'b1011;

    for (i = 0; i < N_LOG; i = i + 1) begin
        @(posedge clk);
        
        if(i % OS == 0) begin
            if (prbs_tx != prbs_tx_log[i / OS])
                vm_prbs_tx_errors = vm_prbs_tx_errors + 1;
            if ((i/OS > 0) && (bits_rx != bits_rx_log[i/OS - 1]))
                vm_bits_rx_errors = vm_bits_rx_errors + 1;
        end

        if(data != data_log[i])
            vm_data_errors = vm_data_errors + 1;
    end

    repeat(511*SYNC_PHASES*OS)
        @(posedge clk);
    
    @(posedge clk);
    switch = 4'b0111;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    switch = 4'b0011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    switch = 4'b1111;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);

    // // -- Simulacion larga para probar el correlador de 1024 (SYNC_PHASES = 1024) --
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1011;

    // repeat(511*SYNC_PHASES*OS + 40000)
    //     @(posedge clk);
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1001;
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1011;

    // repeat(511*SYNC_PHASES*OS + 40000)
    //     @(posedge clk);
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1010;
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1011;

    // repeat(511*SYNC_PHASES*OS + 40000)
    //     @(posedge clk);
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1001;
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1000;
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1010;
    
    // #10000;
    // @(posedge clk);
    // switch = 4'b1011;

    // repeat(511*SYNC_PHASES*OS + 40000)
    //     @(posedge clk);

    // // -- Termina la simulacion larga
    
    #10000;
    @(posedge clk);
    i_rst_n = 1'b0;

    #10000;
    $display("Errores en los bits del TX:  %d" , vm_prbs_tx_errors);
    $display("Errores en la salida del TX: %d", vm_data_errors);
    $display("Errores en los bits del RX:  %d" , vm_bits_rx_errors);
    $finish;
end

top #(
    .NB_ENABLE  (NB_ENABLE),
    .NB_LED     (NB_LED),
    .NB_RGB     (NB_RGB),
    .N_RGB_LEDS (N_RGB_LEDS),
    .NB_PRBS    (NB_PRBS),
    .SEED_PRBS_I(SEED_PRBS_I),
    .SEED_PRBS_Q(SEED_PRBS_Q),
    .OS         (OS),
    .NB_COUNTER (NB_COUNTER),
    .N_BAUD     (N_BAUD),
    .NB_DATA    (NB_DATA),
    .NBF_DATA   (NBF_DATA),
    .NB_COEFF   (NB_COEFF),
    .NBF_COEFF  (NBF_COEFF),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_BER     (NB_BER)
)
dut (
    .o_led              (o_led),
    .o_led_rgb          (o_led_rgb),
    .o_sample_count_i   (o_sample_count_i),
    .o_sample_count_q   (o_sample_count_q),
    .o_error_count_i    (o_error_count_i),
    .o_error_count_q    (o_error_count_q),
    .clk                (clk),
    .i_rst_n            (i_rst_n),
    .i_enable           (i_enable),
    .i_phase_sel        (i_phase_sel)
);

endmodule