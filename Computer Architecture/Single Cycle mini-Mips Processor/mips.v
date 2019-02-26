/****************************************************Mips CPU**********************************************************/
module ALU(result, carry, overflow, Zero, data1, data2, operation);
  input [31:0] data1, data2;
  input [2:0]operation;
  
  output overflow, carry, Zero;
  output [31:0]result;
  
  reg [31:0]result;
  reg overflow, carry, Zero;
  reg [31:0]complement;
  
  always @(data1 or data2 or operation) 
  begin
    case(operation)
        3'b010 : //add
        begin
          {carry, result} = data1 + data2;
          overflow = 0;
          if((data1[31] == data2[31]) && (result[31] != data1[31]))
          begin
            overflow = 1;
            carry = 0;
          end
        end
        3'b110 : //subtract
        begin
          /*complement = ~data2;
          complement = complement + 1;
          {carry, result} = data1 + complement;*/
          {carry, result} = data1 - data2;
          if((data1[31] == data2[31]) && (result[31] != data1[31]))
          begin
            overflow = 1;
          end
        end
        3'b000 : begin
          result = (data1 | data2); //OR
          $display("OR %d %d %d", data1, data2, result);
        end
        3'b001 : result = (data1 & data2); //AND
        3'b111 : //SLT
        begin
          /*if(data1[31] > data2[31])
          begin
            result = 1;
          end
          else if(data1[31] < data2[31])
          begin
            result = 0;
          end
          else
          begin
            if(data1[31] == 0)
              if(data1 < data2)
                result = 1;
              else
                result = 0;
            else
              if(data1 > data2)
                result = 1;
              else
                result = 0;
          end*/
          if($signed(data1) < $signed(data2))
            result = 1;
          else 
            result = 0;
        end
      endcase
	  Zero = (result == 0);
  end
endmodule
/*************************************************************************/
module registerFile(out1, out2, WriteEnable, clk, data, regToWrite, RegisterNum1, RegisterNum2, Reset);

  input WriteEnable, clk, Reset;
  input [4:0] regToWrite, RegisterNum1, RegisterNum2;
  input [31:0] data;
  
  output [31:0] out1, out2;
  
  integer counter;
  
  reg [31:0] Reg [31:0];
  wire [31:0] out1, out2;
  
  always @(posedge clk or posedge Reset)
  begin
    Reg[0] = 0;
    if(Reset == 1)
      begin
        for(counter = 1; counter < 32; counter = counter + 1)
        begin
          Reg[counter] = 0;
        end
      end
    if((WriteEnable == 1) && (Reset == 0) && (regToWrite != 0)) //register 0 should always be zero;
      begin
        Reg[regToWrite] = data;
      end
  end 
	assign out1 = Reg[RegisterNum1];
    assign out2 = Reg[RegisterNum2];
endmodule
/*************************************************************************/
module InstMem(out, address);
	reg [31:0] Mem [1023:0];
	
	input [9:0] address;
	
	output [31:0] out;
	
	assign out = Mem[address];
endmodule
/************************************************************************/
module DataMem(out, clk, address, memRead, memWrite, data, reset);
  output [31:0] out;
  
	reg [31:0] Mem [1023:0];
	wire [31:0] out;
	
	input [31:0] address, data;
	input memRead, memWrite, clk, reset;
	
	integer i;
	always @(posedge clk or posedge reset)begin
		if(reset == 1)begin
			for(i = 0; i < 1024; i = i + 1)begin
				Mem[i] = 0;
			end
		end
		else begin
			/*if(memRead)begin
			  out = Mem[address];
			end*/
			if(memWrite == 1) begin
				Mem[address] = data;
			end
		end
	end
	assign out = Mem[address];
endmodule
/************************************************************************/
module ProgramCounter(Q, D, clk, reset);
	input clk, reset;
	input [31:0] D;
	
	output [31:0] Q;
	
	reg [31:0] Q;

	always @(posedge clk, posedge reset) begin
		if(reset == 1)
			Q = 0;
		else
			Q = D;
	end
endmodule
/************************************************************************/
module Adder(sum, num1, num2);
	input [31:0] num1, num2;
	
	output [31:0] sum;
	
	assign sum = num1 + num2;
endmodule
/*************************************************************************/
module MUX2(out, in1, in2, select);
	input [31:0] in1, in2;
	input select;
	
	output [31:0] out;
	reg [31:0] out;
	always @(*) begin
		out = (select == 0) ? in1 : in2;
	end
endmodule
/*************************************************************************/
module MUX4_5(out, in1, in2, in3, in4, select);
	input [4:0] in1, in2, in3, in4;
	input [1:0] select;
	output reg [4:0] out;
	always @(*) begin
		case(select)
			0 : out = in1;
			1 : out = in2;
			2 : out = in3;
			3 : out = in4;
		endcase
	end
endmodule
/*************************************************************************/
module MUX4(out, in1, in2, in3, in4, select);
	input [31:0] in1, in2, in3, in4;
	input [1:0] select;
	output [31:0] out;
	reg [31:0] out;
	always @(*)begin
		case(select)
			2'b00 : out = in1;
			2'b01 : out = in2;
			2'b10 : out = in3;
			2'b11 : out = in4;
		endcase
	end
endmodule
/*************************************************************************/
module SignExtend(signExt, data);
	input [15:0] data;

	output [31:0] signExt;
	
	reg [31:0] signExt;
	
	integer i;
	
	always @(data) begin
		signExt = data;
		for(i = 16; i < 32; i = i + 1) begin
			signExt[i] = data[15];
		end
	end
endmodule
/*************************************************************************/
module Shift(shiftedValue, data);
	input [31:0] data;
	
	output [31:0] shiftedValue;
	
	assign shiftedValue = data << 2;
endmodule
/*************************************************************************/
module Controller(ALUop, regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc, opcode, funct, Zero);
	input [5:0] opcode, funct;
	input Zero;
	
	output [2:0] ALUop;
	output ALUsrc, regWrite, memRead, memWrite;
	output [1:0] PCsrc, regDst, memToReg;
	
	reg [2:0] ALUop;
	reg ALUsrc, regWrite, memRead, memWrite;
	reg [1:0] PCsrc, regDst, memToReg;
	
	always @(opcode or funct) begin
		case(opcode)
			6'b000000: begin	//R Type
				PCsrc = 2'b11;
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg} = 8'b10_0_1_0_0_01;
				case(funct)
					6'b100000: begin //ADD
						ALUop = 3'b010;
					end
					6'b100010: begin	//SUB
						ALUop = 3'b110;
					end
					6'b100100: begin //AND
						ALUop = 3'b001;
					end
					6'b100101: begin //OR
						ALUop = 3'b000;
					end
					6'b101010: begin //SLT
						ALUop = 3'b111;
					end
					6'b001000: begin //JR
						PCsrc = 2'b01;
						regWrite = 0;
					end
				endcase
			end
			6'b001000: begin //ADDI
				ALUop = 3'b010;
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc} = 10'b01_1100_01_11;
			end
			6'b100011: begin //LW
				ALUop = 3'b010;
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc} = 10'b01_1110_00_11;
			end
			6'b101011: begin //SW
				ALUop = 3'b010;
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc} = 10'bxx_1001_xx_11;
			end
			6'b000100: begin //BEQ
				ALUop = 3'b110;
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg} = 8'bxx_0000_xx;
				if(Zero == 1)begin
				  PCsrc = 2'b00;
				end	
				else begin
				  PCsrc =  2'b11;
				end
			end
			6'b000010: begin //J
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc} = 10'bxx_x000_xx_10;
			end
			6'b000011:begin //JAL
				{regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc} = 10'b00_x100_10_10;
			end
		endcase	
	end
endmodule
/***********************************************************************************/
module DataPath(inst, zero, carry, overflow, clk, reset, ALUop, regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc);
	input clk, reset, ALUsrc, regWrite, memRead, memWrite;
	input [1:0] regDst, memToReg, PCsrc;
	input [2:0] ALUop;
	
	output [31:0] inst;
	output zero, carry, overflow;	
	
	ProgramCounter PC(, muxPCsrc.out, clk, reset);
	
	registerFile RegFile(, , regWrite, clk, muxRegData.out, muxRegDst.out, instMem.out[25:21], instMem.out[20:16], reset);
	//registerFile(out1,out2, WriteEnable, clk, data, regToWrite, RegisterNum1, RegisterNum2, Reset);
	ALU alu(, carry, overflow, zero, RegFile.out1, muxAlu.out, ALUop);
	//module ALU(result, carry, overflow, Zero, data1, data2, operation);
	DataMem dataMem(, clk, alu.result, memRead, memWrite, RegFile.out2, reset);
	//module DataMem(out, clk, address, memRead, memWrite, data, reset);
	InstMem instMem(inst, PC.Q[11:2]);
	//module InstMem(out, address);
	Adder PC4(, PC.Q, 4);
	//module Adder(sum, num1, num2);
	Adder Branch(, PC4.sum, shift.shiftedValue);
	
	Shift shift(, signExtend.signExt);
	SignExtend signExtend(, instMem.out[15:0]);
	
	MUX2 muxAlu(, RegFile.out2, signExtend.signExt, ALUsrc);
	MUX4 muxRegData(, dataMem.out, alu.result, PC4.sum, 0, memToReg);
	MUX4_5 muxRegDst(, 5'b11111, instMem.out[20:16], instMem.out[15:11], 5'b00000, regDst);
	MUX4 muxPCsrc(, Branch.sum, RegFile.out1, {PC4.sum[31:28], instMem.out[25:0], 2'b00}, PC4.sum, PCsrc);	
endmodule
/***********************************************************************************/
module MipsCPU(Zero, Carry, Overflow, Clock, Reset);
	input Clock, Reset;
	
	output Zero, Carry, Overflow;
	
	wire  ALUsrc, regWrite, memRead, memWrite;
	wire [1:0] PCsrc, memToReg, regDst;
	wire [2:0] ALUop;
	wire [31:0] inst;

    Controller controller(ALUop, regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc, inst[31:26], inst[5:0], Zero);
	DataPath datapath(inst, Zero, Carry, Overflow, Clock, Reset, ALUop, regDst, ALUsrc, regWrite, memRead, memWrite, memToReg, PCsrc);
endmodule
/***********************************************************************************/

module CPUtest();
	reg Reset, Clock;
	
	wire Zero, Carry, Overflow;
	
	integer i, j;
	
	MipsCPU Mips(Zero, Carry, Overflow, Clock, Reset);

	initial begin
		Clock = 0;
		Reset = 1;
		#1 Reset = 0;
	end
	
	always #50 Clock = ~Clock;
	
	initial begin
	  $readmemh("code.txt", Mips.datapath.instMem.Mem);
		for(i = 0; i < 1024; i = i + 1)begin
			$display("%d : %h", i, Mips.datapath.instMem.Mem[i]);
		end
		while(1) begin
		  if (Mips.datapath.instMem.out == 32'h1000ffff)begin
		    $display("Finish");
		    $stop;
		  end
		  #100;
		  $display("\n%h\n", Mips.datapath.instMem.out);
    		/*for(i = 0; i < 10; i = i + 1) begin
				$display("%d %d", i, Mips.datapath.dataMem.Mem[i]);
			end*/
			$display("------------------------");
			for(i = 0; i < 32; i = i + 1) begin
				$display("%d %d", i, Mips.datapath.RegFile.Reg[i]);
			end
		end
	end
endmodule

