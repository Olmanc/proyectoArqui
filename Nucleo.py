from threading import Thread
import random
import OS as OpSystem
import Instruccion
class Nucleo(Thread):
    def __init__(self, name, idCore, instrCache, dataCache, instMem, trapFlag):
        self.pc = 0
        self.registers = [0]*32 #mejor use 0's para no tener problemas con operadores
        #self.currentStage = None
        self.instructionSet = {8: self.daddi, 32: self.dadd, 34: self.dsub,
                               12: self.dmul, 14: self.ddiv, 4: self.beqz,
                               5: self.bneqz, 3: self.jal, 2: self.jr, 35: self.lw, 43: self.sw, 63: self.end}
        Thread.__init__(self)
        self.name = name
        self.id = idCore
        self.instrCache = instrCache
        self.dataCache = dataCache
        self.instMemory = instMem
        self.trapFlag = trapFlag
       
    def run(self):
      
      print("Starting " + self.name + '\n')
      #self.execute()
      
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
        opCode = 0
        cicles = 0
        while(opCode != 63 and OpSystem.opSystem.getQuantum() > cicles):
            inst = self.__fetch()
            if type(inst) != type(Instruccion.Intruccion('63','0','0','0')):
                break
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
        if(opCode == 63):
            return True
        else:
            return False

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
        self.registers[dr] = self.registers[sr] * self.registers[tr]

    def ddiv(self, sr, tr, dr):
        self.registers[dr] = self.registers[sr] / self.registers[tr]

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
        self.pc = sr

    def lw(self, sr, dr, imm):
        pass
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
        #calcula bloque y palabra
        '''addr = self.registers[sr]+imm
        block = addr//16
        word = addr%4        
        #bloquear cache (try)

        #esta en cache?
        hit = self.dataCache.findBlock(addr)
        print(hit)
        if hit:
            #esta en cache
            readBlock = self.sharedMemory.read(self.registers[sr]+imm-256)
            registers[dr] = readBlock[word]
        else:
            #no esta en cache
            #bloque victima
            if self.dataCache.cache[word]['state'] == 'M':
                pass
                #escribe bloque victima a memoria 
                
            #bloquear directorio? (try)
            
            #U/C (trae de memoria) vs M (copia a memoria)'''
    
    def sw(self, sr, dr, imm):
        #calcular mem y buscar
        pass
    
    def end(self, sr, dr, imm):
        self.__mem()
        print ("Finished thread " + self.name + '\n')
        return True

    def stop(self):
        self.isRunning = False
            
        
        


