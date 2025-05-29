`ifndef TINYNPU_CTRL_V
`define TINYNPU_CTRL_V

`include "Reg.v"

`define LD0 2'b00
`define MAC 2'b01
`define LD1 2'b10
`define OUT 2'b11

module TinyNPU_ctrl
#(
  parameter SIZE = 4
)(
  input  logic                    clk,
  input  logic                    rst,

  input  logic                    d2c_x_load_val,
  input  logic                    d2c_w_load_val,
  input  logic [$clog2(SIZE)-1:0] d2c_w_load_sel,
  input  logic                    d2c_mac_val,

  input  logic                    d2c_x_fifo_empty,
  input  logic                    d2c_w_fifo_empty [SIZE],

  output logic                    c2d_x_sel,
  output logic                    c2d_x_fifo_wen,
  output logic                    c2d_w_fifo_wen [SIZE],

  output logic                    c2d_istream_val,
  output logic                    c2d_x_fifo_ren,
  output logic                    c2d_w_fifo_ren,
  output logic                    c2d_ostream_req,

  output logic [3:0] trace_state
);

  //==========================================================
  // State Transition
  //==========================================================

  logic [1:0] state;
  logic [1:0] state_next;
  
  assign trace_state = state;

  // FIFO Status

  logic empty;

  always_comb begin
    empty = d2c_x_fifo_empty;
    for(int i = 0; i < SIZE; i++) begin
      empty = (empty & d2c_w_fifo_empty[i]);
    end
  end

  // MAC Output Stream Latency Counter

  logic [1:0] mac_lat;
  logic [1:0] mac_lat_next;
  
  always_comb begin
    mac_lat_next = (mac_lat + 1);
  end

  logic mac_lat_state;
  assign mac_lat_state = ((state == `MAC) & empty);

  logic mac_ostream_rdy;
  assign mac_ostream_rdy = (mac_lat == 2'b10);

  Reg #(2) mac_lat_counter
  (
    .clk (clk),
    .rst (rst | mac_ostream_rdy),
    .en  (mac_lat_state),
    .d   (mac_lat_next),
    .q   (mac_lat)
  );

  // State Register

  always_comb begin
    case(state)
      `LD0:    state_next = (d2c_mac_val ? `MAC : `LD0);
      `MAC:    state_next = (mac_ostream_rdy ? `LD1 : `MAC);
      `LD1:    state_next = `LD1; // TBD
      `OUT:    state_next = `OUT; // TBD
      default: state_next = `LD0;
    endcase
  end

  Reg #(2) state_reg
  (
    .clk (clk),
    .rst (rst),
    .en  (1),
    .d   (state_next),
    .q   (state)
  );

  //==========================================================
  // Output Logic
  //==========================================================

  logic fifo_wen_state;
  assign fifo_wen_state = (((state == `LD0) | (state == `LD1)));

  logic mac_val_state;
  assign mac_val_state = ((state == `MAC) & ~empty);

  always_comb begin
    case(state)
      `LD0:    c2d_x_sel =  0;
      `MAC:    c2d_x_sel = 'x;
      `LD1:    c2d_x_sel =  1;
      `OUT:    c2d_x_sel = 'x;
      default: c2d_x_sel =  0;
    endcase

    c2d_x_fifo_wen = (fifo_wen_state & d2c_x_load_val);

    for(int i = 0; i < SIZE; i++) begin
      c2d_w_fifo_wen[i] = (
        fifo_wen_state & d2c_w_load_val & (i == d2c_w_load_sel)
      );
    end

    c2d_istream_val = mac_val_state;
    c2d_x_fifo_ren  = mac_val_state;
    c2d_w_fifo_ren  = mac_val_state;
    c2d_ostream_req = mac_ostream_rdy;
  end

endmodule

`endif