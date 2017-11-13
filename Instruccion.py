class Intruccion:
    #OpCode: int
    #RegDest: int
    #RegSource: int
    #RegToImm: int
    def __init__(self, code, regSour1, regSour2, regDest):
        self.OpCode = code
        self.RegSour1 = regSour1
        self.RegSour2 = regSour2
        self.RegDest = regDest

    def getOpCode(self):
        return self.OpCode

    def getRegDest(self):
        return self.RegDest

    def getRegSource(self):
        return self.RegSource

    def getRegTOrImm(self):
        return self.RegToImm