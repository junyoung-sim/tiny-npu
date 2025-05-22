from TestUtil import *

#==========================================================

DEPTH = 4

#==========================================================

async def reset(dut):
  dut.rst.value = 1
  await RisingEdge(dut.clk)
  dut.rst.value = 0

async def rw_ptr_step(dut, wen, ren, full, empty):
  dut.rst.value = 0
  dut.wen.value = wen
  dut.ren.value = ren

  await RisingEdge(dut.clk)

  assert (dut.full.value == full)
  assert (dut.empty.value == empty)

async def step(dut, wen, ren, d, q, full, empty):
  dut.rst.value = 0
  dut.wen.value = wen
  dut.ren.value = ren
  dut.d.value   = d.get()

  await RisingEdge(dut.clk)

  assert (dut.q.value == q.get())
  assert (dut.full.value == full)
  assert (dut.empty.value == empty)

#==========================================================

@cocotb.test()
async def test_case_1_random_rw_ptr(dut):
  clock = init_clock(dut)

  await reset(dut)

  full       = 0
  empty      = 1
  curr_depth = 0

  trials = 10000
  for T in range(trials):
    wen = random.randint(0, 1)
    ren = random.randint(0, 1)

    await rw_ptr_step(dut, wen, ren, full, empty)

    curr_depth += (wen & (full == 0))
    curr_depth -= (ren & (empty == 0))

    full  = (curr_depth == DEPTH)
    empty = (curr_depth == 0)

@cocotb.test()
async def test_case_2_random_rw(dut):
  clock = init_clock(dut)

  await reset(dut)

  stream     = []
  stream_idx = 0
  full       = 0
  empty      = 1
  curr_depth = 0

  trials = 10000
  for T in range(trials):
    wen = random.randint(0, 1)
    ren = random.randint(0, 1)
    d   = rand_fp(NBITS, DBITS)
    q   = zero_fp(NBITS, DBITS)

    if(ren & (empty == 0)):
      q = stream[stream_idx]
      stream_idx += 1

    await step(dut, wen, ren, d, q, full, empty)

    curr_depth += (wen & (full == 0))
    curr_depth -= (ren & (empty == 0))

    if (wen & (full == 0)):
      stream.append(d)

    full  = (curr_depth == DEPTH)
    empty = (curr_depth == 0)