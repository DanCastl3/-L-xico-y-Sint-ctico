import ply.lex as lex
from flask import Flask, render_template, request

app = Flask(__name__)

# Definición de palabras reservadas prueba
reserved = {
    'programa': 'PROGRAMA',
    'read': 'READ',
    'int': 'INT',
    'printf': 'PRINTF',
    'end': 'END'
}

# Lista de tokens
tokens = ['PABIERTO', 'PCERRADO', 'LLAVE_ABIERTA', 'LLAVE_CERRADA', 'OPERADOR', 'SIMBOLO', 'ID', 'CADENA', 'NUMERO', 'COMA'] + list(reserved.values())

# Expresiones regulares para los tokens
t_OPERADOR = r'='
t_PABIERTO = r'\('
t_PCERRADO = r'\)'
t_LLAVE_ABIERTA = r'\{'
t_LLAVE_CERRADA = r'\}'
t_COMA = r','
t_ignore = ' \t'

# Palabras reservadas como tokens individuales
def t_RESERVED(t):
    r'\bprograma\b|\bread\b|\bint\b|\bprintf\b|\bend\b'
    t.type = reserved.get(t.value, 'ID')  
    return t

# Identificadores (variables como 'a', 'b', 'c')
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value in reserved:
        t.type = reserved.get(t.value)
    return t

# Números
def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Símbolos y caracteres especiales (;, etc.)
def t_SIMBOLO(t):
    r'[;]'
    return t

# Contador de líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos
def t_error(t):
    print(f"Caracter no válido: {t.value[0]}")
    t.lexer.skip(1)

# Construcción del lexer
lexer = lex.lex()

def analizar_sintaxis(expresion):
    lexer.input(expresion)
    estado = "INICIO"
    linea_actual = 1

    for token in lexer:
        if token.type == "NEWLINE":
            linea_actual += 1

        if estado == "INICIO":
            if token.type == "PROGRAMA":
                estado = "NOMBRE_PROGRAMA"
            else:
                return f"Error en la estructura: Se esperaba 'programa' en la línea {linea_actual}"

        elif estado == "NOMBRE_PROGRAMA":
            if token.type == "ID":
                estado = "ABRE_PAREN"
            else:
                return f"Error en la estructura: Se esperaba un nombre de programa en la línea {linea_actual}"

        elif estado == "ABRE_PAREN":
            if token.type == "PABIERTO":
                estado = "TIPO_VAR"
            else:
                return f"Error en la estructura: Se esperaba '(' en la línea {linea_actual}"

        elif estado == "TIPO_VAR":
            if token.type == "INT":
                estado = "LISTA_VARS"
            else:
                return f"Error en la estructura: Se esperaba 'int' en la línea {linea_actual}"

        elif estado == "LISTA_VARS":
            if token.type == "ID":
                estado = "SIGUIENTE_VAR"
            else:
                return f"Error en la estructura: Se esperaba un identificador en la línea {linea_actual}"

        elif estado == "SIGUIENTE_VAR":
            if token.type == "COMA":
                estado = "TIPO_VAR"
            elif token.type == "LLAVE_ABIERTA":
                estado = "LECTURAS"
            else:
                return f"Error en la estructura: Se esperaba ',' o '{{' en la línea {linea_actual}"

        elif estado == "LECTURAS":
            if token.type == "READ":
                estado = "ID_READ"
            else:
                return f"Error en la estructura: Se esperaba 'read' en la línea {linea_actual}"

        elif estado == "ID_READ":
            if token.type == "ID":
                estado = "LLAVE_CERRADA"
            else:
                return f"Error en la estructura: Se esperaba un identificador después de 'read' en la línea {linea_actual}"

        elif estado == "LLAVE_CERRADA":
            if token.type == "LLAVE_CERRADA":
                estado = "SUMAS"
            else:
                return f"Error en la estructura: Se esperaba '}}' en la línea {linea_actual}"

        elif estado == "SUMAS":
            if token.type == "ID":
                estado = "ASIGNACION"
            else:
                return f"Error en la estructura: Se esperaba un identificador para la suma en la línea {linea_actual}"

        elif estado == "ASIGNACION":
            if token.type == "OPERADOR":
                estado = "ID_DOS"
            else:
                return f"Error en la estructura: Se esperaba '=' en la línea {linea_actual}"

        elif estado == "ID_DOS":
            if token.type == "ID":
                estado = "SUMA"
            else:
                return f"Error en la estructura: Se esperaba un identificador en la línea {linea_actual}"

        elif estado == "SUMA":
            if token.type == "OPERADOR":
                estado = "ID_TRES"
            else:
                return f"Error en la estructura: Se esperaba un operador en la línea {linea_actual}"

        elif estado == "ID_TRES":
            if token.type == "ID":
                estado = "IMPRIMIR"
            else:
                return f"Error en la estructura: Se esperaba un identificador en la línea {linea_actual}"

        elif estado == "IMPRIMIR":
            if token.type == "PRINTF":
                estado = "CADENA"
            else:
                return f"Error en la estructura: Se esperaba 'printf' en la línea {linea_actual}"

        elif estado == "CADENA":
            if token.type == "CADENA":
                estado = "FIN"
            else:
                return f"Error en la estructura: Se esperaba una cadena entre comillas en la línea {linea_actual}"

        elif estado == "FIN":
            if token.type == "END":
                return "Estructura correcta"
            else:
                return f"Error en la estructura: Se esperaba 'end' en la línea {linea_actual}"

    return "Error en la estructura"  # Si se llega al final y no se encontró un "END"

@app.route('/', methods=['GET', 'POST'])
def index():
    contador = {
        'RESERVADO': 0,
        'IDENTIFICADOR': 0,
        'CADENA': 0,  
        'NUMERO': 0,
        'SIMBOLO': 0
    }

    mensaje_sintaxis = ""

    if request.method == 'POST':
        expresion = request.form.get('Expresion')
        lexer.lineno = 1  
        
        # Análisis sintáctico
        mensaje_sintaxis = analizar_sintaxis(expresion)

        lexer.input(expresion)
        
        # Proceso de tokens en el orden en que aparecen, con número de línea
        result_lexema = []
        
        for token in lexer:
            if token.type in reserved.values():
                result_lexema.append(("RESERVADO", token.value, token.lineno))
                contador['RESERVADO'] += 1  
            elif token.type == "ID":
                result_lexema.append(("IDENTIFICADOR", token.value, token.lineno))
                contador['IDENTIFICADOR'] += 1  
            elif token.type == "PABIERTO":
                result_lexema.append(("PARENTESIS IZQUIERDO", token.value, token.lineno))
            elif token.type == "PCERRADO":
                result_lexema.append(("PARENTESIS DERECHO", token.value, token.lineno))
            elif token.type == "LLAVE_ABIERTA" or token.type == "LLAVE_CERRADA":
                result_lexema.append(("DELIMITADOR", token.value, token.lineno))
            elif token.type == "OPERADOR":
                result_lexema.append(("OPERADOR", token.value, token.lineno))
            elif token.type == "SIMBOLO":
                result_lexema.append(("SIMBOLO", token.value, token.lineno))
                contador['SIMBOLO'] += 1  
            elif token.type == "NUMERO":
                result_lexema.append(("NUMERO", token.value, token.lineno))
                contador['NUMERO'] += 1  
        
        return render_template('index.html', tokens=result_lexema, contador=contador, expresion=expresion, mensaje_sintaxis=mensaje_sintaxis)
    
    return render_template('index.html', expresion=None, contador=contador)

if __name__ == '__main__':
    app.run(debug=True)
