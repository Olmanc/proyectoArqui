from threading import Thread, Barrier, BrokenBarrierError
import random
import OS as OpSystem
import Instruccion
import queue 
import time
import Bloque
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
    
    #inicializa los hilos de cada nucleo
    def run(self):
        print("Starting " + self.name + '\n')
        self.isRunning = True
        while(self.isRunning):
            self.execute()

    #incrementa el pc del nucleo
    def incPC(self):
        self.pc += 4
    
    #devuelve el pc actual del nucleo
    def getPC(self):
        return self.pc
    
    #asigna un valor al pc
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

    #suma el valor de un registro con un valor inmediato
    def daddi(self, sr, dr, imm):
        self.registers[dr] = self.registers[sr] + imm
    
    #sumar los valores de 2 registros
    def dadd(self, sr, tr, dr):
        self.registers[dr] = self.registers[sr] + self.registers[tr]
    
    #resta los valores de 2 registros
    def dsub(self, sr, tr, dr):
        self.registers[dr] = self.registers[sr] - self.registers[tr]

    #multiplica los valores de 2 registros
    def dmul(self, sr, tr, dr):
        self.registers[dr] = int(self.registers[sr] * self.registers[tr])

    #divideresta los valores de 2 registros
    def ddiv(self, sr, tr, dr):
        self.registers[dr] = int(self.registers[sr] / self.registers[tr])
    
    #compara si el valor de un registro es igual a 0
    def beqz(self, sr, tr, imm):
        if(self.registers[sr] == 0):
            self.pc += imm * 4
        
    #compara si el valor de un registro es igual a 0
    def bneqz(self, sr, tr, imm):
        if not (self.registers[sr] == 0):
            self.pc += imm * 4

    #
    def jal(self, sr, tr, imm):
        self.registers[31] = self.pc
        self.pc += imm

    def jr(self, sr, tr, imm):
        self.pc = self.registers[sr]
    
    #carga un dato d memoria a registro
    def lw(self, sr, dr, imm):
        #calcula bloque, palabra y espacio en cache
        addr = self.registers[sr]+imm
        block = (addr//16)
        cacheSpace = block%4
        word = (addr-(block*16))//4
        finish = False
        while not finish:
            #intenta bloquear cache
            if self.cacheLock.acquire(False):
                hit = self.dataCache.findBlock(addr)
                # es hit (esta en cache)
                if hit:
                    #carga dato al registro
                    rBlock = self.sharedMemory.read(addr)
                    self.registers[dr] = rBlock.getWord(word)
                    finish = True
                    #libera cache
                    self.cacheLock.release()
                else:
                    #miss, bloque victima
                    #intenta bloquear directorio           
                    if self.dirLock.acquire(False):
                        self.cicles += 1
                        #bloque victima
                        victim = self.dataCache.cache[cacheSpace]
                        #victima con estado M
                        if victim['state'] == 'M':
                            #intenta bloquear bus
                            if self.busLock.acquire(False):
                                #escribe bloque victima a memoria
                                self.sharedMemory.writeBlock(victim['block'],victim['tag']*16)
                                #actualiza directorio y cache
                                self.directory.directory[victim['tag']]['state'] = 'U'
                                self.directory.directory[victim['tag']]['flags'][int(self.name)] = True
                                self.dataCache.cache[cacheSpace]['state'] = 'I'
                                #libera el bus                    
                                self.busLock.release()
                            else:
                                #no pudo bloquear bus, libera recursos
                                self.dirLock.release()
                                self.cacheLock.release()
                                continue #cambio de ciclo
                        #bloque en directorio es U o C
                        if self.directory.directory[word]['state'] == 'U' or 'C':
                            #intenta bloquear bus
                            if self.busLock.acquire(False):
                                #carga bloque de mamoria a cache           
                                self.dataCache.cache[cacheSpace]['block'] = self.sharedMemory.read(addr) 
                                #libera el bus                               
                                self.busLock.release()
                                #actualiza directorio y cache
                                self.directory.directory[block]['state'] = 'C'
                                self.directory.directory[block]['flags'][int(self.name)] = True
                                self.dataCache.cache[cacheSpace]['state'] = 'C'
                                self.dataCache.cache[cacheSpace]['tag'] = int(block)
                                #libera directorio
                                self.dirLock.release()
                                #carga dato a registro
                                self.registers[dr] = self.dataCache.cache[cacheSpace]['block'].getWord(word)
                                #libera cache
                                self.cacheLock.release()
                                self.cicles += 16
                                finish = True
                            else:
                                #no pudo bloquear bus, libera recursos
                                self.dirLock.release()
                                self.cacheLock.release()
                                continue #cambio de ciclo
                        #bloque es M
                        elif self.directory.directory[block]['state'] == 'M':
                            #intenta bloquear bus
                            if self.busLock.acquire():
                                #escribe bloque a cache
                                self.dataCache.cache[cacheSpace]['block'] = self.sharedMemory.read(addr)
                                #libera bus
                                self.busLock.release()
                                #actualiza directorio y cache
                                self.directory.directory[block]['state'] = 'C'
                                self.directory.directory[block]['flags'][int(self.name)] = True
                                self.dataCache.cache[cacheSpace]['state'] = 'C'
                                self.dataCache.cache[cacheSpace]['tag'] = int(block)
                                #libera directorio
                                self.dirLock.release()
                                #carga dato a registro
                                self.registers[dr] = self.dataCache.cache[cacheSpace]['block'].getWord(word)
                                #libera cache
                                self.cacheLock.release()
                                finish = True
                            else:
                                #no pudo bloquear bus, libera recursos
                                self.dirLock.release()
                                self.cacheLock.release()
                                self.cicles += 1
                                continue #cambio de ciclo
                    else:
                        #no pudo bloquear directorio, libera cache
                        self.cacheLock.release()
                        self.cicles += 1
                        continue #cambio de ciclo
            else:
                #no pudo bloquear cache, cambia de ciclo
                self.cicles += 1
                continue #cambio de ciclo
        #'''
        
    def sw(self, sr, dr, imm):
        #calcula bloque, palabra y espacio de cache     
        addr = self.registers[sr]+imm
        block = (addr//16)
        cacheSpace = block%4
        word = (addr-(block*16))//4
        finish = False
        while not finish:
            #bloquear cache
            if self.cacheLock.acquire(False):
                hit = self.dataCache.findBlock(addr)
                if hit: #esta en cache              
                    # si es M
                    if self.dataCache.cache[cacheSpace]['state'] == 'M':                        
                        self.dataCache.cache[cacheSpace]['block'].setWord(word,self.registers[dr])
                        self.cacheLock.release()
                        finish = True
                        self.cicles += 1
                        continue
                    #si es C
                    elif self.dataCache.cache[cacheSpace]['state'] == 'C':
                        #bloquear directorio
                        if self.dirLock.acquire(False):
                            #invalidar en otras caches (bloquear cache remota? o usar cola?)                                           
                            '''self.neighborProcessors.invalidateCache(block)
                            self.parentProcessor.invalidateCache(block)'''
                            #escribir en cache local
                            self.dataCache.cache[cacheSpace]['block'] = Bloque.Bloque(0)
                            for i in range(4):
                                self.dataCache.cache[cacheSpace]['block'].block[i] = self.sharedMemory.memory[self.dataCache.cache[cacheSpace]['tag']].getWord(i)
                            #self.dataCache.cache[cacheSpace]['block'] = self.sharedMemory.memory[self.dataCache.cache[cacheSpace]['tag']]
                            self.dataCache.cache[cacheSpace]['block'].setWord(word, self.registers[dr])
                            #marcar como M en cache Y directorio
                            #actualiza cache y directorio
                            self.dataCache.cache[cacheSpace]['state'] = 'M'
                            self.directory.directory[block]['state'] = 'M'
                            #desbloquear candados
                            self.dirLock.release()
                            self.cacheLock.release()
                            finish = True
                            self.cicles += 16
                            continue
                        else:
                            #no pudo bloquear directorio, libera cache
                            self.cacheLock.release()
                            self.cicles += 1
                            continue
                else: #no esta en cache (miss)
                    #bloquear directorio
                    if self.dirLock.acquire(False):
                        #bloque victima (copiar a memoria)
                        victim = self.dataCache.cache[cacheSpace]
                        self.sharedMemory.memory[victim['tag']] = victim['block']                        
                        #invalidar y actualizar directorio
                        self.directory.directory[block]['state'] = 'U'
                        self.directory.directory[block]['flags'][int(self.name)] = False
                        #si es U
                        if self.directory.directory[block]['state'] == 'U':
                            #bloquear bus
                            if self.busLock.acquire(False):
                                #cargar en cache de memoria
                                self.dataCache.cache[cacheSpace]['block'] = Bloque.Bloque(0)
                                for i in range(4):
                                    self.dataCache.cache[cacheSpace]['block'].block[i] = self.sharedMemory.memory[block].getWord(i)
                                #self.dataCache.cache[cacheSpace]['block'] = self.sharedMemory.memory[block]
                                #escribe en cache
                                self.dataCache.cache[cacheSpace]['block'].setWord(word, self.registers[dr])
                                #marcar como M
                                self.dataCache.cache[cacheSpace]['state'] = 'M'
                                self.dataCache.cache[cacheSpace]['tag'] = int(block)
                                self.directory.directory[block]['state'] = 'M'
                                self.directory.directory[block]['flags'][int(self.name)] = True
                                #desbloquear candados
                                self.busLock.release()
                                self.dirLock.release()
                                self.cacheLock.release()
                                finish = True
                                self.cicles += 16
                                continue
                            else:
                                #no pudo bloquear bus, libera recursos
                                self.dirLock.release()
                                self.cacheLock.release()
                                self.cicles += 1
                                continue
                        #else si es M
                        elif self.directory.directory[block]['state'] == 'M':
                            if busLock.acquire(False):                                
                                #donde esta el bloque?
                                flag = self.directory.directory[block]['flags']
                                #esta en cache local
                                if flag[int(self.name)] == True:
                                    #copiar a cache de memoria
                                    self.dataCache.cache[cacheSpace]['block'] = Bloque.Bloque(0)
                                    for i in range(4):
                                        self.dataCache.cache[cacheSpace]['block'].block[i] = self.sharedMemory.memory[block].getWord(i)
                                    #self.dataCache.cache[cacheSpace]['block'] = self.sharedMemory.memory[block]
                                    #escribe en cache
                                    self.dataCache.cache[cacheSpace]['block'].setWord(word, self.registers[dr])
                                    #(se mantiene M) actualiza cache
                                    self.dataCache.cache[cacheSpace]['state'] = 'M'
                                    self.dataCache.cache[cacheSpace]['tag'] = int(block)
                                    #desbloquear canados
                                    self.busLock.release()
                                    self.dirLock.release()
                                    self.cacheLock.release()
                                    finish = True
                                    self.cicles += 16
                                    continue
                                #esta en cache remota
                                else:
                                    self.cicles += 40
                                    pass
                            else:
                                #no pudo bloquear bus, libera recursos
                                self.dirLock.release()
                                self.cacheLock.release()
                                self.cicles += 1
                                continue
                        #else si es C
                        elif self.directory.directory[block]['state'] == 'C':
                            if busLock.acquire(False):
                                #invalidar en otras caches
                                '''self.neighborProcessors.invalidateCache(block)
                                self.parentProcessor.invalidateCache(block)'''
                                #carga en cache de memoria
                                self.dataCache.cache[cacheSpace]['block'] = Bloque.Bloque(0)
                                for i in range(4):
                                    self.dataCache.cache[cacheSpace]['block'].block[i] = self.sharedMemory.memory[block].getWord(i)
                                #self.dataCache.cache[cacheSpace]['block'] = self.sharedMemory.memory[block]
                                #escribe en cache
                                self.dataCache.cache[cacheSpace]['block'].setWord(word, dr)
                                #marca como M
                                self.dataCache.cache[cacheSpace]['state'] = 'M'
                                self.dataCache.cache[cacheSpace]['tag'] = int(block)
                                self.directory.directory[block]['state'] = 'M'
                                self.directory.directory[block]['flags'][int(self.name)] = True
                                #desbloquear candados
                                self.busLock.release()
                                self.dirLock.release()
                                self.cacheLock.release()
                                finish = True
                                continue
                            else:
                                #el bloque no es U, C o M (no pasa)
                                self.dirLock.release()
                                self.cacheLock.release()
                                self.cicles += 1
                                continue
                        else:
                            #no pudo bloquear bus, libera recursos
                            self.dirLock.release()
                            self.cacheLock.release()
                            self.cicles += 1
                            continue
                    else:
                        #no pudo bloquear directorio, libera cache
                        self.cacheLock.release()
                        self.cicles +=1
                        continue
            else:
                #no pudo bloquear cache, cambia de ciclo
                self.cicles += 1
                continue


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