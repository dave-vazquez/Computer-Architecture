LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class BranchTable:
    def __init__(self):
        self.branchtable = {}
        self.branchtable[LDI] = self._handle_LDI
        self.branchtable[PRN] = self._handle_PRN
        self.branchtable[HLT] = self._handle_HLT
        self.branchtable[MUL] = self._handle_MUL
        self.branchtable[PUSH] = self._handle_PUSH
        self.branchtable[POP] = self._handle_POP

    def _handle_LDI(self, cpu, inst):
        # read the register number from RAM at address: pc + 1
        reg_num = cpu.ram_read(cpu.pc + 1)
        # read the value from RAM at address: pc + 2
        value = cpu.ram_read(cpu.pc + 2)
        # set the value to the register
        cpu.reg[reg_num] = value
        # increment the program counter by 3 to get to the next instruction
        cpu.pc += inst["num_ops"] + 1

        return cpu

    def _handle_PRN(self, cpu, inst):
        # read the register number from RAM at address: pc + 1
        reg_num = cpu.ram_read(cpu.pc + 1)

        # get the value stored in the register
        value = cpu.reg[reg_num]
        # print it
        print(value)
        # increment the program counter by 2 to get to the next instruction
        cpu.pc += inst["num_ops"] + 1

        return cpu

    # ALU
    def _handle_MUL(self, cpu, inst):
        # reads/stores the register numbers from the next two instructions
        reg_num_a = cpu.ram_read(cpu.pc + 1)
        reg_num_b = cpu.ram_read(cpu.pc + 2)

        # reads/stores the values from each of the registers
        operand_1 = cpu.reg[reg_num_a]
        operand_2 = cpu.reg[reg_num_b]
        # multiplies the values together
        result = operand_1 * operand_2
        # stores the value back in the register
        cpu.reg[reg_num_a] = result

        # increments the counter
        cpu.pc += inst["num_ops"] + 1

        return cpu

    def _handle_PUSH(self, cpu, inst):
        cpu.reg[7] = cpu.reg[7] - 1
        reg_num = cpu.ram_read(cpu.pc + 1)
        value = cpu.reg[reg_num]
        stack_address = cpu.reg[7]

        cpu.ram_write(stack_address, value)

        cpu.pc += inst["num_ops"] + 1

        return cpu

    def _handle_POP(self, cpu, inst):
        reg_num = cpu.ram_read(cpu.pc + 1)
        stack_address = cpu.reg[7]
        value = cpu.ram_read(stack_address)
        cpu.reg[reg_num] = value
        cpu.reg[7] = stack_address + 1

        cpu.pc += inst["num_ops"] + 1

        return cpu

    def _handle_HLT(self):
        return false

    def run(self, inst, cpu):
        cpu = self.branchtable[inst["op_code"]](cpu, inst)
        return cpu

    def get_op_codes(self):
        return self.branchtable.keys()
