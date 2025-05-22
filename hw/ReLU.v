`ifndef RELU_V
`define RELU_V

module ReLU
#(
  parameter NBITS = 8
)(
  input  logic [NBITS-1:0] in0,
  output logic [NBITS-1:0] out
);

  assign out = (in0[NBITS-1] ? 0 : in0);

endmodule

`endif