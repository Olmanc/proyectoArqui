import glob
import Instruccion
import Processor
import OS

#recibe nombre de la carpeta donde esta los hilos
#y el procesador donde carga la instrucciones
def getHilos(dir, procesador):
    a = glob.glob('./'+ dir +'/*.txt')
    l = (len(procesador.instMemory.memory)*4)
    cont = 0
    for x in a:
        fo = open(x,"r")
        procesador.writeContext(cont*4, x)
        for line in fo.readlines():
            c = line.split('\s')
            d = [int(t) for t in c[0].split()]
            if cont < l:
                bloque = cont//4
                palabra = cont%4
                inst = Instruccion.Intruccion(d[0],d[1],d[2],d[3])
                procesador.instMemory.write(bloque,palabra,inst)
            else:
                print("no se pudo guardar la instruccion", c)
            cont += 1
#prueba crear un procesador y  palabras de memoria de instrucciones metidas a memoria

def main():
    quantum = int(input("Digite el quantum: \n"))
    OS.opSystem.setQuantum(quantum)
    print(OS.opSystem.getQuantum())
    p1 = Processor.Processor(2, 24, 16, 4, 0)
    #p2 = Processor.Processor(1, 24, 16, 4, 0)
    dir1 = 'p4'
    #dir2 = 'p3'
    getHilos(dir1, p1)
    #getHilos(dir2, p2)
    #procs = [p1, p2]
    procs = [p1]
    for proc in procs:
        for core in proc.cores:
            core.start()
        total = 0
        finished = []
        while not (proc.context.empty()):

            for core in proc.cores:
                context = proc.readContext()
                if (context['status'] and context not in finished):
                    total += 1
                    proc.writeContext(context['pc'], context['id'], context['registers'], context['status'])
                    finished.append(context)
                else:
                    core.instrCache.write(context['pc'], proc.instMemory.read(context['pc']))
                    core.registers = context['registers']
                    core.setPC(context['pc'])
                    print('Context id: {0} with pc: {1} on thread: {2}'.format(context['id'], context['pc'], core.id))
                    status = core.execute()
                    proc.writeContext(core.getPC(), context['id'], core.getRegisters(), status)
            if(total == proc.context.qsize()):
                print (proc.context.qsize())
                break
    for core in proc.cores:
        core.stop()

    while not (proc.context.empty()):
        context = proc.readContext()
        print ('Context id: {0} with pc: {1} and registers: {2}'.format(context['id'], context['pc'], context['registers']))

'''b = Processor.Processor(2, 24, 16, 4, 0)
dir = input('directorio?:\n')
getHilos(dir,b)
for core in b.cores:
    core.start()
total = 0
finished = []
while not (b.context.empty()):

    for core in b.cores:
        context = b.readContext()
        if (context['status'] and context not in finished):
            total += 1
            b.writeContext(context['pc'], context['id'], context['registers'], context['status'])
            finished.append(context)
        else:
            core.instrCache.write(context['pc'], b.instMemory.read(context['pc']))
            core.registers = context['registers']
            core.setPC(context['pc'])
            print('Context id: {0} with pc: {1} on thread: {2}'.format(context['id'], context['pc'], core.id))
            status = core.execute()
            b.writeContext(core.getPC(), context['id'], core.getRegisters(), status)
    if(total == b.context.qsize()):
        print (b.context.qsize())
        break


for core in b.cores:
    core.stop()

while not (b.context.empty()):
    context = b.readContext()
    print ('Context id: {0} with pc: {1} and registers: {2}'.format(context['id'], context['pc'], context['registers']))
'''
'''#b.cores[0].instrCache.write(0, b.instMemory.read(0))
#b.cores[0].start()
l = (len(b.instMemory.memory)*4)
for i in range(l):
    bloq = i//4
    wrd = i%4
    print("bloque: ", bloq, " palabra: ", wrd, "valor:",b.instMemory.read2(bloq, wrd))'''

main()
