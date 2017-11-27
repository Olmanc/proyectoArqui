from Bloque import Bloque
#clase Memory
class Memory():
    #contiene un array de Bloque para representar la memoria
    def __init__(self, size):
        self.memory = [Bloque(0) for i in range(size)]
    #escribe un dato a una palabra en un bloque
    def write(self, block, word, data):
        self.memory[block].setWord(word, data)
    #escribe un bloque en la direccion especificada
    def writeBlock(self, block, addressInBytes):
        blk = int(addressInBytes / 16)
        self.memory[blk] = block
    #devuelve el bloque que se encuentra en la direccion provista
    def read(self, addressInBytes):
        return self.__findBlock(addressInBytes)
    #devuelve si u bloque se encuentra o no
    def __findBlock(self, addressInBytes):
        block = int(addressInBytes / 16)%16
        return self.memory[block]
