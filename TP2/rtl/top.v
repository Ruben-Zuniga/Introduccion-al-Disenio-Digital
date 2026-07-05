`timescale 1ns/100ps
// Sugerencia: que el nombre del archivo sea igual al del modulo
// Probar subir a la fpga con NB_COUNTER = 16
module top 
#(
    parameter NB_SWITCH  = 4 ,
    parameter NB_COUNTER = 32,
    parameter NB_LEDS    = 4
)
(
    // Se tiene que acordar con el equipo el orden de los puertos
    output [NB_LEDS - 1 : 0]   o_led       ,
    output [NB_LEDS - 1 : 0]   o_led_blue  ,
    output [NB_LEDS - 1 : 0]   o_led_green ,
    input  [NB_SWITCH - 1 : 0] i_switch    ,
    input                      i_rst       ,
    // clk no se le pone i_ a no ser que tengamos multiples clocks en el diseño
    input                      clk
);

// Module connections
wire                     connect_valid;
wire [NB_LEDS - 1 : 0]   connect_leds ;
wire [NB_SWITCH - 1 : 0] connect_switch;

// VIO Inputs
wire [NB_SWITCH - 1 : 0]   switch_from_VIO; //! Switchs
wire 		               reset_from_VIO ; //! Reset **active low**
wire                       select_VIO     ; //! Ctrl from
    
// Reverse Reset
assign connect_switch = (select_VIO) ? switch_from_VIO : i_switch;
assign connect_reset  = (select_VIO) ? ~reset_from_VIO : ~i_rst  ;

shiftreg
    #(
        .NB_LEDS(NB_LEDS)
    )
    u_shiftreg
    (
        .o_led   (connect_leds ),
        .i_valid (connect_valid),
        .i_rst   (connect_reset),
        .clk     (clk          )
    );

count
    #(
        .NB_COUNTER (NB_COUNTER   ),
        .NB_SWITCH  (NB_SWITCH - 1)
    )
    u_count
    (
        .o_valid  (connect_valid      ),
        .i_switch (connect_switch[2:0]),
        .i_rst    (connect_reset      ),
        .clk      (clk                )
    );

//! VIO instance
vio
    u_vio
    (
        .clk_0       (clk),
        .probe_in0_0 (o_led),
        .probe_in1_0 (o_led_blue),
        .probe_in2_0 (o_led_green),
        .probe_out0_0(select_VIO),
        .probe_out1_0(reset_from_VIO),
        .probe_out2_0(switch_from_VIO)
    );

//! ILA Instance
ila
    u_ila
    (
        .clk_0    (clk),
        .probe0_0 (o_led)
    );

assign o_led       = connect_leds;
assign o_led_blue  = (connect_switch[3] == 1'b0) ? connect_leds : {NB_LEDS{1'b0}};
assign o_led_green = (connect_switch[3] == 1'b1) ? connect_leds : {NB_LEDS{1'b0}};

endmodule