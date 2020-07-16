'''
picorv32_regs
'''

from pyhcl import *


class Picorv32Regs(Module):
    io = IO(
        wen=Input(Bool),
        waddr=Input(U.w(6)),
        raddr1=Input(U.w(6)),
        raddr2=Input(U.w(6)),
        wdata=Input(U.w(32)),
        rdata1=Output(U.w(32)),
        rdata2=Output(U.w(32)),

    )

    regs = Reg(Vec(31, U.w(32)))

    with when(io.wen):
        regs[~io.waddr[4:0]] <<= io.wdata

    io.rdata1 <<= regs[~io.raddr1[4:0]]
    io.rdata2 <<= regs[~io.raddr2[4:0]]


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32Regs()), "Picorv32Regs.fir")
    Emitter.dumpVerilog(f)
