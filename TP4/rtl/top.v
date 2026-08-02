module top 
#(
    // Placa
    parameter NB_SWITCH = 4,
    parameter NB_LED = 4,
    // PRBS9
    parameter NB_PRBS   = 9,
    parameter SEED_PRBS_I = 9'h1AA,
    parameter SEED_PRBS_Q = 9'h1FE,
    // Filtro
    parameter OS         = 4         ,
    parameter NB_COUNTER = $clog2(OS), // 2
    parameter N_BAUD     = 6         ,
    parameter NB_DATA  = 8         ,
    parameter NBF_DATA = 7         ,
    parameter NB_COEFF   = 8         ,
    parameter NBF_COEFF  = 7         ,
    // BER
    parameter SYNC_PHASES = 1024,
    parameter NB_ERRORS = 64
)
(
    output wire [NB_LED-1 : 0] o_led,
    input wire clk,
    input wire i_rst_n,
    input wire [NB_SWITCH-1 : 0] i_switch
);

// wire                     connect_reset ;
// wire [NB_SWITCH - 1 : 0] connect_switch;

// // Reverse Reset
// assign connect_switch = (select_VIO) ? switch_from_VIO : i_switch;
// assign connect_reset  = (select_VIO) ? ~reset_from_VIO : ~i_rst_n;

wire signed [NB_DATA-1    : 0] data ;
wire                           valid;
wire        [NB_COUNTER-1 : 0] count;
wire        [NB_ERRORS-1  : 0] errors;
wire        [NB_LED-1     : 0] led;

// Control: Contador
counter
#(
    .OS(OS),
    .NB_COUNTER(NB_COUNTER)
)
u_counter
(
    .o_valid(valid),
    .o_count(count),
    .clk(clk),
    .i_rst_n(i_rst_n)
);

// Transmisor: PRBS + Filtro
tx
#(
    .NB_PRBS(NB_PRBS),
    .SEED_PRBS(SEED_PRBS_I),
    .OS(OS),
    .NB_COUNTER(NB_COUNTER),
    .N_BAUD(N_BAUD),
    .NB_DATA(NB_DATA),
    .NBF_DATA(NBF_DATA),
    .NB_COEFF(NB_COEFF),
    .NBF_COEFF(NBF_COEFF)
)
u_tx
(
    .o_data(data)    ,
    .clk(clk)          ,
    .i_rst_n(i_rst_n)  ,
    .i_enable(i_switch[0]),
    .i_valid(valid)  ,
    .i_count(count)
);

// Receptor: Decimador + BER
rx
#(
    .NB_PRBS(NB_PRBS),
    .SEED_PRBS(SEED_PRBS_I),
    .OS(OS),
    .NB_COUNTER(NB_COUNTER),
    .NB_DATA(NB_DATA),
    .SYNC_PHASES(SYNC_PHASES),
    .NB_ERRORS(NB_ERRORS)
)
u_rx
(
    .o_led(led),
    .o_errors(errors),
    .clk(clk),
    .i_rst_n(i_rst_n),
    .i_enable(i_switch[1]),
    .i_valid(valid),
    .i_phase(i_switch[3:2]),
    .i_data(data)
);

assign o_led[0] = i_rst_n;
assign o_led[1] = i_switch[0];
assign o_led[2] = i_switch[1];
assign o_led[3] = led;
    
endmodule