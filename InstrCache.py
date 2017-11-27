from Bloque import Bloque
#Cache de instrucciones
class InstrCache:
    def __init__(self, size):
        #Bloque de 4 instrucciones
        self.cache = [Bloque(0) for r in range(size)]
    #devuelve la instruccion en la dreccion dada
    def getInstruction(self, address):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        return self.cache[cacheBlock].getWord(word)
    #escribe una instruccion a la cache
    def write(self, address, block):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        self.cache[cacheBlock] = block
    
