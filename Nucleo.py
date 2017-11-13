class Nucleo:
    #PC: int
    #Registers: Array(int)
    #currentStage: int
    def __init__(self):
        self.pc = 0
        self.registers = [0]*32 #mejor use 0's para no tener problemas con operadores
        self.currentStage = None

    def incPC(self):
        self.pc += 1

    def getPC(self):
        return self.pc

    def getStage(self):
        return self.currentStage

    def fetch(self):
        pass

    def decode(self):
        pass

    def execute(self):
        pass

    def mem(self):
        pass

    def writeback(self):
        pass

    def getRegisters(self):
        return self.registers