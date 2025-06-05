`ifndef TINYNPU_V
`define TINYNPU_V

`include "TinyNPU_ctrl.v"
`include "TinyNPU_dpath.v"

module TinyNPU
#(
  parameter SIZE  = 4,
  parameter NBITS = 8,
  parameter DBITS = 4
)(
  input  logic                    clk,
  input  logic                    rst,

  input  logic [NBITS-1:0]        x_in,
  input  logic [NBITS-1:0]        w_in,

  input  logic                    x_load_val,
  input  logic                    w_load_val,
  input  logic [$clog2(SIZE)-1:0] w_load_sel,
  
  input  logic                    mac_val,
  input  logic                    out_val,

  output logic [NBITS-1:0]        z_out,

  output logic [1:0]              trace_state
);

  // Control

  logic                    c2d_x_sel;
  logic                    c2d_x_fifo_wen;
  logic                    c2d_w_fifo_wen [SIZE];

  logic                    c2d_istream_val;
  logic                    c2d_x_fifo_ren;
  logic                    c2d_w_fifo_ren;
  logic                    c2d_ostream_req;

  logic [$clog2(SIZE):0]   c2d_ostream_sel;
  logic                    c2d_mac_rst;

  logic                    c2d_z_out_sel;

  // Status

  logic                    d2c_x_load_val;
  logic                    d2c_w_load_val;
  logic [$clog2(SIZE)-1:0] d2c_w_load_sel;

  logic                    d2c_x_fifo_empty;
  logic                    d2c_w_fifo_empty [SIZE];

  logic                    d2c_mac_val;
  logic                    d2c_out_val;

  TinyNPU_ctrl #(SIZE) ctrl
  (
    .*
  );

  TinyNPU_dpath #(SIZE, NBITS, DBITS) dpath
  (
    .*
  );

endmodule

`endif