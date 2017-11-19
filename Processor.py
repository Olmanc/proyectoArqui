from Nucleo import Nucleo
from Memory import Memory
from DataCache import DataCache
from InstrCache import InstrCache
from Directorio import Directorio
from queue import Queue
from threading import Lock
class Processor():
    def __init__(self, coreAmount, instMemSize, sharedMemSize, cacheSize, trapFlag):
        self.sharedMemory = Memory(sharedMemSize)
        self.instMemory = Memory(instMemSize)
        self.directory = Directorio(cacheSize)
        self.dirLock = Lock()
        self.cacheLock = Lock()
        self.busLock = Lock()
        self.cores = [Nucleo(i, str(i), InstrCache(cacheSize), DataCache(cacheSize), self.instMemory, self.sharedMemory, trapFlag, self.directory, self.dirLock, self.cacheLock, self.busLock, 512-(256*coreAmount)) for i in range(coreAmount)]
        self.context = Queue()
    def run(self):
        #aqui se corren las weas lel
        pass
    def writeContext(self, pc, idThread, registers = None, status = False):
        if not (registers):
            registers = [0] * 32
        self.context.put({'id': idThread, 'pc': pc, 'registers': registers, "status": status})

    def readContext(self):
        return self.context.get()
