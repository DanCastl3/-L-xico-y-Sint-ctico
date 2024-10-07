import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, render_template, request

app = Flask(__name__)

reserved = {
    'programa': 'PROGRAMA',
    'read': 'READ',
    'int': 'INT',
    'printf': 'PRINTF',
    'end': 'END'
}

tokens = [
    'PABIERTO', 'PCERRADO', 'LLAVE_ABIERTA', 'LLAVE_CERRADA',
    'OPERADOR', 'SIMBOLO', 'ID', 'CADENA', 'NUMERO', 'COMA'
] + list(reserved.values())

t_OPERADOR = r'='
t_PABIERTO = r'\('
t_PCERRADO = r'\)'
t_LLAVE_ABIERTA = r'\{'
t_LLAVE_CERRADA = r'\}'
t_COMA = r','
t_SIMBOLO = r';'
t_CADENA = r'"[^"]*"'  
t_ignore = ' \t\n'  

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  
    return t


def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_error(t):
    print(f"Caracter no válido: {t.value[0]} en la línea {t.lineno}")
    t.lexer.skip(1)


lexer = lex.lex()


def p_programa(p):
    '''programa : PROGRAMA ID PABIERTO PCERRADO LLAVE_ABIERTA declaraciones LLAVE_CERRADA END'''
    if p[2] != "suma":
        raise SyntaxError("El nombre del programa debe ser 'suma'.")
    print("Programa válido: 'suma'.")

def p_declaraciones(p):
    '''declaraciones : declaracion declaraciones
                     | operacion declaraciones
                     | imprimir declaraciones
                     | empty'''
    print("Declaraciones válidas.")

def p_declaracion(p):
    '''declaracion : INT lista_variables SIMBOLO'''
    print(f"Declaración válida: {p[0]}")

def p_lista_variables(p):
    '''lista_variables : ID COMA lista_variables
                       | ID'''
    print(f"Lista de variables válida: {p[0]}")

def p_operacion(p):
    '''operacion : READ ID SIMBOLO
                 | ID OPERADOR ID SIMBOLO
                 | ID OPERADOR NUMERO SIMBOLO'''
    print(f"Operación válida: {p[0]}")

def p_imprimir(p):
    '''imprimir : PRINTF PABIERTO CADENA PCERRADO SIMBOLO'''
    if p[3] != '"la suma es"':
        raise SyntaxError("El argumento de printf debe ser 'la suma es'.")
    print(f"Imprimir válido: {p[0]}")

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p is None:
        print("Error de sintaxis: Fin del input inesperado.")
    else:
        print(f"Error de sintaxis en '{p.value}', tipo: {p.type}, línea: {p.lineno}.")

parser = yacc.yacc()

def analizar_sintaxis(expresion):
    lexer.input(expresion)  
    try:
        resultado = parser.parse(expresion, lexer=lexer)
        return "No hay errores de sintaxis."
    except Exception as e:
        return f"Error de sintaxis: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def index():
    contador = {
        'RESERVADO': 0,
        'IDENTIFICADOR': 0,
        'CADENA': 0,  
        'NUMERO': 0,
        'SIMBOLO': 0,
        'PARENTESIS': 0,  
        'DELIMITADOR': 0,  
        'OPERADOR': 0      
    }

    mensaje_sintaxis = ""
    result_lexema = []

    if request.method == 'POST':
        expresion = request.form.get('Expresion')
        lexer.lineno = 1  
        
        mensaje_sintaxis = analizar_sintaxis(expresion)

        lexer.input(expresion)
        
        for token in lexer:
            if token.type in reserved.values():
                result_lexema.append(("RESERVADO", token.value, token.lineno))
                contador['RESERVADO'] += 1  
            elif token.type == "ID":
                result_lexema.append(("IDENTIFICADOR", token.value, token.lineno))
                contador['IDENTIFICADOR'] += 1  
            elif token.type == "PABIERTO" or token.type == "PCERRADO":
                result_lexema.append(("PARENTESIS", token.value, token.lineno))
                contador['PARENTESIS'] += 1  
            elif token.type == "LLAVE_ABIERTA" or token.type == "LLAVE_CERRADA":
                result_lexema.append(("DELIMITADOR", token.value, token.lineno))
                contador['DELIMITADOR'] += 1  
            elif token.type == "OPERADOR":
                result_lexema.append(("OPERADOR", token.value, token.lineno))
                contador['OPERADOR'] += 1  
            elif token.type == "SIMBOLO":
                result_lexema.append(("SIMBOLO", token.value, token.lineno))
                contador['SIMBOLO'] += 1  
            elif token.type == "NUMERO":
                result_lexema.append(("NUMERO", token.value, token.lineno))
                contador['NUMERO'] += 1  
        
        return render_template('index.html', tokens=result_lexema, contador=contador, expresion=expresion, mensaje_sintaxis=mensaje_sintaxis)
    
    return render_template('index.html', tokens=[], contador=contador, expresion=None, mensaje_sintaxis="")

if __name__ == '__main__':
    app.run(debug=True)

