module tx 
#(
    // PRBS9
    parameter NB_PRBS   = 9                        ,
    parameter SEED_PRBS = {{NB_PRBS-1{1'b0}}, 1'b1},
    // Filtro
    parameter OS         = 4         ,
    parameter NB_COUNTER = $clog2(OS), // 2
    parameter N_BAUD     = 6         ,
    parameter NB_OUTPUT  = 8         ,
    parameter NBF_OUTPUT = 7         ,
    parameter NB_COEFF   = 8         ,
    parameter NBF_COEFF  = 7 
)
(
    output wire [NB_OUTPUT-1 : 0]  o_data  ,
    input  wire                    clk     ,
    input  wire                    i_rst_n ,
    input  wire                    i_enable,
    input  wire                    i_valid ,
    input  wire [NB_COUNTER-1 : 0] i_count
);

localparam NB_SUM     = 8 + $clog2(N_BAUD)    ; // 8 + 3 = 11
localparam NBF_SUM    = NBF_COEFF             ; // 7
localparam NBI_SUM    = NB_SUM - NBF_SUM      ; // 11 - 7 = 4
localparam NBI_OUTPUT = NB_OUTPUT - NBF_OUTPUT; // 8 - 7 = 1
localparam NB_SAT     = NBI_SUM - NBI_OUTPUT  ; // 4 - 1 = 3

// Lectura del archivo de coeficientes
reg signed [NB_COEFF-1 : 0] coeff [OS*N_BAUD-1 : 0];
initial begin
    $readmemh("coeff.mem", coeff);
end

// localparam signed [NB_COEFF-1 : 0] coeff_matrix [OS-1 : 0] [N_BAUD-1 : 0] = '{
//     '{coeff[23], coeff[19], coeff[15], coeff[11], coeff[7], coeff[3]}  // Fase 3
//     '{coeff[22], coeff[18], coeff[14], coeff[10], coeff[6], coeff[2]}, // Fase 2
//     '{coeff[21], coeff[17], coeff[13], coeff[9] , coeff[5], coeff[1]}, // Fase 1
//     '{coeff[20], coeff[16], coeff[12], coeff[8] , coeff[4], coeff[0]}, // Fase 0
// };

// PRBS
wire                 prbs_bit;
reg  [NB_PRBS-1 : 0] lfsr    ;
// Filtro
reg        [N_BAUD-1   : 1] input_filter                  ;
reg signed [NB_COEFF-1 : 0] prod         [OS*N_BAUD-1 : 0];
reg signed [NB_SUM-1   : 0] sum          [OS-1        : 0];
reg signed [NB_SUM-1   : 0] data                          ;

assign prbs_bit = lfsr[NB_PRBS-1]; // 0 -> 1 ; 1 -> -1

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        lfsr <= SEED_PRBS;
        input_filter <= {N_BAUD-1{1'b0}};
        data <= {NB_SUM{1'b0}};
    end
    else if(i_enable) begin

        if(i_valid) begin
            lfsr[NB_PRBS-1 : 1] <= lfsr[NB_PRBS-2 : 0];
            lfsr[0] <= prbs_bit ^ lfsr[4];

            input_filter[N_BAUD-1 : 2] <= input_filter[N_BAUD-2 : 1];
            input_filter[1] <= prbs_bit;
        end

        data <= sum[i_count]; // Probar
    end
end

// // Productos parciales
// generate
//     genvar baud;
//     genvar phase;

//     for(baud = 0; baud < N_BAUD; baud = baud + 1) begin
//         if (baud == 0)
//             for(phase = 0; phase < OS; phase = phase + 1)
//                 // Niego con "-" porque no puede haber overflow si el filtro esta normalizado
//                 assign prod[baud*OS + phase] = (prbs_bit) ? -coeff[baud*OS + phase] : coeff[baud*OS + phase];
//         else
//             for(phase = 0; phase < OS; phase = phase + 1)
//                 assign prod[baud*OS + phase] = (input_filter[baud]) ? -coeff[baud*OS + phase] : coeff[baud*OS + phase];
//     end
// endgenerate

// Productos y sumas
integer phase;
integer baud;

always @(*) begin

    // Productos
    for(baud = 0; baud < N_BAUD; baud = baud + 1) begin
        if (baud == 0)
            for(phase = 0; phase < OS; phase = phase + 1)
                // Niego con "-" porque no puede haber overflow si el filtro esta normalizado
                prod[baud*OS + phase] = (prbs_bit) ? -coeff[baud*OS + phase] : coeff[baud*OS + phase];
        else
            for(phase = 0; phase < OS; phase = phase + 1)
                prod[baud*OS + phase] = (input_filter[baud]) ? -coeff[baud*OS + phase] : coeff[baud*OS + phase];
    end

    // Sumas
    for(phase = 0; phase < OS; phase = phase + 1) begin
        sum[phase] = {NB_SUM{1'b0}};
        for(baud = 0; baud < N_BAUD; baud = baud + 1) begin
            sum[phase] = sum[phase] + prod[baud*OS + phase];
        end
    end
end

// Salida saturada
assign o_data = ( ~|data[NB_SUM-1 -: NB_SAT+1] || &data[NB_SUM-1 -: NB_SAT+1]) ? data[NB_SUM-(NBI_SUM-NBI_OUTPUT) - 1 -: NB_OUTPUT] :
                    (data[NB_SUM-1]) ? {{1'b1},{NB_OUTPUT-1{1'b0}}} : {{1'b0},{NB_OUTPUT-1{1'b1}}};
    
endmodule