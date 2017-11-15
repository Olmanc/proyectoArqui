import glob
import Instruccion
import Processor

#recibe nombre de la carpeta donde esta los hilos
#y el procesador donde carga la instrucciones
def getHilos(dir, procesador):
    a = glob.glob('./'+ dir +'/*.txt')
    l = (len(procesador.instMemory.memory)*4)
    cont = 0
    for x in a:
        fo = open(x,"r")
        print(x)
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
b = Processor.Processor(1,24,16,4,0)
dir = input('directorio?:\n')
getHilos(dir,b)
b.cores[0].instrCache.write(0, b.instMemory.read(0))
b.cores[0].start()
'''l = (len(b.instMemory.memory)*4)
for i in range(l):
    bloq = i//4
    wrd = i%4
    print("bloque: ", bloq, " palabra: ", wrd, "valor:",b.instMemory.read2(bloq, wrd))'''