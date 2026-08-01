`timescale 1ns/100ps

module tb_rx();

// General
parameter NB_PRBS = 9;
parameter SEED_PRBS = 9'h1AA;
parameter OS = 4;
parameter NB_COUNTER = $clog2(OS); // 2
// TX
parameter N_BAUD     = 6;
parameter NB_OUTPUT  = 8;
parameter NBF_OUTPUT = 7;
parameter NB_COEFF   = 8;
parameter NBF_COEFF  = 7;
// RX
parameter NB_INPUT = 8;
parameter SYNC_PHASES = 16;
parameter NB_ERRORS = 64;

wire o_led;
reg clk     ;
reg i_rst_n ;
reg i_enable;
wire valid ;
reg [NB_COUNTER-1 : 0] i_phase;
reg [NB_COUNTER-1 : 0] count;
wire signed [NB_INPUT-1 : 0] data;

// Vector Matching
integer errors;
integer i;
reg [NB_INPUT-1 : 0] o_data_log [39997-1 : 0];

always #5 clk = ~clk;

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        count <= {NB_COUNTER{1'b0}};
    end
    else begin
        count <= count + 1'b1;
    end
end

// El valid se levanta cuando count = 3
assign valid = (&count) ? 1'b1 : 1'b0;

initial begin
    clk = 1'b0;
    i_rst_n = 1'b0;
    i_enable = 1'b0;
    i_phase = 2'd1;

    errors = 0;
    $readmemh("out_tx_log.mem", o_data_log);

    #1000;
    @(posedge clk);
    i_rst_n = 1'b1;

    #10000;
    @(posedge clk);
    i_enable = 1;

    for (i = 0; i < (511*SYNC_PHASES*OS + 40000); i = i + 1) begin
        @(posedge clk);
        // $display("o_data: %d, o_data_log: %d", o_data, o_data_log[i]);

        // if(o_data != o_data_log[i]) begin
        //     errors = errors + 1;
        // end

        // data = o_data_log[i % (511*OS)];
    end
    
    @(posedge clk);
    i_enable = 0;

    #10000;
    @(posedge clk);
    // i_enable = 1;

    // #10000;
    // @(posedge clk);
    // i_enable = 0;

    // #10000;
    // @(posedge clk);
    // i_rst_n = 1'b0;

    // #10000;
    // @(posedge clk);
    // i_rst_n = 1'b1;
    // i_enable = 1;

    // #10000;
    // @(posedge clk);
    // i_rst_n = 1'b0;

    // #10000;
    // $display("Errores: %d", errors);
    $finish;
end

tx
#(
    .NB_PRBS(NB_PRBS),
    .SEED_PRBS(SEED_PRBS),
    .OS(OS),
    .NB_COUNTER(NB_COUNTER),
    .N_BAUD(N_BAUD),
    .NB_OUTPUT(NB_OUTPUT),
    .NBF_OUTPUT(NBF_OUTPUT),
    .NB_COEFF(NB_COEFF),
    .NBF_COEFF(NBF_COEFF)
)
u_tx
(
    .o_data(data)    ,
    .clk(clk)          ,
    .i_rst_n(i_rst_n)  ,
    .i_enable(i_enable),
    .i_valid(valid)  ,
    .i_count(count)
);

rx
#(
    .NB_PRBS(NB_PRBS),
    .SEED_PRBS(SEED_PRBS),
    .OS(OS),
    .NB_COUNTER(NB_COUNTER),
    .NB_INPUT(NB_INPUT),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_ERRORS(NB_ERRORS)
)
u_rx
(
    .o_led(o_led),
    .clk(clk),
    .i_rst_n(i_rst_n),
    .i_enable(i_enable),
    .i_valid(valid),
    .i_phase(i_phase),
    .i_data(data),
    .i_count(count)
);

endmodule