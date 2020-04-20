"""CPU functionality."""

import sys


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
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
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
            self.trace()
            # reads the instruction from RAM at address: PC (program counter)
            inst = self.ram_read(self.pc)

            # LDI - register immediate, sets the value of a register to an integer
            if inst == self.LDI:
                # read the register number from RAM at address: pc + 1
                reg_num = self.ram_read(self.pc + 1)
                # read the value from RAM at address: pc + 2
                value = self.ram_read(self.pc + 2)
                # set the value to the register
                self.reg[reg_num] = value
                # increment the program counter by 3 to get to the next instruction
                self.pc += 3

            # PRN - register, print to the console the value stored in the given register
            elif inst == self.PRN:
                # read the register number from RAM at address: pc + 1
                reg_num = self.ram_read(self.pc + 1)
                # get the value stored in the register
                value = self.reg[reg_num]
                # print it
                print(value)
                # increment the program counter by 2 to get to the next instruction
                self.pc += 2
            # HLT - half the CPU (and exit the emulator)
            elif inst == self.HLT:
                # flag running to False, and let the program exit
                running = False
