import csv
import struct
import time
import random
from ipcqueue import sysvmq
numeroPagina=0
memoriaPrincipal=[]
numeroFilas=13
contadorFilaActual=0
max8 = 10575
max5 = 16920
buzonLlamados=sysvmq.Queue(9)
buzonRetornos=sysvmq.Queue(7)
buzonParametros=sysvmq.Queue(3)
#HabilitarPagina = 0
#pedirPagina =1
#guardar=2
for i in range(numeroFilas):
    memoriaPrincipal.append([])

def pasarPaginaMPrincipalSecundaria(pagSwap):
	global memoriaPrincipal
	numeroPage = memoriaPrincipal[pagSwap][0]
	nombrePagina=str(numeroPage)+".csv"
	#Se crea un archivo con los datos de la pagina seleccionada 	
	with open(nombrePagina, 'wb') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
					quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(memoriaPrincipal[pagSwap])
	#Esto es para borrar en memoria principal
	memoriaPrincipal[pagSwap].clear()
	
	
def pasarPaginaMSecundariaPrincipal(pagSwap,numP):
	global memoriaPrincipal
	#Para buscar la pagina deseada en memoria principal
	arregloTemporal = []
	nombrePagina=str(numP)+".csv"
	with open(nombrePagina, 'rb') as csvfile:
		arregloTemporal = list(csv.reader(csvfile))
	 #Para colocar la pagina en memoria principal
	memoriaPrincipal[pagSwap].append(arregloTemporal[0])
	
	
def busquedaPaginaSwap():
	global memoriaPrincipal,max5,max8
	pagSwapB = False
	indMemSwap = -1
	while(i<13 and pagSwapB == False):
		if(memoriaPrincipal[i][1] == 5):
			if(len(memoriaPrincipal[i]) == max5):
				pagSwapB = True
				indMemSwap = i
		elif(memoriaPrincipal[i][1] == 8):
			if(len(memoriaPrincipal[i]) == max8):
				pagSwapB = True
				indMemSwap = i
		i+=1
	if(pagSwapB==False):
		indMemSwap=random.randint(0,13)
	return indMemSwap


def busquedaPaginaMemoriaPrincipal(numPABuscar):
	global memoriaPrincipal
	indiceARetornar=-1
	paginaEncontrada=False
	while(i<13 and paginaEncontrada==False):
		if(memoriaPrincipal[i][0]==numPABuscar):
			indiceARetornar=numPABuscar
			paginaEncontrada=True
		i+=1
	return indiceARetornar
			
			
#Habilitarle una pagina a un proceso y la coloca en la memoria principal     
def habilitarPagina(tamanoPagina):
	global numeroPagina, contadorFilaActual,memoriaPrincipal,max5,max8
	if (contadorFilaActual < 13): 
		memoriaPrincipal[contadorFilaActual].append(numeroPagina)
		numeroPagina+=1
		memoriaPrincipal[contadorFilaActual].append(tamanoPagina)
		contadorFilaActual+=1
	else:
		indMemSwap=busquedaPaginaSwap()
		pasarPaginaMPrincipalSecundaria(indMemSwap)
		#Agregar nueva pagina en memoria
		memoriaPrincipal[indMemSwap].append(numeroPagina)
		numeroPagina += 1
		memoriaPrincipal[indMemSwap].append(tamanoPagina)
		
	
	return numeroPagina-1


#Es para entregarle a la interfaz la pagina solicitada.		
def pedirPagina(numeroP):
	global memoriaPrincipal,numeroFilas,max5,max8
	paginaADevolver=[]
	for i in range(numeroFilas):
		#Si la pagina esta en memoria principal
		if(memoriaPrincipal[i][0]==numeroP):
			paginaADevolver = memoriaPrincipal[i][:]#Revisar esto
		#No esta en memoria
		else:
			indMemSwap=busquedaPaginaSwap()
			pasarPaginaMPrincipalSecundaria(indMemSwap)
			
			pasarPaginaMSecundariaPrincipal(pagSwap,numeroP)
			 #Se toma de la memoria la pagina deseada
			paginaADevolver = memoriaPrincipal[indMemSwap][:]
	return paginaADevolver
	
def paginallenaMemoriaPrincipal(indiceP):
	paginallena=False
	if(memoriaPrincipal[indiceP][1] == 5):
		if(len(memoriaPrincipal[indiceP]) == max5):
			paginaLlena = True
	elif(memoriaPrincipal[indiceP][1] == 8):
		if(len(memoriaPrincipal[indiceP]) == max8):
			paginaLlena = True
	return paginallena
	
def guardar(pack,numP):
	global numeroFilas, memoriaPrincipal,max5,max8
	numeroPag=-1
	indiceP=busquedaPaginaMemoriaPrincipal(numP)
	if(indiceP!=-1):
		paginaLlena=paginallenaMemoriaPrincipal(indiceP)
		#Si tiene espacio
		if(paginaLlena==False):
			#Guarda el dato
			memoriaPrincipal[indiceP].append(pack)
		#Si esta llena
		else:
			pagNueva = habilitarPagina(memoriaPrincipal[indiceP][1])
			#Ver en que posicion de memoria principal quedo, y luego ya se puede guardar
			indiceP=busquedaPaginaMemoriaPrincipal(pagNueva)
			memoriaPrincipal[indiceP].append(pack)
			numeroPag=pagNueva
	else:
		indMemSwap=busquedaPaginaSwap()
		pasarPaginaMPrincipalSecundaria(indMemSwap)
		pasarPaginaMSecundariaPrincipal(indMemSwap,numP)
		paginaLlena=paginallenaMemoriaPrincipal(indMemSwap)
		if(paginaLlena==False):
			#Para guardar
			memoriaPrincipal[indMemSwap].append(pack)
		else:
			pagNueva=habilitarPagina(memoriaPrincipal[indMemSwap][1])
			indMemSwap=busquedaPaginaMemoriaPrincipal(pagNueva)
			memoriaPrincipal[indMemSwap].append(pack)
			numeroPag=pagNueva
	return numeroPag
	
#NOTA:Antes de llamar a guardar se debe hacer un nuevo pack sin el codigo.
while(True):
	codigoLlamado=buzonLlamados.get()
	if(codigoLlamado==0):
		parametro=buzonParametros.get()
		paginaHabilitada=habilitarPagina(parametro)
		buzonRetornos.put(paginaHabilitada)
	elif(codigoLlamado==1):
		parametro=buzonParametros.get()
		paginaADevolver=pedirPagina(parametro)
		buzonRetornos.put(paginaADevolver)
		
	elif(codigoLlamado==2):
		parametro1=buzonParametros.get()
		parametro2=buzonParametros.get()
		numPage=guardar(parametro1,parametro2)
		buzonRetornos.put(numPag)
	
	
		
		
			

	
			
			
			
			
		
	
