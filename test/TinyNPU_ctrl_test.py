from TestUtil import *

#===========================================================

SIZE = 4

LD0 = 0b00
MAC = 0b01
LD1 = 0b10
OUT = 0b11

x = 'x'

#===========================================================

async def reset(dut):
  dut.rst.value = 1
  await RisingEdge(dut.clk)
  dut.rst.value = 0

#===========================================================

async def check (
  dut, d2c_x_load_val, d2c_w_load_val, d2c_w_load_sel,
  d2c_mac_val, d2c_x_fifo_empty, d2c_w_fifo_empty: [], d2c_out_val,
  c2d_x_sel, c2d_x_fifo_wen, c2d_w_fifo_wen: [], c2d_istream_val,
  c2d_x_fifo_ren, c2d_w_fifo_ren, c2d_ostream_req, c2d_ostream_sel, c2d_mac_rst, trace_state
):
  dut.rst.value = 0
  dut.d2c_x_load_val.value   = d2c_x_load_val
  dut.d2c_w_load_val.value   = d2c_w_load_val
  dut.d2c_w_load_sel.value   = d2c_w_load_sel
  dut.d2c_mac_val.value      = d2c_mac_val
  dut.d2c_x_fifo_empty.value = d2c_x_fifo_empty

  for i in range(SIZE):
    dut.d2c_w_fifo_empty[i].value = d2c_w_fifo_empty[i]
  
  dut.d2c_out_val.value = d2c_out_val

  await RisingEdge(dut.clk)

  assert (dut.c2d_x_sel.value == c2d_x_sel)
  assert (dut.c2d_x_fifo_wen.value == c2d_x_fifo_wen)

  for i in range(SIZE):
    assert (dut.c2d_w_fifo_wen[i].value == c2d_w_fifo_wen[i])
  
  assert (dut.c2d_istream_val.value == c2d_istream_val)
  assert (dut.c2d_x_fifo_ren.value == c2d_x_fifo_ren)
  assert (dut.c2d_w_fifo_ren.value == c2d_w_fifo_ren)
  assert (dut.c2d_ostream_req.value == c2d_ostream_req)
  assert (dut.c2d_ostream_sel.value == c2d_ostream_sel)
  assert (dut.c2d_mac_rst.value == c2d_mac_rst)
  assert (dut.trace_state.value == trace_state)

#===========================================================

@cocotb.test()
async def test_case_1_directed_LD0(dut):
  clock = init_clock(dut)

  await reset(dut)

  await check (
    dut, 0, 0, 0, 
    0, 0, [0,0,0,0], 0,
    0, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )

  # write input fifo
  await check (
    dut, 1, 0, 0,
    0, 0, [0,0,0,0], 0,
    0, 1, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )

  # write weight fifo
  await check (
    dut, 0, 1, 0,
    0, 0, [0,0,0,0], 0,
    0, 0, [1,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 1, 1,
    0, 0, [0,0,0,0], 0,
    0, 0, [0,1,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 1, 2,
    0, 0, [0,0,0,0], 0,
    0, 0, [0,0,1,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 1, 3,
    0, 0, [0,0,0,0], 0,
    0, 0, [0,0,0,1], 0,
    0, 0, 0, 0, 0, LD0
  )

  # state transition (LD0 -> MAC)
  await check (
    dut, 0, 0, 0,
    1, 0, [0,0,0,0], 0,
    0, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 0,
    x, 0, [0,0,0,0], 1,
    1, 1, 0, 0, 0, MAC
  )

#===========================================================

@cocotb.test()
async def test_case_2_directed_MAC(dut):
  clock = init_clock(dut)

  await reset(dut)

  # state transition (LD0 -> MAC)
  await check (
    dut, 0, 0, 0,
    1, 0, [0,0,0,0], 0,
    0, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 0,
    x, 0, [0,0,0,0], 1,
    1, 1, 0, 0, 0, MAC
  )

  # feedforward
  for i in range(SIZE):
    await check (
      dut, 0, 0, 0,
      0, 0, [0,0,0,0], 0,
      x, 0, [0,0,0,0], 1,
      1, 1, 0, 0, 0, MAC
    )
  
  # empty FIFOs
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, MAC
  )

  # MAC output stream latency
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, MAC
  )
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 1, 0, 0, MAC
  )

  # state transition (MAC -> LD1)
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    1, 1, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD1
  )

#===========================================================

@cocotb.test()
async def test_case_3_directed_LD1_MAC(dut):
  clock = init_clock(dut)

  await reset(dut)

  # state transition (LD0 -> MAC)
  await check (
    dut, 0, 0, 0,
    1, 0, [0,0,0,0], 0,
    0, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 0,
    x, 0, [0,0,0,0], 1,
    1, 1, 0, 0, 0, MAC
  )

  # empty FIFOs
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, MAC
  )

  # MAC output stream latency
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, MAC
  )
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 1, 0, 0, MAC
  )

  # state transition (MAC -> LD1)
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    1, 1, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD1
  )

  # MAC output stream selection
  await check (
    dut, 0, 1, 0,
    0, 0, [0,0,0,0], 0,
    1, 1, [1,0,0,0], 0,
    0, 0, 0, 1, 0, LD1
  )
  await check (
    dut, 0, 1, 1,
    0, 0, [0,0,0,0], 0,
    1, 1, [0,1,0,0], 0,
    0, 0, 0, 2, 0, LD1
  )
  await check (
    dut, 0, 1, 2,
    0, 0, [0,0,0,0], 0,
    1, 1, [0,0,1,0], 0,
    0, 0, 0, 3, 0, LD1
  )
  await check (
    dut, 0, 1, 3,
    0, 0, [0,0,0,0], 0,
    1, 0, [0,0,0,1], 0,
    0, 0, 0, 4, 1, LD1
  )

  # state transition (LD1 -> MAC)
  await check (
    dut, 0, 0, 0,
    1, 0, [0,0,0,0], 0,
    1, 0, [0,0,0,0], 0,
    0, 0, 0, 4, 1, LD1
  )
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 0,
    x, 0, [0,0,0,0], 1,
    1, 1, 0, 4, 0, MAC
  )

#===========================================================

@cocotb.test()
async def test_case_4_directed_LD1_OUT(dut):
  clock = init_clock(dut)

  await reset(dut)

  # state transition (LD0 -> MAC)
  await check (
    dut, 0, 0, 0,
    1, 0, [0,0,0,0], 0,
    0, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD0
  )
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 0,
    x, 0, [0,0,0,0], 1,
    1, 1, 0, 0, 0, MAC
  )

  # empty FIFOs
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, MAC
  )

  # MAC output stream latency
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 0, 0, MAC
  )
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 1, 0, 0, MAC
  )

  # state transition (MAC -> LD1)
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    1, 1, [0,0,0,0], 0,
    0, 0, 0, 0, 0, LD1
  )

  # MAC output stream selection
  await check (
    dut, 0, 1, 0,
    0, 0, [0,0,0,0], 0,
    1, 1, [1,0,0,0], 0,
    0, 0, 0, 1, 0, LD1
  )
  await check (
    dut, 0, 1, 1,
    0, 0, [0,0,0,0], 0,
    1, 1, [0,1,0,0], 0,
    0, 0, 0, 2, 0, LD1
  )
  await check (
    dut, 0, 1, 2,
    0, 0, [0,0,0,0], 0,
    1, 1, [0,0,1,0], 0,
    0, 0, 0, 3, 0, LD1
  )
  await check (
    dut, 0, 1, 3,
    0, 0, [0,0,0,0], 0,
    1, 0, [0,0,0,1], 0,
    0, 0, 0, 4, 1, LD1
  )

  # state transition (LD1 -> OUT)
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 1,
    1, 0, [0,0,0,0], 0,
    0, 0, 0, 4, 1, LD1
  )
  await check (
    dut, 0, 0, 0,
    0, 0, [0,0,0,0], 0,
    x, 0, [0,0,0,0], 0,
    1, 1, 0, 4, 0, OUT
  )
  await check (
    dut, 0, 0, 0,
    0, 1, [1,1,1,1], 0,
    x, 0, [0,0,0,0], 0,
    0, 0, 0, 4, 0, OUT
  )