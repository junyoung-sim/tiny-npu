from TestUtil import *

#==========================================================

async def check(dut, in0, in1, out):
  dut.in0.value = in0.get()
  dut.in1.value = in1.get()

  await Timer(1, units="ns")
  
  assert (dut.out.value == out.get())

#==========================================================

@cocotb.test()
async def test_case_1_random(dut):
  trials = 10000
  for t in range(trials):
    in0 = rand_fp(NBITS, DBITS)
    in1 = rand_fp(NBITS, DBITS)
    out = add_fp(in0, in1)
    await check(dut, in0, in1, out)