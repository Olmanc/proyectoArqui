
class Directorio:
    #Directorio con los estado de los bloques en memoria
    def __init__(self, size, cores):
        self.coreAmount = cores
        self.directory = [{'block': i, 'state': 'U', 'flags':[False]*3} for i in range(size)]

    def isHome(self):
        pass

    def updateStatus(self, flag, core, block):
        if(flag):
            self.directory[block]['state'] = 'C'
            self.directory[block]['flags'][core] = flag
        else:
            self.directory[block]['flags'][core] = flag
            isCached = False
            for i in self.directory[block]['flags']:
                if i:
                    isCached = True
                    break
            if not (isCached):
                self.directory[block]['state'] = 'U'
            
    def getCoreOwner(self, block):
        for i in range(len(self.directory[block]['flags'])):
            if self.directory[block]['flags'][i]:
                return i
        return -1
    def getBlockStatus(self, block):
        return self.directory[block]['state']
