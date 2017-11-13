import Bloque
class Memory():
    self.__init__(self, size):
        self.memory = [Bloque() for i in range(size)]
    self.write(self, block, word, data):
        self.memory[block][word] = data
    self.read(self, addressInBytes):
        return self._findBlock(addressInBytes)
    self._findBlock(self, addressInBytes):
        block = int(addressInBytes / 16)
        return self.memory[block]