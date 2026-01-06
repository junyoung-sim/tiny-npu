# Tiny Neural Processing Unit

**Summer 2025**

I designed and implemented TinyNPU, a simple fully-connected neural network inference accelerator prototype, within just two months to explore possible deep learning hardware architectures and practice the digital design flow.

## RTL Design

### Data Path

The objective of TinyNPU is to accelerate a fully-connected neural network with many rectified linear unit (ReLU) layers. This leads to the design schematic of TinyNPU shown below.

![fig1](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig1.png)

Essentially, there are N multiply-accumulate (MAC) processing elements (PE) receiving data from a universal first-in-first-out (FIFO) buffer that stores an input vector and a unique FIFO buffer that stores a weight vector for each PE. Notice that the input FIFO receives either an external input or an output from one of the PEs to allow “circular” feedforward propagation by leveraging hardware reuse. Also note that the weight FIFOs can be written with external data at a specified location.

![fig2](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig2.png)

The figure above shows the design schematic for each PE. Each PE performs its MAC operations over four cycles for (1) receiving the input and weight values, (2) multiplying the input and weight, (3) accumulating the product, and (4) applying ReLU to the sum. This pipelined process allows obtaining low latency products between small bitwidth numbers (e.g., Q4.4) through a fixed point combinational multiplier. Note that the PE is only enabled when istream_val (abbreviated as ival) is set high, and the final output is dumped only when ostream_req (abbreviated as oreq) is set high.

### Control Logic

TinyNPU has a four-state control logic where LD0 (00) is for loading an external input vector and first hidden layer weights; MAC (01) for performing MAC operations between the input FIFO and weight FIFOs of each PE; LD1 (10) for loading MAC outputs to the input FIFO and inner hidden layer weights to their respective FIFOs; and OUT (11) for reading the MAC outputs stored in the input FIFO to dump the inference output. Below is the full FSM diagram showing the state transition and output logic (along with relevant counters).

![fig3](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig3.png)

## Design Verification

Cocotb (Synopsys VCS) tests for TinyNPU consist of single- and multi-layer inference for 100 trials each with randomized inputs and weights using default top-level module parameters.

The waveform below is generated when performing one trial of multi-layer inference. Note that this waveform has four more cycles than necessary during the LD1 states to verify that MAC outputs are correctly loaded into the input FIFO before loading new weights.

![fig4](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig4.png)

Below is the coverage report for testing TinyNPU’s top-level module. Full coverage is achieved except for instances where (1) the most-significant bit of numbers transformed via ReLU is always zero and (2) the control logic’s state register is always enabled.

![fig5](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig5.png)

## Physical Design

***Technical details beyond what is provided below cannot be shared under the non-disclosure agreement between Cornell Custom Silicon Systems, MPW (Multi-Project-Wafer) University Service (MUSE), and Taiwan Semiconductor Manufacturing Company (TSMC).***

The MUSE TSMC 180 nm process node was used to collect power, performance, and area metrics for TinyNPU with default top-level module parameters.

### Area

The total area of TinyNPU with default top-level module parameters is reported to be approximately 46,400 µm2 or 0.0464 mm2 where 97.4% and 2.6% of this area is allocated for its data path and control logic, respectively. The majority of this area is occupied by the PEs and FIFO buffers, and the demultiplexer logic for loading values into the weight FIFO buffers is optimized during synthesis and included in the buffers.

Approximately 53% of the area for each processing element is occupied by the fixed point combinational multiplier. The remaining area is allocated equally among the registers placed between each pipeline registers. Note that the combinational logic for the adder and ReLU are optimized during synthesis and included in the registers.

![fig6](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig6.png)

### Performance

Setup time slack is met by 0.720 ns at a clock period of 5 ns where the critical path only goes through the fixed point combinational multiplier. Hold time conditions are almost met.

The setup time report is shown below.

```
Path 1: MET Setup Check with Pin dpath/g_pe_3__pe/s1_mul_reg/q_reg_7_/CP 
Endpoint:   dpath/g_pe_3__pe/s1_mul_reg/q_reg_7_/D (v) checked with  leading 
edge of 'TinyNPU_clk'
Beginpoint: dpath/g_pe_3__pe/s0_x_reg/q_reg_2_/Q   (v) triggered by  leading 
edge of 'TinyNPU_clk'
Path Groups: {TinyNPU_clk}
Analysis View: analysis_typical
Other End Arrival Time          0.000
- Setup                         0.055
+ Phase Shift                   5.000
+ CPPR Adjustment               0.000
= Required Time                 4.945
- Arrival Time                  4.225
= Slack Time                    0.720
     Clock Rise Edge                 0.000
     + Clock Network Latency (Ideal) 0.000
     = Beginpoint Arrival Time       0.000
     +---------------------------------------------------------------------------------------------------------+ 
     |                  Instance                  |     Arc      |      Cell      | Delay | Arrival | Required | 
     |                                            |              |                |       |  Time   |   Time   | 
     |--------------------------------------------+--------------+----------------+-------+---------+----------| 
     | dpath/g_pe_3__pe/s0_x_reg/q_reg_2_         | CP ^         |                |       |   0.000 |    0.720 | 
     | dpath/g_pe_3__pe/s0_x_reg/q_reg_2_         | CP ^ -> Q v  | xxxxxxxxxx     | 0.267 |   0.267 |    0.987 | 
     | dpath/g_pe_3__pe/s1_multiplier/U195        | I v -> ZN ^  | xxxxxxxxxx     | 0.099 |   0.366 |    1.087 | 
     | dpath/g_pe_3__pe/s1_multiplier/U182        | B1 ^ -> Z ^  | xxxxxxxxxx     | 0.498 |   0.865 |    1.585 | 
     | dpath/g_pe_3__pe/s1_multiplier/U66         | I ^ -> ZN v  | xxxxxxxxxx     | 0.021 |   0.885 |    1.606 | 
     | dpath/g_pe_3__pe/s1_multiplier/U58         | C v -> Z v   | xxxxxxxxxx     | 0.401 |   1.287 |    2.007 | 
     | dpath/g_pe_3__pe/s1_multiplier/U163        | B1 v -> Z v  | xxxxxxxxxx     | 0.212 |   1.498 |    2.219 | 
     | dpath/g_pe_3__pe/s1_multiplier/U164        | I v -> ZN ^  | xxxxxxxxxx     | 0.080 |   1.578 |    2.299 | 
     | dpath/g_pe_3__pe/s1_multiplier/U200        | A2 ^ -> Z ^  | xxxxxxxxxx     | 0.130 |   1.709 |    2.429 | 
     | dpath/g_pe_3__pe/s1_multiplier/U171        | C ^ -> ZN v  | xxxxxxxxxx     | 0.187 |   1.896 |    2.616 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U8 | B v -> CO v  | xxxxxxxxxx     | 0.315 |   2.211 |    2.931 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U7 | CI v -> CO v | xxxxxxxxxx     | 0.214 |   2.424 |    3.145 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U6 | B v -> CO v  | xxxxxxxxxx     | 0.327 |   2.751 |    3.471 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U5 | CI v -> CO v | xxxxxxxxxx     | 0.198 |   2.949 |    3.669 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U4 | CI v -> CO v | xxxxxxxxxx     | 0.200 |   3.149 |    3.869 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U3 | CI v -> CO v | xxxxxxxxxx     | 0.195 |   3.343 |    4.064 | 
     | dpath/g_pe_3__pe/s1_multiplier/intadd_1_U2 | CI v -> CO v | xxxxxxxxxx     | 0.197 |   3.541 |    4.261 | 
     | dpath/g_pe_3__pe/s1_multiplier/U77         | A4 v -> Z ^  | xxxxxxxxxx     | 0.299 |   3.840 |    4.560 | 
     | dpath/g_pe_3__pe/s1_multiplier/U197        | A1 ^ -> Z v  | xxxxxxxxxx     | 0.167 |   4.007 |    4.727 | 
     | dpath/g_pe_3__pe/s1_mul_reg/U9             | B2 v -> Z v  | xxxxxxxxxx     | 0.218 |   4.225 |    4.945 | 
     | dpath/g_pe_3__pe/s1_mul_reg/q_reg_7_       | D v          | xxxxxxxxxx     | 0.000 |   4.225 |    4.945 | 
     +---------------------------------------------------------------------------------------------------------+ 
```

The hold time report is shown below.

```
Path 1: MET Hold Check with Pin ctrl/state_reg/q_reg_0_/CP 
Endpoint:   ctrl/state_reg/q_reg_0_/CN (^) checked with  leading edge of 
'TinyNPU_clk'
Beginpoint: rst                        (v) triggered by  leading edge of 
'TinyNPU_clk'
Path Groups: {TinyNPU_clk}
Analysis View: analysis_typical
Other End Arrival Time          0.000
+ Hold                         -0.032
+ Phase Shift                   0.000
- CPPR Adjustment               0.000
= Required Time                -0.032
  Arrival Time                  0.029
  Slack Time                    0.061
     Clock Rise Edge                      0.000
     + Input Delay                        0.005
     = Beginpoint Arrival Time            0.005

     +------------------------------------------------------------------------------------+ 
     |        Instance         |     Arc     |     Cell      | Delay | Arrival | Required | 
     |                         |             |               |       |  Time   |   Time   | 
     |-------------------------+-------------+---------------+-------+---------+----------| 
     |                         | rst v       |               |       |   0.005 |   -0.056 | 
     | ctrl/U26                | I v -> ZN ^ | xxxxxxxxxxx   | 0.024 |   0.029 |   -0.032 | 
     | ctrl/state_reg/q_reg_0_ | CN ^        | xxxxxxxxxxx   | 0.000 |   0.029 |   -0.032 | 
     +------------------------------------------------------------------------------------+ 
```

Assume a hidden layer requiring full hardware utilization (i.e., full input and weight FIFOs, all PEs involved). Loading inputs and/or weights during LD0 or LD1 states and performing MAC operations requires N+1 and N+2 cycles, respectively. Dumping MAC outputs also takes N cycles. For sufficiently large N, this would roughly equal 3N cycles per hidden layer. Thus, setting N = 10000 with the critical path time of 5 ns yields an estimated runtime of 0.15 ms per hidden layer.

### Power

The power report summary is shown below. Units are in mW.

```
Total Power
-----------------------------------------------------------------------------------------
Total Internal Power:       13.02298915 	   83.6161%
Total Switching Power:       2.55158896 	   16.3829%
Total Leakage Power:         0.00016594 	    0.0011%
Total Power:                15.57474405
-----------------------------------------------------------------------------------------

Group                           Internal   Switching     Leakage       Total  Percentage 
                                Power      Power         Power         Power  (%)        
-----------------------------------------------------------------------------------------
Sequential                         9.235      0.6387   5.814e-05       9.873       63.39
Macro                                  0           0           0           0           0
IO                                     0           0           0           0           0
Combinational                      3.788       1.913   0.0001078       5.701       36.61
Clock (Combinational)                  0           0           0           0           0
Clock (Sequential)                     0           0           0           0           0
-----------------------------------------------------------------------------------------
Total                              13.02       2.552   0.0001659       15.57         100
-----------------------------------------------------------------------------------------

Rail                  Voltage   Internal   Switching     Leakage       Total  Percentage 
                                Power      Power         Power         Power  (%)        
-----------------------------------------------------------------------------------------
VDD                       1.8      13.02       2.552   0.0001659       15.57         100
```

Similar to area, about 98% and 2% of the power is consumed by TinyNPU’s data path and control logic, respectively. Moreover, the PEs and FIFOs consume the most of this power.

![fig7](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig7.png)

### Layout

Below is the final layout of TinyNPU without filler cells.

![fig8](https://github.com/junyoung-sim/tiny-npu/blob/main/docs/fig8.png)
