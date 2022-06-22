import time
import rrdtool
import os

from CreateRRD import crearRRD
from getSNMP import consultaSNMP
from graphRRD import Graficar

PckgMulticastSentIn = 0
PckgMulticastSentOut = 0
PckgIPv4SumTrans = 0
MsjICMPRecIn = 0
MsjICMPRecOut = 0
SegRetrans = 0
DatagramSentIn = 0
DatagramSentOut = 0

def actualizaRRD(agente, consultas, nombres, tiempo_monitoreo):

    print('tiempo monitoreo', tiempo_monitoreo)
    # Crear los archivos
    for nombre in nombres:
        crearRRD( nombre )

    cont = 1
    load = 'Generando reporte '

    while cont <= tiempo_monitoreo:
        # Paquete multicast que ha enviado una interfaz:
        PckgMulticastSentIn = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 0 ])

        PckgMulticastSentOut = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 1 ])

        # Paquete IPv4 que los protocolos locales de usuarios de IPv4 suministraron a IPv4 en las solicitudes de transmisión:
        PckgIPv4SumTrans = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 2 ])

        # Mensajes ICMP que ha recibido el agente:
        MsjICMPRecIn = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 3 ])

        MsjICMPRecOut = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 4 ])

        # Segmentos retransmitidos:
        SegRetrans = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 5 ])

        # Datagramas enviados por el agente:
        DatagramSentIn = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 6 ])

        DatagramSentOut = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'],
                        consultas[ 7 ])

        PckgMulticastSentV = "N:" + str( PckgMulticastSentIn ) + ":" + str( PckgMulticastSentOut )
        PckgIPv4SumTransV = "N:" + str( PckgIPv4SumTrans ) + ":" + str( PckgIPv4SumTrans )
        MsjICMPRecV = "N:" + str( MsjICMPRecIn ) + ":" + str( MsjICMPRecOut )
        SegRetransV = "N:" + str( SegRetrans ) + ":" + str( SegRetrans )
        DatagramSentV = "N:" + str( DatagramSentIn ) + ":" + str( DatagramSentOut )

        rrdtool.update(str(nombres[ 0 ] + '.rrd'), PckgMulticastSentV)
        rrdtool.dump(str(nombres[ 0 ] + '.rrd'), str(nombres[ 0 ] + '.xml'))

        rrdtool.update(str(nombres[ 1 ] + '.rrd'), PckgIPv4SumTransV)
        rrdtool.dump(str(nombres[ 1 ] + '.rrd'), str(nombres[ 1 ] + '.xml'))

        rrdtool.update(str(nombres[ 2 ] + '.rrd'), MsjICMPRecV)
        rrdtool.dump(str(nombres[ 2 ] + '.rrd'), str(nombres[ 2 ] + '.xml'))

        rrdtool.update(str(nombres[ 3 ] + '.rrd'), SegRetransV)
        rrdtool.dump(str(nombres[ 3 ] + '.rrd'), str(nombres[ 3 ] + '.xml'))

        rrdtool.update(str(nombres[ 4 ] + '.rrd'), DatagramSentV)
        rrdtool.dump(str(nombres[ 4 ] + '.rrd'), str(nombres[ 4 ] + '.xml'))

        time.sleep(1)

        #print( ((cont * 100) / tiempo_monitoreo) )
        load += (str( ((cont * 100) / tiempo_monitoreo) ) + '%' ) if ( (((cont * 100) / tiempo_monitoreo) % 25 ) == 0 ) else '.'
        os.system('cls' if os.name == 'nt' else 'clear')
        print( load )
        
        cont += 1


    Graficar( 'Paquete multicast que ha enviado una interfaz', nombres[ 0 ], tiempo_monitoreo )
    Graficar( 'Paquete IPv4 que los protocolos locales de usuarios de IPv4 suministraron a IPv4 en las solicitudes de transmisión', nombres[ 1 ], tiempo_monitoreo )
    Graficar( 'Mensajes ICMP que ha recibido el agente', nombres[ 2 ], tiempo_monitoreo )
    Graficar( 'Segmentos retransmitidos', nombres[ 3 ], tiempo_monitoreo )
    Graficar( 'Datagramas enviados por el agente', nombres[ 4 ], tiempo_monitoreo )

    return True

    if ret:
        print (rrdtool.error())
        time.sleep(300)