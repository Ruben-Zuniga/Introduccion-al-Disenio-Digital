    #10000;
    @(posedge clk);
    i_switch = 4'b1011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1001;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1010;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1001;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1000;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1010;
    
    #10000;
    @(posedge clk);
    i_switch = 4'b1011;

    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);