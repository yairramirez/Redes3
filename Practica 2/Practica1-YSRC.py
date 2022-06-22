from Funciones import diasHastaFecha, monitoreo, menu
from GeneratePDF import genPDF

# Main
diasVividos = diasHastaFecha(11, 9, 1996, 23, 2, 2022)
modulos = (diasVividos % 3) + 1

print('He vivido', diasVividos, 'dias, me tocan los modulos', modulos, '\n')

# monitoreo()
menu()
