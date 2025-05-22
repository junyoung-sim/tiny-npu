from TestUtil import *

#==========================================================

async def reset(dut):
  dut.rst.value = 1
  await RisingEdge(dut.clk)
  dut.rst.value = 0

async def check(dut, rst, en, d, q):
  dut.rst.value = rst
  dut.en.value  = en
  dut.d.value   = d.get()

  await RisingEdge(dut.clk)

  assert (dut.q.value == q.get())

#==========================================================

@cocotb.test()
async def test_case_1_random(dut):
  clock = init_clock(dut)

  await reset(dut)

  q = zero_fp(NBITS, DBITS)

  trials = 10000
  for t in range(trials):
    rst = random.randint(0, 1)
    en  = random.randint(0, 1)
    d   = rand_fp(NBITS, DBITS)

    await check(dut, rst, en, d, q)

    if(rst):
      q = zero_fp(NBITS, DBITS)
    else:
      q = (d if(en) else q)