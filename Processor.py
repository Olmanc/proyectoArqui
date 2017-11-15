from Nucleo import Nucleo
from Memory import Memory
from DataCache import DataCache
from InstrCache import InstrCache
from Directorio import Directorio
from queue import Queue
class Processor():
    def __init__(self, coreAmount, instMemSize, sharedMemSize, cacheSize):
        self.cores = [Nucleo(i, ''+str(i)) for i in range(coreAmount)]
        self.dataCaches = [DataCache(cacheSize) for i in range(coreAmount)]
        self.instCaches = [InstrCache(cacheSize) for i in range(coreAmount)]
        self.sharedMemory = Memory(sharedMemSize)
        self.instMemory = Memory(instMemSize)
        self.directory = Directorio()
        self.context = Queue()
    def run(self):
        #aqui se corren las weas lel
        pass
    def writeContext(self):
        #escribir contextos
        pass
    def readContext(self):
        #leer contextos
        pass
    

