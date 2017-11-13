import Nucleo, Memory, DataCache, InstCache, Directorio
from Queue import Queue
class Processor():
    self.__init__(self, coreAmount, memSize, cacheSize):
        self.cores = [Nucleo() for i in range(coreAmount)]
        self.dataCaches = [DataCache(cacheSize) for i in range(coreAmount)]
        self.instCaches = [InstCache(cacheSize) for i in range(coreAmount)]
        self.sharedMemory = Memory(memSize)
        self.instMemory = Memory(memSize)
        self.directory = Directorio()
        self.context = Queue()
    self.run(self):
        #aqui se corren las weas lel
        pass
    self.writeContext(self):
        #escribir contextos
        pass
    self.readContext(self):
        #leer contextos
        pass
    

