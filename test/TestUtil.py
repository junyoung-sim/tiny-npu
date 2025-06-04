import random
import cocotb
import subprocess
from fixedpt import Fixed
from cocotb.triggers import *
from cocotb.clock import Clock

#===========================================================

def zero_fp(n, d):
  return Fixed(0, 1, n, d, raw=True)

def rand_fp(n, d):
  return Fixed (
    random.randint(0, (1 << n) - 1), 1, n, d, raw=True
  )

def add_fp(a: Fixed, b: Fixed):
  return (a + b).resize(None, a._n, a._d)

def mul_fp(a: Fixed, b: Fixed):
  return (a * b).resize(None, a._n, a._d)

def dot_fp(a: [], b: [], n, d):
  dot = zero_fp(n, d)
  for i in range(len(a)):
    dot = add_fp(dot, mul_fp(a[i], b[i]))
  return dot

def relu_fp(x: Fixed):
  return (zero_fp(NBITS, DBITS) if (x < 0) else x)

#===========================================================

def init_clock(dut):
  return cocotb.start_soon (
    Clock(dut.clk, 1, units="ns").start(start_high=False)
  )

#===========================================================

NBITS = 8
DBITS = 4

ZERO_FP = zero_fp(NBITS, DBITS)