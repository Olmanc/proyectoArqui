from threading import Thread
import random
class Nucleo(Thread):
    def __init__(self, name, id):
        self.pc = 0
        self.registers = [0]*32 #mejor use 0's para no tener problemas con operadores
        #self.currentStage = None
        self.instructionSet = {8: self.daddi, 32: self.dadd, 34: self.dsub,
                               12: self.dmul, 14: self.ddiv, 4: self.beqz,
                               5: self.bneqz, 3: self.jal, 2: self.jr, 35: self.lw, 43: self.sw, 63: self.end}
        Thread.__init__(self)
        self.name = name
        self.id = id
    def run(self):
      print("Starting " + self.name + '\n')
      self.execute()
      

    def incPC(self):
        self.pc += 1

    def getPC(self):
        return self.pc

    #def getStage(self):
        #return self.currentStage

    def _fetch(self):
        pass

    def _decode(self):
        pass

    def execute(self):
        inst = 0
        while(inst != 63):
            
            inst = random.choice([8, 32, 34, 63])
            sr = random.choice(list(range(32)))
            tr = random.choice(list(range(32)))
            dr = random.choice(list(range(1,32)))
            print(repr(self.instructionSet[inst]) + '\n')
            self.instructionSet[inst](sr, tr, dr)

    def _mem(self):
        pass

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

    def beqz(self, sr, imm):
        if(sr == 0):
            self.pc += imm * 4    
    
    def bneqz(self, sr, imm):
        if not (sr == 0):
            self.pc += imm * 4   

    def jal(self, imm):
        self.registers[31] = self.pc
        self.pc += imm 

    def jr(self, sr):
        self.pc = sr

    def lw(self, sr, dr, imm):
        #calcular mem y buscar
        pass
    
    def sw(self, sr, dr, imm):
        #calcular mem y buscar
        pass
    
    def end(self, sr, dr, imm):
        print ("Exiting " + self.name + '\n')
        return
            
        
        


