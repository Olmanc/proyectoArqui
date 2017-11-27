import Bloque
class DataCache:
    def __init__(self, size):
        self.cache = [{'block': Bloque.Bloque(0), 'state': 'I', 'tag': -1} for i in range(size)]
    def write(self, address, data):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        self.cache[cacheBlock]['block'][word] = data
        self.cache[cacheBlock]['state'] = 'M'
    def findBlock(self, addressInBytes):
        blockNum = int(addressInBytes // 16)
        for block in self.cache:
            if (block['tag'] == blockNum):
                return True
        return False

    def getBlock(self, address):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        return self.cache[cacheBlock]['block']

    def setBlock(self, address, block):
        memBlock = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4
        self.cache[cacheBlock]['block'] = block
