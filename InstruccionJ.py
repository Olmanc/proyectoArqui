class IntruccionJ:
    #OpCode: int
    #DirMem: int
    def __init__(self, code, dir):
        self.OpCode = code
        self.DirMem = dir

    def getOpCode(self):
        return self.OpCode

    def getDirMem(self):
        return self.DirMem