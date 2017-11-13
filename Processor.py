import Nucleo, Memory, DataCache, InstCache, Directorio
from Queue import Queue
class Processor():
    def self.__init__(self, coreAmount, instMemSize, sharedMemSize, cacheSize):
        self.cores = [Nucleo() for i in range(coreAmount)]
        self.dataCaches = [DataCache(cacheSize) for i in range(coreAmount)]
        self.instCaches = [InstCache(cacheSize) for i in range(coreAmount)]
        self.sharedMemory = Memory(memSize)
        self.instMemory = Memory(memSize)
        self.directory = Directorio()
        self.context = Queue()
    def self.run(self):
        #aqui se corren las weas lel
        pass
    def self.writeContext(self):
        #escribir contextos
        pass
    def self.readContext(self):
        #leer contextos
        pass
    

