import json
import string

from getSNMP import consultaSNMP
from updateRRD import actualizaRRD
from GeneratePDF import genPDF

agentes = {}

# Leemos el archivo con los agentes
with open('agentes.json') as file:
    agentes = json.load( file )

# Funcion para obtener los dias vividos hasta el 23/02/2022 y el id de los bloques a realizar
def diasHastaFecha(day1, month1, year1, day2, month2, year2):

    # Función para calcular si un año es bisiesto o no
    
    def esBisiesto(year):
        return year % 4 == 0 and year % 100 != 0 or year % 400 == 0

    # Caso de años diferentes

    if (year1<year2):
        
        # Días restante primer año
        
        if esBisiesto(year1) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
        restoMes = diasMes[month1] - day1

        restoYear = 0
        i = month1 + 1

        while i <= 12:
            restoYear = restoYear + diasMes[i]
            i = i + 1

        primerYear = restoMes + restoYear

        # Suma de días de los años que hay en medio

        sumYear = year1 + 1
        totalDias = 0

        while (sumYear<year2):
            if esBisiesto(sumYear) == False:
                totalDias = totalDias + 365
                sumYear = sumYear + 1
            else:
                totalDias = totalDias + 366
                sumYear = sumYear + 1

        # Dias año actual

        if esBisiesto(year2) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        llevaYear = 0
        lastYear = 0
        i = 1

        while i < month2:
            llevaYear = llevaYear + diasMes[i]
            i = i + 1

        lastYear = day2 + llevaYear

        return totalDias + primerYear + lastYear

    # Si estamos en el mismo año

    else:
        
        if esBisiesto(year1) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        llevaYear = 0
        total = 0
        i = month1
        
        if i < month2:
            while i < month2:
                llevaYear = llevaYear + diasMes[i]
                i = i + 1
            total = day2 + llevaYear - 1
            return total 
        else:
            total = day2 - day1
            return total

# Resumen monitoreo
def monitoreo( index = -1 ):
    
    if ( index == -1 ):
        
        print('Nùmero de dispositivos (agentes) que estan en monitoreo:', len( agentes['agentes'] ), '\n')
        
        if ( len( agentes['agentes'] ) > 0 ):
            for agente in agentes['agentes']:
                nombre = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0') 
                print('Agente:', 'Windows' if (nombre == 'Hardware:') else nombre)
                # Estado de conectividad con cada agente (up or down)
                estado = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0')
                print('Estado de conectividad:', 'Down' if ( estado == 'Error' ) else 'Up')
                # Numero de interfaces de red del agente
                interfaces = int( consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.2.1.0') )
                print('Nùmero de interfaces de red del agente:', interfaces, '\n')

                idx = 1

                while idx <= interfaces:
                    # Estado administrativo y descripcion de cada una de sus interfaces de red (up or down)
                    edoAdmin = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.2.2.1.7.' + str( idx ))
                    descr = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.2.2.1.2.' + str( idx ))

                    if ( isHex(descr) ):
                        descr = decodeHex( descr )
                                        
                    print(idx, '-> \t', '( Up )\t' if (int( edoAdmin ) == 1) else '( Down )', descr)
                    idx += 1
        else:
            print('No hay agentes para monitorear')

    else:

        verAgentes( False )

        opc = int( input('\n¿Qúe agente quiere monitorizar?: ') )
        tiempo_monitoreo = int( input('Escriba el tiempo en minutos de monitoreo: ') ) * 60
        consultas = ['1.3.6.1.2.1.2.2.1.18.1', '1.3.6.1.2.1.2.2.1.17.1', 
            '1.3.6.1.2.1.4.10.0',
            '1.3.6.1.2.1.5.8.0', '1.3.6.1.2.1.5.21.0', 
            '1.3.6.1.2.1.6.12.0',
            '1.3.6.1.2.1.7.1.0', '1.3.6.1.2.1.7.4.0'
        ]
        nombres_arch = ['PckgMulticastSent', 'PckgIPv4SumTrans', 'MsjICMPRec', 'SegRetrans', 'DatagramSent']

        fin = actualizaRRD(agentes['agentes'][ opc ], consultas, nombres_arch, tiempo_monitoreo)# 

        genPDF( agentes['agentes'][opc] )

        print('¡Reporte generado!')

        menu()

# Es hexadecimal
def isHex( cadena ):
    try:
        int(cadena, 16)
        return True
    except ValueError:
        return False

# Decodificar hexadecimal
def decodeHex( hex ):
    hex_string = hex[2:]
    bytes_object = bytes.fromhex( hex_string )
    ascii_string = bytes_object.decode("ASCII")

    return ascii_string

# Escribir archivo json
def actualizaArchivo( msj ):
    with open("agentes.json", "w") as file:
        json.dump(agentes, file)

    print( msj )

    verAgentes()

# Ver agentes
def verAgentes( fin = True ):
    print('\n...:: Agentes monitoreando ::...\n\n')

    for idx, agente in enumerate( agentes['agentes'] ):
        print('(', idx, ').', agente['ip'])

    if ( fin ):
        menu()

# Agregar agente
def agregarAgente():
    nvoAgente = {
        "ip": "",
        "version": 0,
        "comunidad": "",
        "puerto": 0
    }

    print('\n...:: Agregar agente ::...\n')
    nvoAgente['ip'] = input('IP del agente: ')
    nvoAgente['version'] = int( input('Versión de SNMP (0 para v1/1 para v2): ') )
    nvoAgente['comunidad'] = input('Comunidad del agente: ')
    nvoAgente['puerto'] = int( input('Puerto del agente: ') )

    agentes['agentes'].append( nvoAgente )

    msj = '\n...:: Agente agregado ::...\n'

    actualizaArchivo( msj )

# Borrar agente
def borrarAgente():

    print('\n...:: Borrar agente ::..\n')
    
    verAgentes( False )

    opc = int( input('\nSeleccione el indice del agente a eliminar: ') )

    agentes['agentes'].pop( opc )

    msj = '\n...:: Agente eliminado ::...\n'

    actualizaArchivo( msj )

# Reporte contabilildad
def contabilidad():
    print('Activos abiertos \t',                 consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.5.0"))
    print('Pasivos abiertos \t',                 consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.6.0"))
    print('Intentos fallidos \t',                consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.7.0"))
    print('Reinicios de conexión \t',            consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.8.0"))
    print('Conexiones establecidas ',             consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.9.0"))
    print('Segmentos de entrada \t',             consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.10.0"))
    print('Segmentos de salida \t',              consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.11.0"))
    print('Segmentos retransmitidos',            consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.12.0"))
    # print('\nEstado de conexión \t',            consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.13.1.1.0"))
    # print('Dirección local \t',                  consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.13.1.2.0"))
    # print('Puerto local    \t',                     consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.13.1.3.0"))
    # print('Dirección remota \t',                 consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.13.1.4.0"))
    # print('Puerto remoto    \t',                    consultaSNMP("escom", 1, "127.0.0.2", 161, "1.3.6.1.2.1.6.13.1.5.0"))

# Salir
def salir():
  print('¡Adios!')

# Menu
def menu():
    print('\n...:: Menu ::...\n\n')
    print('1. Agregar dispositivo (agente)')
    print('2. Eliminar dispositivo (agente)')
    print('3. Ver dispositivos (agentes)')
    print('4. Reporte de información del dispositivo (agente)')
    print('5. Reporte contabilidad')
    print('6. Salir')

    opc = int( input('\nSeleccione una opción: ') )

    if ( opc == 1 ):
      agregarAgente()
    elif ( opc == 2 ):
      borrarAgente()
    elif ( opc == 3 ):
      verAgentes()
    elif ( opc == 4 ):
      monitoreo( 1 )
    elif ( opc == 5 ):
      contabilidad()
    elif ( opc == 6 ):
      salir()
