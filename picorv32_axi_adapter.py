'''
picorv32_axi_adapter
'''

from pyhcl import *


class Picorv32AxiAdapter(Module):
    io = IO(
        # AXI4-lite master memory interface

        mem_axi_awvalid=Output(Bool),
        mem_axi_awready=Input(Bool),
        mem_axi_awaddr=Output(U.w(32)),
        mem_axi_awprot=Output(U.w(3)),

        mem_axi_wvalid=Output(Bool),
        mem_axi_wready=Input(Bool),
        mem_axi_wdata=Output(U.w(32)),
        mem_axi_wstrb=Output(U.w(4)),

        mem_axi_bvalid=Input(Bool),
        mem_axi_bready=Output(Bool),

        mem_axi_arvalid=Output(Bool),
        mem_axi_arready=Input(Bool),
        mem_axi_araddr=Output(U.w(32)),
        mem_axi_arprot=Output(U.w(3)),

        mem_axi_rvalid=Input(Bool),
        mem_axi_rready=Output(Bool),
        mem_axi_rdata=Input(U.w(32)),

        # Native PicoRV32 memory interface

        mem_valid=Input(Bool),
        mem_instr=Input(Bool),
        mem_ready=Output(Bool),
        mem_addr=Input(U.w(32)),
        mem_wdata=Input(U.w(32)),
        mem_wstrb=Input(U.w(4)),
        mem_rdata=Output(U.w(32)),
    )

    ack_awvalid = RegInit(U.w(1)(0))
    ack_arvalid = Reg(U.w(1))
    ack_wvalid = Reg(U.w(1))
    xfer_done = Reg(U.w(1))

    mem_wstrb_or = RegInit(U.w(1)(0))
    for i in range(4):
        mem_wstrb_or |= io.mem_wstrb[i]

    io.mem_axi_awvalid <<= io.mem_valid & mem_wstrb_or & (~ack_awvalid)
    io.mem_axi_awaddr <<= io.mem_addr
    io.mem_axi_awprot <<= U(0)

    io.mem_axi_arvalid <<= io.mem_valid & (~io.mem_wstrb.to_bool()) & (~ack_arvalid)
    io.mem_axi_araddr <<= io.mem_addr
    io.mem_axi_arprot <<= Mux(io.mem_instr, U.w(3)(0b100), U.w(3)(0b000))

    io.mem_axi_wvalid <<= io.mem_valid & mem_wstrb_or & (~ack_wvalid)
    io.mem_axi_wdata <<= io.mem_wdata
    io.mem_axi_wstrb <<= io.mem_wstrb

    io.mem_ready <<= io.mem_axi_bvalid | io.mem_axi_rvalid
    io.mem_axi_bready <<= io.mem_valid & mem_wstrb_or
    io.mem_axi_rready <<= io.mem_valid & (~io.mem_wstrb.to_bool())
    io.mem_rdata <<= io.mem_axi_rdata

    xfer_done <<= io.mem_valid & io.mem_ready
    with when(io.mem_axi_awready & io.mem_axi_awvalid):
        ack_awvalid <<= U(1)
    with when(io.mem_axi_arready & io.mem_axi_arvalid):
        ack_arvalid <<= U(1)
    with when(io.mem_axi_wready & io.mem_axi_wvalid):
        ack_wvalid <<= U(1)
    with when(xfer_done | (~io.mem_valid)):
        ack_awvalid <<= U(0)
        ack_arvalid <<= U(0)
        ack_wvalid <<= U(0)


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32AxiAdapter()), "Picorv32AxiAdapter.fir")
    Emitter.dumpVerilog(f)
