module registerFile(ReadEnable, clk, in, RegisterNum1, RegisterNum2, out1, out2);
  input ReadEnable, clk;
  input [4:0] RegisterNum1, RegisterNum2;
  input [31:0] in;
  
  output [31:0] out1, out2;
  
  reg [31:0] rFile [31:0];
  reg [31:0] out1, out2;
  
  always @(posedge clk)
  begin
    if(ReadEnable == 0)
      begin
        rFile[RegisterNum1] <= in;
      end
    else
      begin
        out1 <= rFile[RegisterNum1];
        out2 <= rFile[RegisterNum2];
      end
      
  end
    
endmodule


module registerFile_testbench;
  reg [31:0] data;
  reg clk, read;
  reg [4:0] register1, register2;
  
  wire [31:0] out1, out2;
  
  integer i;
  
  registerFile RF(read, clk, data, register1, register2, out1, out2);
  
  always #10 clk = ~clk;
  
  initial
  begin
    clk = 0;
  end
  
  initial
  begin
    $display("Here we write a data in two registers, then we read them to test");
    for(i = 0; i < 32; i = i + 1)
    begin
      read = 0;
      data = $random;
      register1 = i;
      #30
      read = 1;
      #30
      if(out1 == data)
        begin
          $display("Case %d Passed", i+1);
          $display("Data to write: %d\nRegister Value : %d", data, out1);
        end
        
      else
      begin
        $display("Case %d Failed\nData to write : %d, out1 = %d", i+1, data, out1);
      end
    end
    for(i = 0; i < 32; i = i + 1)
    begin
      data = i;
      register1 = i;
      read = 0;
      #30;
    end
    $display("Filling registers with 0 to 31\nTesting two read operation");
    for(i = 0; i < 32; i = i + 2)
    begin
      register1 = i;
      register2 = i + 1;
      read = 1;
      #50
      if(out1 == i && out2 == i + 1)
      begin
        $display("Case %d Passed\nRegister1 Value: %d\nRegister2 Value: %d", 33 + i, out1, out2);
      end
      else
      begin
        $display("Case %d Failed\nRegister1 Value: %d, right value: %d\nRegister2 Value: %d, right value: %d", 33 + i, out1, i, out2, i + 1);
      end
    end
    
    $display("\n\nNow Testing just Write without using a read after it to check\n\n);
    
    for(i = 0; i < 32; i = i + 1)
    begin
      read = 0; //so it will write a data
      data = $random;
      register1 = $random;
      register1 = register1 % 32;
      #30
      if(RF.rFile[register1] == data)
        begin
          $display("Case %d Passed", 65 + i);
          $display("Data to write: %d\nRegister Value : %d", data, RF.rFile[register1]);
        end
        
      else
      begin
        $display("Case %d Failed\nData to write : %d, Register Value = %d", 65 + i, data, RF.rFile[register1]);
      end
    end
  end
endmodule