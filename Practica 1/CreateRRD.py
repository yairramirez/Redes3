#!/usr/bin/env python

import rrdtool

def crearRRD( nombre ):
    ret = rrdtool.create(str(nombre + '.rrd'),
                        "--start",'N', # A partir de que momento almacenar la info (N = now)
                        "--step",'60', # Cada 60s se aplica la func (linea 11)
                        "DS:inoctets:COUNTER:120:U:U", # Coleccion de octetos de entrada (counter), cada 120s, sin limite inferior, sin limite superior
                        "DS:outoctets:COUNTER:120:U:U", # Coleccion de octetos de salida (counter), cada 120s, sin limite inferior, sin limite superior
                        "RRA:AVERAGE:0.5:6:5",
                        "RRA:AVERAGE:0.5:1:20") # Cada 1 step al menos (0.5) la mitad, debe ser valido, y se hace un average de las (20) filas

    if ret:
        print (rrdtool.error())