from TestUtil import *

#==========================================================

SIZE = 4

#==========================================================

async def check(dut, in0: [], sel, out):
  for i in range(SIZE):
    dut.in0[i].value = in0[i].get()
  dut.sel.value = sel

  await Timer(1, units="ns")

  assert (dut.out.value == out.get())

#==========================================================

@cocotb.test()
async def test_case_1_random(dut):
  
  trials = 10000
  for t in range(trials):
    in0 = []
    for i in range(SIZE):
      in0.append(rand_fp(NBITS, DBITS))
    sel = random.randint(0, SIZE-1)

    out = in0[sel]

    await check(dut, in0, sel, out)