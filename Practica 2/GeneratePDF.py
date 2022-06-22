from getSNMP import consultaSNMP

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Generar PDF
def genPDF( agente ):
  w, h = A4
  c = canvas.Canvas("Reporte-" + agente['ip'] + ".pdf")
  # c = canvas.Canvas("Reporte-" + 'prueba' + ".pdf")
  c.setPageSize( landscape(A4) )

  # Encabezado
  imagen = consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0') 
  imagen = 'logo-Windows.png' if (imagen == 'Hardware:') else 'logo-Linux.png'
  c.drawImage(imagen, 10, w-60, width=50, height=50)

  xlist = [60, (h-(h/3)-5)]
  ylist = [w-10, w-60]
  c.grid(xlist, ylist)

  text = c.beginText(65, w-35)
  text.setFont("Times-Roman", 12)

  text.textLine( consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0') )

  c.drawText( text )

  altoImgs = (w-(w/3)) - (w-10)

  # Columnas izquierda
  anchoImgsIzq = (h-(h/3)-10) - 10

  xlist = [10, (h-(h/3)-10)]
  ylist = [w-60, w-(w/3)]
  c.grid(xlist, ylist)

  text = c.beginText(15, w-85)
  text.setFont("Times-Roman", 12)

  text.textLine('Descripción: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0'))
  text.textLine('Hardware: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0'))
  text.textLine('Sistema operativo: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.1.0'))
  text.textLine('Nombre del sistema: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.5.0'))
  text.textLine('Contacto: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.4.0'))
  text.textLine('Ubicación: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.6.0'))
  text.textLine('Uptime: ' + consultaSNMP(agente['comunidad'], agente['version'], agente['ip'], agente['puerto'], '1.3.6.1.2.1.1.3.0'))

  c.drawText( text )

  xlist = [10, (h-(h/3)-10)]
  ylist = [w-(w/3), w-(w*(2/3))]
  c.grid(xlist, ylist)
  c.drawImage("PckgMulticastSent.png", 10, w-(w/3)-5, width=anchoImgsIzq, height=altoImgs)

  xlist = [10, (h-(h/3)-10)]
  ylist = [w-(w*(2/3)), 10]
  c.grid(xlist, ylist)
  c.drawImage("PckgIPv4SumTrans.png", 10, w-(w*(2/3)), width=anchoImgsIzq, height=altoImgs)

 

  # Columnas derecha
  anchoImgsDer = (h-10) - (h-(h/3)+10)

  xlist = [(h-(h/3)+5), h-10]
  ylist = [w-10, w-(w/3)]
  c.grid(xlist, ylist)
  c.drawImage("MsjICMPRec.png", (h-(h/3)+5), w-10, width=anchoImgsDer, height=altoImgs)

  xlist = [(h-(h/3)+5), h-10]
  ylist = [w-(w/3), w-(w*(2/3))]
  c.grid(xlist, ylist)
  c.drawImage("SegRetrans.png", (h-(h/3)+5), w-(w/3)-5, width=anchoImgsDer, height=altoImgs)

  xlist = [(h-(h/3)+5), h-10]
  ylist = [w-(w*(2/3)), 10]
  c.grid(xlist, ylist)
  c.drawImage("DatagramSent.png", (h-(h/3)+5), w-(w*(2/3)), width=anchoImgsDer, height=altoImgs)

  c.showPage()

  c.save()