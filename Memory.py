import Bloque
class Memory():
    def self.__init__(self, size):
        self.memory = [Bloque() for i in range(size)]
    def self.write(self, block, word, data):
        self.memory[block][word] = data
    def self.read(self, addressInBytes):
        return self._findBlock(addressInBytes)
    def self._findBlock(self, addressInBytes):
        block = int(addressInBytes / 16)
        return self.memory[block]
