/**********************CarryLookAhead****************************/
module CarryGenerator(p, g, c0, C_out, carry, P, G);
  
  input [3:0] p, g;
  input c0;
  
  output [2:0] carry;
  output P, G, C_out;
  
  wire [9:0] tmp;
  
  //C1
  and #1(tmp[0], p[0], c0);//p0c0
  or #1(carry[0], g[0], tmp[0]);//g0 + p0c0
  //C2
  and #1(tmp[1], p[1], p[0], c0);//p1p0c0
  and #1(tmp[2], p[1], g[0]);//p1g0
  or #1(carry[1], g[1], tmp[2], tmp[1]);//g1 + p1g0 + p1p0c0
  //C3
  and #1(tmp[3], p[2], g[1]);//p2g1
  and #1(tmp[4], p[2], p[1], g[0]);//p2p1g0
  and #1(tmp[5], p[2], p[1], p[0], c0);//p2p1p0c0
  or #1(carry[2], g[2], tmp[3], tmp[4], tmp[5]);//g2 + p2g1 + p2p1g0 + p2p1p0c0
  //C4
  and #1(tmp[6], p[3], g[2]);//p3g2
  and #1(tmp[7], p[3], p[2], g[1]);//p3p2g1
  and #1(tmp[8], p[3], p[2], p[1], g[0]);//p3p2p1g0
  and #1(tmp[9], p[3], p[2], p[1], p[0], c0);//p3p2p1p0c0
  or #1(C_out, g[3], tmp[6], tmp[7], tmp[8], tmp[9]);  
  //G
  or #1(G, g[3], tmp[6], tmp[7], tmp[8]);
  //P
  and #1(P, p[3],p[2], p[1], p[0]);
  
endmodule
/**************************** ONE BIT ADDER ****************************/
module Adder1(bit1, bit2, cin, p, g, sum);
 
  input bit1, bit2, cin;

  output p, g, sum;
  
  xor #1(p, bit1, bit2);
  and #1(g, bit1, bit2);
  xor #1(sum, cin, bit1, bit2);
  
endmodule

/*************************** FOUR BIT ADDER ****************************/
module Adder4(num1, num2, c0, P, G, sum);

  input [3:0] num1;
  input [3:0] num2;
  input c0;

  wire [2:0] carry;//Carry look ahead
  wire C_out;
  wire [3:0] p, g;
    
  output [3:0] sum;
  output P, G;//Propagation and Generation of 4 bits 
  
  Adder1 adder1(num1[0], num2[0], c0, p[0], g[0], sum[0]);
  Adder1 adder2(num1[1], num2[1], carry[0], p[1], g[1], sum[1]);
  Adder1 adder3(num1[2], num2[2], carry[1], p[2], g[2], sum[2]);
  Adder1 adder4(num1[3], num2[3], carry[2], p[3], g[3], sum[3]);
  CarryGenerator CG1(p, g, c0, C_Out, carry, P, G);
  
endmodule
/*********************************SIXTEEN BIT ADDER **************************************/
module Adder16(num1, num2, c0, P, G, sum);
  
  input [15:0] num1, num2;
  input c0;
  
  wire [3:0] carry;//Carry look ahead
  wire [3:0] p, g;
  wire C_out;
  
  output [15:0] sum;
  output P, G;//Propagation and Generation of 16 bits
  
  Adder4 Adder1(num1[3:0], num2[3:0], c0, p[0], g[0], sum[3:0]);  
  Adder4 Adder2(num1[7:4], num2[7:4], carry[0], p[1], g[1], sum[7:4]);
  Adder4 Adder3(num1[11:8], num2[11:8], carry[1], p[2], g[2], sum[11:8]);
  Adder4 Adder4(num1[15:12], num2[15:12], carry[2], p[3], g[3], sum[15:12]);
  CarryGenerator CG2(p, g, c0, C_out, carry, P, G);
  
endmodule
/************************** 64 Bit Adder ***************************/
module Adder64(num1, num2, c0, P, G, sum, overflow, C_out);

  input [63:0] num1, num2;
  input c0;
  
  wire [2:0] carry;//Carry look ahead
  wire [3:0] p, g;
  wire [4:0] tmp;

  output [63:0] sum;
  output P, G, C_out, overflow;//Propagation and Generation of 64 bits
  
  Adder16 Adder1(num1[15:0], num2[15:0], c0, p[0], g[0], sum[15:0]);  
  Adder16 Adder2(num1[31:16], num2[31:16], carry[0], p[1], g[1], sum[31:16]);
  Adder16 Adder3(num1[47:32], num2[47:32], carry[1], p[2], g[2], sum[47:32]);
  Adder16 Adder4(num1[63:48], num2[63:48], carry[2], p[3], g[3], sum[63:48]);
  CarryGenerator CG3(p, g, c0, C_out, carry[2:0], P, G);
  not #1(tmp[0], sum[31]);//sum_31Not
  not #1(tmp[1], num1[31]);//num1_31Not
  not #1(tmp[2], num2[31]);//num2_31Not
  and #1(tmp[3], tmp[0], num1[31], num2[31]);
  and #1(tmp[4], tmp[1], tmp[2], sum[31]);
  or #1(overflow, tmp[3], tmp[4]);
  
endmodule
/****************************Test_Bench*****************************/
module Adder64_TestBench;
  
  reg [63:0] num1, num2, Res;
  reg c0, COUT, OF;
  
  wire [63:0] sum, p, g;
  wire P, G, C_out, overflow;
  
  integer counter, fail;
  
  Adder64 adder(num1, num2, c0, P, G, sum, overflow, C_out);
  
  initial
  begin
    OF = 0;
    counter = 0;
    COUT = 0;
    fail = 0;
    $display("Test Bench Launched");
    for(counter = 0; counter < 10000; counter = counter + 1)
    begin
      num1[31:0] = $random();
      num1[63:32] = $random();
      num2[31:0] = $random();
      num2[63:32] = $random();
      c0 = $random();
      {COUT, Res} = num1 + num2 + c0;
      OF = (((num1[31] & num2[31]) & (~Res[31])) | (((~num1[31])&(~num2[31])) & Res[31]));//overflow flag
      #15 // because of overflow, without calculating overflow it will be 12
      $display("--------------------------------------------------------------------");
      $display("Test         %d\nNumber1             %d\nNumber2             %d\nC_in                %d\nExpected Result     %d\nSum Result          %d\nCarryOut%13d\nOVERFLOW%13d", (counter + 1), num1, num2, c0, Res ,sum, C_out, overflow);
      if((sum == Res) && (COUT == C_out) && (OF == overflow))
        $display("\n      Pass");
      else
        begin
          fail = fail + 1;
          $display("\n      Fail");      
        end
    end
    $display("-----------------------------------------------------------------------");
    $display("Failed Tests:  %d", fail);
    $stop;
  end
  
endmodule
