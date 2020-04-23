"""CPU functionality."""
import pprint
import sys

p_print = pprint.PrettyPrinter(width=30).pprint

# RESERVED REGISTERS
IM = 5
IS = 6
SP = 7
# RESERVED ADDRESSES
STACK_START_ADDRESS = 0b11110011
# OPERATION CODES
HLT = 0b00000001
LDI = 0b00000010
PRN = 0b00000111
PSH = 0b00000101
POP = 0b00000110
# ALU OPERATION CODES
ADD = 0b00000000
SUB = 0b00000001
MUL = 0b00000010
DIV = 0b00000011
MOD = 0b00000100
INC = 0b00000101
DEC = 0b00000110
CMP = 0b00000111
AND = 0b00001000
NOT = 0b00001001
OR = 0b00001010
XOR = 0b00001011
SHL = 0b00001100
SHR = 0b00001101


class CPU:
    """Main CPU class."""

    def __init__(self):
        # initialize 256-byte RAM
        self.ram = [0] * 256
        # initialize registers R0 - R7
        self.reg = [0] * 8
        # initialize program counter
        self.pc = 0
        # set R7, SP (Stack Pointer), to the address of the start of stack
        self.reg[SP] = STACK_START_ADDRESS

        # initializes operation branch table
        self.operations = {
            PRN: self.PRN,
            LDI: self.LDI,
            PSH: self.PSH,
            POP: self.POP
        }

    def load(self, program_file_name):
        address = 0
        # reads each line of the program
        with open(program_file_name) as f:
            for line in f:
                # parses each line of binary instruction
                line = line.split('#')
                line = line[0].strip()

                # skips lines that do not contain a binary instruction
                if line == '':
                    continue
                # adds the instruction to RAM at the address value
                # and increments the address
                self.ram[address] = int(line, 2)
                address += 1

    def alu(self, op, operands):
        """ALU operations."""
        reg_a, reg_b = operands

        if op is ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):
        # returns the MDR (Memory Data Register)
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        # writes the MDR (Memory Data Register)
        # to the MAR (Memory Address Register)
        self.ram[mar] = mdr

    def run(self):
        running = True
        while running:
            next_instruction = self.ram_read(self.pc)
            running = self.execute(next_instruction)

    def execute(self, instruction):
        # parses instruction, stores parsed instruction as dict in 'inst'
        inst = self.parse_instruction(instruction)

        if inst["inst_id"] is not HLT:
            # destructures parsed 'inst' dict
            num_ops, is_alu, sets_pc, inst_id = inst.values()
            # initializes operand list of length 'num_ops'
            operands = [None] * num_ops

            # reads operands from memory and stores in 'operands' list
            for i in range(len(operands)):
                operand = self.ram_read(self.pc + i + 1)
                operands[i] = operand

            # redirects to ALU if instruction is an ALU instruction
            if is_alu:
                self.alu(inst_id, operands)
            # otherwise executes directly from `operations` branch-table
            else:
                self.operations[inst_id](operands)

            # increments pc if the instruction requires it
            self.pc += num_ops + 1

            # continues run-loop if 'inst_id' is not HLT
            return True

        return False

    def parse_instruction(self, inst):
        # masks all but first 2 bits, bit-wise shifts 6 to right, castes to int
        num_ops = int((0b11000000 & inst) >> 6)
        # masks all but 3rd bit, bit-wise shifts 5 to right, castes to bool
        is_alu = bool((0b00100000 & inst) >> 5)
        # masks all but 4th bit, bit-wise shifts 4 to right, castes to bool
        sets_pc = bool((0b00010000 & inst) >> 4)
        # masks all but last four bits
        inst_id = 0b00001111 & inst

        # returns vals as a dictionary
        return {
            "num_ops": num_ops,
            "is_alu": is_alu,
            "sets_pc": sets_pc,
            "inst_id": inst_id,
        }

    def PRN(self, operand):
        reg_num = operand[0]
        value = self.reg[reg_num]
        print(value)

    def LDI(self, operands):
        # read the register number from RAM at address: pc + 1
        reg_num, value = operands
        # read the value from RAM at address: pc + 2
        value = operands[1]
        # set the value to the register
        self.reg[reg_num] = value

    def PSH(self, operand):
        # extract the operand
        reg_num = operand[0]
        # decrements the SP
        self.reg[SP] -= 1
        # extract the value stored in the target register
        value = self.reg[reg_num]
        # extract the stack address stored in the SP register
        stack_address = self.reg[SP]
        # write the value to the stack address
        self.ram_write(stack_address, value)

    def POP(self, operand):
        reg_num = operand[0]
        # extracts the stack address stored in the SP register
        stack_address = self.reg[SP]
        # extracts the value read from RAM at the stack address
        value = self.ram_read(stack_address)
        # stores the value in the given register
        self.reg[reg_num] = value
        # increments the SP
        self.reg[SP] += 1
