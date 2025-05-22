from TestUtil import *

#==========================================================

async def check(dut, in0, out):
  dut.in0.value = in0.get()

  await Timer(1, units="ns")

  assert (dut.out.value == out.get())

#==========================================================

@cocotb.test()
async def test_case_1_random(dut):
  trials = 10000
  for t in range(trials):
    in0 = rand_fp(NBITS, DBITS)
    
    out = (zero_fp(NBITS, DBITS) if(in0 < 0) else in0)
    
    await check(dut, in0, out)