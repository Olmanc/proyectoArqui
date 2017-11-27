class Bloque:
    #Clase Bloque
    def __init__(self, value):
        #va a contener un array de 4 elementos (ints, instrucciones, etc)
        self.block = [value]*4
    
    #devuelve el elemento de la posicion especificada del array
    def getWord(self, position):
        return self.block[position]
    
    #guarda un valor en la posicion especificada del array
    def setWord(self, position, inst):
        self.block[position] = inst
