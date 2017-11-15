
class DataCache:
    def __init__(self, size):
        self.cache = [{'block': None, 'state': 'I', 'tag': None} for i in range(size)]
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
        return false
