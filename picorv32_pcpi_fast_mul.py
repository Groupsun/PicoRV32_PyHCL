'''
picorv32_pcpi_fast_mul
'''

from pyhcl import *

EXTRA_MUL_FFS = 0
EXTRA_INSN_FFS = 0
MUL_CLKGATE = 0


class Picorv32PcpiFastMul(Module):
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

    instr_mul = Reg(Bool)
    instr_mulh = Reg(Bool)
    instr_mulhsu = Reg(Bool)
    instr_mulhu = Reg(Bool)
    instr_any_mul = instr_mul | instr_mulh | instr_mulhsu | instr_mulhu
    instr_any_mulh = instr_mulh | instr_mulhsu | instr_mulhu
    instr_rs1_signed = instr_mulh | instr_mulhsu
    instr_rs2_signed = instr_mulh

    shift_out = Reg(Bool)
    active = RegInit(U.w(4)(0))
    rs1 = Reg(U.w(33))
    rs2 = Reg(U.w(33))
    rs1_q = Reg(U.w(33))
    rs2_q = Reg(U.w(33))
    rd = Reg(U.w(64))
    rd_q = Reg(U.w(64))

    pcpi_insn_valid = io.pcpi_valid & (io.pcpi_insn[6:0] == U.w(7)(0b0110011) & (io.pcpi_insn[31:25] == U.w(7)(0b0000001)))
    pcpi_insn_valid_q = Reg(Bool)

    instr_mul <<= U(0)
    instr_mulh <<= U(0)
    instr_mulhsu <<= U(0)
    instr_mulhu <<= U(0)

    with when((~Module.reset) & Mux(U(EXTRA_INSN_FFS), pcpi_insn_valid_q, pcpi_insn_valid)):
        with when(io.pcpi_insn[14:12] == U.w(3)(0b000)):
            instr_mul <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b001)):
            instr_mulh <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b010)):
            instr_mulhsu <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b011)):
            instr_mulhu <<= U(1)

    pcpi_insn_valid_q <<= pcpi_insn_valid
    with when(~U(MUL_CLKGATE) | active[0]):
        rs1_q <<= rs1
        rs2_q <<= rs2
    with when(~U(MUL_CLKGATE) | active[1]):
        rd <<= (Mux(U(EXTRA_MUL_FFS), rs1_q, rs1).to_sint() * Mux(U(EXTRA_MUL_FFS), rs2_q, rs2).to_sint()).to_uint()
    with when(~U(MUL_CLKGATE) | active[2]):
        rd_q <<= rd

    with when(instr_any_mul & ~(Mux(U(EXTRA_MUL_FFS), active[3:0], active[1:0]))):
        with when(instr_rs1_signed):
            rs1 <<= (io.pcpi_rs1.to_sint()).to_uint()
        with otherwise():
            rs1 <<= io.pcpi_rs1.to_uint()

        with when(instr_rs2_signed):
            rs2 <<= (io.pcpi_rs2.to_sint()).to_uint()
        with otherwise():
            rs2 <<= io.pcpi_rs2.to_uint()
        active <<= active | U.w(4)(0b0001)
    with otherwise():
        active <<= active & U.w(4)(0b1110)

    active <<= CatBits(active[2:0], active[0])
    shift_out <<= instr_any_mulh

    io.pcpi_wr <<= Mux(U(EXTRA_MUL_FFS), active[3], active[1])
    io.pcpi_wait <<= U(0)
    io.pcpi_ready <<= Mux(U(EXTRA_MUL_FFS), active[3], active[1])

    io.pcpi_rd <<= Mux(shift_out, Mux(U(EXTRA_MUL_FFS), rd_q, rd) >> 32, Mux(U(EXTRA_MUL_FFS), rd_q, rd))


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32PcpiFastMul()), "Picorv32PcpiFastMul.fir")
    Emitter.dumpVerilog(f)
