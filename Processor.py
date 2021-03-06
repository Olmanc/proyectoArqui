from Nucleo import Nucleo
from Memory import Memory
from DataCache import DataCache
from InstrCache import InstrCache
from Directorio import Directorio
from queue import Queue
from threading import Lock, Thread
class Processor(Thread):
    def __init__(self, coreAmount, instMemSize, sharedMemSize, cacheSize, trapFlag, procId):
        Thread.__init__(self, daemon=True)
        self.sharedMemory = Memory(sharedMemSize)
        self.instMemory = Memory(instMemSize)
        self.directory = Directorio(sharedMemSize, coreAmount)
        self.dirLock = Lock()
        self.cacheLock = Lock()
        self.busLock = Lock()
        self.context = Queue()
        self.finished = []
        self.id = procId
        self.receiveQueue = Queue()
        self.cores = [Nucleo(i, 'Thread {}'.format(i), InstrCache(cacheSize), DataCache(cacheSize), self.instMemory, self.sharedMemory, trapFlag, self.directory, self.dirLock, self.cacheLock, self.busLock, 512-(256*coreAmount), self, self.receiveQueue) for i in range(coreAmount)]
    def run(self):
        #aqui se corren las weas lel
        pass
        
    def writeContext(self, pc, idThread, registers = None, status = False, cicles = 0, elapsedTime = 0):
        if not (registers):
            registers = [0] * 32
        self.context.put({'id': idThread, 'pc': pc, 'registers': registers, "status": status, 'cicles': cicles, 'elapsedTime': elapsedTime})

    def readContext(self):
        return self.context.get()

    def stop(self):
        for core in self.cores:
            core.stop()
