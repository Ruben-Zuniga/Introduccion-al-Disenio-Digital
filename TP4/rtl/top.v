module top 
#(
    parameter NB_SWITCH = 4,
    parameter NB_LED = 4,
    parameter OS = 4,
    parameter PRBS_SEED_I = 9'h1AA,
    parameter PRBS_SEED_Q = 9'h1FE
)
(
    output wire [NB_LED-1 : 0] o_led,
    input wire clk,
    input wire i_rst_n,
    input wire [NB_SWITCH-1 : 0] i_switch
);

wire                     connect_reset ;
wire [NB_SWITCH - 1 : 0] connect_switch;

// Reverse Reset
assign connect_switch = (select_VIO) ? switch_from_VIO : i_switch;
assign connect_reset  = (select_VIO) ? ~reset_from_VIO : ~i_rst_n;
    
endmodule