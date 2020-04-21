"""CPU functionality."""

import pprint
import sys

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
        self.op_codes = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "HLT": 0b00000001,
            "MUL": 0b10100010
        }

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
            # self.trace()
            # reads the instruction from RAM at address: PC (program counter)
            next_inst = self.ram_read(self.pc)
            inst = self.parse_instruction(next_inst)
            # LDI - register immediate, sets the value of a register to an integer
            if inst["op_code"] == self.op_codes["LDI"]:
                # read the register number from RAM at address: pc + 1
                reg_num = self.ram_read(self.pc + 1)
                # read the value from RAM at address: pc + 2
                value = self.ram_read(self.pc + 2)
                # set the value to the register
                self.reg[reg_num] = value
                # increment the program counter by 3 to get to the next instruction
                self.pc += inst["num_ops"] + 1

            # PRN - print register, print to the console the value stored in the given register
            elif inst["op_code"] == self.op_codes["PRN"]:
                # read the register number from RAM at address: pc + 1
                reg_num = self.ram_read(self.pc + 1)
                # get the value stored in the register
                value = self.reg[reg_num]
                # print it
                print(value)
                # increment the program counter by 2 to get to the next instruction
                self.pc += inst["num_ops"] + 1

            # MUL - registerA registerB - mutiplies values stored in each register
            #   and stores back in registerA
            elif inst["op_code"] == self.op_codes["MUL"]:
                # reads/stores the register numbers from the next two instructions
                reg_num_a = self.ram_read(self.pc + 1)
                reg_num_b = self.ram_read(self.pc + 2)

                # reads/stores the values from each of the registers
                operand_1 = self.reg[reg_num_a]
                operand_2 = self.reg[reg_num_b]
                # multiplies the values together
                result = operand_1 * operand_2
                # stores the value back in the register
                self.reg[reg_num_a] = result

                # increments the counter
                self.pc += inst["num_ops"] + 1

            # HLT - halt the CPU (and exit the emulator)
            elif inst["op_code"] == self.op_codes["HLT"]:
                # flag running to False, and let the program exit
                running = False

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
        for code in self.op_codes.values():
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
