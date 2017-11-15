from Bloque import Bloque
class InstrCache:
    def __init__(self, size):
        self.cache = [Bloque() for r in range(size)]
    def getInstruction(self, address):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        self.cache[cacheBlock][word] = data
    def write(self, address, inst):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        self.cache[cacheBlock][word] = inst
    
