nosRemove = [
    'ID',
    'id',
    'ABRE_PARENTESE',
    'FECHA_PARENTESE',
    'lista_parametros',
    'var',
    ':',
    'tipo',
    'INTEIRO',
    'FLUTUANTE',
    'ATRIBUICAO',
    'dois_pontos',
    'FIM',
    'RETORNA',
    'numero',
    'NUM_INTEIRO',
    'NUM_PONTO_FLUTUANTE',
    'cabecalho',
    '(',
    ')',
    'vazio',
    'declaracao',
    'lista_declaracoes',
    'atribuicao',
    'expressao',
    'expressao_logica',
    'expressao_simples',
    'expressao_aditiva',
    'expressao_multiplicativa',
    'expressao_unaria',
    'operador_relacional',
    'operador_logico',
    'operador_negacao',
    'fator',
    'lista_variaveis',
    'abre_colchete',
    'fecha_colchete',
    'indice',
    'chamada_funcao',
    'lista_argumentos',
]

def noRemove(arvore):
    pai = arvore.parent
    aux = []

    for i in range(len(pai.children)):
        if (pai.children[i].name == arvore.name):
            aux += arvore.children
        else:
            aux.append(pai.children[i])

    pai.children = aux

def poda(root):
    podaAux(root)
    return root

def podaAux(root):
    
    # para cada um dos nos
    for no in root.children:
        poda(no)

    # remove o no
    if root.name in nosRemove:
        noRemove(root)
    
    # remove caso não tenha nenhum filho
    if root.name == 'corpo' or root.name == 'retorna':
        if len(root.children) == 0:
            noRemove(root)
