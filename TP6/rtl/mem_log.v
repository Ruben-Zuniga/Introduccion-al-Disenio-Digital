module mem_log 
#(
    parameter SIZE      = 1024          ,
    parameter NB_SIZE   = $clog2(SIZE-1), // 10
    parameter NB_LOG    = 32            ,
    parameter NB_DATA   = 8
)
(
    input  wire                           clk           ,
    input  wire                           i_rst_n       ,
    input  wire signed [NB_DATA-1  : 0]   i_data_tx_i   ,
    input  wire signed [NB_DATA-1  : 0]   i_data_tx_q   ,  
    input  wire                           i_run_log     ,
    input  wire                           i_read_log    ,
    input  wire        [NB_SIZE-1  : 0]   i_address     ,
    output wire        [NB_LOG -1  : 0]   o_data_log    ,
    output wire                           o_full_mem    
);

localparam IDLE    = 2'd0;
localparam SAVING  = 2'd1;
localparam DONE    = 2'd2;

reg  [            1 : 0] state        ;
reg  [            1 : 0] state_next   ;
reg  [NB_SIZE   - 1 : 0] address_count;
reg                      full_mem     ;
wire [NB_LOG    - 1 : 0] data_log     ;

wire [NB_LOG    - 1 : 0] data_ram     ;
reg                      write_en     ;

assign data_ram = {{NB_LOG/2 - NB_DATA {1'b0}}, i_data_tx_i,
                  {NB_LOG/2 - NB_DATA {1'b0}}, i_data_tx_q};

// /* -- BRAM -- */
bram #(
    .SIZE   (SIZE   ),
    .NB_SIZE(NB_SIZE),
    .NB_LOG (NB_LOG )
)
u_bram
(
    .i_data         (data_ram     ),
    .i_wr_address   (address_count),
    .i_rd_address   (i_address    ),
    .i_wr_enable    (write_en     ),
    .i_rd_enable    (i_read_log   ),
    .i_rst_n        (i_rst_n      ),
    .i_reg_enable   (i_read_log   ),
    .clk            (clk          ),
    .o_data         (data_log     )
);

always @(posedge clk or negedge i_rst_n) begin
    if (!i_rst_n) begin
        state <= IDLE;
        address_count <= 'd0;
        write_en <= 1'b0;
        full_mem <= 1'b0;
    end
    else begin
        state <= state_next;

        case (state)
            IDLE: begin
                address_count <= 1'b0;
            end
            SAVING: begin
                address_count <= address_count + 1'b1;
                write_en <= 1'b1;
                full_mem <= 1'b0;
            end
            DONE: begin
                write_en <= 1'b0;
                full_mem <= 1'b1;
            end
        endcase
    end
end

always @(*) begin
    case (state)
        IDLE:
            if (i_run_log)
                state_next = SAVING;
            else
                state_next = IDLE;
        SAVING:
            if (&address_count)
                state_next = DONE;
            else
                state_next = SAVING;
        DONE:
            state_next = IDLE;
        default: 
            state_next = IDLE;
    endcase
end

assign o_data_log = data_log;
assign o_full_mem = full_mem;

endmodule