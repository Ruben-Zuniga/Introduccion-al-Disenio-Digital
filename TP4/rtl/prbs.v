module prbs9 
#(
    parameter N_BITS = 9,
    parameter SEED = 9'b001
)
(
    output wire prbs_bit,
    input wire clk,
    input wire i_rst_n,
    input wire i_en_tx,
    input wire i_prbs_en
);

reg [N_BITS-1 : 0] lfsr;

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        lfsr <= SEED;
    end
    else if(i_prbs_en) begin
        lfsr[N_BITS-1 : 1] <= lfsr[N_BITS-2 : 0];
        lfsr <= {lfsr[N_BITS-2 : 0], lfsr[8] ^ lfsr[4]};
    end
end

assign prbs_bit = lfsr[8]; // 0 -> 1 ; 1 -> -1
    
endmodule