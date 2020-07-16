'''
picorv32
'''

from pyhcl import *


class Picorv32(Module):
    io = IO(
        trap=Output(Bool),

        mem_valid=Output(Bool),
        mem_instr=Output(Bool),
        mem_ready=Input(Bool),

        mem_addr=Output(U.w(32)),
        mem_wdata=Output(U.w(32)),
        mem_wstrb=Output(U.w(4)),
        mem_rdata=Input(U.w(32)),

        # Look-Ahead Interface
        mem_la_read=Output(Bool),
        mem_la_write=Output(Bool),
        mem_la_addr=Output(U.w(32)),
        mem_la_wdata=Output(U.w(32)),
        mem_la_wstrb=Output(U.w(4)),

        # Pico Co-Processor Interface (PCPI)
        pcpi_valid=Output(Bool),
        pcpi_insn=Output(U.w(32)),
        pcpi_rs1=Output(U.w(32)),
        pcpi_rs2=Output(U.w(32)),
        pcpi_wr=Input(Bool),
        pcpi_rd=Input(U.w(32)),
        pcpi_wait=Input(Bool),
        pcpi_ready=Input(Bool),

        # IRQ Interface
        irq=Input(U.w(32)),
        eoi=Output(U.w(32)),

        # Trace Interface
        trace_valid=Output(Bool),
        trace_data=Output(U.w(36)),

    )


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32()), "Picorv32.fir")
    Emitter.dumpVerilog(f)
