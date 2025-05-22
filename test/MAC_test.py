from TestUtil import *

#==========================================================

async def reset(dut):
  dut.rst.value = 1
  await RisingEdge(dut.clk)
  dut.rst.value = 0

async def check (
  dut, istream_val, ostream_req, x_in, w_in, z_out
):
  dut.istream_val.value = istream_val
  dut.ostream_req.value = ostream_req

  dut.x_in.value = x_in.get()
  dut.w_in.value = w_in.get()

  await RisingEdge(dut.clk)

  assert (dut.z_out.value == z_out.get())

#==========================================================

@cocotb.test()
async def test_case_1_directed_istream(dut):
  clock = init_clock(dut)

  trials = 100
  for t in range(trials):
    await reset(dut)

    _sum = ZERO_FP

    istream_len = 1000
    for i in range(istream_len):
      x_in = rand_fp(NBITS, DBITS)
      w_in = rand_fp(NBITS, DBITS)

      await check(dut, 1, 0, x_in, w_in, ZERO_FP)

      prod = mul_fp(x_in, w_in)
      _sum = add_fp(_sum, prod)

    z_out = (ZERO_FP if(_sum < 0) else _sum)

    await check(dut, 0, 0, ZERO_FP, ZERO_FP, ZERO_FP)
    await check(dut, 0, 0, ZERO_FP, ZERO_FP, ZERO_FP)
    await check(dut, 0, 1, ZERO_FP, ZERO_FP, ZERO_FP)
    await check(dut, 0, 0, ZERO_FP, ZERO_FP, z_out)

@cocotb.test()
async def test_case_2_random_istream(dut):
  clock = init_clock(dut)

  trials = 100
  for t in range(trials):
    await reset(dut)

    _sum = ZERO_FP

    istream_len = 1000
    while(istream_len != 0):
      x_in = rand_fp(NBITS, DBITS)
      w_in = rand_fp(NBITS, DBITS)

      istream_val = random.randint(0, 1)
      await check (
        dut, istream_val, 0, x_in, w_in, ZERO_FP
      )

      if(istream_val):
        prod = mul_fp(x_in, w_in)
        _sum = add_fp(_sum, prod)
        istream_len -= 1
    
    z_out = (ZERO_FP if(_sum < 0) else _sum)

    await check(dut, 0, 0, ZERO_FP, ZERO_FP, ZERO_FP)
    await check(dut, 0, 0, ZERO_FP, ZERO_FP, ZERO_FP)
    await check(dut, 0, 1, ZERO_FP, ZERO_FP, ZERO_FP)
    await check(dut, 0, 0, ZERO_FP, ZERO_FP, z_out)