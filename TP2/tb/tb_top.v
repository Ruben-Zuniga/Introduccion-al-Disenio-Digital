`timescale 1ns/100ps

module tb_top ();

parameter NB_SWITCH  = 4  ;
parameter NB_COUNTER = 16 ;
parameter NB_LEDS    = 4  ;

// Output
wire [NB_LEDS - 1 : 0] o_led       ;
wire [NB_LEDS - 1 : 0] o_led_blue  ;
wire [NB_LEDS - 1 : 0] o_led_green ;
// Input. Pueden ser wire pero tipicamente se le tiene que dar un valor inicial con el bloque initial (el initial es para variables reg)
reg  [NB_SWITCH - 1 : 0] i_switch ;
reg                      i_rst    ;
reg                      clk      ;

// En el initial Todo se ejecuta a la vez, una especie de asignacion no bloqueante?
initial begin
    clk = 1'b0;
    i_switch = 4'b0000;
    i_rst = 1'b0;

    #1000;
    @(posedge clk);
    i_rst = 1'b1;

    #10000;
    @(posedge clk);
    i_switch = 4'b0001;

    #10000;
    @(posedge clk);
    i_switch = 4'b0010;

    #10000;
    @(posedge clk);
    i_switch = 4'b0011;

    #10000;
    @(posedge clk);
    i_switch = 4'b0101;

    #10000;
    @(posedge clk);
    i_switch = 4'b0111;

    #10000;
    @(posedge clk);
    i_switch = 4'b1111;

    #10000;
    @(posedge clk);
    i_switch = 4'b1001;

    #10000;
    @(posedge clk);
    i_switch = 4'b1000;

    #10000;
    @(posedge clk);
    i_rst = 1'b0;

    #10000;
    @(posedge clk);
    i_rst = 1'b1;
    i_switch = 4'b1001;
    $finish;
end

always #5 clk = ~clk;

top 
#(
    .NB_SWITCH  (NB_SWITCH ),
    .NB_COUNTER (NB_COUNTER),
    .NB_LEDS    (NB_LEDS   )
)
u_top
(
    .o_led       (o_led      ),
    .o_led_blue  (o_led_blue ),
    .o_led_green (o_led_green),
    .i_switch    (i_switch   ),
    .i_rst       (i_rst      ),
    .clk         (clk        )
);

endmodule