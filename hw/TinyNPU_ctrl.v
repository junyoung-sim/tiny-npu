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

  input  logic                    d2c_out_val,

  output logic                    c2d_x_sel,
  output logic                    c2d_x_fifo_wen,
  output logic                    c2d_w_fifo_wen [SIZE],

  output logic                    c2d_istream_val,
  output logic                    c2d_x_fifo_ren,
  output logic                    c2d_w_fifo_ren,
  output logic                    c2d_ostream_req,

  output logic                    c2d_ostream_sel,
  output logic                    c2d_mac_rst,

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

  // MAC Output Stream Selection

  logic [$clog2(SIZE):0] ostream_sel;
  logic [$clog2(SIZE):0] ostream_sel_next;

  always_comb begin
    ostream_sel_next = (ostream_sel + 1);
  end

  logic ostream_fifo_rdy;
  assign ostream_fifo_rdy = (ostream_sel == SIZE);

  logic ostream_load_state;
  assign ostream_load_state = (
    (state == `LD1) & ~ostream_fifo_rdy
  );

  logic ostream_sel_reg_rst;
  assign ostream_sel_reg_rst = (
    (state == `MAC) & (state_next == `LD1)
  );

  Reg #($clog2(SIZE)) ostream_sel_reg
  (
    .clk (clk),
    .rst (rst | ostream_sel_reg_rst),
    .en  (ostream_load_state),
    .d   (ostream_sel_next),
    .q   (ostream_sel)
  );

  // State Register

  logic [1:0] ld1_state_next;

  always_comb begin
    if(~ostream_fifo_rdy | ~(d2c_mac_val ^ d2c_out_val))
      ld1_state_next = `LD1;
    else
      ld1_state_next = (d2c_mac_val ? `MAC : `OUT);
  end

  always_comb begin
    case(state)
      `LD0:    state_next = (d2c_mac_val ? `MAC : `LD0);
      `MAC:    state_next = (mac_ostream_rdy ? `LD1 : `MAC);
      `LD1:    state_next = ld1_state_next;
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

  always_comb begin
    case(state)
      `LD0:    c2d_x_sel =  0;
      `MAC:    c2d_x_sel = 'x;
      `LD1:    c2d_x_sel =  1;
      `OUT:    c2d_x_sel = 'x;
      default: c2d_x_sel =  0;
    endcase

    c2d_x_fifo_wen = (
      ((state == `LD0) & d2c_x_load_val) | ostream_load_state
    );

    for(int i = 0; i < SIZE; i++) begin
      c2d_w_fifo_wen[i] = (
          ((state == `LD0) | (state == `LD1)) 
        & d2c_w_load_val & (i == d2c_w_load_sel)
      );
    end

    c2d_istream_val = (state == `MAC) & ~empty;
    c2d_x_fifo_ren  = (state == `MAC) & ~empty;
    c2d_w_fifo_ren  = (state == `MAC) & ~empty;
    c2d_ostream_req = mac_ostream_rdy;

    c2d_ostream_sel = ostream_sel;
    c2d_mac_rst     = ostream_fifo_rdy;
  end

endmodule

`endif