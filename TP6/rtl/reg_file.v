module reg_file #(
    // Placa
    parameter NB_SWITCH = 4,
    // GPIO
    parameter NB_DATA_RF = 23,
    parameter NB_COMMAND = 8 ,
    parameter NB_GPIO    = NB_DATA_RF + NB_COMMAND + 1, // 32
    // Filtro
    parameter OS         = 4         ,
    parameter NB_COUNTER = $clog2(OS), // 2
    // BER
    parameter NB_BER = 64,
    // Memoria
    parameter SIZE    = 1024        ,
    parameter NB_SIZE = $clog2(SIZE), // 10
    parameter NB_LOG  = 32
)
(
    output wire                         o_rst_dsp_n     ,
    output wire [NB_SWITCH -1 : 0]      o_switch        ,
    output wire                         o_run_log       ,
    output wire                         o_read_log      ,
    output wire [NB_SIZE   -1 : 0]      o_address       ,
    output wire [NB_GPIO   -1 : 0]      o_gpio          ,
    input  wire [NB_BER    -1 : 0]      i_symb_count_i  ,
    input  wire [NB_BER    -1 : 0]      i_symb_count_q  ,
    input  wire [NB_BER    -1 : 0]      i_error_count_i ,
    input  wire [NB_BER    -1 : 0]      i_error_count_q ,
    input  wire [NB_LOG    -1 : 0]      i_data_log      ,
    input  wire                         i_full_mem      ,
    input  wire [NB_GPIO   -1 : 0]      i_gpio          ,
    input  wire                         clk             ,
    input  wire                         i_rst_n
);

// Comandos desde el GPIO - posicion de cada bit
localparam ENABLE_BIT       = NB_DATA_RF          ;
localparam RST_BIT          = 0 + (NB_DATA_RF + 1);
localparam TOGGLE_TX_RX_BIT = 1 + (NB_DATA_RF + 1);
localparam TX_BIT           = 2 + (NB_DATA_RF + 1);
localparam RX_BIT           = 3 + (NB_DATA_RF + 1);
localparam RUN_LOG_BIT      = 4 + (NB_DATA_RF + 1);
localparam READ_ADDRESS_BIT = 5 + (NB_DATA_RF + 1);
localparam READ_BER_BIT     = 6 + (NB_DATA_RF + 1);

// Para indicar qué leer para la BER
localparam READ_ERROR_I = 'd0;
localparam READ_SYMB_I  = 'd1;
localparam READ_ERROR_Q = 'd2;
localparam READ_SYMB_Q  = 'd3;

// Comandos hacia el GPIO
localparam MEM_FULL_BIT     = 'h1;

reg                    rst_dsp_n;
reg [NB_SWITCH -1 : 0] switch   ;
reg                    run_log  ;
reg                    read_log ;
reg [NB_SIZE   -1 : 0] address  ;
reg [NB_GPIO   -1 : 0] data_log ;
reg [NB_GPIO   -1 : 0] symb_count_i_low ;
reg [NB_GPIO   -1 : 0] symb_count_i_high ;
reg [NB_GPIO   -1 : 0] symb_count_q_low ;
reg [NB_GPIO   -1 : 0] symb_count_q_high ;
reg [NB_GPIO   -1 : 0] error_count_i_low;
reg [NB_GPIO   -1 : 0] error_count_i_high;
reg [NB_GPIO   -1 : 0] error_count_q_low;
reg [NB_GPIO   -1 : 0] error_count_q_high;
reg [NB_GPIO   -1 : 0] control;
reg [NB_GPIO   -1 : 0] to_gpio;

always @(posedge clk or negedge i_rst_n) begin
    if (!i_rst_n) begin
        rst_dsp_n <= 1'b0;
        switch <= 'd0;
        run_log <= 'd0;
        read_log <= 'd0;
        address <= 'd0;
        data_log <= 'd0;
        control <= 'd0;

        error_count_i_high <= 'd0;
        error_count_i_low  <= 'd0;
        symb_count_i_high  <= 'd0;
        symb_count_i_low   <= 'd0;
        error_count_q_high <= 'd0;
        error_count_q_low  <= 'd0;
        symb_count_q_high  <= 'd0;
        symb_count_q_low   <= 'd0;
    end
    else begin
        // Leer el GPIO
        control <= i_gpio;
        // Leer bit de enable del GPIO
        if (control[ENABLE_BIT]) begin
            // Reset del DSP
            rst_dsp_n <= (control[RST_BIT]) ? 1'b0 : 1'b1;

            // TX ON/OFF
            if (control[TX_BIT])
                switch[0] <= (control[TOGGLE_TX_RX_BIT]) ? 1'b1 : 1'b0;

            // RX ON/OFF - Ver bien donde poner la asignacion de fase
            if (control[RX_BIT]) begin
                if (control[TOGGLE_TX_RX_BIT]) begin
                    switch[1] <= 1'b1;
                    switch[3:2] <= control[NB_COUNTER-1 : 0];
                end
                else
                    switch[1] <= 1'b0;
            end

            // Run log
            run_log <= (control[RUN_LOG_BIT]) ? 1'b1 : 1'b0;

            // Read 1 address
            if (control[READ_ADDRESS_BIT]) begin
                read_log <= 1'b1;
                address <= control[NB_SIZE-1 : 0];
                data_log <= i_data_log;
            end
            else
                read_log <= 1'b0;

            // Read BER
            error_count_i_high <= i_error_count_i[NB_BER   - 1 : NB_BER/2];
            error_count_i_low  <= i_error_count_i[NB_BER/2 - 1 :        0];
            symb_count_i_high  <= i_symb_count_i [NB_BER   - 1 : NB_BER/2];
            symb_count_i_low   <= i_symb_count_i [NB_BER/2 - 1 :        0];
            error_count_q_high <= i_error_count_q[NB_BER   - 1 : NB_BER/2];
            error_count_q_low  <= i_error_count_q[NB_BER/2 - 1 :        0];
            symb_count_q_high  <= i_symb_count_q [NB_BER   - 1 : NB_BER/2];
            symb_count_q_low   <= i_symb_count_q [NB_BER/2 - 1 :        0];
        end
    end
end

always @(*) begin
    case (control)
        (1'b1 << READ_ADDRESS_BIT):
            to_gpio = data_log;
        ((1'b1 << READ_BER_BIT) & (READ_ERROR_I)):
            to_gpio = error_count_i_high;
        ((1'b1 << READ_BER_BIT) & (READ_SYMB_I)):
            to_gpio = symb_count_i_high;
        ((1'b1 << READ_BER_BIT) & (READ_ERROR_Q)):
            to_gpio = error_count_q_high;
        ((1'b1 << READ_BER_BIT) & (READ_SYMB_Q)):
            to_gpio = symb_count_q_high;
        default: 
            to_gpio = 'd0;
    endcase
end

assign o_rst_dsp_n = rst_dsp_n;
assign o_switch = switch;
assign o_run_log = run_log;
assign o_read_log = read_log;
assign o_address = address;
assign o_gpio = to_gpio;
    
endmodule