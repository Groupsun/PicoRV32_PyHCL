'''
picorv32_pcpi_div
'''

from pyhcl import *


class Picorv32PcpiDiv(Module):
    io = IO(
        pcpi_valid=Input(Bool),
        pcpi_insn=Input(U.w(32)),
        pcpi_rs1=Input(U.w(32)),
        pcpi_rs2=Input(U.w(32)),
        pcpi_wr=Output(Bool),
        pcpi_rd=Output(U.w(32)),
        pcpi_wait=Output(Bool),
        pcpi_ready=Output(Bool),

    )

    pcpi_rs2_or = RegInit(U.w(32)(0))
    for i in range(32):
        pcpi_rs2_or |= io.pcpi_rs2[i]

    instr_div = Reg(Bool)
    instr_divu = Reg(Bool)
    instr_rem = Reg(Bool)
    instr_remu = Reg(Bool)
    instr_any_div_rem = instr_div | instr_divu | instr_rem | instr_remu

    pcpi_wait_q = Reg(Bool)
    start = io.pcpi_wait & (~pcpi_wait_q)

    instr_div <<= U(0)
    instr_divu <<= U(0)
    instr_rem <<= U(0)
    instr_remu <<= U(0)

    with when((~Module.reset) & io.pcpi_valid & (~io.pcpi_ready) & io.pcpi_insn[6:0] == U.w(7)(0b0110011) & io.pcpi_insn[31:25] == U.w(7)(0b0000001)):
        with when(io.pcpi_insn[14:12] == U.w(3)(0b100)):
            instr_div <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b101)):
            instr_divu <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b110)):
            instr_rem <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b111)):
            instr_remu <<= U(1)

    io.pcpi_wait <<= instr_any_div_rem & (~Module.reset)
    pcpi_wait_q <<= io.pcpi_wait & (~Module.reset)

    dividend = Reg(U.w(32))
    divisor = Reg(U.w(63))
    quotient = Reg(U.w(32))
    quotient_msk = Reg(U.w(32))
    runnning = RegInit(U.w(1)(0))
    outsign = Reg(Bool)

    io.pcpi_ready <<= U(0)
    io.pcpi_wr <<= U(0)
    io.pcpi_rd <<= U(0)

    with when(start):
        runnning <<= U(1)
        dividend <<= (instr_div | instr_rem) & Mux(io.pcpi_rs1[31], (-io.pcpi_rs1.to_sint()).to_uint(), io.pcpi_rs1)
        divisor <<= ((instr_div | instr_rem) & Mux(io.pcpi_rs2[31], (-io.pcpi_rs2.to_sint()).to_uint(), io.pcpi_rs2)) << 31
        outsign <<= (instr_div & (io.pcpi_rs1[31] != io.pcpi_rs2[31]) & pcpi_rs2_or) | (instr_rem & io.pcpi_rs1[31])
        quotient <<= U(0)
        quotient_msk <<= U(1 << 31)
    with elsewhen(~quotient_msk & runnning):
        runnning <<= U(0)
        io.pcpi_ready <<= U(1)
        io.pcpi_wr <<= U(1)

        with when(instr_div | instr_divu):
            io.pcpi_rd <<= Mux(outsign, (-quotient.to_sint()).to_uint(), quotient)
        with otherwise():
            io.pcpi_rd <<= Mux(outsign, (-dividend.to_sint()).to_uint(), dividend)
    with otherwise():
        with when(divisor <= dividend):
            dividend <<= dividend - divisor
            quotient <<= quotient | quotient_msk
        divisor <<= divisor >> 1
        quotient_msk <<= quotient_msk >> 1


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32PcpiDiv()), "Picorv32PcpiDiv.fir")
    Emitter.dumpVerilog(f)
