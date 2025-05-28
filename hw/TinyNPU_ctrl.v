`ifndef TINYNPU_CTRL_V
`define TINYNPU_CTRL_V

`define LD0 4'b0001
`define MAC 4'b0010
`define LD1 4'b0100
`define OUT 4'b1000

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

  //=======================================================
  // State Transition
  //=======================================================

  // FIFO Status

  logic empty;

  always_comb begin
    empty = d2c_x_fifo_empty;
    for(int i = 0; i < SIZE; i++) begin
      empty = (empty & d2c_w_fifo_empty[i]);
    end
  end

  // Critical States

  logic [3:0] state;
  assign trace_state = state;

  logic fifo_wen_state;
  assign fifo_wen_state = (
    ((state == `LD0) | (state == `LD1))
  );

  logic mac_val_state;
  assign mac_val_state = ((state == `MAC) & ~empty);

  logic mac_lat_state;
  assign mac_lat_state = ((state == `MAC) & empty);

  // MAC Output Stream Latency Counter

  logic [1:0] mac_lat;
  
  logic mac_ostream_rdy;
  assign mac_ostream_rdy = (mac_lat == 2'b10);

  always_ff @(posedge clk) begin
    if(rst | mac_ostream_rdy)
      mac_lat <= 0;
    else
      mac_lat <= mac_lat + mac_lat_state;
  end

  // State Register

  always_ff @(posedge clk) begin
    if(rst)
      state <= `LD0;
    else begin
      case(state)
        `LD0:    state <= (d2c_mac_val ? `MAC : `LD0);
        `MAC:    state <= (mac_ostream_rdy ? `LD1 : `MAC);
        `LD1:    state <= `LD1; // TBD
        `OUT:    state <= `OUT; // TBD
        default: state <= `LD0;
      endcase
    end
  end

  //=======================================================
  // Output Logic
  //=======================================================

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