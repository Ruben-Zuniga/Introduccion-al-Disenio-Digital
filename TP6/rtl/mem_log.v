module mem_log 
#(
    parameter SIZE      = 1024,
    parameter NB_SIZE   = $clog2(SIZE), // 10
    parameter NB_LOG    = 32,
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

localparam IDLE = 2'd0;
localparam SAVING = 2'd1;
localparam DONE = 2'd2;
localparam READING = 2'd3;

reg [1 : 0] state;
reg [1 : 0] state_next;
reg [NB_LOG/2 - 1 : 0] data_mem_i [SIZE-1 : 0];
reg [NB_LOG/2 - 1 : 0] data_mem_q [SIZE-1 : 0];
reg [NB_LOG-1 : 0] data_log;
reg [NB_SIZE-1 : 0] address_count;
reg                 full_mem;

integer i;

always @(posedge clk or negedge i_rst_n) begin
    if (!i_rst_n) begin
        state <= IDLE;
        data_log <= 'd0;
        address_count <= 'd0;
        full_mem <= 1'b0;
        for (i = 0; i < SIZE; i = i + 1) begin
            data_mem_i[i] <= 'd0;
            data_mem_q[i] <= 'd0;
        end
    end
    else begin
        state <= state_next;
        data_log <= {data_mem_q[address_count], data_mem_i[address_count]};

        case (state)
            IDLE: begin
                address_count <= 1'b0;
            end
            SAVING: begin
                address_count <= address_count + 1'b1;
                data_mem_i[address_count] <= {{NB_LOG/2 - NB_DATA {1'b0}}, i_data_tx_i};
                data_mem_q[address_count] <= {{NB_LOG/2 - NB_DATA {1'b0}}, i_data_tx_q};
                full_mem <= 1'b0;
            end
            DONE: begin
                full_mem <= 1'b1;
                address_count <= 1'b0;
            end
            READING: begin
                address_count <= i_address;
            end
        endcase
    end
end

always @(*) begin
    case (state)
        IDLE:
            if (i_run_log & !i_read_log)
                state_next = SAVING;
            else if (i_read_log & full_mem)
                state_next = READING;
            else
                state_next = IDLE;
        SAVING:
            if (&address_count)
                state_next = DONE;
            else
                state_next = SAVING;
        DONE:
            state_next = IDLE;
        READING:
            if (i_read_log)
                state_next = READING;
            else
                state_next = IDLE;
        default: 
            state_next = IDLE;
    endcase
end

assign o_data_log = data_log;
assign o_full_mem = full_mem;
    
endmodule