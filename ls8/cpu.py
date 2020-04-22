"""CPU functionality."""

import pprint
import sys

from branch_table import BranchTable

p_print = pprint.PrettyPrinter(width=30).pprint


class CPU:
    """Main CPU class."""

    def __init__(self):
        # ram initialized to 256 bytes
        # (each decimal number is an 8-bit binary number)
        self.ram = [0] * 256
        # register initalized to 8-bytes
        self.reg = [0] * 8
        # program counter
        self.pc = 0
        # some stored instructions
        # definitions in the run() method
        self.operations = BranchTable()

    def load(self, program_file_name):
        address = 0
        # reads each line of the program
        with open(program_file_name) as f:
            for line in f:
                # parses each line of binary instruction
                line = line.split('#')
                line = line[0].strip()

                # skips lines that do not contain
                # binary instruction
                if line == '':
                    continue
                # adds the instruction to RAM at the address value
                self.ram[address] = int(line, 2)

                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

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
        # if MAR (Memory Address Register) exists in ram
        if mar < len(self.ram):
            # return the MDR (Memory Data Register)
            return self.ram[mar]
        else:
            print(f"Memory Address Register (MAR): {mar} not found.")

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
            if inst["op_code"] is 0b00000001:
                running = False
            else:
                # else execute the command
                self = self.operations.run(inst, self)

    def parse_instruction(self, inst):
        # masks all but first 2 bits, bit-wise shifts 6 to right, castes to int
        num_ops = int((0b11000000 & inst) >> 6)
        # masks all but 3rd bit, bit-wise shifts 5 to right, castes to bool
        is_alu = bool((0b00100000 & inst) >> 5)
        # masks all but 4th bit, bit-wise shifts 4 to right, castes to bool
        sets_pc = bool((0b00010000 & inst) >> 4)
        # masks all but last four bits
        inst_id = 0b00001111 & inst

        op_code = ""
        # iterates through the dictionary of existing op_codes
        for code in self.operations.get_op_codes():
            # matches/stores the instruction to the op_code
            if inst == code:
                op_code = code

        # returns vals as a dictionary
        return {
            "num_ops": num_ops,
            "is_alu": is_alu,
            "sets_pc": sets_pc,
            "inst_id": inst_id,
            "op_code": op_code
        }
