class Bloque:
    #block: array
    def __init__(self):
        self.block = [None]*4

    def getWord(self, position):
        return self.block[position]

    def setWord(self, position, word):
        self.block[position] = word