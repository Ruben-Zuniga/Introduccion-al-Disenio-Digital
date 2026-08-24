module bram #(
    parameter SIZE      = 1024,
    parameter NB_SIZE   = $clog2(SIZE-1), // 10
    parameter NB_LOG    = 32,
) (
    input  wire [NB_LOG  -1 : 0] i_data,
    input  wire [NB_SIZE -1 : 0] i_wr_address,
    input  wire [NB_SIZE -1 : 0] i_rd_address,
    input  wire                  i_wr_enable,
    input  wire                  i_rd_enable,
    input  wire                  i_rst_n,
    input  wire                  i_reg_enable,
    input  wire                  i_clk,
    output wire [NB_LOG  -1 : 0] o_data
);

reg  [NB_LOG-1 : 0] data_mem [SIZE-1 : 0];
reg  [NB_LOG-1 : 0] data_log = {NB_LOG{1'b0}};

integer ram_index;
initial
    for (ram_index = 0; ram_index < SIZE; ram_index = ram_index + 1)
        data_mem[ram_index] = {NB_LOG{1'b0}};

always @(posedge clk) begin
    if (i_wr_enable)
        data_mem[i_wr_address] <= i_data;
    if (i_rd_enable)
        data_log <= data_mem[i_rd_address];
end

reg [NB_LOG-1:0] data_log_reg = {NB_LOG{1'b0}};

always @(posedge clk) begin
    if (!i_rst_n)
        data_log_reg <= {NB_LOG{1'b0}};
    else if (i_rd_enable)
        data_log_reg <= data_log;
end

assign o_data = data_log_reg;
    
endmodule