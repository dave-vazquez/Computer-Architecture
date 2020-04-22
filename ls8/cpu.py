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
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


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
            PRN: self.handle_PRN,
            LDI: self.handle_LDI,
            MUL: self.handle_MUL,
            PUSH: self.handle_PUSH,
            POP: self.handle_POP
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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
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
            # read the next instruction from RAM
            next_inst = self.ram_read(self.pc)
            # parse the instruction
            inst = self.parse_instruction(next_inst)
            # if HLT, terminate the loop
            if next_inst is HLT:
                running = False
            else:
                self.operations[next_inst](inst["num_ops"])

    def handle_PRN(self, num_ops):
        # read the register number from RAM at address: pc + 1
        reg_num = self.ram_read(self.pc + 1)

        # get the value stored in the register
        value = self.reg[reg_num]
        # print it
        print(value)
        # increment the program counter by 2 to get to the next instruction
        self.pc += num_ops + 1

    def handle_LDI(self, num_ops):
        # read the register number from RAM at address: pc + 1
        reg_num = self.ram_read(self.pc + 1)
        # read the value from RAM at address: pc + 2
        value = self.ram_read(self.pc + 2)
        # set the value to the register
        self.reg[reg_num] = value
        # increment the program counter by 3 to get to the next instruction
        self.pc += num_ops + 1

    def handle_MUL(self, num_ops):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_a, reg_b)

        self.pc += num_ops + 1

    def handle_PUSH(self, num_ops):
        self.reg[7] -= 1
        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num]
        stack_address = self.reg[7]

        self.ram_write(stack_address, value)

        self.pc += num_ops + 1

    def handle_POP(self, num_ops):
        reg_num = self.ram_read(self.pc + 1)
        stack_address = self.reg[7]
        value = self.ram_read(stack_address)
        self.reg[reg_num] = value
        self.reg[7] += 1

        self.pc += num_ops + 1

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
