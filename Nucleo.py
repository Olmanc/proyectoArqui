from threading import Thread, Barrier, BrokenBarrierError
import random
import OS as OpSystem
import Instruccion
import queue 
import time
class Nucleo(Thread):
    def __init__(self, name, idCore, instrCache, dataCache, instMem, sharedMemory, trapFlag, directory, dirLock, cacheLock, busLock, start, parentProcessor, sendQ):
        self.pc = 0
        self.registers = [0]*32 #mejor use 0's para no tener problemas con operadores
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
        self.cicles = 0
        self.sendQueue = sendQ
    
    def setNeighborProcessors(self, processors):
        self.neighborProcessors = processors

    def run(self):
        print("Starting " + self.name + '\n')
        self.isRunning = True
        while(self.isRunning):
            self.execute()

    def incPC(self):
        self.pc += 4

    def getPC(self):
        return self.pc

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
            self.cicles = 0
            self.startTime = time.time()
            while(OpSystem.opSystem.getQuantum() > self.cicles and not self.currentContext['status']):
                inst = self.__fetch()                
                #print('INST: {0}, coreId: {1}, pc:{2}'.format(inst, self.id, self.pc))
                opCode = inst.getOpCode()
                #print(opCode)                
                sr = inst.getRegSource()
                tr = inst.getRegTOrImm()
                dr = inst.getRegDest()
                #print(repr(self.instructionSet[opCode]) + '\n')
                self.incPC()
                self.cicles += 1
                if(self.trapFlag):
                    print('INST: {0}, coreId: {1}, pc:{2}'.format(repr(self.instructionSet[opCode]), self.id, self.pc))
                    print('{}\n'.format(self.registers))
                    input()
                self.instructionSet[opCode](sr, tr, dr)
                self.__mem()
                
            finishTime = time.time() - self.startTime
                
            if not (self.currentContext['status']):
                self.parentProcessor.writeContext(self.getPC(), self.currentContext['id'], self.getRegisters(), False, self.cicles + self.currentContext['cicles'], finishTime + self.currentContext['elapsedTime'])

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
                
        addr = self.registers[sr]+imm-self.memStart
        #print('ADDR: ',self.registers[sr]+imm, ' en ', self.name, self.id)
        #print(addr)
        block = (addr//16)%16
        #word = (addr-(block*16))//4
        word = addr % 4
        #print('Load addr {0} block {1} word {2}'.format(addr, block, word))
        finish = False
        while not finish:
            if self.cacheLock.acquire(False):
                hit = self.dataCache.findBlock(addr)
                if hit: #esta en cache C o M
                    rBlock = self.sharedMemory.read(addr)
                    self.registers[dr] = rBlock.block[word]
                    finish = True
                    self.cacheLock.release()
                else:
                    #miss, bloque victima                    
                    if self.dirLock.acquire(False):
                        self.cicles += 1
                        victim = self.dataCache.cache[word]
                        if victim['state'] == 'M':
                            if self.busLock.acquire(False):
                                #write to memory
                                self.sharedMemory.writeBlock(victim['block'],victim['tag'])
                                self.directory.directory[victim['tag']]['state'] = 'U'
                                self.directory.directory[victim['tag']]['flags'][self.id] = True
                                self.dataCache.cache[word]['state'] = 'I'                              
                                self.busLock.release()
                            else:
                                self.cacheLock.release()
                                continue #cambio de ciclo
                        if self.directory.directory[word]['state'] == 'U' or 'C':
                            if self.busLock.acquire(False):                                
                                self.dataCache.cache[word]['block'] = self.sharedMemory.read(addr)                                
                                self.busLock.release()
                                self.directory.directory[block]['state'] = 'C'
                                self.directory.directory[block]['flags'][int(self.name)] = True
                                self.dataCache.cache[word]['state'] = 'C'
                                self.dataCache.cache[word]['tag'] = int(block)
                                self.dirLock.release()
                                self.registers[dr] = self.dataCache.cache[word]['block'].block[word]
                                self.cacheLock.release()
                                self.cicles += 16
                                finish = True
                            else:
                                self.dirLock.release()
                                self.cacheLock.release()
                                continue #cambio de ciclo
                        elif self.directory.directory[block]['state'] == 'M':
                            if self.busLock.acquire():
                                #write to memory
                                self.dataCache.cache[word]['block'] = self.sharedMemory.read(addr)
                                self.busLock.release()
                                self.directory.directory[block]['state'] = 'C'
                                self.directory.directory[block]['flags'][int(self.name)] = True
                                self.dataCache.cache[word]['state'] = 'C'
                                self.dirLock.release()
                                self.registers[dr] = self.dataCache.cache[word]['block'].block[word]
                                self.cacheLock.release()
                                finish = True
                            else:
                                self.dirLock.release()
                                self.cacheLock.release()
                                self.cicles += 1
                                continue #cambio de ciclo
                    else:
                        self.cacheLock.release()
                        self.cicles += 1
                        continue #cambio de ciclo
            else:
                self.cicles += 1
                continue #cambio de ciclo
        #'''
        
    def sw(self, sr, dr, imm):
        #calcular mem y buscar
        addr = self.registers[sr]+imm-self.memStart
        block = int(address / 16)
        word = int(address % 16 / 4)
        cacheBlock = memBlock % 4

        finish = False
        '''
        SW Rx, n(Ry)  =  Rx <-- M(n+Ry)
        SW 43 16 2 0        M[R16] = 2
        SW 43 16 2 4        M[R16] = 2
        SW 43 16 2 8        M[R16] = 2

        self.dirLock = dirLock
        self.cacheLock = cacheLock
        self.busLock = busLock
        '''
        while not finish:
            if self.cacheLock.acquire(False):
                hit = self.dataCache.findBlock(addr)
                # esto deberia ser el propio o el remoto si el directorio casa es remoto
                if self.dirLock.acquire(False):
                    if(hit):
                        victim = self.dataCache.cache[word]
                        if victim['state'] == 'I':
                            print('fetch de algun lugar')
                        else:
                            print('invalidando en otras caches')
                            #usar metorodo de directory.updateStatus(block, core, flag)
                            finish = True
                            self.dirLock.release()
                            self.cacheLock.release()
                            self.dataCache.write(addr, registers[dr])
                    else:
                        print('revisando en caches remotas')
                        isCached = self.parentProcessor.directory.getBlockStatus(block)
                        if (isCached == 'C'):
                            coreOwner = self.parentProcessor.directory.getCoreOwner(block)
                            if(coreOwner < 2):
                                self.dataCache.setBlock(addr, self.parentProcessor.cores[coreOwner].dataCache.read(addr))
                                self.parentProcessor.cores[coreOwner].dataCache[cacheBlock]['state'] = 'I'
                                self.parentProcessor.directory.updateStatus(0, coreOwner)
                                self.neighborProcessors.directory.updateStatus(0, coreOwner)
                            else:
                                self.dataCache.setBlock(addr, self.neighborProcessors.cores[coreOwner].dataCache.read(addr))
                                self.neighborProcessors.cores[coreOwner].dataCache[cacheBlock]['state'] = 'I'
                                self.parentProcessor.directory.updateStatus(0, coreOwner)
                                self.neighborProcessors.directory.updateStatus(0, coreOwner)
                            self.dirLock.release()
                            self.cacheLock.release()
                            self.dataCache.write(addr, registers[dr])
                        else:
                            print('traer de memoria')
        #        hit = self.dataCache.findBlock(addr)
        #        if hit: #esta en cache
        #            finish = True                    
        #             si es M
        #            print(self.dataCache.cache)
        #            continue
        #             if self.dataCache.cache[word]
        #             else si es C
        #                 bloquear directorio
        #                 invalidar en otras caches (bloquear cache remota? o usar cola?)
        #                 escribir en cache local
        #                 marcar como M en cache Y directorio
        #                 actualiza cache y directorio
        #                 desbloquear candados
        #         else: no esta en cache (miss)
        #             bloquear directorio
        #             bloque victima (copira a memoria)
        #             invalidar y actualizar directorio
        #             si es U
        #                 bloquear bus
        #                 cargar de memoria
        #                 cargar en cache
        #                 escribe en cache
        #                 marcar como M
        #                 desbloquear candados
        #             else si es M****
        #                 donde esta el bloque?
        #                 copiar a memoria
        #                 copiar a cache
        #                 escribe en cache
        #                 (se mantiene M)
        #                 desbloquear canados
        #             else si es C
        #                 invalidar en otras caches
        #                 traer de memoria
        #                 carga en cache
        #                 escribe en cache
        #                 marca como M
        #                 desbloquear canados
        #    else:
        #        finish = True 

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
        finishTime = time.time() - self.startTime
        self.currentContext['registers'] = self.getRegisters()
        self.currentContext['pc'] = self.getPC()
        self.currentContext['status'] = True
        self.currentContext['cicles'] += self.cicles
        self.currentContext['elapsedTime'] += finishTime
        self.parentProcessor.finished.append(self.currentContext)
        self.isRunning = False

    def stop(self):
        #barrier.wait()
        for context in self.parentProcessor.finished:
            print(context)
        print('fuga')
        
'''try:
                    barrier.wait()
                except BrokenBarrierError:
                    pass'''