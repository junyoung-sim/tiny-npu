`ifndef ADDER_V
`define ADDER_V

module Adder
#(
  parameter NBITS = 8
)(
  input  logic [NBITS-1:0] in0,
  input  logic [NBITS-1:0] in1,
  output logic [NBITS-1:0] out
);

  assign out = (in0 + in1);

endmodule

`endif