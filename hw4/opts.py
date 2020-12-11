from m5 import fatal
import m5.objects
from textwrap import TextWrapper

#add options for number of ROB entries, IQ entries, and number of physical
#floating point registers
def addOpts(parser):
    # Parameters I added
    parser.add_option("--num-rob-entries", dest="rob", type="int", default=192)
    parser.add_option("--num-iq-entries", dest="iq", type="int", default=64)
    parser.add_option("--num-phys-float-regs", dest="phys", type="int", default=256)

#set parameters taken in from options on command line
def set_config(cpu_list, options):
  for cpu in cpu_list:
    # set parameters for each thing
    cpu.numROBEntries = options.rob
    cpu.numIQEntries = options.iq
    cpu.numPhysFloatRegs = options.phys
