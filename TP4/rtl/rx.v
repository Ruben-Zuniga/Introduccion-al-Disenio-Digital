module rx
#(
    parameter NB_PRBS = 9,
    parameter SEED_PRBS = {{NB_PRBS-1{1'b0}}, 1'b1},
    parameter OS = 4,
    parameter NB_COUNTER = $clog2(OS), // 2
    parameter NB_DATA = 8,
    parameter SYNC_PHASES = 1024,
    parameter NB_ERRORS = 64
)
(
    output wire o_led,
    output wire [NB_ERRORS-1 : 0] o_errors,
    input  wire                    clk     ,
    input  wire                    i_rst_n ,
    input  wire                    i_enable,
    input  wire                    i_valid ,
    input wire [NB_COUNTER-1 : 0] i_phase,
    input wire signed [NB_DATA-1 : 0] i_data
);

integer i;

// Decimador
reg signed [NB_DATA-1 : 0] input_phase [OS-2 : 0]; // 3 registros
reg signed [NB_DATA-1 : 0] decimated;
wire data_bit;

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        for (i = 0; i < OS-1; i = i + 1) begin
            input_phase[i] <= {NB_DATA{1'b0}};
        end
        decimated <= 1'b0;
    end
    else if(i_enable) begin
        if(i_valid) begin
            if(~|i_phase)
                decimated <= i_data;
            else
                decimated <= input_phase[i_phase - 1];
        end

        for (i = 0; i < OS-1; i = i + 1) begin
            if(i == 0)
                input_phase[0] <= i_data;
            else
                input_phase[i] <= input_phase[i - 1];
        end
    end
end

assign data_bit = decimated[NB_DATA-1];

// PRBS del receptor
wire                 prbs_bit;
reg  [NB_PRBS-1 : 0] lfsr    ;

assign prbs_bit = lfsr[NB_PRBS-1]; // 0 -> 1 ; 1 -> -1

always @(posedge clk or negedge i_rst_n) begin
    if(!i_rst_n) begin
        lfsr <= SEED_PRBS;
    end
    else if(i_enable) begin
        if(i_valid) begin
            lfsr[NB_PRBS-1 : 1] <= lfsr[NB_PRBS-2 : 0];
            lfsr[0] <= prbs_bit ^ lfsr[4];
        end
    end
end

// Correlador: maquina de estados
localparam NB_CORR_COUNTER = $clog2(SYNC_PHASES); // 10
localparam PRBS_SEQUENCES = 2**NB_PRBS - 1; // 511
localparam NB_SEQUENCE_COUNTER = $clog2(PRBS_SEQUENCES + 1); // 9
// Estados
localparam SEQUENCEE = 2'd0;
localparam PHASE = 2'd1;
localparam RESET_ERRORS = 2'd2;
localparam SYNCED = 2'd3;
    
reg [1:0] state;
reg [1:0] state_next;
reg [NB_ERRORS-1 : 0] errors; // Nro de errores
reg [NB_COUNTER-1 : 0] phase_prev;

reg [SYNC_PHASES-2 : 0] sync_register;
reg [NB_CORR_COUNTER-1 : 0] corr_count;
reg [NB_CORR_COUNTER-1 : 0] min_error_phase;
reg [NB_ERRORS-1 : 0] min_error;
reg [NB_SEQUENCE_COUNTER-1 : 0] sequence_count;

always @(posedge clk or negedge i_rst_n) begin
    if (!i_rst_n) begin
        state <= SEQUENCEE;
        sync_register <= {SYNC_PHASES-1{1'b0}};
        errors <= {NB_ERRORS{1'b0}};
        min_error <= {NB_ERRORS{1'b1}};
        min_error_phase <= {NB_CORR_COUNTER{1'b0}};
        sequence_count <= {NB_SEQUENCE_COUNTER{1'b0}};
        corr_count <= {NB_CORR_COUNTER{1'b0}};
        phase_prev <= i_phase;
    end
    else if (i_enable) begin
        if (i_valid) begin
            // Pasar al estado siguiente
            state <= state_next;
            // Guardar la fase anterior
            phase_prev <= i_phase;
            // Desplazar registro de sync del prbs
            sync_register[SYNC_PHASES-2 : 1] <= sync_register[SYNC_PHASES-3 : 0];
            sync_register[0] <= prbs_bit;

            case (state)
                SEQUENCEE: begin
                    // Comparar bit de llegada con bit del prbs
                    errors <= errors + (data_bit ^ prbs_shifted);
                    // Incrementar contador de secuencia
                    sequence_count <= sequence_count + 1'b1;
                end
                PHASE: begin
                    // Actualizar el error minimo y la fase correspondiente
                    if(errors <= min_error) begin
                        min_error <= errors;
                        min_error_phase <= corr_count;
                    end

                    // Incrementar contador de fase
                    corr_count <= corr_count + 1'b1;
                    // Resetear errores y contador de secuencia
                    errors <= {NB_ERRORS{1'b0}};
                    sequence_count <= {NB_SEQUENCE_COUNTER{1'b0}};
                end
                RESET_ERRORS: begin
                    // Resetear errores
                    errors <= {NB_ERRORS{1'b0}};
                    // Fijar fase sincronizada
                    corr_count <= min_error_phase;
                end
                SYNCED: begin
                    errors <= errors + (data_bit ^ prbs_shifted);
                end
            endcase
        end
    end
    else begin
        // Resetear el estado si el enable esta en bajo
        state <= SEQUENCEE;
    end
end

always @(*) begin
    case (state)
        SEQUENCEE: begin
            if ((sequence_count >= (PRBS_SEQUENCES - 2)) && (i_phase == phase_prev))
                state_next = PHASE;
            else
                state_next = SEQUENCEE;
        end
        PHASE: begin
            if (&corr_count && (i_phase == phase_prev))
                state_next = RESET_ERRORS;
            else
                state_next = SEQUENCEE;
        end
        RESET_ERRORS: begin
            if(i_phase == phase_prev)
                state_next = SYNCED;
            else
                state_next = SEQUENCEE;
        end
        SYNCED: begin
            if(i_phase == phase_prev)
                state_next = SYNCED;
            else
                state_next = SEQUENCEE;
        end
        default: 
            state_next = SEQUENCEE;
    endcase
end

assign prbs_shifted = (corr_count == 0) ? prbs_bit : sync_register[corr_count - 1];
assign o_errors = errors;
assign o_led = ((state == SYNCED) & ~|errors) ? 1'b1 : 1'b0;

// // Correlador (Arreglar que se ve muy feo)
// localparam NB_CORR_COUNTER = $clog2(SYNC_PHASES); // 10
// localparam PRBS_SEQUENCES = 2**NB_PRBS - 1; // 511
// localparam NB_SEQUENCE_COUNTER = $clog2(PRBS_SEQUENCES + 1); // 9

// reg [SYNC_PHASES-2 : 0] sync_register;
// reg [NB_CORR_COUNTER-1 : 0] corr_count;
// reg [NB_CORR_COUNTER-1 : 0] min_error_phase;
// reg [NB_ERRORS-1 : 0] min_error;
// reg [NB_SEQUENCE_COUNTER-1 : 0] sequence_count;
// reg synced;
// wire prbs_shifted;

// // reg [NB_ERRORS-1 : 0] errors [SYNC_PHASES-1 : 0]; // Registro de errores por fase
// reg [NB_ERRORS-1 : 0] errors; // Nro de errores cuando No esta sincronizado
// reg [NB_ERRORS-1 : 0] errors_synced; // Nro de errores cuando esta sincronizado

// always @(posedge clk or negedge i_rst_n) begin
//     if (!i_rst_n) begin
//         synced <= 1'b0;

//         sync_register <= {SYNC_PHASES{1'b0}};
//         corr_count <= {NB_CORR_COUNTER{1'b0}};
//         sequence_count <= {NB_SEQUENCE_COUNTER{1'b0}};

//         min_error <= {NB_ERRORS{1'b1}};
//         min_error_phase <= {NB_CORR_COUNTER{1'b0}};
        
//         // for (i = 0; i < SYNC_PHASES; i = i + 1) begin // probar
//         //     errors[i] <= {NB_ERRORS{1'b0}};
//         // end
//         errors <= {NB_ERRORS{1'b0}};
//         errors_synced <= {NB_ERRORS{1'b0}};
//     end
//     else if (i_enable & i_valid) begin

//         if (!synced) begin
//             // errors[corr_count] <= errors[corr_count] + (data_bit ^ prbs_shifted);
//             errors <= errors + (data_bit ^ prbs_shifted);
//             sequence_count <= sequence_count + 1'b1;

//             if (&sequence_count) begin
//                 // if(errors[corr_count] <= min_error) begin
//                 //     min_error <= errors[corr_count];
//                 //     min_error_phase <= corr_count;
//                 // end
//                 if(errors <= min_error) begin
//                     min_error <= errors;
//                     min_error_phase <= corr_count;
//                 end

//                 corr_count <= corr_count + 1'b1;
//                 errors <= {NB_ERRORS{1'b0}};
//                 sync_register[SYNC_PHASES-1 : 1] <= sync_register[SYNC_PHASES-2 : 0];
//                 sync_register[0] <= prbs_bit;

//                 if (&corr_count) begin
//                     synced <= 1'b1;
//                 end
//             end
//         end
//         else begin
//             errors_synced <= errors_synced + (data_bit ^ prbs_shifted);
//         end
//     end
// end

// assign prbs_shifted = (min_error_phase == 0) ? prbs_bit : sync_register[min_error_phase - 1];
// assign o_led = (~|errors_synced & synced) ? 1'b1 : 1'b0;

endmodule