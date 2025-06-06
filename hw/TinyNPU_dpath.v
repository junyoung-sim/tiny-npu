`ifndef TINYNPU_DPATH_V
`define TINYNPU_DPATH_V

`include "Mux.v"
`include "MAC.v"
`include "FIFO.v"

module TinyNPU_dpath
#(
  parameter SIZE  = 4,
  parameter NBITS = 8,
  parameter DBITS = 4
)(
  input  logic                    clk,
  input  logic                    rst,

  // I/O

  input  logic [NBITS-1:0]        x_in,
  input  logic [NBITS-1:0]        w_in,

  input  logic                    x_load_val,
  input  logic                    w_load_val,
  input  logic [$clog2(SIZE)-1:0] w_load_sel,
  
  input  logic                    mac_val,
  input  logic                    out_val,

  output logic [NBITS-1:0]        z_out,

  // Control

  input  logic                    c2d_x_sel,
  input  logic                    c2d_x_fifo_wen,
  input  logic                    c2d_w_fifo_wen [SIZE],

  input  logic                    c2d_istream_val,
  input  logic                    c2d_x_fifo_ren,
  input  logic                    c2d_w_fifo_ren,
  input  logic                    c2d_ostream_req,

  input  logic [$clog2(SIZE):0]   c2d_ostream_sel,
  input  logic                    c2d_mac_rst,

  input  logic                    c2d_z_out_sel,

  // Status

  output logic                    d2c_x_load_val,
  output logic                    d2c_w_load_val,
  output logic [$clog2(SIZE)-1:0] d2c_w_load_sel,

  output logic                    d2c_x_fifo_empty,
  output logic                    d2c_w_fifo_empty [SIZE],

  output logic                    d2c_mac_val,
  output logic                    d2c_out_val
);

  genvar i;

  assign d2c_mac_val = mac_val;
  assign d2c_out_val = out_val;

  //=======================================================
  // Input Mux
  //=======================================================

  logic [NBITS-1:0] x_mux_in [2];
  logic [NBITS-1:0] x_mux_out;

  assign x_mux_in[0] = x_in;

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
  // Output Mux
  //=======================================================

  logic [NBITS-1:0] _z_out [2];

  assign _z_out[0] = 0;
  assign _z_out[1] = x;

  Mux #(2, NBITS) out_mux
  (
    .in0 (_z_out),
    .sel (c2d_z_out_sel),
    .out (z_out)
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

  //=======================================================
  // MAC
  //=======================================================

  logic [NBITS-1:0] mac_out [SIZE];

  generate
    for(i = 0; i < SIZE; i++) begin: g_pe
      MAC #(NBITS, DBITS) pe
      (
        .clk         (clk),
        .rst         (rst | c2d_mac_rst),
        .istream_val (c2d_istream_val),
        .ostream_req (c2d_ostream_req),
        .x_in        (x),
        .w_in        (w[i]),
        .z_out       (mac_out[i])
      );
    end
  endgenerate

  //=======================================================
  // MAC Output Mux
  //=======================================================

  Mux #(SIZE, NBITS) mac_mux
  (
    .in0 (mac_out),
    .sel (c2d_ostream_sel[$clog2(SIZE)-1:0]),
    .out (x_mux_in[1])
  );

endmodule

`endif