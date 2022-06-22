import sys
import rrdtool
import time

def Graficar( grafico, nombre, minutos ):
  tiempo_actual = int(time.time())
  #Grafica desde el tiempo actual menos diez minutos
  tiempo_inicial = tiempo_actual - minutos


  ret = rrdtool.graph( nombre + ".png",
                      "--start",str(tiempo_inicial),
                      "--end","N",
                      "--vertical-label=Bytes/s",
                      "--title=" + grafico + " \n Usando SNMP y RRDtools",
                      "DEF:inoctets=" + nombre + ".rrd:inoctets:AVERAGE",
                      "DEF:outoctets=" + nombre + ".rrd:outoctets:AVERAGE",
                      "AREA:inoctets#00FF00:Tráfico de entrada",
                      "LINE3:outoctets#0000FF:Tráfico de salida")
