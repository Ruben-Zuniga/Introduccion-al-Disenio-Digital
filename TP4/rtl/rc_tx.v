module rc_tx 
#(
    parameter NB_OUT = 8 + $clog2(6), // 8 + 6
    parameter NB_COEFF = 8
)
(
    output wire signed [NB_OUT-1:0] o_data,
    input wire clk,
    input wire i_rst_n,
    input wire i_en_tx,
    input wire i_rc_en,
    input wire i_prbs_bit,
    input wire [2-1:0] i_phase_sel
);

reg [6-1:0] shift_reg;

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        shift_reg <= 6'b0;
    end
    else if (i_en_tx && i_rc_en) begin
        shift_reg <= {shift_reg[6-2:0], i_prbs_bit};
    end
end

localparam signed [NB_COEFF-1 : 0] phase_coeff [0:4-1] [0:6-1] = '{
    '{h0, h4, h8 , h12, h16, h20}, // Fase 0
    '{h1, h5, h9 , h13, h17, h21}, // Fase 1
    '{h2, h6, h10, h14, h18, h22}, // Fase 2
    '{h3, h7, h11, h15, h19, h23}  // Fase 3
};

// subfiltros en paralelo
wire signed [NB_OUT-1 : 0] sum [4-1:0];
wire signed [NB_COEFF-1 : 0] mult ;

always @(*) begin
    mult = (i_prbs_bit) ? -phase_coeff[i][j] : phase_coeff[i][j];
end

always @(*) begin
    sum[0] = 0;
    sum[1] = 0;
    sum[2] = 0;
    sum[3] = 0;

    sum[i] = sum[i] + mult;
end
    
endmodule