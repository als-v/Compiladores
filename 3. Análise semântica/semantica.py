import anytree
from anytree import Node
import tppparser as sintatico
from tabulate import tabulate
import numpy as np

# definicoes dos operadores
operadores = [
    '+', 
    '-', 
    '*', 
    '/', 
    ':=', 
    ':'
]

# definicoes das definicoes operadores
operadores_definicao = [
    'operador_soma',
    'operador_multiplicacao'
]

# definicoes dos nomes
nomes = [
    'acao', 
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
    'lista_variaveis'
]

# funcao para poda no
def podaNo(tree):
    aux = []
    pai = tree.parent

    for i in range(len(pai.children)):
        if (pai.children[i].name == arvore.name):
            aux += arvore.children
        else:
            aux.append(pai.children[i])

    pai.children = aux

# funcao para poda operadores
def podaOperadores(tree):
    aux = []
    print('poda operadores: ', tree.name)
    print(tree.children)
    if tree.parent.name in operadores_definicao:
        podaNo(tree.parent)
    
    pai = tree.parent
    aux = [pai.children[0], pai.children[2]] 
    tree.children = aux
    pai.children = [tree]

# funcao que realiza a poda na arvore
def podaArvore(tree):
    # print('poda arvore: ', tree.name)

    for no in tree.children:
        podaArvore(no)
    
    if tree.name in operadores:
        podaOperadores(tree)
    
    if (tree.name in nomes) and tree.parent.name == tree.name:
        print('caiu aqui')
        podaNo(tree)

# funcao que gera indexes
def geraIndex(size):
    indexes = []

    for i in range(size):
        indexes.append(i)
    
    return indexes

# funcao que gera as tabelas de funcoes e de variaveis
def gerarTabela(list, flag):

    if flag == 'fun':
        labels = ['NOME', 'TIPO', 'QUANTIDADE', 'PARAMETROS', 'PARÂMETROS', 'INICIO', 'LINHA INICIAL', 'LINHA FINAL']
        table = []
        list_index = geraIndex(len(labels))
        table.append(labels)

        for element in list:
            for func in list[element]:
                aux_array = []
                for index in list_index:
                    aux_array.append(func[index])
                table.append(aux_array)
    elif flag == 'var':
        labels = ['NOME', 'TIPO', 'DIMENSÕES', 'TAMANHO DIMENSÕES', 'ESCOPO', 'LINHA']
        table = []
        list_index = geraIndex(len(labels))
        table.append(labels)

        for element in list:
            for func in list[element]:
                aux_array = []
                for index in list_index:
                    if index == 3:
                        dim_tam = []
                        for j in range(len(func[index])):
                            if func[index][j][1] == 'NUM_PONTO_FLUTUANTE':
                                value = float(func[index][j][0])
                            else:
                                value = int(func[index][j][0])
                            dim_tam.append(value)
                        aux_array.append(dim_tam)
                    else:
                        aux_array.append(func[index])
                table.append(aux_array)
    
    return table

# funcao para mostrar as tabelas
def showTable(table, opt):
    labels = ''

    if opt == 'func':
        for i, row in enumerate(table):
            for idx, data in enumerate(row):
                print(str(data).ljust(16), end=' | ')
            print()

    elif opt == 'var':
        for i, row in enumerate(table):
            for idx, data in enumerate(row):
                print(str(data).ljust(18), end=' | ')
            print()

# funcao que retorna tabelas de funcoes e de variaveis
def tabelas(listaVariaveis, listaFuncoes):
    # para cada variavel
    for variavel in listaVariaveis:
        # index da variavel
        for variavelIdx in range(len(listaVariaveis[variavel])):
            # escopo da variavel
            variavelEscopo = listaVariaveis[variavel][variavelIdx][4]

            # caso a variavel nao esteja no escopo global
            if 'global' not in variavelEscopo:
                # qtd de vezes que foi chamada
                chamadasQtd = len(listaVariaveis[variavel][variavelIdx][-1])
                chamadasIdx = 0

                # para cada uma das vezes
                while chamadasIdx < chamadasQtd:
                    chamadas = listaVariaveis[variavel][variavelIdx][-1][chamadasIdx]
                    
                    # caso a variavel tenha sido chamada em outro escopo
                    if not listaFuncoes[variavelEscopo][0][5] <= chamadas[0] < listaFuncoes[variavelEscopo][0][6]:
                        listaVariaveis[variavel][variavelIdx][-1].pop(chamadasIdx)
                        chamadasQtd -= 1
                        chamadasIdx -= 1

                    chamadasIdx += 1
    
    tabelaFuncao = gerarTabela(listaFuncoes, 'fun')
    tabelaVariaveis = gerarTabela(listaVariaveis, 'var')

    print('Tabela de funções:')
    showTable(tabelaFuncao, 'func')
    print('\n\nTabela de variaveis:')
    showTable(tabelaVariaveis, 'var')
    print('\n\n')

    return tabelaFuncao, tabelaVariaveis

# funcao para verificar todas os possiveis erros
def regrasSemanticas(tree, listaFuncoes, listaVariaveis, listaErros, tabelaFuncao, tabelaVariaveis):
    semanticaFuncaoPrincipal(listaFuncoes, listaErros)
    semanticaRetornoFuncoes(listaFuncoes, listaErros)
    print(listaErros)

# funcao que verifica a semantica do retorno das funcoes
def semanticaRetornoFuncoes(listaFuncoes, message_list):
    message = ''

    for nomeFuncao in listaFuncoes:
        for funcao in listaFuncoes[nomeFuncao]:
            tipoFuncao = funcao[1]

            tiposRetorno = []
            for tipoRetorno in funcao[4]:
                tiposRetorno.append(tipoRetorno[0])

            tiposRetorno = list(set(tiposRetorno))

            if tipoFuncao == 'vazio':
                if len(tiposRetorno) > 0:
                    if len(tiposRetorno) > 1:
                        message = ('ERROR', f'Erro: Função ' + str(nomeFuncao) + ' deveria retornar vazio, mas retorna: ' + str(tiposRetorno[0]) + ' e ' + str(tiposRetorno[1]) + '.')
                    else:
                        message = ('ERROR', 'Erro: Função ' + str(nomeFuncao) + ' deveria retornar vazio, mas retorna ' + str(tiposRetorno[0]) + '.')
            elif tipoFuncao == 'inteiro':
                if len(tiposRetorno) == 0:
                    message = ('ERROR', 'Erro: Função ' + str(nomeFuncao) + ' deveria retornar inteiro, mas retorna vazio.')
                else:
                    for tipoRetorno in tiposRetorno:
                        if tipoRetorno != 'inteiro' and tipoRetorno != 'ERROR':
                            message = ('ERROR', 'Erro: Função ' + str(nomeFuncao) + ' deveria retornar inteiro, mas retorna flutuante.')
                            break
            elif tipoFuncao == 'flutuante':
                if len(tiposRetorno) == 0:
                    message = ('ERROR', 'Erro: Função ' + str(nomeFuncao) + ' deveria retornar flutuante, mas retorna vazio.')
                else:
                    for tipoRetorno in tiposRetorno:
                        if tipoRetorno != 'flutuante' and tipoRetorno != 'ERROR':
                            message = ('ERROR', 'Erro: Função ' + str(nomeFuncao) + ' deveria retornar flutuante, mas retorna inteiro.')
                            break

            if message != '':
                message_list.append(message)

# funcao que verifica a semantica da funcao principal
def semanticaFuncaoPrincipal(listaFuncoes, listaErros):
    # caso nao exista a funcao principal
    if 'principal' not in listaFuncoes or not listaFuncoes['principal'][0][7]:
        listaErros.append(('ERROR', f'Erro: Função principal não declarada.'))
    
    # caso exista funcao principal
    else:

        # para todas as funcoes
        for funcoes in listaFuncoes['principal'][0][-1]:
            
            # caso a funcao principal tenha sido chamada dentro de outra funcao
            if not listaFuncoes['principal'][0][5] <= funcoes[0] < listaFuncoes['principal'][0][6]:
                listaErros.append(('ERROR', f'Erro: Chamada para a função principal não permitida.'))
    
def main(file):
    global tree, listaFuncoes, listaVariaveis, listaErros

    tree, listaFuncoes, listaVariaveis, listaErros = sintatico.main(file)

    tabelaFuncao, tabelaVariaveis = tabelas(listaVariaveis, listaFuncoes)

    regrasSemanticas(tree, listaFuncoes, listaVariaveis, listaErros, tabelaFuncao, tabelaVariaveis)
    # podaArvore(tree)
    return None

if __name__ == "__main__":
    main()