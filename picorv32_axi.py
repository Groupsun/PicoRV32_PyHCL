'''
picorv32_axi
'''

from pyhcl import *
from example import picorv32_axi_adapter as paa
from example import picorv32 as pic


class Picorv32Axi(Module):
    io = IO(
        trap=Output(Bool),
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
    )

    mem_valid = Wire(Bool)
    mem_addr = Wire(U.w(32))
    mem_wdata = Wire(U.w(32))
    mem_wstrb = Wire(U.w(4))
    mem_instr = Wire(Bool)
    mem_ready = Wire(Bool)
    mem_rdata = Wire(U.w(32))

    axi_adapter = paa.Picorv32AxiAdapter()

    axi_adapter.io.mem_axi_awvalid = io.mem_axi_awvalid
    axi_adapter.io.mem_axi_awready = io.mem_axi_awready
    axi_adapter.io.mem_axi_awaddr = io.mem_axi_awaddr
    axi_adapter.io.mem_axi_awprot = io.mem_axi_awprot
    axi_adapter.io.mem_axi_wvalid = io.mem_axi_wvalid
    axi_adapter.io.mem_axi_wready = io.mem_axi_wready
    axi_adapter.io.mem_axi_wdata = io.mem_axi_wdata
    axi_adapter.io.mem_axi_wstrb = io.mem_axi_wstrb
    axi_adapter.io.mem_axi_bvalid = io.mem_axi_bvalid
    axi_adapter.io.mem_axi_bready = io.mem_axi_bready
    axi_adapter.io.mem_axi_arvalid = io.mem_axi_arvalid
    axi_adapter.io.mem_axi_arready = io.mem_axi_arready
    axi_adapter.io.mem_axi_araddr = io.mem_axi_araddr
    axi_adapter.io.mem_axi_arprot = io.mem_axi_arprot
    axi_adapter.io.mem_axi_rvalid = io.mem_axi_rvalid
    axi_adapter.io.mem_axi_rready = io.mem_axi_arready
    axi_adapter.io.mem_axi_rdata = io.mem_axi_rdata
    axi_adapter.io.mem_valid = mem_valid
    axi_adapter.io.mem_instr = mem_instr
    axi_adapter.io.mem_ready = mem_ready
    axi_adapter.io.mem_addr = mem_addr
    axi_adapter.io.mem_wdata = mem_wdata
    axi_adapter.io.mem_wstrb = mem_wstrb
    axi_adapter.io.mem_rdata = mem_rdata

    picorv32_core = pic.Picorv32()

    picorv32_core.io.mem_valid = mem_valid
    picorv32_core.io.mem_addr = mem_addr
    picorv32_core.io.mem_wdata = mem_wdata
    picorv32_core.io.mem_wstrb = mem_wstrb
    picorv32_core.io.mem_instr = mem_instr
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


if __name__ == '__main__':
    f = Emitter.dump(Emitter.emit(Picorv32Axi()), "Picorv32Axi.fir")
    Emitter.dumpVerilog(f)
