`ifndef DEMUX_V
`define DEMUX_V

module Demux
#(
  parameter SIZE  = 4,
  parameter NBITS = 8
)(
  input  logic [NBITS-1:0]        in0,
  input  logic [$clog2(SIZE)-1:0] sel,
  output logic [NBITS-1:0]        out [SIZE]
);

  always_comb begin
    for(int i = 0; i < SIZE; i++) begin
      out[i] = ((i == sel) ? in0 : 0);
    end
  end

endmodule

`endif