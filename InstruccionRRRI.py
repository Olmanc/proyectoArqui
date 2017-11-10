class IntruccionRRRI:
    #OpCode: int
    #RegDest: int
    #RegSource: int
    #RegToImm: int
    def __init__(self, code, dest, source, imm):
        self.OpCode = code
        self.RegDest = dest
        self.RegSource = source
        self.RegToImm = imm

    def getOpCode(self):
        return self.OpCode

    def getRegDest(self):
        return self.RegDest

    def getRegSource(self):
        return self.RegSource

    def getRegTOrImm(self):
        return self.RegToImm