from TestUtil import *

#==========================================================

SIZE = 4

LD0 = 0b0001
MAC = 0b0010
LD1 = 0b0100
OUT = 0b1000

x = 'x'

#==========================================================

async def reset(dut):
  dut.rst.value = 1
  await RisingEdge(dut.clk)
  dut.rst.value = 0

#==========================================================

async def check_LD0 (
  dut, d2c_x_load_val, d2c_w_load_val, d2c_w_load_sel, d2c_mac_val,
  c2d_x_sel, c2d_x_fifo_wen, c2d_w_fifo_wen: [], trace_state
):
  dut.rst.value = 0
  dut.d2c_x_load_val.value = d2c_x_load_val
  dut.d2c_w_load_val.value = d2c_w_load_val
  dut.d2c_w_load_sel.value = d2c_w_load_sel
  dut.d2c_mac_val.value    = d2c_mac_val

  await RisingEdge(dut.clk)

  assert (dut.c2d_x_sel.value == c2d_x_sel)
  assert (dut.c2d_x_fifo_wen.value == c2d_x_fifo_wen)

  for i in range(SIZE):
    assert (dut.c2d_w_fifo_wen[i].value == c2d_w_fifo_wen[i])
  
  assert (dut.trace_state.value == trace_state)

#==========================================================

@cocotb.test()
async def test_case_1_directed_LD0(dut):
  clock = init_clock(dut)

  await reset(dut)

  # reset
  await check_LD0(dut, 0, 0, 0, 0, 0, 0, [0,0,0,0], LD0)
  
  # write input fifo
  await check_LD0(dut, 1, 0, 0, 0, 0, 1, [0,0,0,0], LD0)

  # write weight fifo
  await check_LD0(dut, 0, 1, 0, 0, 0, 0, [1,0,0,0], LD0)
  await check_LD0(dut, 0, 1, 1, 0, 0, 0, [0,1,0,0], LD0)
  await check_LD0(dut, 0, 1, 2, 0, 0, 0, [0,0,1,0], LD0)
  await check_LD0(dut, 0, 1, 3, 0, 0, 0, [0,0,0,1], LD0)

  # state transition (LD0 -> MAC)
  await check_LD0(dut, 0, 0, 0, 1, 0, 0, [0,0,0,0], LD0)
  await check_LD0(dut, 0, 0, 0, 0, x, 0, [0,0,0,0], MAC)

