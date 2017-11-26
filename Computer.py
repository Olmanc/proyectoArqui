import glob
import Instruccion
import Processor
import OS
from threading import Barrier
barrier = Barrier(2)

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
    p1 = Processor.Processor(2, 24, 16, 4, 0, 0)
    p2 = Processor.Processor(1, 24, 16, 4, 0, 1)
    dir1 = 'p3'
    dir2 = 'p4'
    getHilos(dir1, p1)
    getHilos(dir2, p2)
    procs = [p1, p2]
    cores = []
    for proc in procs:
        for core in proc.cores:
            cores.append(core)
    print(cores)
    for core in cores:
        core.start()
    for core in cores:
        core.join()
    print('Gathering contexts for printing...')
    print('Formatting registers for output...')
    print('Done!\n')
    for proc in procs:
        for context in proc.finished:
            
            registers = context['registers']
            ppRegisters = {}
            for i in range(len(registers)):
                ppRegisters['R{}'.format(i)] = registers[i]
            print('Thread ID: {0}, finalPC: {1}, registers: {2}, totalCicles: {3}, totalTime: {4}\n'
                    .format(context['id'], context['pc'], ppRegisters, context['cicles'], context['elapsedTime']))


main()
