###             ARVORE.PY               ###
#
#  Este arquivo contem todas as funcoes   #
#  referentes ao processamento da arvore  #
#
###                                     ###

# definicoes das labels dos operadores
operadores = [
    '+', 
    '-', 
    '*', 
    '/', 
    ':=', 
    ':'
]

# definicoes dos labels dos nos
labels = [
    'ID', 
    'var', 
    'lista_variaveis', 
    'dois_pontos', 
    'tipo',
    'INTEIRO', 
    'FLUTUANTE', 
    'NUM_INTEIRO', 
    'NUM_PONTO_FLUTUANTE',
    'NUM_NOTACAO_CIENTIFICA', 
    'LEIA', 
    'abre_parentese', 
    'fecha_parentese',
    'lista_declaracoes', 
    'declaracao', 
    'indice', 
    'numero', 
    'fator',
    'abre_colchete', 
    'fecha_colchete', 
    'expressao', 
    'expressao_logica',
    'expressao_simples', 
    'expressao_aditiva', 
    'expressao_multiplicativa',
    'expressao_unaria', 
    'inicializacao_variaveis', 
    'ATRIBUICAO', 
    'atribuicao',
    'operador_soma', 
    'mais', 
    'chamada_funcao', 
    'lista_argumentos', 
    'VIRGULA',
    'virgula', 
    'fator', 
    'cabecalho', 
    'FIM', 
    'lista_parametros', 
    'vazio',
    '(', 
    ')', 
    ':', 
    ',', 
    'RETORNA', 
    'ESCREVA', 
    'SE', 
    'ENTAO', 
    'SENAO', 
    'MAIOR',
    'MENOR', 
    'REPITA', 
    'IGUAL', 
    'menos', 
    'MENOR_IGUAL', 
    'MAIOR_IGUAL', 
    'operador_logico',
    'operador_multiplicacao', 
    'MULTIPLICACAO', 
    'vezes',
    'ABRE_PARENTESE',
    'FECHA_PARENTESE',
    'MAIS',
    'MENOS'
]

def buscarNos(tree, label, listaNos):
    # para cada um dos nos
    for no in tree.children:
        # realizo a busca
        listaNos = buscarNos(no, label, listaNos)

        # caso for igual a label
        if no.label == label:
            listaNos.append(no)

    # retorna a lista
    return listaNos

# funcao para poda no
def podaNo(tree):
    auxiliar = []
    noPai = tree.parent
    tamNoPai = len(noPai.children)

    for i in range(tamNoPai):
        # print('Olha aqui: ', noPai.children[i].label)

        # caso o pai tenha um filho que seja igual ao no atual
        if (noPai.children[i].name == arvore.name):
            auxiliar += arvore.children
        else:
            auxiliar.append(noPai.children[i])

    noPai.children = auxiliar

# funcao que realiza a poda na arvore
def podaArvore(tree):

    # para cada um dos nos
    for no in tree.children:
        podaArvore(no)

    # caso encontre uma label a remover
    if tree.label in labels:

        # pego o pai do no
        noPai = tree.parent
        auxiliar = []

        # para cada um dos filhos do pai
        for noFilho in noPai.children:

            # caso o filho seja diferente do no atual
            if noFilho != tree:
                auxiliar.append(noFilho)

        # para cada um dos filhos do no
        for noFilho in tree.children:
            auxiliar.append(noFilho)
        
        # atualizo os filhos
        tree.children = auxiliar
        noPai.children = auxiliar

    # caso: declaracao_funcao
    if tree.label == 'declaracao_funcao':

        # e se nao for um error
        if 'ERROR' not in tree.children[0].label:
            valor = tree.children[1]
            auxiliar = []

            # para cada um dos filhos do no
            for noFilho in tree.children:

                # caso: fim
                if noFilho.label == 'fim':
                    auxiliar.append(valor)
                
                # caso o noFilho seja diferente do valor atual
                if noFilho != valor:
                    auxiliar.append(noFilho)
            
            # atualizo o no
            tree.children = auxiliar

    # caso: corpo
    if tree.label == 'corpo':

        # se nao tiver mais algum no
        if len(tree.children) == 0:

            # pego o pai do no
            noPai = tree.parent
            auxiliar = []

            # para cada um dos filhos do pai
            for noFilho in noPai.children:

                # caso o filho seja diferente do no atual
                if noFilho != tree:
                    auxiliar.append(noFilho)
            
            # para cada um dos filhos do no
            for noFilho in tree.children:
                auxiliar.append(noFilho)

            # atualizo os filhos
            tree.children = auxiliar
            noPai.children = auxiliar

def labelsAjuste(tree):

    # percorrer a arvore
    for no in tree.children:
        labelsAjuste(no)

    # pego o pais do no
    noPai = tree.parent
    auxiliarRepita = []

    # caso: repita
    if tree.label == 'repita':

        # se tiver algum no
        if len(tree.children) > 0:

            # para cada um dos filhos do no
            for noFilho in tree.children:

                # se for diferente de repita
                if noFilho.label != 'repita':
                    auxiliarRepita.append(noFilho)

            # atualizo os filhos
            tree.children = auxiliarRepita

    auxiliarSe = []

    # caso: se
    if tree.label == 'se':

        # se tiver algum no
        if len(tree.children) > 0:

            # para cada um dos filhos do no
            for noFilho in tree.children:

                # se for diferente de se
                if noFilho.label != 'se':
                    auxiliarSe.append(noFilho)

        # atualizo os filhos
        tree.children = auxiliarSe
    
    auxiliar = []

    # caso: leia, escreva ou retorna
    if tree.label == 'leia' or tree.label == 'escreva' or tree.label == 'retorna':
        
        # se nao tiver nenhum filho
        if len(tree.children) == 0:

            # pego o pai do no
            for noFilho in noPai.children:

                # se for diferente do no atual
                if noFilho != tree:
                    auxiliar.append(noFilho)

            # atualizo o valor
            noPai.children = auxiliar
    
    zerarFilhos = False
    # alteracoes nas labels
    if tree.label == 'ATE':
        tree.label, tree.name = 'até', 'até'
        zerarFilhos = True

    if tree.label == 'e' and tree.children[0].label == '&&':
        tree.label, tree.name = '&&', '&&'
        zerarFilhos = True

    if tree.label == 'ou' and tree.children[0].label == '||':
        tree.label, tree.name = '||', '||'
        zerarFilhos = True
    
    if zerarFilhos:
        tree.children = []

def alteracoesArvore(tree):
    podaArvore(tree)
    labelsAjuste(tree)