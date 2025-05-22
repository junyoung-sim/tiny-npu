`ifndef MAC_V
`define MAC_V

`include "Reg.v"
`include "Multiplier.v"

module MAC
#(
  parameter NBITS = 8,
  parameter DBITS = 4
)(
  input  logic             clk,
  input  logic             rst,
  input  logic             istream_val,
  input  logic             ostream_req,
  input  logic [NBITS-1:0] x_in,
  input  logic [NBITS-1:0] w_in,
  output logic [NBITS-1:0] z_out
);

  //=======================================================
  // Pipeline Enables
  //=======================================================

  logic s0_en;
  logic s1_en;
  logic s2_en;
  logic s3_en;

  assign s0_en = istream_val;

  Reg #(1) s0s1_en_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (1'b1),
    .d   (s0_en),
    .q   (s1_en)
  );

  Reg #(1) s1s2_en_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (1'b1),
    .d   (s1_en),
    .q   (s2_en)
  );

  assign s3_en = ostream_req;

  //=======================================================
  // Stage 0
  //=======================================================

  logic [NBITS-1:0] x;
  logic [NBITS-1:0] w;

  Reg #(NBITS) s0_x_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (s0_en),
    .d   (x_in),
    .q   (x)
  );

  Reg #(NBITS) s0_w_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (s0_en),
    .d   (w_in),
    .q   (w)
  );

  //=======================================================
  // Stage 1
  //=======================================================

  logic [NBITS-1:0] _mul;
  logic [NBITS-1:0] mul;

  Multiplier #(NBITS, DBITS) s1_multiplier
  (
    .in0 (x),
    .in1 (w),
    .out (_mul)
  );

  Reg #(NBITS) s1_mul_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (s1_en),
    .d   (_mul),
    .q   (mul)
  );

  //=======================================================
  // Stage 2
  //=======================================================

  logic [NBITS-1:0] _sum;
  logic [NBITS-1:0] sum;

  Adder #(NBITS) s2_adder
  (
    .in0 (mul),
    .in1 (sum),
    .out (_sum)
  );

  Reg #(NBITS) s2_sum_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (s2_en),
    .d   (_sum),
    .q   (sum)
  );

  //=======================================================
  // Stage 3
  //=======================================================

  logic [NBITS-1:0] _z_out;

  ReLU #(NBITS) s3_relu
  (
    .in0 (sum),
    .out (_z_out)
  );

  Reg #(NBITS) s3_z_out_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (s3_en),
    .d   (_z_out),
    .q   (z_out)
  );

endmodule

`endif