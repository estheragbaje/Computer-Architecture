"""CPU functionality."""

import sys

# opcodes
HLT = 0b00000001  
PRN = 0b01000111
LDI = 0b10000010
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101  
POP = 0b01000110
RET = 0b00010001 
CALL = 0b01010000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
         # set memory to a list of 256 zeros
        self.ram = [0] * 256
        # set registers to a list of 8 zeros
        self.reg = [0] * 8
        # set program counter to zero
        self.pc = 0
        self.halted = False
        self.sp = 7
        self.flag = 0
        self.reg[self.sp] = 0xF4
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        

    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    # split line before and after comment symbol
                    comment_split = line.split("#")

                    # extract our number
                    num = comment_split[0].strip() # trim whitespace

                    if num == '':
                        continue # ignore blank lines

                    # convert our binary string to a number
                    val = int(num, 2)

                    # store val at address in memory
                    self.ram_write(val, address)

                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
      """Ram read method"""
      return self.ram[address]

    def ram_write(self, value, address):
      """Ram write method"""
      self.ram[address] = value

    def run(self):
        """Run the CPU."""
        # inc_size = 0
        while not self.halted:
            cmd = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if cmd in self.branchtable:
                self.branchtable[cmd](operand_a, operand_b)
            else:
                print(f"Invalid instruction")
                sys.exit(1)
            inc_size = ((cmd >> 6) & 0b11) + 1
            if not self.halted:
                self.pc += inc_size

    
    def handle_HLT(self, opr1, opr2):
        self.halted = True
        sys.exit(-1)

    def handle_PRN(self, opr1, opr2):
        reg_index = opr1
        num = self.reg[reg_index]
        print(num)
        self.pc += 2

    def handle_LDI(self, opr1, opr2):
        reg_index = opr1
        num = self.reg[reg_index]
        print(num)
        self.pc += 2

    def handle_ADD(self, opr1, opr2):
        self.alu("ADD", opr1, opr2)
        self.pc += 3

    def handle_MUL(self, opr1, opr2):
        self.alu("MUL", opr1, opr2)
        self.pc += 3
    
    def handle_PUSH(self, opr1, opr2):
        val = self.reg[opr1]
        self.reg[self.sp] -= 1
        self.ram_write(val, self.reg[self.sp])
        self.pc += 2 

    def handle_POP(self, opr1, opr2):
        val = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        self.reg[opr1] = val
        self.pc += 2

    def handle_RET(self, opr1, opr2):
        return_address = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        self.pc = return_address

    def handle_CALL(self, opr1, opr2):
        self.reg[self.SP] -= 1  
        self.ram[self.reg[self.SP]] = self.pc + 2
        self.pc = self.reg[opr1]
        self.halted = True
        self.pc += 2

    def handle_CMP(self, opr1, opr2):
        reg_a = self.reg[opr1]
        reg_b = self.reg[opr2]
        if reg_a < reg_b:
            self.flag = 1
        elif reg_a > reg_b:
            self.flag = 1
        else:
            self.flag = 1

        self.halted = False

        if not self.halted:
            self.pc += 3

    def handle_JMP(self, opr1, opr2):
        self.pc = self.reg[opr1]

        self.halted = True

        if not self.halted:
            self.pc += 2
    
    def handle_JEQ(self, opr1, opr2):
        if self.flag == 1:
            self.pc = self.reg[opr1]
            self.halted = True

        if not self.halted:
            self.pc += 2

    def handle_JNE(self, opr1, opr2):
        if self.flag == 0:
            self.pc = self.reg[opr1]
            self.halted = True

        if not self.halted:
            self.pc += 2