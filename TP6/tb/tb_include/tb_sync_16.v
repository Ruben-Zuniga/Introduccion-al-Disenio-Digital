    #10000;
    @(posedge clk);
    i_switch = 4'b1011;

    for (i = 0; i < N_LOG; i = i + 1) begin
        @(posedge clk);
        
        if(i % OS == 0) begin
            if (prbs_tx != prbs_tx_log[i / OS])
                vm_prbs_tx_errors = vm_prbs_tx_errors + 1;
            if ((i/OS > 0) && (bits_rx != bits_rx_log[i/OS - 1]))
                vm_bits_rx_errors = vm_bits_rx_errors + 1;
        end

        if(data != data_log[i])
            vm_data_errors = vm_data_errors + 1;
    end

    repeat(511*SYNC_PHASES*OS)
        @(posedge clk);
    
    @(posedge clk);
    i_switch = 4'b0111;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    i_switch = 4'b0011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    @(posedge clk);
    i_switch = 4'b1111;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);