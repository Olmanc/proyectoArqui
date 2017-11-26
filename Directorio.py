import Bloque
class Directorio:
    #Directory: Array(Dictionary)
    def __init__(self, size):
        self.directory = [{'block': Bloque.Bloque(), 'state': 'U', 'flags':[False]*3}for i in range(size)]
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
