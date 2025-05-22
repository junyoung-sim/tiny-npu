`ifndef MUX_V
`define MUX_V

module Mux
#(
  parameter SIZE  = 4,
  parameter NBITS = 8
)(
  input  logic [NBITS-1:0]        in0 [SIZE],
  input  logic [$clog2(SIZE)-1:0] sel,
  output logic [NBITS-1:0]        out
);

  assign out = in0[sel];

endmodule

`endif