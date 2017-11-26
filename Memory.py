from Bloque import Bloque
class Memory():
    def __init__(self, size):
        self.memory = [Bloque(1) for i in range(size)]
    def write(self, block, word, data):
        self.memory[block].setWord(word, data)
    def writeBlock(self, block, addressInBytes):
        blk = int(addressInBytes / 16)
        self.memory[blk] = block
    def read(self, addressInBytes):
        return self.__findBlock(addressInBytes)
    def __findBlock(self, addressInBytes):
        block = int(addressInBytes / 16)%16
        return self.memory[block]
    #metodo temporal para imprimir en  prueba
    def read2(self, block, word):
        return self.memory[block].block[word]
