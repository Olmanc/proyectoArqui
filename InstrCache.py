from Bloque import Bloque
class InstrCache:
    def __init__(self, size):
        self.cache = [Bloque(0) for r in range(size)]
    def getInstruction(self, address):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        return self.cache[cacheBlock].getWord(word)
    def write(self, address, block):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        self.cache[cacheBlock] = block
    
