import socket
import struct 
import time

MINE = "10.1.138.139"

UDP_PORT = 10001
FORMAT = 'BiBBBBBf'
ListaIdGrupo=["Whitenoise","FlamingoBlack","GISSO","KOF","Equipo 404","Poffis"]
listaSensores=["KeepAlive","Movimiento","Sonido","Luz","Shock","Touch","Humedad","BigSound","Temperatura","Ultrasonico"]

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((MINE, UDP_PORT))

while True:
	data, addr = sock.recvfrom(50) # buffer size is 1024 bytes
	var = struct.unpack(FORMAT,data)
	t = var[1]
	t = time.ctime(t)
	packAck=struct.pack('BBBBB',var[0],var[2],0,0, var[5]) 
	sock.sendto(packAck, (addr))
	print ("Mensaje recibido de: "+ str(ListaIdGrupo[var[2]-1]) )
	print ("Sensor: "+ str(listaSensores[var[6]]) )
	print ("Numero Ack: "+ str(var[0]))
	print ("Fecha: " + str(t))
	print ("Dato: " + str(var[7]))
	print ("----------------------------------------------------------")
