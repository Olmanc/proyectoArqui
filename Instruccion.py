class Intruccion:
    #OpCode: int
    #RegDest: int
    #RegSource: int
    #RegToImm: int
    def __init__(self, code, regSour1, regTOrImm, regDest):
        self.OpCode = code
        self.RegSource = regSour1
        self.RegTOrImm = regTOrImm
        self.RegDest = regDest

    def getOpCode(self):
        return self.OpCode

    def getRegDest(self):
        return self.RegDest

    def getRegSource(self):
        return self.RegSource

    def getRegTOrImm(self):
        return self.RegTOrImm