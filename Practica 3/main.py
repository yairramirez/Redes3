from pysnmp.hlapi import *
import rrdtool
from time import *
import json
import os
import threading

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class Agente:

    def __init__(self,comunidad:str,host:str):
        self.Comunidad=comunidad
        self.Host=host
        self.Nombre_sistema=self.consultaSNMP("1.3.6.1.2.1.1.1.0")
        self.Num_interfaces=self.consultaSNMP("1.3.6.1.2.1.2.1.0")
        self.Tiempo_Activo=self.consultaSNMP("1.3.6.1.2.1.1.3.0")

        self.ramUsed=None
        self.hrStorageUsed=None
        self.hrProcessorLoad=None
        # Creando carpeta para almacenar la base de datos generadas
        self.path=self.Host+"/"
        self.strBaseRRD=self.path+"Base.rrd"
        self.strBaseXML=self.path+"Base.xml"
        self.strCPUPNG=self.path+"CPU.png"
        self.strRAMPNG=self.path+"RAM.png"
        self.strDISCOPNG=self.path+"DISCO.png"
        try:
            os.mkdir(self.Host)
        except:
            pass

    

    def update(self,duracion=60,time_step=6):
        filas=int(duracion/time_step)
        self.createRRD(time_step,filas) # creando base de datos 

        inicio=time()
        fin= inicio + duracion# un minuto
        espera=5
        hilo_notificacion=threading.Thread(target=self.umbrales, args=(inicio,fin+espera,espera))
        hilo_notificacion.start()
        while True:
            self.consultas()
            print(self.ramUsed,self.hrStorageUsed,self.hrProcessorLoad)
            inicio=time()
            if not inicio < fin:
                break

    def umbrales(self,inicio,fin,espera):
        sleep(espera)
        while(True):
            if float(self.ramUsed) >= 1.0:
                self.graficaRAM()
                self.notificar(self.strRAMPNG)
                sleep(espera)
                print("sale")
            elif int(self.hrProcessorLoad) >= 40:
                self.graficaCPU()
                self.notificar(self.strCPUPNG)
                sleep(espera)
            elif float(self.hrStorageUsed) >= 20.0:
                self.graficaDISCO()
                self.notificar(self.strDISCOPNG)
                sleep(espera)
            else: 
                pass
            inicio=time()
            if not inicio < fin:
                break
        print("Fin de Hilo")
        

    def notificar(self,imgpath):

        mailsender = "dummycuenta3@gmail.com"
        mailreceip = "dummycuenta3@gmail.com"
        mailserver = 'smtp.gmail.com: 587'
        password = 'Secreto123@'

        msg = MIMEMultipart()
        msg['Subject'] = "Notificacionde yair ramirez Edwin Bernardo Cruz villalba"
        msg['From'] = mailsender
        msg['To'] = mailreceip
        fp = open(imgpath, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        s = smtplib.SMTP(mailserver)

        s.starttls()
        # Login Credentials for sending the mail
        s.login(mailsender, password)

        s.sendmail(mailsender, mailreceip, msg.as_string())
        s.quit()



    def consultas(self)->bool:
        # str_mib="1.3.6.1.2.1"
        # host-resources-mib= str_mib+".25"
        # snmpwalk -v1 -c 123 localhost 

        # ram total:1.3.6.1.4.1.2021.4.5
        # ram usada:1.3.6.1.4.1.2021.4.6
        # self.ramTotal=self.consultaSNMP("1.3.6.1.4.1.2021.4.5.0")
        # print(int(self.consultaSNMP("1.3.6.1.4.1.2021.4.5.0"))*1e-6)
        self.ramUsed="{:.2f}".format(int(self.consultaSNMP("1.3.6.1.4.1.2021.4.6.0"))*1e-6)

        # hrStorageTable:1.3.6.1.2.1.25.2.3
        # self.hrStorageSize=self.consultaSNMP("1.3.6.1.2.1.25.2.3.1.5.1")
        # self.hrStorageUsed=self.consultaSNMP("1.3.6.1.2.1.25.2.3.1.6.1")
        self.hrStorageUsed="{:.2f}".format(int(self.consultaSNMP("1.3.6.1.2.1.25.2.3.1.6.1"))*1e-6)

        # disco total:1.3.6.1.4.1.2021.6.6
        # disco usado:1.3.6.1.4.1.2021.6.8
        
        # hrProcessorTable:1.3.6.1.2.1.25.3.3
        self.hrProcessorLoad=self.consultaSNMP("1.3.6.1.2.1.25.3.3.1.2.196608")
        # self.hrProcessorLoad=self.consultaSNMP("1.3.6.1.2.1.25.3.3.1.2.6")

        # CPUSistemaPorcent:1.3.6.1.4.1.2021.11.9
        # CPUSistemaBrutoTiempo:1.3.6.1.4.1.2021.11.50
        # self.CPUSistemaPorcent=self.consultaSNMP("1.3.6.1.4.1.2021.11.9.0")
        # self.CPUSistemaBrutoTiempo=self.consultaSNMP("1.3.6.1.4.1.2021.11.50.0")

        rrdtool.update(self.strBaseRRD,"N:" + self.ramUsed + ":"
        # rrdtool.update("basura.rrd","N:" + self.ramUsed + ":"
                                            + self.hrStorageUsed + ":" 
                                            + self.hrProcessorLoad)
                                            
        rrdtool.dump(self.strBaseRRD ,self.strBaseXML)

        return True

    def consultaSNMP(self,oid:str):
        
        # snmpget -v1 -c "123" "localhost" 1.3.6.1.2.1.25.3.3.1.2

        errorIndication, errorStatus, errorIndex, varBinds = next(
            # hace la solicitud getsnmp
            getCmd(SnmpEngine(),
                CommunityData(self.Comunidad),
                UdpTransportTarget((self.Host, 161)), # udp
                ContextData(),
                ObjectType(ObjectIdentity(oid))))

        # tratamiento de errores
        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                varB=(' = '.join([x.prettyPrint() for x in varBind]))
                # print(varB)
                resultado= varB.split()[2] # se agarra la ultima parte de la consulta
        return resultado

    def createRRD(self,tiempo_step:int,numero_filas:int):
        # creamos la bae de datos
        ret = rrdtool.create(self.strBaseRRD,
        # ret = rrdtool.create("basura.rrd",
        # Tiempo en segs y fecha del sistema al momento de iniciar el almacenamiento
                            "--start",'N',
        # Duracion del step en segundos,
        # cada cuantos segundos tomara los datos del buffer y aplicar la funcion que nosotros queremos
                            "--step",str(tiempo_step),
        # Data Source
        #DS:
            # Nombre de la variable: 
                    # Tipo de dato de la variable: 
                            # segundos que deben de pasar para que el dato sea invalido(siempre igual que el del step): 
                                    # Limite inferior: 
                                            # Limite superior
                            "DS:var1:GAUGE:"+str(tiempo_step)+":U:U",   # self.ramUsed
                            "DS:var2:GAUGE:"+str(tiempo_step)+":U:U",   # self.hrStorageUsed
                            "DS:var3:GAUGE:"+str(tiempo_step)+":U:U",   # self.hrProcessorLoad
        # Lo que se va almacenart en cada fila
        #RRA: 
            # Funcion que se le aplicara a los datos contenidos en el buffer (de cada step): 
                    # la mitad de muestras se validan: cada 1 step : 
                            # numero de filas en la base de datos
                            "RRA:AVERAGE:0.5:1:"+str(numero_filas)) 

        #en caso de haber un error lo sabremos
        if ret:
            print (rrdtool.error())

    def graficaCPU(self,duracion=60):

        tiempo_final=int(rrdtool.last(self.strBaseRRD))
        tiempo_inicial=tiempo_final-duracion
        

        ret=rrdtool.graphv(self.strCPUPNG,
                    "--start",str(tiempo_inicial),
                    "--end",str(tiempo_final),
                    "--vertical-label=porcentaje",
                    "--title=CPU by yair ramirez",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
        #obteniendo valores de la base de datos
                    "DEF:CPU="+self.strBaseRRD+":var3:AVERAGE",
        #creando variables y asignandoles un valor a partir del valor leido de la base y la funcion elegida
                    "VDEF:cargaMAX=CPU,MAXIMUM",
                    "VDEF:cargaMIN=CPU,MINIMUM",
                    "VDEF:cargaSTDEV=CPU,STDEV", #promedio
                    "VDEF:cargaLAST=CPU,LAST",
        # se le asigna un valor a la variable a partir de la notacion rpn.
        #se transforman datos antes de graficar
                    "CDEF:umbralCPU1=CPU,40,LT,0,CPU,IF",  # if (CPU <= 40){CDFE=0} else{CDEF=CPU}
                    "CDEF:umbralCPU2=CPU,60,LT,0,CPU,IF",  # if (CPU <= 60){CDFE=0} else{CDEF=CPU}
                    "CDEF:umbralCPU3=CPU,80,LT,0,CPU,IF",  # if (CPU <= 80){CDFE=0} else{CDEF=CPU}
                    "CDEF:umbralCPU4=CPU,100,LT,0,CPU,IF",  # if (CPU <= 100){CDFE=0} else{CDEF=CPU}
        # pinta una area en el grafico
                    "AREA:CPU#0d31d4:Carga CPU", # todos los datos
                    "AREA:umbralCPU1#98d40d:Umbral CPU1", # dato filtrado
                    "AREA:umbralCPU2#d4b60d:Umbral CPU2", # dato filtrado
                    "AREA:umbralCPU3#d4660d:Umbral CPU3", # dato filtrado
                    "AREA:umbralCPU4#d40d0d:Umbral CPU4", # dato filtrado
        # pinta una linea en el grafico
                    "HRULE:40#FF0000:U1",
                    "HRULE:60#FF0000:U2",
                    "HRULE:80#FF0000:U3",
        # regresamos los valores al grear el grafico y al consultar la base de datos
                    "PRINT:cargaLAST:%6.2lf",
                    "GPRINT:cargaMIN:%6.2lf %SMIN",
                    "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                    "GPRINT:cargaLAST:%6.2lf %SLAST" )

        # print(ret)

    def graficaRAM(self,duracion=60):

        tiempo_final=int(rrdtool.last(self.strBaseRRD))
        tiempo_inicial=tiempo_final-duracion
        

        ret=rrdtool.graphv(self.strRAMPNG,
                    "--start",str(tiempo_inicial),
                    "--end",str(tiempo_final),
                    "--vertical-label=GB",
                    "--title=RAM by yair ramirez",
                    '--lower-limit', '0.0',
                    '--upper-limit', '2.0',
        #obteniendo valores de la base de datos
                    "DEF:RAM="+self.strBaseRRD+":var1:AVERAGE",
        #creando variables y asignandoles un valor a partir del valor leido de la base y la funcion elegida
                    "VDEF:cargaMAX=RAM,MAXIMUM",
                    "VDEF:cargaMIN=RAM,MINIMUM",
                    "VDEF:cargaSTDEV=RAM,STDEV", #promedio
                    "VDEF:cargaLAST=RAM,LAST",
        # se le asigna un valor a la variable a partir de la notacion rpn.
        #se transforman datos antes de graficar
                    "CDEF:umbralRAM1=RAM,0.1,LT,0,RAM,IF",  # if (CPU <= 40){CDFE=0} else{CDEF=CPU}
                    "CDEF:umbralRAM2=RAM,0.2,LT,0,RAM,IF",  # if (CPU <= 60){CDFE=0} else{CDEF=CPU}
                    "CDEF:umbralRAM3=RAM,0.3,LT,0,RAM,IF",  # if (CPU <= 80){CDFE=0} else{CDEF=CPU}
                    "CDEF:umbralRAM4=RAM,0.4,LT,0,RAM,IF",  # if (CPU <= 100){CDFE=0} else{CDEF=CPU}
        # pinta una area en el grafico
                    "AREA:RAM#0d31d4:Carga RAM", # todos los datos
                    "AREA:umbralRAM1#98d40d:Umbral RAM1", # dato filtrado
                    "AREA:umbralRAM2#d4b60d:Umbral RAM2", # dato filtrado
                    "AREA:umbralRAM3#d4660d:Umbral RAM3", # dato filtrado
                    "AREA:umbralRAM4#d40d0d:Umbral RAM4", # dato filtrado
        # pinta una linea en el grafico
                    "HRULE:0.1#FF0000:U1",
                    "HRULE:0.2#FF0000:U2",
                    "HRULE:0.3#FF0000:U3",
        # regresamos los valores al grear el grafico y al consultar la base de datos
                    "PRINT:cargaLAST:%6.2lf",
                    "GPRINT:cargaMIN:%6.2lf %SMIN",
                    "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                    "GPRINT:cargaLAST:%6.2lf %SLAST" )

        # print(ret)

    def graficaDISCO(self,duracion=60):

        tiempo_final=int(rrdtool.last(self.strBaseRRD))
        tiempo_inicial=tiempo_final-duracion
        

        ret=rrdtool.graphv(self.strDISCOPNG,
                    "--start",str(tiempo_inicial),
                    "--end",str(tiempo_final),
                    "--vertical-label=GB",
                    "--title=DISCO by yair ramirez",
                    '--lower-limit', '0',
                    '--upper-limit', '50',
        #obteniendo valores de la base de datos
                    "DEF:DISCO="+self.strBaseRRD+":var2:AVERAGE",
        #creando variables y asignandoles un valor a partir del valor leido de la base y la funcion elegida
                    "VDEF:cargaMAX=DISCO,MAXIMUM",
                    "VDEF:cargaMIN=DISCO,MINIMUM",
                    "VDEF:cargaSTDEV=DISCO,STDEV", #promedio
                    "VDEF:cargaLAST=DISCO,LAST",
        # se le asigna un valor a la variable a partir de la notacion rpn.
        #se transforman datos antes de graficar
                    "CDEF:umbralDISCO1=DISCO,20,LT,0,DISCO,IF",  # if (DISCO <= 40){CDFE=0} else{CDEF=DISCO}
                    "CDEF:umbralDISCO2=DISCO,30,LT,0,DISCO,IF",  # if (DISCO <= 60){CDFE=0} else{CDEF=DISCO}
                    "CDEF:umbralDISCO3=DISCO,40,LT,0,DISCO,IF",  # if (DISCO <= 80){CDFE=0} else{CDEF=DISCO}
                    "CDEF:umbralDISCO4=DISCO,50,LT,0,DISCO,IF",  # if (DISCO <= 100){CDFE=0} else{CDEF=DISCO}
        # pinta una area en el grafico
                    "AREA:DISCO#0d31d4:Carga DISCO", # todos los datos
                    "AREA:umbralDISCO1#98d40d:Umbral DISCO1", # dato filtrado
                    "AREA:umbralDISCO2#d4b60d:Umbral DISCO2", # dato filtrado
                    "AREA:umbralDISCO3#d4660d:Umbral DISCO3", # dato filtrado
                    "AREA:umbralDISCO4#d40d0d:Umbral CPU4", # dato filtrado
        # pinta una linea en el grafico
                    "HRULE:20#FF0000:U1",
                    "HRULE:30#FF0000:U2",
                    "HRULE:40#FF0000:U3",
        # regresamos los valores al grear el grafico y al consultar la base de datos
                    "PRINT:cargaLAST:%6.2lf",
                    "GPRINT:cargaMIN:%6.2lf %SMIN",
                    "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                    "GPRINT:cargaLAST:%6.2lf %SLAST" )

        # print(ret)

    def __eq__(self, agente):
        return self.Host==agente.Host

    # def __eq__ ==
    # def __lt__ <
    # def __gt__ >
    # def __le__ <=
    # def __ge__ >=
    # def __ne__ !=

    def __str__(self)->str:
        s1="\n|=============="+self.Host+"================|"
        s2="\nComunidad:",self.Comunidad
        s3="\nHost:",self.Host
        s4="\nNombre del sistema:",self.Nombre_sistema
        s5="\nNumero de interfaces de red:",self.Num_interfaces
        s6="\nTiempo desde el ultimo reinicio:"+self.Tiempo_Activo+"Segs"
        s7="\n"+self.InMemorySize
        s8="\n"+self.hrSystemInitialLoadDevice
        s9="\n"+self.hrSystemInitialLoadParameters
        s10="\n|==========================================|\n"

        return s1+s2+s3+s4+s5+s6+s7+s8+s9+s10


pc=Agente("escom", "127.0.0.1")

pc.update()
pc.graficaCPU()
pc.graficaDISCO()
pc.graficaRAM()
# pc.notificar(pc.strCPUPNG)
# pc.notificar(pc.strRAMPNG)
# pc.notificar(pc.strDISCOPNG)