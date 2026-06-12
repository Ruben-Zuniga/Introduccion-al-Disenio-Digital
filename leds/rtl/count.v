`timescale 1ns/100ps
`define NB_COUNTER 32

module count
#(
    parameter NB_SWITCH = 3,
    parameter NB_COUNTER = 32
    // parameter NB_COUNTER = `NB_COUNTER
)
(
    output                     o_valid  ,
    input  [NB_SWITCH - 1 : 0] i_switch ,
    input                      i_rst    ,
    input                      clk
);

// Division que da menor a cero te tira cero (divisiones enteras)
localparam R0 = 2**(NB_COUNTER - 11) - 1;
localparam R1 = 2**(NB_COUNTER - 12) - 1;
localparam R2 = 2**(NB_COUNTER - 13) - 1;
localparam R3 = 2**(NB_COUNTER - 14) - 1;

// Opcion 2: assign

wire [NB_COUNTER - 1:0] limit_counter;
reg [NB_COUNTER - 1 : 0] counter;
reg valid;

assign limit_counter = (i_switch[2:1] == 2'b00) ? R0 :
                       (i_switch[2:1] == 2'b01) ? R1 :
                       (i_switch[2:1] == 2'b10) ? R2 : R3;

always @(posedge clk) begin
    if(i_rst) begin
        // counter <= `NB_COUNTER'd0;
        counter <= {NB_COUNTER{1'b0}};
        valid <= 1'b0;
    end
    else if(i_switch[0]) begin
        if (counter >= limit_counter) begin
            counter <= {NB_COUNTER{1'b0}};
            valid <= 1'b1;
        end
        else begin
            counter <= counter + 1;
            valid <= 1'b0;
        end
    end
    // No hay problema si este else no esta. Es asignacion no bloqueante
    else begin
        counter <= counter;
        valid <= valid;
    end
end

assign o_valid = valid;


// Opcion 1: Always

// localparam OP0 = 2'b00;
// localparam OP1 = 2'b01;
// localparam OP2 = 2'b10;
// localparam OP3 = 2'b11;

// reg [NB_COUNTER - 1:0] limit_counter;

// always @(*) begin
//     // Con CASE
//     case (i_switch[2:1])
//         OP0 : limit_counter = R0;
//         OP1 : limit_counter = R1;
//         OP2 : limit_counter = R2;
//         OP3 : limit_counter = R3;
//     endcase

//     // Con IF con prioridad
//     if (i_switch[2:1] == OP0)
//         limit_counter = R0;

//     else if (i_switch[2:1] == OP1)
//         limit_counter = R1;

//     else if (i_switch[2:1] == OP2)
//         limit_counter = R2;

//     else
//         limit_counter = R3;

//     // Con IF sin prioridad. SI TUVIERA MAS BITS EN EL SWITCH, PUEDO INFERIR LATCH. EN ESTE CASO CUBRO TODO ASI QUE NO HABRIA PROBLEMA
//     if (i_switch[2:1] == OP0)
//         limit_counter = R0;

//     if (i_switch[2:1] == OP1)
//         limit_counter = R1;

//     if (i_switch[2:1] == OP2)
//         limit_counter = R2;

//     if (i_switch[2:1] == OP3)
//         limit_counter = R3;
// end

endmodule