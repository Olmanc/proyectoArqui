from threading import Thread, Barrier, BrokenBarrierError
import random
import OS as OpSystem
import Instruccion
import queue 
barrier = Barrier(2, timeout=5)
class Nucleo(Thread):
    def __init__(self, name, idCore, instrCache, dataCache, instMem, sharedMemory, trapFlag, directory, dirLock, cacheLock, busLock, start, parentProcessor, sendQ):
        self.pc = 0
        self.registers = [0]*32 #mejor use 0's para no tener problemas con operadores
        #self.currentStage = None
        self.instructionSet = {8: self.daddi, 32: self.dadd, 34: self.dsub,
                               12: self.dmul, 14: self.ddiv, 4: self.beqz,
                               5: self.bneqz, 3: self.jal, 2: self.jr, 35: self.lw, 43: self.sw, 63: self.end}
        Thread.__init__(self, daemon=True)
        self.name = name
        self.id = idCore
        self.instrCache = instrCache
        self.dataCache = dataCache
        self.instMemory = instMem
        self.sharedMemory = sharedMemory
        self.trapFlag = trapFlag
        self.memStart = start
        self.directory = directory
        self.dirLock = dirLock
        self.cacheLock = cacheLock
        self.busLock = busLock
        self.parentProcessor = parentProcessor
        self.currentContext = None
        self.sendQueue = sendQ


    def run(self):
      print("Starting " + self.name + '\n')
      self.isRunning = True
      while(self.isRunning):
        self.execute()

    def incPC(self):
        self.pc += 4

    def getPC(self):
        return self.pc

    #def getStage(self):
        #return self.currentStage
    def setPC(self, pc):
        self.pc  = pc

    def __fetch(self):
        #print(self.instrCache.getInstruction(self.pc))
        return self.instrCache.getInstruction(self.pc)

    def __decode(self):
        pass

    def execute(self):
        while(self.loadContext()):
            opCode = 0
            cicles = 0
            while(OpSystem.opSystem.getQuantum() > cicles and not self.currentContext['status']):
                inst = self.__fetch()
                #if type(inst) != type(Instruccion.Intruccion('63','0','0','0')):
                # break
                #print('INST: {0}, coreId: {1}, pc:{2}'.format(inst, self.id, self.pc))
                opCode = inst.getOpCode()
                sr = inst.getRegSource()
                tr = inst.getRegTOrImm()
                dr = inst.getRegDest()
                #print(repr(self.instructionSet[opCode]) + '\n')
                self.incPC()
                cicles += 1
                self.instructionSet[opCode](sr, tr, dr)
                self.__mem()
                if(self.trapFlag):
                    print('INST: {0}, coreId: {1}, pc:{2}'.format(repr(self.instructionSet[opCode]), self.id, self.pc))
                    print('{}\n'.format(self.registers))
                    input()
                
            if not (self.currentContext['status']):
                self.parentProcessor.writeContext(self.getPC(), self.currentContext['id'], self.getRegisters(), False)

    def __mem(self):
        self.instrCache.write(self.pc, self.instMemory.read(self.pc))

    def writeback(self):
        pass

    def getRegisters(self):
        return self.registers

    def daddi(self, sr, dr, imm):
        self.registers[dr] = self.registers[sr] + imm

    def dadd(self, sr, tr, dr):
        self.registers[dr] = self.registers[sr] + self.registers[tr]

    def dsub(self, sr, tr, dr):
        self.registers[dr] = self.registers[sr] - self.registers[tr]

    def dmul(self, sr, tr, dr):
        self.registers[dr] = int(self.registers[sr] * self.registers[tr])

    def ddiv(self, sr, tr, dr):
        self.registers[dr] = int(self.registers[sr] / self.registers[tr])

    def beqz(self, sr, tr, imm):
        if(self.registers[sr] == 0):
            self.pc += imm * 4

    def bneqz(self, sr, tr, imm):
        if not (self.registers[sr] == 0):
            self.pc += imm * 4

    def jal(self, sr, tr, imm):
        self.registers[31] = self.pc
        self.pc += imm

    def jr(self, sr, tr, imm):
        self.pc = self.registers[sr]

    def lw(self, sr, dr, imm):
        '''
        LW Rx, n(Ry)  =  Rx <-- M(n+Ry)
        lw 35 0 12 0        R0 = 0+R12
        lw 35 0 14 28       R0 = 28+R14
        lw 35 0 15 364      R0 = 364+R15
        '''
        #calcular mem y buscar
        '''addr = self.registers[sr]+imm
        block = addr//16
        word = addr%4
        readBlock = self.sharedMemory.read(self.registers[sr]+imm)
        data = readBlock.block[word]
        self.registers[dr] = data
        print("dato:", self.registers[dr])'''

        #(sr, dr, imm)

        addr = self.registers[sr]+imm-self.memStart
        block = addr//16
        word = addr % 4
        finish = False
        while not finish:
            if self.cacheLock.acquire(False):
                hit = self.dataCache.findBlock(addr)
                if hit:
                    rBlock = self.sharedMemory.memory.read(addr)
                    self.registers[dr] = rBlock[word]
                else:
                    #miss, bloque victima
                    victim = self.dataCache.cache[word]
                    if victim['state'] == 'M':
                        if self.busLock.acquire(False):
                            #write to memory
                            self.sharedMemory.writeBlock(victim['block'],victim['tag'])
                            self.busLock.release()
                        else:
                            self.cacheLock.release()
                            continue #cambio de ciclo
                    if self.dirLock.acquire(False):
                        if self.directory.directory[word]['state'] == 'U' or 'C':
                            if self.busLock.acquire(False):
                                #self.dataCache.cache[word]['block'] = self.sharedMemory.read(addr)?
                                self.busLock.release()
                                self.directory.directory[word]['block'] = 'C'
                                self.dirLock.release()
                                self.registers[dr] = self.dataCache.cache[word]['block'].block[word]
                                self.cacheLock.release()
                                finish = True
                            else:
                                self.dirLock.release()
                                self.cacheLock.release()
                                continue #cambio de ciclo
                        elif self.directory.directory[word]['state'] == 'M':
                            if self.busLock.acquire():
                                #write to memory
                                #self.dataCache.cache[word]['block'] = self.sharedMemory.read(addr)?
                                self.busLock.release()
                                self.directory.directory[word]['block'] = 'C'
                                self.dirLock.release()
                                self.registers[dr] = self.dataCache.cache[word]['block'].block[word]
                                self.cacheLock.release()
                                finish = True
                            else:
                                self.dirLock.release()
                                self.cacheLock.release()
                                continue #cambio de ciclo
                    else:
                        self.cacheLock.release()
                        continue #cambio de ciclo
            else:
                continue #cambio de ciclo
        #'''
        pass
    def sw(self, sr, dr, imm):
        #calcular mem y buscar
        pass

    def loadContext(self):

        try:
            self.currentContext = self.parentProcessor.context.get(True, 5)
            self.instrCache.write(self.currentContext['pc'], self.parentProcessor.instMemory.read(self.currentContext['pc']))
            self.pc = self.currentContext['pc']
            self.registers = self.currentContext['registers']
            return True
        except queue.Empty:
            return False
    def end(self, sr, dr, imm):
        print ("Finished thread " + self.currentContext['id'] + '\n')
        self.currentContext['registers'] = self.getRegisters()
        self.currentContext['pc'] = self.getPC()
        self.currentContext['status'] = True
        self.parentProcessor.finished.append(self.currentContext)
        self.isRunning = False

    def stop(self):
        #barrier.wait()
        for context in self.parentProcessor.finished:
            print(context)
        print('fuga')
        
        self.isRunning = False
'''try:
                    barrier.wait()
                except BrokenBarrierError:
                    pass'''