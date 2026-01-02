import json
import re
import sqlite3  
import datetime
import os
from conexionBD import *


# Funciones para procesar el archivo CICSADM.TXT
def extraer_lineas(texto):
    lineas = []

    for linea in texto.splitlines():
        linea = re.sub(r'^\s*\d+\s*', '', linea).strip()
        linea = linea.strip()

        if linea:
            lineas.append(linea)

    return lineas


# Extraer el título del segmento de una línea TS
def extrearTitulo_segmento(linea):

    arrTitulos = []
    # el titulo del segmento comienza despues del primer guion o numero
    match = re.search(r'[-0-9](.*)', linea) 
    if match:
        titulo_segmento = match.group(1).strip()
    else:
        titulo_segmento = linea.strip()


    #dividir en dos partes si la separacion es muy grande y regresaar un array con las dos o mas partes
    arrTitulos = re.split(r'\s{10,}', titulo_segmento)
    #print(f"Titulo(s) segmento extraido: {arrTitulos}")

    return arrTitulos


# Extraer campos y valores de una línea DE
def extraer_campos(texto):
    # Expresión regular más robusta:
    # Captura "campo" seguido de ":" y luego "valor"
    patron = re.compile(r'([^:]+?)\s*:\s*([^\s].*?)(?=\s{2,}[^:]+:|$)')

    campos = []

    for linea in texto.splitlines():
        # Eliminar número inicial y espacios
        linea = re.sub(r'^\s*\d+\s*', '', linea)

        # Buscar coincidencias campo:valor en la línea
        coincidencias = patron.findall(linea)

        for campo, valor in coincidencias:
            campo = campo.strip().replace('.', '').replace('\t', '')
            campo = re.sub(r'\s+', ' ', campo)  # Reemplazar múltiples espacios por uno solo
            campo = campo.strip()
    
            valor = valor.strip()
            campos.append((campo, valor))
    return campos


# Identificar el tipo de línea
def identificar_tipo_linea(linea):
    if not linea:
        return 'VA'  #vacia  
    elif re.search(r'\bPAGE\b', linea, re.IGNORECASE):
        return 'EN' #encabezado
    elif re.match(r'-[A-Z][a-z]', linea):
        return 'TS'  #titulo segmento
    elif re.match(r'0[A-Z][a-z]', linea):
        return 'TS'  #titulo segmento
    elif re.match(r'\+_____________________________', linea):
        return 'IS'  #inicio segmento
    elif re.match(r'\+__', linea):
        return 'ID'  #inicio detalle
    # fin detalle debe ser igual a 0------------------------------------------------------------------------------------------------------------------------------------
    elif re.match(r'0------------------------------------------------------------------------------------------------------------------------------------', linea):
        return 'FD'  #fin detalle
    else:
        return 'DE'  #detalle
    

def validarCargaFecha(fecha_str):
    #validar si en base de datos ya existe un segmento con la misma 
    conn = conectar_base_datos()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM validacion_sistema WHERE fecha = ?", (fecha_str))   
    count = cursor.fetchone()[0]
    conn.close()    
    return count


# Validar si ya existe un segmento con la misma fecha
def validarArchivoFecha(nombreArchivo, fecha_str):
    #validar si en base de datos ya existe un segmento con la misma 
    conn = conectar_base_datos()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM validacion_sistema WHERE archivo = ? AND fecha = ?", (nombreArchivo, fecha_str))   
    count = cursor.fetchone()[0]
    conn.close()    
    return count


# Insertar segmentos en la base de datos
def insertarSegmentos(fechaActual, nombreArchivo, diccionarioSegmentos):

    #crear conexion con base de datos SQL 
    conn_sqlserver = conectar_base_datos()
    cursor_sqlserver = conn_sqlserver.cursor()  
    cursor_sqlserver.execute('''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='segmentos' AND xtype='U')
            CREATE TABLE validacion_sistema  
            (id INT IDENTITY(1,1) PRIMARY KEY,
             archivo NVARCHAR(255), 
                segmento NVARCHAR(255),
                campo NVARCHAR(255),
                valor NVARCHAR(MAX),
                fecha DATE,
                INDEX IX_validacion_sistema_fecha (fecha))''')
    conn_sqlserver.commit()
    cantidadRegFechaActual = validarArchivoFecha(nombreArchivo, fechaActual)
    print( f"Cantidad de registros para la fecha {fechaActual}: {cantidadRegFechaActual}" )

    if cantidadRegFechaActual > 0:
        print(f"Ya existen segmentos registrados para la fecha {fechaActual}. No se insertarán nuevos registros.")
        conn_sqlserver.close()
        return
    else:   
        print(f"Insertando nuevos segmentos para la fecha {fechaActual}.")      

        for segmento_id, segmento in diccionarioSegmentos.items():
            titulo = segmento['titulo']
            detalles_json = json.dumps(segmento['detalles'])  

            #recorrer los detalles
            for detalles_json in segmento['detalles']:
                #obtener campo y valor
                for campo, valor in detalles_json.items():
                    print(f"Archivo: {nombreArchivo}, Segmento: {titulo}, Campo: {campo}, Valor: {valor}")
                    cursor_sqlserver.execute("INSERT INTO validacion_sistema (archivo, segmento, campo, valor, fecha) VALUES (?, ?, ?, ?, ?)", (nombreArchivo, titulo, campo, valor, fechaActual))
        conn_sqlserver.commit()
        conn_sqlserver.close()   
        print("Inserción de validación completada.")