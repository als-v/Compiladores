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
    'operador_soma',
    'MAIS',
    'virgula',
    'VIRGULA',
    ',',
    'ESCREVA',
    'SE',
    'MAIOR',
    'ENTAO',
    'então',
    'REPITA',
    'ATE',
    'IGUAL',
    'LEIA',
    'SENAO',
    'senão',
]

def remove(no):

    # pego o pai do no
    pai = no.parent

    # var auxiliar
    aux = []

    # para cada um dos filhos do pai
    for i in range(len(pai.children)):

        # se o filho for o no que quero remover
        if (pai.children[i].name == no.name):
            aux += no.children

        # se nao, adiciono a lista auxiliar
        else:
            aux.append(pai.children[i])

    # adiciono a lista auxiliar ao pai
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
        remove(root)
    
    # remove caso não tenha nenhum filho
    if root.name == 'corpo' or root.name == 'retorna' or root.name == 'escreva' or root.name == 'se' or root.name == 'repita' or root.name == 'até' or root.name == 'leia':
        if len(root.children) == 0:
            remove(root)
