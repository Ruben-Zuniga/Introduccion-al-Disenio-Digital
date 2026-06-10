module shiftreg 
#(
    parameter NB_LEDS = 4
)
(
    output [NB_LEDS - 1 : 0] o_led   ,
    input                    i_valid ,
    input                    i_rst   ,
    input                    clk
);

// Variables
reg [NB_LEDS - 1 : 0] shift_register;

// integer ptr;

always @(posedge clk ) begin
    if (i_rst) begin
        shift_register <= {1'b1, {NB_LEDS - 1{1'b0}}};
    end
    else if (i_valid) begin

        // // Opcion 1: for
        // for (ptr = 0; ptr < NB_LEDS; ptr = ptr + 1) begin: shift_register_for
        //     shift_register[ptr + 1] <= shift_register[ptr];
        // end
        // shift_register[0] <= shift_register[NB_LEDS - 1];

        // // Opcion 2: asignacion directa
        // shift_register[1] <= shift_register[0];
        // shift_register[2] <= shift_register[1];
        // shift_register[3] <= shift_register[2];
        // shift_register[0] <= shift_register[3];

        // // Opcion 3: shift bits
        // shift_register <= shift_register << 1;
        // shift_register[0] <= 

        // // Opcion 4: case
        // case (shift_register)
        //     4'b0001: shift_register <= 4'b0010;
        //     4'b0010: shift_register <= 4'b0100;
        //     4'b0100: shift_register <= 4'b1000;
        //     4'b1000: shift_register <= 4'b0001;
        //     default: 
        // endcase

        // Opcion 5: concatenar
        shift_register <= {shift_register[NB_LEDS - 2 -: NB_LEDS - 1], shift_register[NB_LEDS - 1]};
    end
    else begin
        shift_register <= shift_register;
    end
end

assign o_led = shift_register;
    
endmodule