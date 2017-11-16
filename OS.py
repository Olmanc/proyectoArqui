class OS:
    def __init__(self, quantum):
        self.quantum = quantum

    def getQuantum(self):
        return self.quantum
    
    def setQuantum(self, quantum):
        self.quantum = quantum
        
opSystem = OS(5)
