from TestUtil import *

#==========================================================

SIZE = 4

#==========================================================

async def check(dut, in0, sel, out: []):
  dut.in0.value = in0.get()
  dut.sel.value = sel

  await Timer(1, units="ns")
  
  for i in range(SIZE):
    assert (dut.out[i].value == out[i].get())

#==========================================================

@cocotb.test()
async def test_case_1_random(dut):
  trials = 10000
  for t in range(trials):
    in0 = rand_fp(NBITS, DBITS)
    sel = random.randint(0, SIZE-1)
    
    out = []
    for i in range(SIZE):
      if(i == sel):
        out.append(in0)
      else:
        out.append(zero_fp(NBITS, DBITS))
    
    await check(dut, in0, sel, out)