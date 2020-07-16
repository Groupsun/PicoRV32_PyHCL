'''
picorv32_pcpi_mul
'''

from pyhcl import *

STEPS_AT_ONCE = 1
CARRY_CHAIN = 4


class Picorv32PcpiMul(Module):
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

    pcpi_wait_q = Reg(Bool)
    mul_start = io.pcpi_wait & (~pcpi_wait_q)

    instr_mul <<= U(0)
    instr_mulh <<= U(0)
    instr_mulhsu <<= U(0)
    instr_mulhu <<= U(0)

    with when((~Module.reset) & io.pcpi_valid & (io.pcpi_insn[6:0] == U.w(7)(0b0110011)) & (io.pcpi_insn[31:25] == U.w(7)(0b0000001))):
        with when(io.pcpi_insn[14:12] == U.w(3)(0b000)):
            instr_mul <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b001)):
            instr_mulh <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b010)):
            instr_mulhsu <<= U(1)
        with elsewhen(io.pcpi_insn[14:12] == U.w(3)(0b011)):
            instr_mulhu <<= U(1)

    io.pcpi_wait <<= instr_any_mul
    pcpi_wait_q <<= io.pcpi_wait

    rs1 = Reg(U.w(64))
    rs2 = Reg(U.w(64))
    rd = Reg(U.w(64))
    rdx = Reg(U.w(64))
    next_rs1 = Reg(U.w(64))
    next_rs2 = Reg(U.w(64))
    this_rs2 = Reg(U.w(64))
    next_rd = Reg(U.w(64))
    next_rdx = Reg(U.w(64))
    next_rdt = Reg(U.w(64))
    mul_counter = Reg(U.w(7))
    mul_waiting = RegInit(U.w(1)(1))
    mul_finish = Reg(Bool)

    next_rd <<= rd
    next_rdx <<= rdx
    next_rs1 <<= rs1
    next_rs2 <<= rs2

    for i in range(STEPS_AT_ONCE):
        this_rs2 <<= Mux(next_rs1[0], next_rs2, U(0))
        with when(U(CARRY_CHAIN == 0)):
            next_rdt <<= next_rd ^ next_rdx ^ this_rs2
            next_rdx <<= ((next_rd & next_rdx) | (next_rd & this_rs2) | (next_rdx & this_rs2)) << 1
            next_rd <<= next_rdt
        with otherwise():
            next_rdt <<= U(0)
            for j in range(0, 64, CARRY_CHAIN):
                pass    # need to fix
            next_rdx <<= next_rdt << 1

        next_rs1 <<= next_rs1 >> 1
        next_rs2 <<= next_rs2 << 1

    mul_finish <<= U(0)
    with when(mul_waiting):
        with when(instr_rs1_signed):
            rs1 <<= (io.pcpi_rs1.to_sint()).to_uint()
        with otherwise():
            rs1 <<= io.pcpi_rs1.to_uint()

        with when(instr_rs2_signed):
            rs2 <<= (io.pcpi_rs2.to_sint()).to_uint()
        with otherwise():
            rs2 <<= io.pcpi_rs2.to_uint()

        rd <<= U(0)
        rdx <<= U(0)
        mul_counter <<= Mux(instr_any_mulh, U(63 - STEPS_AT_ONCE), U(31 - STEPS_AT_ONCE))
        mul_waiting <<= ~mul_start
    with otherwise():
        rd <<= next_rd
        rdx <<= next_rdx
        rs1 <<= next_rs1
        rs2 <<= next_rs2

        mul_counter <<= mul_counter - U(STEPS_AT_ONCE)
        with when(mul_counter[6]):
            mul_finish <<= U(1)
            mul_waiting <<= U(1)

    io.pcpi_wr <<= U(0)
    io.pcpi_ready <<= U(0)
    io.pcpi_rd <<= U(0)
    with when(mul_finish & (~Module.reset)):
        io.pcpi_wr <<= U(1)
        io.pcpi_ready <<= U(1)
        io.pcpi_rd <<= Mux(instr_any_mulh, rd >> 32, rd)


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32PcpiMul()), "Picorv32PcpiMul.fir")
    Emitter.dumpVerilog(f)
