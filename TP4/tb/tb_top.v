`timescale 1ns/100ps

module tb_top ();

// Placa
parameter NB_SWITCH = 4;
parameter NB_LED = 4;
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
parameter NB_ERRORS = 64;

wire prbs_tx;
wire bits_rx;
wire signed [NB_DATA-1 : 0] data;
wire [NB_LED-1 : 0] o_led;
reg  clk;
reg  i_rst_n;
reg  [NB_SWITCH-1 : 0] i_switch;

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

    vm_data_errors = 0;
    vm_prbs_tx_errors = 0;
    vm_bits_rx_errors = 0;
    $readmemh("out_tx_log.mem", data_log);
    $readmemh("symb_tx_log.mem", prbs_tx_log);
    $readmemh("symb_rx_log.mem", bits_rx_log);

    #1000;
    @(posedge clk);
    i_rst_n = 1'b1;

    #10000;
    @(posedge clk);
    i_switch = 4'b1011;

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
    i_switch = 4'b0111;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    i_switch = 4'b0011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    i_switch = 4'b1111;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    i_switch = 4'b1101;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1100;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1110;
    
    #10000;
    @(posedge clk);
    i_rst_n = 1'b0;

    #10000;
    $display("Errores en los bits del TX:  %d" , vm_prbs_tx_errors);
    $display("Errores en la salida del TX: %d", vm_data_errors);
    $display("Errores en los bits del RX:  %d" , vm_bits_rx_errors);
    $finish;
end

top
#(
    .NB_SWITCH(NB_SWITCH),
    .NB_LED(NB_LED),
    .NB_PRBS(NB_PRBS),
    .SEED_PRBS_I(SEED_PRBS_I),
    .SEED_PRBS_Q(SEED_PRBS_Q),
    .OS(OS),
    .NB_COUNTER(NB_COUNTER),
    .N_BAUD(N_BAUD),
    .NB_DATA(NB_DATA),
    .NBF_DATA(NBF_DATA),
    .NB_COEFF(NB_COEFF),
    .NBF_COEFF(NBF_COEFF),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_ERRORS(NB_ERRORS)
)
dut
(
    .o_led(o_led),
    .clk(clk),
    .i_rst_n(i_rst_n),
    .i_switch(i_switch)
);

endmodule