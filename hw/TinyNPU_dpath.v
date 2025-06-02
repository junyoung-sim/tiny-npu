`ifndef TINYNPU_DPATH_V
`define TINYNPU_DPATH_V

`include "Mux.v"
`include "FIFO.v"

module TinyNPU_dpath
#(
  parameter SIZE  = 4,
  parameter NBITS = 8,
  parameter DBITS = 4
)(
  input logic clk,
  input logic rst,

  input logic [NBITS-1:0] x_in,
  input logic [NBITS-1:0] w_in,

  input logic x_load_val,
  input logic w_load_val,
  input logic [$clog2(SIZE)-1:0] w_load_sel,

  //

  input logic c2d_x_sel,
  input logic c2d_x_fifo_wen,
  input logic c2d_w_fifo_wen [SIZE],

  input logic c2d_x_fifo_ren,
  input logic c2d_w_fifo_ren,

  //

  output logic d2c_x_load_val,
  output logic d2c_w_load_val,
  output logic [$clog2(SIZE)-1:0] d2c_w_load_sel,

  output logic d2c_x_fifo_empty,
  output logic d2c_w_fifo_empty [SIZE]
);

  genvar i;

  //=======================================================
  // Input Mux
  //=======================================================

  logic [NBITS-1:0] x_mux_in [2];
  logic [NBITS-1:0] x_mux_out;

  assign x_mux_in[0] = x_in;
  assign x_mux_in[1] = 0;    // REPLACE

  Mux #(2, NBITS) x_mux
  (
    .in0 (x_mux_in),
    .sel (c2d_x_sel),
    .out (x_mux_out)
  );

  assign d2c_x_load_val = x_load_val;

  //=======================================================
  // Input FIFO
  //=======================================================

  logic [NBITS-1:0] x;
  
  logic x_fifo_full_unused;

  FIFO #(SIZE, NBITS) x_fifo
  (
    .clk   (clk),
    .rst   (rst),
    .wen   (c2d_x_fifo_wen),
    .ren   (c2d_x_fifo_ren),
    .d     (x_mux_out),
    .q     (x),
    .full  (x_fifo_full_unused),
    .empty (d2c_x_fifo_empty)
  );

  //=======================================================
  // Weight Demux
  //=======================================================

  logic [NBITS-1:0] w_demux_out [SIZE];

  Demux #(SIZE, NBITS) w_demux
  (
    .in0 (w_in),
    .sel (w_load_sel),
    .out (w_demux_out)
  );

  assign d2c_w_load_val = w_load_val;
  assign d2c_w_load_sel = w_load_sel;

  //=======================================================
  // Weight FIFO
  //=======================================================

  logic [NBITS-1:0] w [SIZE];

  logic w_fifo_full_unused [SIZE];

  generate
    for(i = 0; i < SIZE; i++) begin: g_w_fifo
      FIFO #(SIZE, NBITS) w_fifo
      (
        .clk   (clk),
        .rst   (rst),
        .wen   (c2d_w_fifo_wen[i]),
        .ren   (c2d_w_fifo_ren),
        .d     (w_demux_out[i]),
        .q     (w[i]),
        .full  (w_fifo_full_unused[i]),
        .empty (d2c_w_fifo_empty[i])
      );
    end
  endgenerate

endmodule

`endif`