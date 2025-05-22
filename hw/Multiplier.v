`ifndef MULTIPLIER_V
`define MULTIPLIER_V

module Multiplier
#(
  parameter NBITS = 8,
  parameter DBITS = 4
)(
  input  logic [NBITS-1:0] in0,
  input  logic [NBITS-1:0] in1,
  output logic [NBITS-1:0] out
);

  logic [NBITS+DBITS-1:0] in0_ext;
  logic [NBITS+DBITS-1:0] in1_ext;
  logic [NBITS+DBITS-1:0] prod;

  assign in0_ext = {{(DBITS){in0[NBITS-1]}}, in0};
  assign in1_ext = {{(DBITS){in1[NBITS-1]}}, in1};

  assign prod = (in0_ext * in1_ext);
  assign out  = prod[NBITS+DBITS-1:DBITS];

endmodule

`endif