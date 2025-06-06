from TestUtil import *

#===========================================================

SIZE   = 4
LAYERS = 5

LD0 = 0b00
MAC = 0b01
LD1 = 0b10
OUT = 0b11

MAC_LAT = 2

#===========================================================

async def reset(dut):
  dut.rst.value = 1
  await RisingEdge(dut.clk)
  dut.rst.value = 0

async def check (
  dut, x_in, w_in, x_load_val, w_load_val, w_load_sel,
  mac_val, out_val, z_out, trace_state
):
  dut.rst.value = 0

  dut.x_in.value = x_in.get()
  dut.w_in.value = w_in.get()
  
  dut.x_load_val.value = x_load_val
  dut.w_load_val.value = w_load_val
  dut.w_load_sel.value = w_load_sel
  
  dut.mac_val.value = mac_val
  dut.out_val.value = out_val
  
  await RisingEdge(dut.clk)

  assert (dut.z_out.value == z_out.get())
  assert (dut.trace_state.value == trace_state)

#===========================================================

@cocotb.test()
async def test_case_1_reset(dut):
  clock = init_clock(dut)

  await reset(dut)

  await check (
    dut, ZERO_FP, ZERO_FP, 0, 0, 0, 0, 0, ZERO_FP, LD0
  )

@cocotb.test()
async def test_case_2_single_layer(dut):
  clock = init_clock(dut)

  trials = 100

  for trial in range(trials):
    x = []
    w = []
    z = []

    for i in range(SIZE):
      x.append(rand_fp(NBITS, DBITS))
    
    for i in range(SIZE):
      w_i = []
      for j in range(SIZE):
        w_i.append(rand_fp(NBITS, DBITS))
      w.append(w_i)
      
      dot = dot_fp(x, w[i], NBITS, DBITS)
      
      z.append(relu_fp(dot))

    ###

    await reset(dut)

    x_i = 0
    w_i = 0
    w_j = 0

    x_load_val = 1
    w_load_val = 1

    # load input and weights
    while(x_load_val | w_load_val):
      await check (
        dut, x[x_i], w[w_i][w_j],
        x_load_val, w_load_val, w_i,
        0, 0, ZERO_FP, LD0
      )

      x_load_val = not(x_i == SIZE-1)
      w_load_val = not((w_i == SIZE-1) & (w_j == SIZE-1))

      x_i += x_load_val
      w_j += w_load_val

      if(w_j == SIZE):
        w_i += 1
        w_j = 0
    
    # request MAC
    await check (
      dut, ZERO_FP, ZERO_FP,
      0, 0, 0,
      1, 0, ZERO_FP, LD0
    )

    # MAC
    for t in range(SIZE+MAC_LAT+1):
      await check (
        dut, ZERO_FP, ZERO_FP,
        0, 0, 0,
        0, 0, ZERO_FP, MAC
      )
    
    # load output stream to FIFO
    for t in range(SIZE):
      await check (
        dut, ZERO_FP, ZERO_FP,
        0, 0, 0,
        0, 0, ZERO_FP, LD1
      )
    
    # request OUT
    await check (
      dut, ZERO_FP, ZERO_FP,
      0, 0, 0,
      0, 1, ZERO_FP, LD1
    )

    # verify output stream
    for i in range(SIZE):
      await check (
        dut, ZERO_FP, ZERO_FP,
        0, 0, 0,
        0, 0, z[i], OUT
      )

@cocotb.test()
async def test_case_3_multi_layer(dut):
  clock = init_clock(dut)

  trials = 100

  for trial in range(trials):
    x = []
    w = []
    z = []

    for i in range(SIZE):
      x.append(rand_fp(NBITS, DBITS))
    
    for i in range(SIZE):
      w_i = []
      for j in range(SIZE):
        w_i.append(rand_fp(NBITS, DBITS))
      w.append(w_i)
      
      dot = dot_fp(x, w[i], NBITS, DBITS)
      
      z.append(relu_fp(dot))
    
    ###

    await reset(dut)

    x_i = 0
    w_i = 0
    w_j = 0

    x_load_val = 1
    w_load_val = 1

    # load input and weights
    while(x_load_val | w_load_val):
      await check (
        dut, x[x_i], w[w_i][w_j],
        x_load_val, w_load_val, w_i,
        0, 0, ZERO_FP, LD0
      )

      x_load_val = not(x_i == SIZE-1)
      w_load_val = not((w_i == SIZE-1) & (w_j == SIZE-1))

      x_i += x_load_val
      w_j += w_load_val

      if(w_j == SIZE):
        w_i += 1
        w_j = 0

    for l in range(LAYERS):
      # request MAC
      await check (
        dut, ZERO_FP, ZERO_FP,
        0, 0, 0,
        1, 0, ZERO_FP, (LD0 if(l == 0) else LD1)
      )

      # MAC
      for t in range(SIZE+MAC_LAT+1):
        await check (
          dut, ZERO_FP, ZERO_FP,
          0, 0, 0,
          0, 0, ZERO_FP, MAC
        )
      
      # load output stream to FIFO
      for t in range(SIZE):
        await check (
          dut, ZERO_FP, ZERO_FP,
          0, 0, 0,
          0, 0, ZERO_FP, LD1
        )
      
      if(l == LAYERS-1):
        break
    
      # generate new weights and compute
      x = z
      w = []
      z = []

      for i in range(SIZE):
        w_i = []
        for j in range(SIZE):
          w_i.append(rand_fp(NBITS, DBITS))
        w.append(w_i)
        
        dot = dot_fp(x, w[i], NBITS, DBITS)
        
        z.append(relu_fp(dot))
      
      # load weights
      w_i = 0
      w_j = 0

      x_load_val = 0
      w_load_val = 1

      # load input and weights
      while(w_load_val):
        await check (
          dut, ZERO_FP, w[w_i][w_j],
          x_load_val, w_load_val, w_i,
          0, 0, ZERO_FP, LD1
        )

        w_load_val = not((w_i == SIZE-1) & (w_j == SIZE-1))

        w_j += w_load_val

        if(w_j == SIZE):
          w_i += 1
          w_j = 0
    
    # request OUT
    await check (
      dut, ZERO_FP, ZERO_FP,
      0, 0, 0,
      0, 1, ZERO_FP, LD1
    )

    # verify output stream
    for i in range(SIZE):
      await check (
        dut, ZERO_FP, ZERO_FP,
        0, 0, 0,
        0, 0, z[i], OUT
      )