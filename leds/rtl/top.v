`timescale 1ns/100ps
// Sugerencia: que el nombre del archivo sea igual al del modulo
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

wire                   connect_valid;
wire [NB_LEDS - 1 : 0] connect_leds ;
    
shiftreg
    #(
        .NB_LEDS(NB_LEDS)
    )
    u_shiftreg
    (
        .o_led   (connect_leds ),
        .i_valid (connect_valid),
        .i_rst   (~i_rst       ),
        .clk     (clk          )
    );

count
    #(
        .NB_COUNTER (NB_COUNTER   ),
        .NB_SWITCH  (NB_SWITCH - 1)
    )
    u_count
    (
        .o_valid  (connect_valid),
        .i_switch (i_switch[2:0]),
        .i_rst    (~i_rst       ),
        .clk      (clk          )
    );

assign o_led       = connect_leds;
assign o_led_blue  = (i_switch[3] == 1'b0) ? connect_leds : {NB_LEDS{1'b0}};
assign o_led_green = (i_switch[3] == 1'b1) ? connect_leds : {NB_LEDS{1'b0}};

endmodule