import glob
import Instruccion
import Processor
import OS
from threading import Barrier
barrier = Barrier(2)

#recibe nombre de la carpeta donde esta los hilos
#y el procesador donde carga la instrucciones
def getPosiblesHilos(computerDir):
    a = glob.glob('./'+ computerDir +'/*.txt')
    threads = {}
    i = 1
    for x in a:
        threads[i] = x
        i += 1
    return threads
def getHilos(dir, procesador):
    #a = glob.glob('./'+ dir +'/*.txt')
    l = (len(procesador.instMemory.memory)*4)
    cont = 0
    for x in dir:
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

def formatSharedMemForOutput(sharedMem, ppSharedMem = {}):
    for i in range(len(sharedMem)):
        ppSharedMem[i] = sharedMem[i].block
    return ppSharedMem

def formatCacheForOutput(cache, ppCache = []):
    for i in cache.cache:
        ppCacheBlock = {}
        ppCacheBlock['block'] = i['block'].block
        ppCacheBlock['state'] = i['state']
        ppCacheBlock['tag'] = i['tag']
        ppCache.append(ppCacheBlock)
    return ppCache
def main():
    quantum = int(input("Digite el quantum: \n"))
    OS.opSystem.setQuantum(quantum)
    print('Set quantum to {}\n'.format(OS.opSystem.getQuantum()))
    p1PHilos = getPosiblesHilos('p0')
    p2PHilos= getPosiblesHilos('p1')
    hilosP1 = [int(i) for i in input('Digite el id (numero) de los hilos que desea ejecutar para procesador 0, separados por un espacio.\nHilos: {}\n'.format(p1PHilos)).strip().split()]
    dir1 = [p1PHilos[i] for i in hilosP1]
    hilosP2 = [int(i) for i in input('Digite el id (numero) de los hilos que desea ejecutar para procesador 0, separados por un espacio.\nHilos: {}\n'.format(p2PHilos)).strip().split()]
    dir2 = [p2PHilos[i] for i in hilosP2]
    p1 = Processor.Processor(2, 24, 24, 4, 0, 0)
    p2 = Processor.Processor(1, 16, 24, 4, 0, 1)
    getHilos(dir1, p1)
    getHilos(dir2, p2)
    
    # getHilos(dir1, p1)
    # getHilos(dir2, p2)
    procs = [p1, p2]
    #procs = [p2]
    cores = []
    for proc in procs:
        for core in proc.cores:
            cores.append(core)
    cores[0].setNeighborProcessors(p2)
    cores[1].setNeighborProcessors(p2)
    cores[2].setNeighborProcessors(p1)
    for core in cores:
        core.start()
    for core in cores:
        core.join()
    #for p in procs:
    #    for d in p.directory.directory:
    #        print(d)
    #for core in cores:
    #    for c in core.dataCache.cache:
    #        print(c)
    print('Gathering contexts for printing...')
    print('Formatting registers for output...')
    print('Done!\n')

    ppSharedMem = formatSharedMemForOutput(p1.sharedMemory.memory)
    print('SharedMem: {} \n'.format(ppSharedMem))
    ppCacheCore0P0 = formatCacheForOutput(p1.cores[0].dataCache)
    ppCacheCore1P0 = formatCacheForOutput(p1.cores[1].dataCache)
    ppCacheCore0P1 = formatCacheForOutput(p2.cores[0].dataCache)
    print('Data Cache for Core 0 in P0: {}\n'.format(ppCacheCore0P0))
    print('Data Cache for Core 1 in P0: {}\n'.format(ppCacheCore1P0))
    print('Data Cache for Core 0 in P1: {}\n'.format(ppCacheCore0P1))
    print('Directory: {}\n'.format(p1.directory.directory))
    for proc in procs:
        
        for context in proc.finished:
            
            registers = context['registers']
            ppRegisters = {}
            for i in range(len(registers)):
                if registers[i] != 0:
                    ppRegisters['R{}'.format(i)] = registers[i]
            print('Thread ID: {0}\n finalPC: {1}\n registers: {2}\n totalCicles: {3}\n totalTime: {4}\n'
                    .format(context['id'], context['pc'], ppRegisters, context['cicles'], context['elapsedTime']))


main()
