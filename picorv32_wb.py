'''
picorv32_wb
'''

from pyhcl import *
from example import picorv32 as pic


class Picorv32Wb(Module):
    io = IO(
        trap=Output(Bool),

        # Wishbone interfaces
        wbm_adr_o=Output(U.w(32)),
        wbm_dat_o=Output(U.w(32)),
        wbm_dat_i=Input(U.w(32)),
        wbm_we_o=Output(Bool),
        wbm_sel_o=Output(U.w(4)),
        wbm_stb_o=Output(Bool),
        wbm_ack_i=Input(Bool),
        wbm_cyc_o=Output(Bool),

        # Pico Co-Processor Interface (PCPI)
        pcpi_valid=Output(Bool),
        pcpi_insn=Output(U.w(32)),
        pcpi_rs1=Output(U.w(32)),
        pcpi_rs2=Output(U.w(32)),
        pcpi_wr=Input(Bool),
        pcpi_rd=Input(U.w(32)),
        pcpi_wait=Input(Bool),
        pcpi_ready=Input(Bool),

        # IRQ interface
        irq=Input(U.w(32)),
        eoi=Output(U.w(32)),

        # Trace Interface
        trace_valid=Output(Bool),
        trace_data=Output(U.w(36)),

        mem_instr=Output(Bool),
    )

    mem_valid = Wire(Bool)
    mem_addr = Wire(U.w(32))
    mem_wdata = Wire(U.w(32))
    mem_wstrb = Wire(U.w(4))
    mem_ready = Reg(Bool)
    mem_rdata = Reg(U.w(32))

    picorv32_core = pic.Picorv32()

    picorv32_core.io.mem_valid = mem_valid
    picorv32_core.io.mem_addr = mem_addr
    picorv32_core.io.mem_wdata = mem_wdata
    picorv32_core.io.mem_wstrb = mem_wstrb
    picorv32_core.io.mem_instr = io.mem_instr
    picorv32_core.io.mem_ready = mem_ready
    picorv32_core.io.mem_rdata = mem_rdata

    picorv32_core.io.pcpi_valid = io.pcpi_valid
    picorv32_core.io.pcpi_insn = io.pcpi_insn
    picorv32_core.io.pcpi_rs1 = io.pcpi_rs1
    picorv32_core.io.pcpi_rs2 = io.pcpi_rs2
    picorv32_core.io.pcpi_wr = io.pcpi_wr
    picorv32_core.io.pcpi_rd = io.pcpi_rd
    picorv32_core.io.pcpi_wait = io.pcpi_wait
    picorv32_core.io.pcpi_ready = io.pcpi_ready

    picorv32_core.io.irq = io.irq
    picorv32_core.io.eoi = io.eoi

    picorv32_core.io.trace_valid = io.trace_valid
    picorv32_core.io.trace_data = io.trace_data

    IDLE = U.w(2)(0b00)
    WBSTART = U.w(2)(0b01)
    WBEND = U.w(2)(0b10)

    state = RegInit(IDLE)

    we = mem_wstrb[0] | mem_wstrb[1] | mem_wstrb[2] | mem_wstrb[3]

    io.wbm_adr_o <<= U(0)
    io.wbm_dat_o <<= U(0)
    io.wbm_we_o <<= U(0)
    io.wbm_sel_o <<= U(0)
    io.wbm_stb_o <<= U(0)
    io.wbm_cyc_o <<= U(0)

    with when(state == IDLE):
        with when(mem_valid):
            io.wbm_adr_o <<= mem_addr
            io.wbm_dat_o <<= mem_wdata
            io.wbm_we_o <<= we
            io.wbm_sel_o <<= mem_wstrb

            io.wbm_stb_o <<= U(1)
            io.wbm_cyc_o <<= U(1)
            state <<= WBSTART
        with otherwise():
            mem_ready <<= U(0)

            io.wbm_stb_o <<= U(0)
            io.wbm_cyc_o <<= U(0)
            io.wbm_we_o <<= U(0)
    with elsewhen(state == WBSTART):
        mem_rdata <<= io.wbm_dat_i
        mem_ready <<= U(1)

        state <<= WBEND

        io.wbm_stb_o <<= U(0)
        io.wbm_cyc_o <<= U(0)
        io.wbm_we_o <<= U(0)
    with elsewhen(state == WBEND):
        mem_ready <<= U(0)

        state <<= IDLE
    with otherwise():
        state <<= IDLE

    io.pcpi_rs1 <<= U(0)
    io.trace_valid <<= U(0)
    io.trace_data <<= U(0)
    io.eoi <<= U(0)
    io.pcpi_insn <<= U(0)
    io.pcpi_valid <<= U(0)
    io.pcpi_rs2 <<= U(0)
    io.trap <<= U(0)
    io.mem_instr <<= U(0)
    mem_valid <<= U(0)
    mem_addr <<= U(0)
    mem_wdata <<= U(0)
    mem_wstrb <<= U(0)


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32Wb()), "Picorv32Wb.fir")
    Emitter.dumpVerilog(f)
