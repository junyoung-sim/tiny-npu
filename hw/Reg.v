`ifndef REG_V
`define REG_V

module Reg
#(
  parameter NBITS = 8
)(
  input  logic             clk,
  input  logic             rst,
  input  logic             en,
  input  logic [NBITS-1:0] d,
  output logic [NBITS-1:0] q
);

  always_ff @(posedge clk) begin
    if(rst)
      q <= 0;
    else
      q <= (en ? d : q);
  end

endmodule

`endif