from TestUtil import *

#==========================================================

def mux_size(dut):
  return len(dut.in0)

#==========================================================

async def check(dut, in0: [], sel, out):
  SIZE = mux_size(dut)
  for i in range(SIZE):
    dut.in0[i].value = in0[i].get()
  dut.sel.value = sel

  await Timer(1, units="ns")

  assert (dut.out.value == out.get())

#==========================================================

@cocotb.test()
async def test_case_1_random(dut):
  SIZE = mux_size(dut)
  
  trials = 10000
  for t in range(trials):
    in0 = []
    for i in range(SIZE):
      in0.append(rand_fp(NBITS, DBITS))
    sel = random.randint(0, SIZE-1)

    out = in0[sel]

    await check(dut, in0, sel, out)