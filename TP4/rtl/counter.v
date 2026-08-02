// Modulo de contador aparte para no tener logica en el top
module counter
#(
    parameter OS = 4,
    parameter NB_COUNTER = $clog2(OS) // 2
)
(
    output wire o_valid,
    output wire [NB_COUNTER-1 : 0] o_count,
    input wire clk,
    input wire i_rst_n
);

reg [NB_COUNTER-1 : 0] count;

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        count <= {NB_COUNTER{1'b0}};
    end
    else begin
        count <= count + 1'b1;
    end
end

assign o_count = count;
// El valid se levanta cuando count = 3
assign o_valid = (&count) ? 1'b1 : 1'b0;
    
endmodule