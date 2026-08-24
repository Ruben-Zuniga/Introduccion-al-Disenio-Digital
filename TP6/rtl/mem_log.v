module mem_log 
#(
    parameter SIZE      = 1024,
    parameter NB_SIZE   = $clog2(SIZE-1), // 10
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
    input  wire        [NB_SIZE-1  : 0]   i_address,
    output wire        [NB_LOG -1  : 0]   o_data_log    ,
    output wire                           o_full_mem
);

localparam IDLE    = 2'd0;
localparam SAVING  = 2'd1;
localparam DONE    = 2'd2;
localparam READING = 2'd3;

reg  [            1 : 0] state                  ;
reg  [            1 : 0] state_next             ;
// reg  [NB_LOG/2  - 1 : 0] data_mem_i [SIZE-1 : 0];
// reg  [NB_LOG/2  - 1 : 0] data_mem_q [SIZE-1 : 0];
reg  [NB_LOG    - 1 : 0] data_log = {NB_LOG{1'b0}};
reg  [NB_SIZE   - 1 : 0] address_count          ;
reg                      full_mem               ;

integer i;

/* -- BRAM -- */
reg  [NB_LOG    - 1 : 0] data_mem   [SIZE-1 : 0];
integer ram_index;
initial
    for (ram_index = 0; ram_index < SIZE; ram_index = ram_index + 1)
        data_mem[ram_index] = {NB_LOG{1'b0}};

wire [NB_LOG-1 : 0] data_in;

assign data_in = {{NB_LOG/2 - NB_DATA {1'b0}}, i_data_tx_i,
                  {NB_LOG/2 - NB_DATA {1'b0}}, i_data_tx_q};

reg write_en;

always @(posedge clk) begin
    if (write_en)
        data_mem[address_count] <= data_in;
    if (i_read_log)
        data_log <= data_mem[i_address];
end

reg [NB_LOG-1:0] data_log_reg = {NB_LOG{1'b0}};

always @(posedge clk) begin
    if (!i_rst_n)
        data_log_reg <= {NB_LOG{1'b0}};
    else if (i_read_log)
        data_log_reg <= data_log;
end

assign o_data_log = data_log_reg;
/* -- BRAM end -- */

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
            // READING: begin
            // end
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
        // READING:
        //     if (i_read_log)
        //         state_next = READING;
        //     else
        //         state_next = IDLE;
        default: 
            state_next = IDLE;
    endcase
end

// assign o_data_log = data_log;
assign o_full_mem = full_mem;
    

//   //  Xilinx Simple Dual Port Single Clock RAM
//   //  This code implements a parameterizable SDP single clock memory.
//   //  If a reset or enable is not necessary, it may be tied off or removed from the code.

//   parameter RAM_WIDTH = NB_LOG;                  // Specify RAM data width
//   parameter RAM_DEPTH = SIZE;                  // Specify RAM depth (number of entries)
//   parameter RAM_PERFORMANCE = "LOW_LATENCY"; // Select "HIGH_PERFORMANCE" or "LOW_LATENCY" 
//   parameter INIT_FILE = "";                       // Specify name/location of RAM initialization file if using one (leave blank if not)

//   <wire_or_reg> [clogb2(RAM_DEPTH-1)-1:0] <addra>; // Write address bus, width determined from RAM_DEPTH
//   <wire_or_reg> [clogb2(RAM_DEPTH-1)-1:0] <addrb>; // Read address bus, width determined from RAM_DEPTH
//   <wire_or_reg> [RAM_WIDTH-1:0] <dina>;          // RAM input data
//   <wire_or_reg> <clka>;                          // Clock
//   <wire_or_reg> <wea>;                           // Write enable
//   <wire_or_reg> <enb>;                           // Read Enable, for additional power savings, disable when not in use
//   <wire_or_reg> <rstb>;                          // Output reset (does not affect memory contents)
//   <wire_or_reg> <regceb>;                        // Output register enable
//   wire [RAM_WIDTH-1:0] <doutb>;                  // RAM output data

//   reg [RAM_WIDTH-1:0] <ram_name> [RAM_DEPTH-1:0];
//   reg [RAM_WIDTH-1:0] <ram_data> = {RAM_WIDTH{1'b0}};

//   // The following code either initializes the memory values to a specified file or to all zeros to match hardware
//   generate
//     if (INIT_FILE != "") begin: use_init_file
//       initial
//         $readmemh(INIT_FILE, <ram_name>, 0, RAM_DEPTH-1);
//     end else begin: init_bram_to_zero
//       integer ram_index;
//       initial
//         for (ram_index = 0; ram_index < RAM_DEPTH; ram_index = ram_index + 1)
//           <ram_name>[ram_index] = {RAM_WIDTH{1'b0}};
//     end
//   endgenerate

//   always @(posedge <clka>) begin
//     if (<wea>)
//       <ram_name>[<addra>] <= <dina>;
//     if (<enb>)
//       <ram_data> <= <ram_name>[<addrb>];
//   end

//   //  The following code generates HIGH_PERFORMANCE (use output register) or LOW_LATENCY (no output register)
//   generate
//     if (RAM_PERFORMANCE == "LOW_LATENCY") begin: no_output_register

//       // The following is a 1 clock cycle read latency at the cost of a longer clock-to-out timing
//        assign <doutb> = <ram_data>;

//     end else begin: output_register

//       // The following is a 2 clock cycle read latency with improve clock-to-out timing

//       reg [RAM_WIDTH-1:0] doutb_reg = {RAM_WIDTH{1'b0}};

//       always @(posedge <clka>)
//         if (<rstb>)
//           doutb_reg <= {RAM_WIDTH{1'b0}};
//         else if (<regceb>)
//           doutb_reg <= <ram_data>;

//       assign <doutb> = doutb_reg;

//     end
//   endgenerate

//   //  The following function calculates the address width based on specified RAM depth
//   function integer clogb2;
//     input integer depth;
//       for (clogb2=0; depth>0; clogb2=clogb2+1)
//         depth = depth >> 1;
//   endfunction
						
						

endmodule