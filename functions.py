import re

def extraer_lineas(texto):
    lineas = []

    for linea in texto.splitlines():
        linea = re.sub(r'^\s*\d+\s*', '', linea).strip()
        linea = linea.strip()

        if linea:
            lineas.append(linea)

    return lineas


def extrearTitulo_segmento(linea):
    # el titulo del segmento comienza despues del primer guion o numero
    match = re.search(r'[-0-9](.*)', linea) 
    if match:
        titulo_segmento = match.group(1).strip()
    else:
        titulo_segmento = linea.strip()

    # Limpiar espacios adicionales
    titulo_segmento = re.sub(r'\s+', ' ', titulo_segmento)
    
    return titulo_segmento


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