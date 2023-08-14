from dataclasses import dataclass
from picozk import *
from picozk.functions import picozk_function

# instruction set:
# 0 - add src1 src2 dest
# 1 - je src1 src2 pcdest
# 2 - jmp pcdest
# else nop

# global program and memory
prog = None
mem = None

# Class to hold a single instruction
@dataclass
class Instr:
    opcode: int
    src1: int
    src2: int
    dest: int

# Class to hold a program as multiple lists of instructions
@dataclass
class Program:
    opcode: ZKList
    src1: ZKList
    src2: ZKList
    dest: ZKList

# Fetch an instruction from a program
def fetch(prog: Program, pc: SecretInt):
    return Instr(prog.opcode[pc],
                 prog.src1[pc],
                 prog.src2[pc],
                 prog.dest[pc])

# Take one step of the CPU
def step(prog: Program, pc: SecretInt, mem: ZKList):
    instr = fetch(prog, pc)
    a1 = mem[instr.src1]
    a2 = mem[instr.src2]
    new_pc = pc

    # add instruction
    cond0 = instr.opcode == 0
    dest = mux(cond0, instr.dest, 0)
    mem[dest] = mux(cond0, a1 + a2, mem[dest])
    new_pc = mux(cond0, pc + 1, new_pc)

    # je instruction
    cond1 = instr.opcode == 1
    new_pc = mux(cond1,
                 mux(a1 == a2, instr.dest, pc + 1),
                 new_pc)

    # jmp instruction
    cond2 = instr.opcode == 2
    new_pc = mux(cond2, instr.dest, new_pc)

    return new_pc

# Translate a program into the Program class
# Requires an upper bound on the program's length
# (to avoid revealing the number of instructions)
def make_program(prog, length):
    opcode = ZKList([3 for _ in range(length)])
    src1 = ZKList([0 for _ in range(length)])
    src2 = ZKList([0 for _ in range(length)])
    dest = ZKList([0 for _ in range(length)])

    for i, instr in enumerate(prog):
        opcode[i] = instr.opcode
        src1[i] = instr.src1
        src2[i] = instr.src2
        dest[i] = instr.dest

    return Program(opcode, src1, src2, dest)

# add 0 1 1  -- add loc 0 and 1, put result in 1
# je 1 2 3   -- halt (goto 3) if loc 1 and 2 are equal
# jmp 0      -- go back to start
test_prog = [Instr(0, 0, 1, 1),
             Instr(1, 2, 1, 3),
             Instr(2, 0, 0, 0)]
# accumulator = 0, increment = 1, target = 10
init_memory = [1, 0, 10]

with PicoZKCompiler('picozk_test', options=['ram']):
    # Generate the program
    program = make_program(test_prog, 10)
    # Initialize the memory
    memory = ZKList(init_memory)

    # Run the CPU for 100 steps
    pc = 0
    for i in range(100):
        pc = step(program, pc, memory)
        # print('step:', i, 'new pc:', val_of(pc))
        # print('new memory:', val_of(memory))
    reveal(memory[1])
    print('Final count:', memory[1])
