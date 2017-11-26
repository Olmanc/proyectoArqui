from Nucleo import Nucleo
from Memory import Memory
from DataCache import DataCache
from InstrCache import InstrCache
from Directorio import Directorio
from queue import Queue
from threading import Lock, Thread
class Processor(Thread):
    def __init__(self, coreAmount, instMemSize, sharedMemSize, cacheSize, trapFlag, procId, sendQ, receiveQ):
        Thread.__init__(self)
        self.sharedMemory = Memory(sharedMemSize)
        self.instMemory = Memory(instMemSize)
        self.directory = Directorio(cacheSize)
        self.dirLock = Lock()
        self.cacheLock = Lock()
        self.busLock = Lock()
        self.context = Queue()
        self.finished = []
        self.id = procId
        self.sendQueue = sendQ
        self.receiveQueue = receiveQ
        self.end = False
        self.cores = [Nucleo(i, 'Thread {}'.format(i), InstrCache(cacheSize), DataCache(cacheSize), self.instMemory, self.sharedMemory, trapFlag, self.directory, self.dirLock, self.cacheLock, self.busLock, 512-(256*coreAmount), self, self.sendQueue) for i in range(coreAmount)]
    def run(self):
        #aqui se corren las weas lel
        #mientras los hilos no acaben, trate de leer de la cola
        #cuando termina el ultio hilo, cambiar a True
        while not self.end:
            if self.receiveQueue.empty():
                msg = self.receiveQueue.get()
        
    def writeContext(self, pc, idThread, registers = None, status = False):
        if not (registers):
            registers = [0] * 32
        self.context.put({'id': idThread, 'pc': pc, 'registers': registers, "status": status})

    def readContext(self):
        return self.context.get()

    def stop(self):
        for core in self.cores:
            core.stop()
