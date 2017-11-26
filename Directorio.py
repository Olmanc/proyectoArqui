import Bloque
class Directorio:
    #Directory: Array(Dictionary)
    def __init__(self, size, cores):
        self.coreAmount = cores
        self.directory = [{'block': i, 'state': 'U', 'flags':[False]*cores }for i in range(size)]
        pass

    def isBlocked(self):
        pass

    def isHome(self):
        pass

    def updateStatus(self):
        pass

    def block(self):
        pass

    def findBlock(self):
        pass

    def getBlockStatus(self):
        pass
