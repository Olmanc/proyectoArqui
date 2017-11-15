class Context:
    def __init__(self, pc, start):
        self.context = [{'pc': pc, 'registers': [0]*32, 'startTime': None, 'starCycle': start}]
