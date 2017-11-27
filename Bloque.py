class Bloque:
    #block: array
    def __init__(self, value):
        self.block = [value]*4

    def getWord(self, position):
        return self.block[position]

    def setWord(self, position, inst):
        self.block[position] = inst
    def copy(self, other):
        for i in range(4):
            self.block[i] = other.block[i]