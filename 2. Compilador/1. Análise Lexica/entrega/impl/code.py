import logging
import ply.lex as lex
from ply.lex import TOKEN
from sys import argv, exit

# configurações de log
logging.basicConfig(
     level = logging.DEBUG,
     filename = "log.txt",
     filemode = "w",
     format = "%(filename)10s:%(lineno)4d:%(message)s"
)

log = logging.getLogger()

# lista dos tokens
tokens = [
    "ID",                       # identificador
    
    # numerais
    "NUM_NOTACAO_CIENTIFICA",   # ponto flutuante em notaçao científica
    "NUM_PONTO_FLUTUANTE",      # ponto flutuante
    "NUM_INTEIRO",              # inteiro
    # operadores binarios
    "MAIS",                     # +
    "MENOS",                    # -
    "MULTIPLICACAO",            # *
    "DIVISAO",                  # /
    "E_LOGICO",                 # &&
    "OU_LOGICO",                # ||
    "DIFERENCA",                # <>
    "MENOR_IGUAL",              # <=
    "MAIOR_IGUAL",              # >=
    "MENOR",                    # <
    "MAIOR",                    # >
    "IGUAL",                    # =
    
    # operadores unarios
    "NEGACAO",                  # !
    
    # simbolos
    "ABRE_PARENTESE",           # (
    "FECHA_PARENTESE",          # )
    "ABRE_COLCHETE",            # [
    "FECHA_COLCHETE",           # ]
    "VIRGULA",                  # ,
    "DOIS_PONTOS",              # :
    "ATRIBUICAO",               # :=

    # 'COMENTARIO', # {***}
]

# lista das palavras reservadas
reserved_words = {
    "se":           "SE",
    "então":        "ENTAO",
    "senão":        "SENAO",
    "fim":          "FIM",
    "repita":       "REPITA",
    "flutuante":    "FLUTUANTE",
    "retorna":      "RETORNA",
    "até":          "ATE",
    "leia":         "LEIA",
    "escreva":      "ESCREVA",
    "inteiro":      "INTEIRO",
}

# uniao dos tokens com as palavras reservadas
tokens = tokens + list(reserved_words.values())

## definição das expressões regulares complexas
digito = r'([0-9])'

letra = r'([a-zA-ZáÁãÃàÀéÉíÍóÓõÕ])'

sinal = r'([\-\+]?)'

# id deve começar com uma letra
id = r"(" + letra + r"(" + digito + r"+|_|" + letra + r")*)"
#id = r'((letra)(letra|_|([0-9]))*)'
#id = r'(([a-zA-ZáÁãÃàÀéÉíÍóÓõÕ])(([0-9])+|_|([a-zA-ZáÁãÃàÀéÉíÍóÓõÕ]))*)'

inteiro = r"\d+"
# inteiro = r"(" + sinal + digito + r"+)"
# inteiro = r"(" + digito + r"+)"

flutuante = r'\d+[eE][-+]?\d+|(\.\d+|\d+\.\d*)([eE][-+]?\d+)?'
# flutuante = r'(' + digito + r'+\.' + digito + r'+?)'
# flutuante = r'(([-\+]?)([0-9]+)\.([0-9]+))'
# flutuante = r'[-+]?[0-9]+(\.([0-9]+)?)'
# flutuante = r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'

notacao_cientifica = r'(' + sinal + r'([1-9])\.' + digito + r'+[eE]' + sinal + digito + r'+)'
# notacao_cientifica = r'(([-\+]?)([1-9])\.([0-9])+[eE]([-\+]?)([0-9]+))'

comentario = r'(\{((.|\n)*?)\})'
nova_linha = r'\n+'
 
## definição das expressões regulares simples

# simbolos
t_MAIS =            r'\+'
t_MENOS =           r'-'
t_MULTIPLICACAO =   r'\*'
t_DIVISAO =         r'/'
t_ABRE_PARENTESE =  r'\('
t_FECHA_PARENTESE = r'\)'
t_ABRE_COLCHETE =   r'\['
t_FECHA_COLCHETE =  r'\]'
t_VIRGULA =         r','
t_ATRIBUICAO =      r':='
t_DOIS_PONTOS =     r':'

# operadores logicos
t_E_LOGICO =    r'&&'
t_OU_LOGICO =   r'\|\|'
t_NEGACAO =     r'!'

# operadores relacionais
t_DIFERENCA =   r'<>'
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_MENOR =       r'<'
t_MAIOR =       r'>'
t_IGUAL =       r'='

t_ignore = " \t"

@TOKEN(id)
def t_ID(token):

    # não é necessário fazer regras/regex para cada palavra reservada se o token não for uma palavra reservada automaticamente é um id as palavras reservadas têm precedências sobre os ids
    token.type = reserved_words.get(token.value, 'ID')  

    return token

@TOKEN(notacao_cientifica)
def t_NUM_NOTACAO_CIENTIFICA(token):

    return token

@TOKEN(flutuante)
def t_NUM_PONTO_FLUTUANTE(token):

    return token

@TOKEN(inteiro)
def t_NUM_INTEIRO(token):

    return token

@TOKEN(comentario)
def t_COMENTARIO(token):
    
    # para poder contar as quebras de linha dentro dos comentarios
    token.lexer.lineno += token.value.count("\n")
    
    # não a necessidade de retornar o token

@TOKEN(nova_linha)
def t_NEWLINE(token):
    
    # para pular as linhas referentes ao valor
    token.lexer.lineno += len(token.value)

    # não a necessidade de retornar o token

# tratamento de erros
def t_error(token):

    # variaveis para controle
    global error, detailed, arq

    error = True

    if detailed:
        print(
            'Foi encontrado um caracter inválido: "{}", na linha: {} e na coluna {}'
            .format(token.value, token.lineno, token.lexpos)
        )

        arq.write('Foi encontrado um caracter inválido: "{}", na linha: {} e na coluna {}'.format(token.value, token.lineno, token.lexpos))
    
    else:
        print("Caracter inválido '{}'".format(token.value[0]))
        arq.write("Caracter inválido '{}'".format(token.value[0]))

    # pulo o erro
    token.lexer.skip(1)

def main():

    # flag para mostrar se deu erro ou se a saída deve ser detalhada 
    global error, detailed, arq

    error, detailed = False, False
    
    # pegar o nome do arquivo
    try:
        aux = argv[1].split('.')
    except:
        print('Arquivo inválido!')
        return

    if aux[-1] != 'tpp':
        print('O arquivo selecionado não tem a extensao .tpp!')
        return
    
    # verificação da flag
    if len(argv) == 3:
        if argv[2] == 'd':
            detailed = True

    # abrir o arquivo
    data = open(argv[1])
    source_file = data.read()

    # construir a instancia do lexer
    lexer = lex.lex(optimize=True, debug=True, debuglog=log)
    lexer.input(source_file)
    
    arq = open('saida.txt', 'w')

    while True:

        # pegar os tokens
        tok = lexer.token()

        # No more input
        if not tok: 
            break

        if detailed:
            print(tok)
            arq.write(str(tok) + '\n')
        else:
            print(tok.type)
            arq.write(str(tok.type) + '\n')

    arq.close()

if __name__ == "__main__":
    main()
