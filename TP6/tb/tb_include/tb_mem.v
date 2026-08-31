    #10000;
    @(posedge clk);
    i_rst_n = 1'b1;
    i_switch = 4'b1011;

    // Sincronizar
    repeat(511*SYNC_PHASES*OS + 40000)
        @(posedge clk);

    // Leer sin haber logeado antes
    i_read_log = 1'b1;
    @(posedge clk);
    @(posedge clk);

    for (i = 0; i < 100; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end

    // Comenzar logeo (i_run_log necesita estar levantado durante 2 flancos)
    #10000;
    @(posedge clk);
    i_read_log = 1'b0;
    i_run_log = 1'b1;
    i_address = 'd0;
    @(posedge clk);
    @(posedge clk);
    i_run_log = 1'b0;

    repeat(2 * SIZE)
        @(posedge clk);
    
    // Leer memoria
    i_read_log = 1'b1;
    i_address = 10'h00F;
    repeat(4)
        @(posedge clk);
    i_address = 10'h3FF;
    @(posedge clk);
    @(posedge clk);
    i_address = 10'h00F;
    @(posedge clk);
    @(posedge clk);

    for (i = 0; i < SIZE; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end
    
    // Cambiar address sin leer
    @(posedge clk);
    i_read_log = 1'b0;

    for (i = 0; i < 100; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end

    // Leer y a la vez iniciar logeo (no debe iniciar)
    i_read_log = 1'b1;
    @(posedge clk);
    @(posedge clk);

    for (i = 0; i < 100; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end

    i_run_log = 1'b1;
    @(posedge clk);
    @(posedge clk);

    repeat(3)
        @(posedge clk);

    i_run_log = 1'b0;

    for (i = 500; i < 600; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end

    // Volver a leer desde 0
    i_read_log = 1'b0;
    i_run_log = 1'b1;
    @(posedge clk);
    @(posedge clk);
    i_run_log = 1'b0;

    repeat(2 * SIZE)
        @(posedge clk);

    i_read_log = 1'b1;
    @(posedge clk);
    @(posedge clk);

    for (i = 0; i < 100; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end

    // Resetear y volver a leer
    i_rst_n = 1'b0;
    
    #1000
    i_rst_n = 1'b1;
    i_read_log = 1'b0;
    i_run_log = 1'b1;
    @(posedge clk);
    @(posedge clk);
    i_run_log = 1'b0;

    repeat(2 * SIZE)
        @(posedge clk);

    i_read_log = 1'b1;
    @(posedge clk);
    @(posedge clk);

    for (i = 0; i < 100; i = i + 1) begin
        i_address = i;
        @(posedge clk);
    end