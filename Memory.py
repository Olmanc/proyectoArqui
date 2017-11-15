from Bloque import Bloque
class Memory():
    def __init__(self, size):
        self.memory = [Bloque() for i in range(size)]
    def write(self, block, word, data):
        self.memory[block].block[word] = data
    def read(self, addressInBytes):
        return self._findBlock(addressInBytes)
    def _findBlock(self, addressInBytes):
        block = int(addressInBytes / 16)
        return self.memory[block]
    #metodo temporal para imprimir en  prueba
    def read2(self, block, word):
        return self.memory[block].block[word]