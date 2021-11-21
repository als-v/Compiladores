import anytree
from anytree import Node
import tppparser as sintatico
from arvore import buscarNos

# funcao que gera indexes
def geraIndex(size):
    indexes = []

    for i in range(size):
        indexes.append(i)
    
    return indexes

# gera tabelas separadas de funcoes e de variaveis
def gerarTabelaSeparada(list, flag):

    if flag == 'fun':
        labels = ['NOME', 'TIPO', 'QTD PARAMETROS', 'PARÂMETROS', 'INICIADA', 'LINHA INICIAL', 'LINHA FINAL']
        table = []
        list_index = [0, 1, 2, 3, 7, 5, 6]
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
        listaIndex = geraIndex(len(labels))
        table.append(labels)

        for element in list:
            for func in list[element]:
                auxArray = []
                for index in listaIndex:
                    if index == 3:
                        valuesDimensoes = []
                        for j in range(len(func[index])):

                            try:
                                value = int(func[index][j][0])
                            except:
                                 value = float(func[index][j][0])

                            valuesDimensoes.append(value)
                        auxArray.append(valuesDimensoes)
                    else:
                        auxArray.append(func[index])
                table.append(auxArray)
    
    return table

# funcao que gera a tabelas
def gerarTabela(listaVariavel, listaFuncao):

    table = []
    labels = ['TIPO', 'NOME', 'DECLARAÇÃO', 'QTD PARAMETROS', 'PARÂMETROS', 'DECLARADA', 'DIMENSÕES', 'TAMANHO DIMENSÕES', 'ESCOPO', 'LINHA INICIAL', 'LINHA FINAL']
    list_index = [0, 1, 2, 3, 7, 5, 6]
    rangeList = len(labels)
    table.append(labels)

    for element in listaFuncao:
        for func in listaFuncao[element]:
            aux_array = []
            aux_array.append('FUNÇÃO')
            for index in list_index:
                aux_array.append(func[index])
                if index == 7:
                    for _ in range(3):
                        aux_array.append('-')
            table.append(aux_array)

    list_index = [0, 1, 2, 3, 4, 5]
    for element in listaVariavel:
        for func in listaVariavel[element]:
            aux_array = []
            aux_array.append('VARIAVEL')
            for index in list_index:
                if index != 3:
                    aux_array.append(func[index])

                if index == 1:
                    for _ in range(3):
                        aux_array.append('-')
                if index == 3:
                    tamanhoArray = []
                    for tamanho in func[index]:
                        try:
                            tamanhoArray.append(int(tamanho[0]))
                        except:
                            tamanhoArray.append(float(tamanho[0]))

                    aux_array.append(tamanhoArray)
                if index == 5:
                    aux_array.append(func[index])

            table.append(aux_array)
    
    return table

# funcao para mostrar as tabelas
def showTables(table, opt):
    labels = ''

    if opt == 'func':
        for i, row in enumerate(table):
            for idx, data in enumerate(row):
                print(str(data).ljust(15), end=' | ')
            print()

    elif opt == 'var':
        for i, row in enumerate(table):
            for idx, data in enumerate(row):
                print(str(data).ljust(18), end=' | ')
            print()

    elif opt == 'all':
        for i, row in enumerate(table):
            for idx, data in enumerate(row):
                print(str(data).ljust(17), end=' | ')
            print()

# funcao que retorna tabelas de funcoes e de variaveis
def tabelas(listaVariaveis, listaFuncoes, showTable = False):

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
    
    tabelaFuncao = gerarTabelaSeparada(listaFuncoes, 'fun')
    tabelaVariaveis = gerarTabelaSeparada(listaVariaveis, 'var')
    tabela = gerarTabela(listaVariaveis, listaFuncoes)

    if showTable:
        print('\n\nTabela:')
        showTables(tabela, 'all')
        print('\n\n')

    return tabelaFuncao, tabelaVariaveis

# retorna chamadas das funcoes 
def chamadasFuncoes(linha, listaFuncoes):
    # para cada elemento da lista de funcoes
    for elemento in listaFuncoes:
        # para cada funcao
        for funcao in listaFuncoes[elemento]:
            # volto a chamada
            if funcao[5] <= linha < funcao[6]:
                return funcao[0]

def parametrosEnviados(no, escopo, listaNos):

    for node in no.children:

        # chamada da funcao 
        if node.label == 'chamada_funcao':
            nomeFuncao = node.descendants[1].label
            tipoFuncao = listaFuncoes[nomeFuncao][0][1]
            listaNos.append((nomeFuncao, tipoFuncao))

            # retorno a lista
            return listaNos
        
        # ID 
        elif node.label == 'ID':
            nomeVariavel = node.children[0].label
            tipoVariavel = ''

            if nomeVariavel in listaVariaveis:
                for variavel in listaVariaveis[nomeVariavel]:
                    if variavel[4] == escopo:
                        tipoVariavel = variavel[1]
                        break

                if tipoVariavel == '':
                    for variavel in listaVariaveis[nomeVariavel]:
                        if variavel[4] == 'global':
                            tipoVariavel = variavel[1]
                            break

                listaNos.append((nomeVariavel, tipoVariavel))

                # retorno a lista
                return listaNos

        # numero 
        elif node.label == 'numero':
            tipoNumerico = node.children[0].label
            
            # inteiro
            if tipoNumerico == 'NUM_INTEIRO':
                numero = int(node.descendants[1].label)
                tipoNumerico = 'inteiro'
            
            # flutuante
            else:
                tipoNumerico = 'flutuante'
                numero = float(node.descendants[1].label)

            listaNos.append((numero, tipoNumerico))

            # retorno a lista
            return listaNos

        listaNos = parametrosEnviados(node, escopo, listaNos)
    
    # retorno a lista
    return listaNos

def buscarNosRoot(no, label, listaNos):
    # passo por todos e se o label for igual, adiciono na lista
    for idx in range(len(no.anchestors)-1, -1, -1):
        if no.anchestors[idx].label == label:
            listaNos.append(no.anchestors[idx])

    # retorna lista
    return listaNos

# funcao para verificar todas os possiveis erros
def regrasSemanticas(tree, listaFuncoes, listaVariaveis, listaErros, tabelaFuncao, tabelaVariaveis):
    semanticaFuncaoPrincipal(listaFuncoes, listaErros)
    semanticaRetornoFuncoes(listaFuncoes, listaErros)
    semanticaChamadasFuncoes(listaFuncoes, listaErros)
    semanticaChamadasVariaveis(listaVariaveis, listaErros, tree)
    semanticaTiposAtribuicoes(listaErros, tree)
    semanticaArranjos(listaVariaveis, listaErros)
    showErros(listaErros)

def showErros(listaErros):
    erros = []
    
    if len(listaErros) > 0:
        for tuplaErros in listaErros:
            if tuplaErros not in erros:
                erros.append(tuplaErros)
    
    init = True
    if len(erros) > 0:
        for idx, erro in enumerate(erros):
            if erro[0] == 'ERROR':
                if init: 
                    print('\nERROS:')
                    init = False
                print(erro[1])

    init = True
    if len(erros) > 0:
        for idx, erro in enumerate(erros):
            if erro[0] == 'WARNING':
                if init: 
                    print('\nWARNINGS:')
                    init = False
                print(erro[1])

def semanticaArranjos(listaVariaveis, message_list):

    # para cada um dos elementos da lista de variaveis
    for elemento in listaVariaveis:

        # para cada uma das variaveis
        for variavel in listaVariaveis[elemento]:

            # caso tenha dimensoes
            if variavel[2] != 0:

                # para cada uma das dimensoes
                for dimension in variavel[3]:
                    
                    # quantidade de dimensoes
                    dimension_number = 0

                    # se nao for inteiro
                    if dimension[1] != 'NUM_INTEIRO':
                        dimension_number = float(dimension[0])
                        message = ('ERROR', 'Erro: Índice de array “'+ str(variavel[0]) + '” não inteiro')
                        message_list.append(message)

                    else:
                        dimension_number = int(dimension[0])

                # para cada no
                for no in variavel[-1]:
                    numero = buscarNos(no[1].descendants[3], 'numero', [])

                    if len(numero) > 0:
                        # caso seja flutuante
                        if len(buscarNos(numero[0], 'NUM_PONTO_FLUTUANTE', [])) > 0:
                            message = ('ERROR', 'Erro: Índice de array “' + str(variavel[0]) + '” não inteiro')
                            message_list.append(message)
                        
                        else:
                            numero = int(numero[0].descendants[-1].label)

                            # caso esteja fora do intervalo
                            if numero > dimension_number - 1:
                                message = ('ERROR', 'Erro: Índice de array “' + str(variavel[0]) + '” fora do intervalo (out of range)')
                                message_list.append(message)

def semanticaTiposAtribuicoes(listaErros, tree):
    
    # pego todos os nos de atribuicao
    nosAtribuicao = buscarNos(tree, 'atribuicao', [])

    # para cada um dos nos
    for idx in range(len(nosAtribuicao)):

        # buscar o escopo da variavel
        try:
            escope_read = buscarNosRoot(nosAtribuicao[idx], 'cabecalho', [])[0].descendants[1].label
        except:
            escope_read = 'global'

        nosDireita = parametrosEnviados(nosAtribuicao[idx], escope_read, [])
        nosEsquerda = nosDireita.pop(0)

        # variavel de controle para o tipo da variavel 
        diffVar = False

        # para cada variavel 
        for varDireita in nosDireita:

            # coercao implícita
            if varDireita[1] != nosEsquerda[1] and varDireita[1] != '':
                diffVar = [varDireita[0], varDireita[1]]
                isValue = True

                try:
                    valor = int(varDireita[0])
                except:
                    isValue = False

                if isValue:
                    message = ('WARNING', 'Aviso: Coerção implícita do valor atribuído para “' + str(nosEsquerda[0]) + '”')
                else:
                    message = ('WARNING', 'Aviso: Coerção implícita do valor retornado por “' + str(varDireita[0]) + '”')
                
                listaErros.append(message)

        if diffVar and diffVar != nosEsquerda[1]:
            message = ('WARNING', 'Aviso: Atribuição de tipos distintos “' + str(nosEsquerda[0]) + '” ' + str(nosEsquerda[1]) + ' e “' + str(diffVar[0]) + '” ' + str(diffVar[1]))
            listaErros.append(message)

def semanticaChamadasVariaveis(listaVariaveis, listaErros, tree):
    # busco os nos que sao das funcoes leia()
    nos = buscarNos(tree, 'LEIA', [])

    # para cada um deles
    for idx in range(len(nos)):

        # pego o no
        nos[idx] = nos[idx].anchestors[-1]

        # o escopo do no
        escopo = buscarNosRoot(nos[idx], 'cabecalho', [])[0].descendants[1].label

        # o id
        idNo = buscarNos(nos[idx], 'ID', [])[0].children[0].label

        # para cada variavel
        if idNo in listaVariaveis[idNo][0][0]:
            for variavel in listaVariaveis[idNo]:
                found = False

                # caso a variavel esteja no escopo
                if variavel[4] == escopo:
                    found = True

                    # vejo se ja foi inicializada
                    if len(variavel[-1]) == 0:
                        message = ('WARNING', 'Aviso: Variável “' + str(idNo) + '” declarada e não utilizada')
                        listaErros.append(message)

                # caso nao esteja
                if not found:

                    # vejo se ela esta no escopo global
                    for variavelIdx in listaVariaveis[idNo]:
                        if variavelIdx[4] == 'global':

                            # vejo se ja foi inicializada
                            if len(variavelIdx[-1]) == 0:
                                message = ('WARNING', 'Aviso: Variável “' + str(idNo) + '” declarada e não utilizada')
                                listaErros.append(message)

    # para cada elemento da lista de variaveis
    for elemento in listaVariaveis:

        # para cada variavel
        for variavel in listaVariaveis[elemento]:

            # caso ela nao tenha sido inicializada
            if len(variavel[-1]) == 0:
                message = ('WARNING', 'Aviso: Variável “' + str(variavel[0]) + '” declarada e não utilizada')
                listaErros.append(message)

            # caso ja tenha sido declarada anteriormente
            if len(listaVariaveis[elemento]) > 1:
                for variavelAgn in listaVariaveis[elemento]:
                    if variavelAgn != variavel and variavelAgn[4] == variavel[4]:
                        message = ('WARNING', 'Aviso: Variável “' + str(variavelAgn[0]) + '” já declarada anteriormente')
                        listaErros.append(message)

# funcao que verifica a semantica das chamadas de funcoes
def semanticaChamadasFuncoes(listaFuncoes, listaErros):
    # mensagem de ERROR/WARNING
    mensagem = ''

    # por cada um dos elementos da lista de funcoes
    for elemento in listaFuncoes:

        # pra cada uma das funcoes
        for funcao in listaFuncoes[elemento]:

            # funcao nao declarada
            if not funcao[-2]:
                mensagem = ('ERROR', 'Erro: Chamada a função “' + str(elemento) + '” que não foi declarada')
                listaErros.append(mensagem)

            else:

                # caso a funcao tenha sido declarada, mas nao utilizada
                if len(funcao[-1]) == 0 and elemento != 'principal':
                    mensagem = ('WARNING', 'Aviso: Função “' + str(elemento) + '” declarada, mas não utilizada')
                    listaErros.append(mensagem)

                else:
                    # variaveis de controle para chamadas e para recursão 
                    chamadas = 0
                    recursao = 0

                    # para cada uma das chamadas da funcao 
                    for cahamdaFuncao in funcao[-1]:
                        if chamadasFuncoes(cahamdaFuncao[0], listaFuncoes) != elemento:
                            chamadas += 1
                        else:
                            recursao += 1

                    # caso seja a funcao principal, não conto
                    if chamadas == 0 and elemento != 'principal':
                        mensagem = ('WARNING', 'Aviso: Função “' + str(elemento) + '” declarada, mas não utilizada')
                        listaErros.append(mensagem)

                    # caso tenha recursão
                    elif recursao > 0:
                        mensagem = ('WARNING', 'Aviso: Chamada recursiva para “' + str(elemento) + '”')
                        listaErros.append(mensagem)

                # para cada chamada da funcao 
                for chamada in funcao[-1]:
                    
                    # a lista dos parametros
                    listaParametros = parametrosEnviados(chamada[1].children[2], funcao[0], list())

                    # caso seja maior que os parametros que a funcao recebe 
                    if len(listaParametros) > funcao[2]:
                        mensagem = ('ERROR', 'Erro: Chamada à função “' + str(funcao[0]) + '” com número de parâmetros maior que o declarado')
                        listaErros.append(mensagem)
                    
                    # caso seja menor que os parametros que a funcao recebe
                    elif len(listaParametros) < funcao[2]:
                        mensagem = ('ERROR', 'Erro: Chamada à função “' + str(funcao[0]) + '” com número de parâmetros menor que o declarado')
                        listaErros.append(mensagem)

                    else:

                        # lista auxiliar para os parametros
                        parametros = []

                        # para cada uma das funcoes
                        for func in listaFuncoes[chamada[1].descendants[1].label]:

                            # para cada um das variaveis da funcao
                            for varFuncao in func[3]:

                                # adiciono na lista auxiliar de parametros
                                for index in range(len(listaVariaveis[varFuncao])):
                                    if listaVariaveis[varFuncao][index][4] == chamada[1].descendants[1].label:
                                        parametros.append((listaVariaveis[varFuncao][index][0], listaVariaveis[varFuncao][index][1]))
                                        break

                        # para cada um deles 
                        for idx in range(len(parametros)):
                            
                            # index do tipo da variavel
                            tipoIdx = listaParametros[idx][1]

                            # flutuante
                            if tipoIdx == 'NUM_PONTO_FLUTUANTE':
                                tipoIdx = 'flutuante'
                            
                            # inteiro
                            else:
                                tipoIdx = 'inteiro'
                            
                            # caso o tipo dele seja diferente do tipo da variavel
                            if parametros[idx][1] != tipoIdx:
                                mensagem = ('WARNING', 'Aviso: Coerção implícita do valor passado para váriavel “' + str(parametros[idx][0]) + '” da função “' + str(chamada[1].descendants[1].label) + '”')
                                listaErros.append(mensagem)

# funcao que verifica a semantica do retorno das funcoes 
def semanticaRetornoFuncoes(listaFuncoes, listaErros):
    mensagem = ''

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
                        mensagem = ('ERROR', 'Erro: Função “' + str(nomeFuncao) + '” deveria retornar vazio, mas retorna: ' + str(tiposRetorno[0]) + ' e ' + str(tiposRetorno[1]))
                    else:
                        mensagem = ('ERROR', 'Erro: Função “' + str(nomeFuncao) + '” deveria retornar vazio, mas retorna ' + str(tiposRetorno[0]))
            elif tipoFuncao == 'inteiro':
                if len(tiposRetorno) == 0:
                    mensagem = ('ERROR', 'Erro: Função “' + str(nomeFuncao) + '” deveria retornar inteiro, mas retorna vazio')
                else:
                    for tipoRetorno in tiposRetorno:
                        if tipoRetorno != 'inteiro' and tipoRetorno != 'ERROR':
                            mensagem = ('ERROR', 'Erro: Função “' + str(nomeFuncao) + '” deveria retornar inteiro, mas retorna flutuante')
                            break
            elif tipoFuncao == 'flutuante':
                if len(tiposRetorno) == 0:
                    mensagem = ('ERROR', 'Erro: Função “' + str(nomeFuncao) + '” deveria retornar flutuante, mas retorna vazio')
                else:
                    for tipoRetorno in tiposRetorno:
                        if tipoRetorno != 'flutuante' and tipoRetorno != 'ERROR':
                            mensagem = ('ERROR', 'Erro: Função “' + str(nomeFuncao) + '” deveria retornar flutuante, mas retorna inteiro')
                            break

            if mensagem != '':
                listaErros.append(mensagem)

# funcao que verifica a semantica da funcao principal
def semanticaFuncaoPrincipal(listaFuncoes, listaErros):
    # caso nao exista a funcao principal
    if 'principal' not in listaFuncoes or not listaFuncoes['principal'][0][7]:
        listaErros.append(('ERROR', 'Erro: Função principal não declarada'))
    
    # caso exista funcao principal
    else:

        # para todas as funcoes
        for funcoes in listaFuncoes['principal'][0][-1]:
            
            # caso a funcao principal tenha sido chamada dentro de outra funcao
            if not listaFuncoes['principal'][0][5] <= funcoes[0] < listaFuncoes['principal'][0][6]:
                listaErros.append(('ERROR', 'Erro: Chamada para a função principal não permitida'))
    
def main(file, detailed = False, showTree = False, showTable = False):
    global tree, listaFuncoes, listaVariaveis, listaErros

    tree, listaFuncoes, listaVariaveis, listaErros, success = sintatico.main(file, d = detailed, showTree = showTree)

    if success:
        tabelaFuncao, tabelaVariaveis = tabelas(listaVariaveis, listaFuncoes, showTable)
        regrasSemanticas(tree, listaFuncoes, listaVariaveis, listaErros, tabelaFuncao, tabelaVariaveis)
        
        return tree

    return None