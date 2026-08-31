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

// Comandos desde el GPIO
localparam READ_ADDRESS = 8'h20;
localparam READ_BER = 8'h40;

localparam ERROR_I_HIGH = 23'h0;
localparam ERROR_I_LOW  = 23'h1;
localparam SYMB_I_HIGH  = 23'h2;
localparam SYMB_I_LOW   = 23'h3;
localparam ERROR_Q_HIGH = 23'h4;
localparam ERROR_Q_LOW  = 23'h5;
localparam SYMB_Q_HIGH  = 23'h6;
localparam SYMB_Q_LOW   = 23'h7;

// Comandos hacia el DSP
reg                    rst_dsp_n_r;
reg [NB_SWITCH -1 : 0] switch   ;
reg                    run_log_r  ;
reg                    read_log ;
reg [NB_SIZE   -1 : 0] address_r  ;

// Datos desde el DSP
reg [NB_GPIO   -1 : 0] data_log ;
reg [NB_GPIO   -1 : 0] symb_count_i_low ;
reg [NB_GPIO   -1 : 0] symb_count_i_high ;
reg [NB_GPIO   -1 : 0] symb_count_q_low ;
reg [NB_GPIO   -1 : 0] symb_count_q_high ;
reg [NB_GPIO   -1 : 0] error_count_i_low;
reg [NB_GPIO   -1 : 0] error_count_i_high;
reg [NB_GPIO   -1 : 0] error_count_q_low;
reg [NB_GPIO   -1 : 0] error_count_q_high;

// Registro hacia el GPIO
reg [NB_GPIO   -1 : 0] to_gpio;

// Comandos desde el GPIO - registro de cada comando
// Campo de comando
reg [NB_COMMAND-1 : 0] command_rf;
reg enable;
reg rst_dsp_n;
reg toggle_tx_rx;
reg tx;
reg rx;
reg run_log;
reg read_address;
reg read_ber;
// Campo de datos
reg [NB_DATA_RF-1 : 0] data_rf;
reg [NB_COUNTER-1 : 0] phase;
reg [NB_SIZE-1 : 0] address;
reg [2 : 0] ber_type;

always @(*) begin
    enable       = i_gpio[ENABLE_BIT];
    rst_dsp_n    = !i_gpio[RST_BIT];
    toggle_tx_rx = i_gpio[TOGGLE_TX_RX_BIT];
    tx           = i_gpio[TX_BIT];
    rx           = i_gpio[RX_BIT];
    run_log      = i_gpio[RUN_LOG_BIT];
    read_address = i_gpio[READ_ADDRESS_BIT];
    read_ber     = i_gpio[READ_BER_BIT];
    phase        = i_gpio[NB_COUNTER-1 : 0];
    address      = i_gpio[NB_SIZE-1 : 0];
    ber_type     = i_gpio[2 : 0];

    command_rf = i_gpio[NB_GPIO-1 -: NB_COMMAND]; // ultimos 8 bits
    data_rf = i_gpio[0 +: NB_DATA_RF]; // primeros 23 bits

    to_gpio      = 'd0;
    case (command_rf)
        READ_ADDRESS: to_gpio = data_log;
        READ_BER:
            case (data_rf)
                ERROR_I_HIGH: to_gpio = error_count_i_high;
                ERROR_I_LOW: to_gpio = error_count_i_low;
                SYMB_I_HIGH: to_gpio = symb_count_i_high;
                SYMB_I_LOW: to_gpio = symb_count_i_low;
                ERROR_Q_HIGH: to_gpio = error_count_q_high;
                ERROR_Q_LOW: to_gpio = error_count_q_low;
                SYMB_Q_HIGH: to_gpio = symb_count_q_high;
                SYMB_Q_LOW: to_gpio = symb_count_q_low;
            endcase
    endcase
end

always @(posedge clk or negedge i_rst_n) begin
    if (!i_rst_n) begin
        rst_dsp_n_r <= 1'b0;
        switch <= 'd0;
        run_log_r <= 'd0;
        read_log <= 'd0;
        address_r <= 'd0;
        data_log <= 'd0;

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
        // Leer bit de enable del GPIO
        if (enable) begin
            // Reset del DSP
            rst_dsp_n_r <= rst_dsp_n;

            // TX y RX ON/OFF + fase
            if (toggle_tx_rx) begin
                switch[0] <= tx;
                switch[1] <= rx;
                if (rx)
                    switch[3:2] <= phase;
            end

            // Run log
            run_log_r <= run_log;

            // Read 1 address - Aca la memoria va a tardar en dar el dato
            if (read_address) begin
                read_log <= 1'b1;
                address_r <= address;
                data_log <= {i_full_mem, i_data_log[NB_LOG - 2 : 0]};
            end
            else
                read_log <= 1'b0;

            // Read BER
            if (read_ber) begin
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
end

assign o_rst_dsp_n = rst_dsp_n_r;
assign o_switch = switch;
assign o_run_log = run_log_r;
assign o_read_log = read_log;
assign o_address = address_r;
assign o_gpio = to_gpio;
    
endmodule