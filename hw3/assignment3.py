# Import SimObjects for ISAs
import m5
from m5.objects import *

# Import simulator binary
import os
gem5_path = os.environ["GEM5"]

# Import caches
from Caches import *

# Instantiate object parser and add prog argument
import optparse
parser = optparse.OptionParser()
parser.add_option("--prog", type="str", default=None)
parser.add_option("--bp", type="str", default=None)
parser.add_option("--bp_size", type="int", default=None)
parser.add_option("--bp_bits", type="int", default=None)

# Add parser for clock speed
parser.add_option("--clock_freq", type="str", default=None)

# Add parser for all cache options
parser.add_option("--is_read_only", type="str", default=None)
parser.add_option("--writeback_clean", type="str", default=None)
parser.add_option("--size", type="str", default=None)
parser.add_option("--assoc", type="int", default=None)
parser.add_option("--tag_latency", type="int", default=None)
parser.add_option("--data_latency", type="int", default=None)
parser.add_option("--response_latency", type="int", default=None)
parser.add_option("--mshrs", type="int", default=None)
parser.add_option("--tgts_per_mshr", type="int", default=None)
parser.add_option("--l1i_size", type="int", default=None)
parser.add_option("--l1i_assoc", type="int", default=None)
parser.add_option("--l1d_size", type="str", default=None)
parser.add_option("--l1d_assoc", type="int", default=None)

(options, args) = parser.parse_args()
program = options.prog

bp = options.bp

# Set clock/voltage domain
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.voltage_domain = VoltageDomain()

# Set clock frequency (using only ARM ISA)
isa = m5.defines.buildEnv['TARGET_ISA']
if options.clock_freq:
    system.clk_domain.clock = options.clock_freq
else:
    system.clk_domain.clock = '1.2GHz'


# Set up memory
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create CPU
if bp == "LocalBP":
    system.cpu = MinorCPU(branchPred = LocalBP())
    system.cpu.branchPred.BTBEntries = options.bp_size
    system.cpu.branchPred.localPredictorSize = options.bp_size
    system.cpu.branchPred.localCtrBits = options.bp_bits
elif bp == "TournamentBP":
    system.cpu = MinorCPU(branchPred=TournamentBP())
    system.cpu.branchPred.BTBEntries = options.bp_size
    system.cpu.branchPred.localPredictorSize = options.bp_size
    system.cpu.branchPred.localCtrBits = options.bp_bits
    system.cpu.branchPred.globalPredictorSize = options.bp_size
    system.cpu.branchPred.globalCtrBits = options.bp_bits
else:
    system.cpu = MinorCPU()

system.membus = SystemXBar()

# TODO Connect ports
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()
# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)


system.cpu.createInterruptController()
if isa == 'x86':
    system.cpu.interrupts[0].pio = system.membus.master
    system.cpu.interrupts[0].int_master = system.membus.slave
    system.cpu.interrupts[0].int_slave = system.membus.master

system.system_port = system.membus.slave

# Create memory controller and connect to memory bus
system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.master



# Create process
process = Process()
apps_path =  "/project/linuxlab/gem5/test_progs/"
if program == "daxpy" and isa == "x86":
    process.cmd = [apps_path + '/daxpy/daxpy_x86']
elif program == "daxpy" and isa == "arm":
    process.cmd = [apps_path + '/daxpy/daxpy_arm']
elif program == "queens" and isa == "x86":
    process.cmd = [apps_path + '/queens/queens_x86']
    process.cmd += ["10 -c"]
elif program == "queens" and isa == "arm":
    process.cmd = [apps_path + 'queens/queens_arm'] 
    process.cmd += ["10 -c"]

system.cpu.workload = process
system.cpu.createThreads()

# Instantiate system and begin execution
root = Root(full_system = False, system = system)
m5.instantiate()
print ("Beginning simulation!")
exit_event = m5.simulate()
print ('Exiting @ tick because ' .format(m5.curTick(), exit_event.getCause()))
