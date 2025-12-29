
import datetime
import json
import os
from functions import *

archivo_path = os.path.join('Reportes_CICS', 'CICSADM.TXT')
# Leer el contenido del archivo solo las primera 150 lineas
cantidadLeer = 150
with open(archivo_path, 'r') as file:
    texto = ''.join([next(file) for _ in range(cantidadLeer)])       


lineas = extraer_lineas(texto)
contador = 0
contadorSegmentos = 0
diccionarioSegmentos = {}

for linea in lineas:
    contador += 1
    tipoLinea = identificar_tipo_linea(linea)

    if tipoLinea == 'IS':
        contadorSegmentos += 1
    
    if tipoLinea == 'TS':
        titulo_segmento = extrearTitulo_segmento(linea)
        linea = titulo_segmento
        diccionarioSegmentos[contadorSegmentos] = {'titulo': linea, 'detalles': []}

    if tipoLinea == 'DE' and contadorSegmentos > 0:
        campos = extraer_campos(linea)
        for campo, valor in campos:
            linea = f"{campo}: {valor}"
            # al agrear los detalles, agregar como tupla campo: valor
            diccionarioSegmentos[contadorSegmentos]['detalles'].append({campo: valor})

    
    if contador < 10:   
        print(f"0{contador} | {tipoLinea} |{linea}")
    else:   
        print(f"{contador} | {tipoLinea} |{linea}")

    

print(f"\nTotal lineas procesadas: {contador}"
      f"\nTotal segmentos encontrados: {contadorSegmentos}")

#transformar diccionarioSegmentos a json

json_data = json.dumps(diccionarioSegmentos, indent=4)  

# Guardar el JSON en un archivo
with open('segmentos.json', 'w') as json_file:
    json_file.write(json_data)  

# imprimir json_data
print("\nJSON de segmentos y Campos:")
print(json_data)

# guardar el json en base de datos sqlite
import sqlite3  
conn = sqlite3.connect('segmentos.db')  
c = conn.cursor()   
# Crear tabla segmentos
c.execute('''CREATE TABLE IF NOT EXISTS segmentos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             segmento TEXT,
             campo TEXT,
             valor TEXT,
             fecha DATE)''')     
# Insertar datos en la tabla
for segmento_id, segmento in diccionarioSegmentos.items():
    titulo = segmento['titulo']
    detalles_json = json.dumps(segmento['detalles'])  

    #recorrer los detalles
    for detalles_json in segmento['detalles']:
        #obtener campo y valor
        for campo, valor in detalles_json.items():
            print(f"DB Segmento: {titulo}, Campo: {campo}, Valor: {valor}")
            c.execute("INSERT INTO segmentos (segmento, campo, valor, fecha) VALUES (?, ?, ?, ?)", (titulo, campo, valor, datetime.date.today()))
conn.commit()
conn.close()    


