
import datetime
import json
import os
from functions import *

# parametros
# fechaActual = datetime.date.today().isoformat()
fechaActual = '2025-12-30'
cantidadLeer = 50


#cantidadRegFechaActual = validarFechaSegmento(fechaActual)
cantidadRegFechaActual = 0
if cantidadRegFechaActual == 0:

    # generar listado de archivos en carpeta Reportes_CICS
    # archivos = os.listdir('Reportes_CICS')
    archivos = os.listdir('Reportes_CICS_TEST')

    for i in range(len(archivos)):
        archivos[i] = archivos[i].upper()

        print(f"Archivo en analisis: {archivos[i]}")
    
        archivo_path = os.path.join('Reportes_CICS', archivos[i])
        # Leer el contenido del archivo solo las primera 150 lineas
        with open(archivo_path, 'r') as file:
            texto = ''.join([next(file) for _ in range(cantidadLeer)])       


        lineas = extraer_lineas(texto)
        contador = 0
        contadorSegmentos = 0
        diccionarioSegmentos = {}

        for linea in lineas:
            contador += 1
            tipoLinea = identificar_tipo_linea(linea)

            if tipoLinea == 'TS':
                arrTitulos = extrearTitulo_segmento(linea)
                for titulo in arrTitulos:
                    contadorSegmentos += 1
                    diccionarioSegmentos[contadorSegmentos] = {'titulo': titulo, 'detalles': []}


            if tipoLinea == 'DE' and contadorSegmentos > 0:
                campos = extraer_campos(linea)
                for campo, valor in campos:
                    linea = f"{campo}: {valor}"
                    # al agregar los detalles, agregar como tupla campo: valor
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

        # quitar extension al nombre del archivo
        nombreArchivo = os.path.splitext(archivos[i])[0]  
        print(f"\nNombre del archivo sin extension: {nombreArchivo}")  
        insertarSegmentos(fechaActual, nombreArchivo, diccionarioSegmentos)

else:
    print(f"Ya existen {cantidadRegFechaActual} registros de segmentos para la fecha actual {fechaActual}. No se procesará el archivo nuevamente.")