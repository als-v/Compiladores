import pandas as pd

def getColunmValue(data, line, column):
    # retorno os valores de uma linha na coluna especificada
    return data.loc[(data['linha'] == line) & (data['coluna'] == column)]

def getEscopeByLine(data, lineInit, lineEnd):
    # retorno os valores entre as linhas de inicio e fim
    return data.loc[(data['linha'] >= lineInit) & (data['linha'] <= lineEnd)]

def searchScope(data, line):
    repeat = True
    qtdFim = 0

    # enquanto poder repetir
    while(repeat):

        # pego a proxima linha
        line += 1

        # pego os dados da linha
        dataLine = data.loc[data['linha'] == line]

        # caso seja um token 'fim'
        if len(dataLine.loc[dataLine['token'] == 'FIM']) == 1:

            # verifico se o token fim e referente ao escopo
            if qtdFim > 0:

                # se nao for, apenas decremento
                qtdFim -= 1

            # caso o token fim seja referente ao escopo
            elif qtdFim == 0:

                # nao necessito repetir mais
                repeat = False
        
        # caso seja um token 'se'
        elif len(dataLine.loc[dataLine['token'] == 'SE']) == 1:
            
            # aumento a quantidade do token 'fim'
            qtdFim += 1

    # pego todos os tokens FIM e vejo a linha da primeira ocorrencia
    lineEndScope = min(dataLine.loc[dataLine['token'] == 'FIM', 'linha'].to_list())
    
    # retorno todos os valores entre a linha e a linha final
    return dataLine.loc[dataLine['linha'] <= lineEndScope]

def searchLineByTwoToken(data, line, token1, token2):
    # pega todos os valores da linha
    lineData = searchDataLine(data, line)

    # filtra pelo token
    columnToken1 = lineData.loc[lineData['token'] == token1, 'coluna'].values[0]
    columnToken2 = lineData.loc[lineData['token'] == token2, 'coluna'].values[0]
    
    # retorno os dados entre as colunas
    return lineData.loc[(lineData['coluna'] > columnToken1) & (lineData['coluna'] < columnToken2)]

def searchLineByTwoTokenByEnd(data, line, token1, token2):
    # pega todos os valores da linha
    lineData = searchDataLine(data, line)

    # filtra pelo token
    columnToken1 = lineData.loc[lineData['token'] == token1, 'coluna'].values[0]
    columnToken2 = lineData.loc[lineData['token'] == token2, 'coluna']
    sizeColumnToken = len(columnToken2)-1
    columnToken2 = columnToken2.values[sizeColumnToken]
    
    # retorno os dados entre os tokens
    return lineData.loc[(lineData['coluna'] > columnToken1) & (lineData['coluna'] < columnToken2)]

def searchDataLineBeforeToken(data, line, token):
    # procuro os tokens da linha
    dataLine = searchDataLine(data, line)

    # pego a coluna inicial e a coluna final
    columnStart = dataLine['coluna'].min()
    columnEnd = dataLine.loc[dataLine['token'] == token, 'coluna'].values[0]

    # retorno os valores entre esse intervalo
    return dataLine.loc[(dataLine['coluna'] >= columnStart) & (dataLine['coluna'] <= columnEnd)]

def searchDataLineAfterToken(data, line, token):
    # procuro os tokens da linha
    dataLine = searchDataLine(data, line)

    # pego a coluna inicial e a coluna final
    columnStart = dataLine.loc[dataLine['token'] == token, 'coluna'].values[0]

    # retorno os valores depois desse intervalo
    return dataLine.loc[(dataLine['coluna'] >= columnStart)]

def searchDataColumn(data, line, coluna):
    # retorna todos os valores da linha
    return data.loc[(data['linha'] == line) & (data['coluna'] == coluna)]

def searchDataLine(data, line):
    # retorna todos os valores da linha
    return data.loc[data['linha'] == line]

def searchTokenLineData(data, line, token):
    # pega todos os valores da linha
    lineData = searchDataLine(data, line)

    # filtra pelo token
    lineDataToken = lineData.loc[lineData['token'] == token]
   
    # retorna TRUE se encontrou o token
    return len(lineDataToken) > 0
    
def openFile():
    data = []
    
    # abre o arquivo
    with open('saida.txt', 'r') as file:
        
        # para cada linha
        for idx, line in enumerate(file):
            
            # retiro a string
            formatedLine = line.replace('LexToken(', '')
            
            # separo por ','
            formatedData = formatedLine.split(',')
            
            # se existir o token VIRGULA
            if formatedLine[0:7] == 'VIRGULA':
                data.append([formatedData[0], ',', int(formatedData[len(formatedData)-2]), int(formatedData[len(formatedData)-1].replace(')\n', '').replace(')', ''))])
            else:
                data.append([formatedData[0], formatedData[1].replace("'", ''), int(formatedData[2]), int(formatedData[3].replace(')\n', '').replace(')', ''))])
    
    # retorno a lista formatada
    return data

def createDataFrame(data):
    # crio colunas para os valores
    dataPD = pd.DataFrame(data, columns = ['token', 'valor', 'linha', 'coluna'])

    # retorna o dataframe
    return dataPD

def isInFunction(functions, line):
    isInFunction = False

    # passo por todas as funções
    for function in functions:

        # caso a declaração esteja entre o inicio e o fim de uma funcao
        if(function[3] < line and line < function[4]):
            isInFunction = True
            break

    return isInFunction

def isInFunctionDF(functionsDF, line):
    return isInFunction(functionsDF.values, line)

def returnFunction(functionsDF, line):
    nameFunction = 'GLOBAL'

    # passo por todas as funções
    for function in functionsDF.values:

        # caso a declaração esteja entre o inicio e o fim de uma funcao
        if(function[3] < line and line < function[4]):
            nameFunction = function[1]
            break

    return nameFunction

def getFunctions(dataPD):
    functions = []

    # linha de inicio
    lineStart = dataPD['linha'].min()
    
    # linha final
    lineEnd = dataPD['linha'].max()

    # para cada linha
    for line in range(lineStart, lineEnd+1):

        # busco os dados da linha
        dataLine = searchDataLine(dataPD, line)

        # se existir algum token
        if len(dataLine) > 0:

            # se não for uma função ja definida (como escreva() e leia())
            if ((not searchTokenLineData(dataPD, line, 'ESCREVA')) and (not searchTokenLineData(dataPD, line, 'LEIA') and (not searchTokenLineData(dataPD, line, 'RETORNA')))):

                # vejo se possui o token '(' e se não é uma atribuição
                if ((searchTokenLineData(dataPD, line, 'ABRE_PARENTESE')) and (not searchTokenLineData(dataPD, line, 'ATRIBUICAO'))):
                    
                    # procuro apenas os ID's
                    lineIDs = dataLine.loc[dataLine['token'] == 'ID']
                    
                    # caso não esteja dentro de uma funcao
                    if(len(lineIDs['linha']) > 0 and not isInFunction(functions, lineIDs['linha'].values[0])):

                        # se existir algum ID
                        if len(lineIDs) != 0:
                            
                            # se existir mais de um, pego apenas o primeiro (que é a função)
                            if len(lineIDs) > 1:
                                function = lineIDs.loc[[lineIDs.index[0]]]
                            else:
                                function = lineIDs

                            # pego tudo da linha da funcao
                            functionLine = searchDataLine(dataPD, line)
                            
                            # pego todo o escopo da funcao
                            functionTotal = searchScope(dataPD, line)

                            # pego o inicio da funcao
                            functionStart = searchDataLineBeforeToken(dataPD, line, 'ABRE_PARENTESE')
                            
                            # linha de inicio e fim dos parametros
                            functionArgs1 = functionLine.loc[functionLine['token'] == 'ABRE_PARENTESE', 'coluna'].values[0]
                            functionArgs2 = functionLine.loc[functionLine['token'] == 'FECHA_PARENTESE', 'coluna'].values[0]
                            functionArgs = []

                            # caso tenha parâmetros
                            if (functionArgs1 != (functionArgs2 - 1)):
                                dataColumnList = []
                                paramIdx = 0
                                
                                # ando pelo intervalo das colunas
                                for column in range((functionArgs1 + 1), functionArgs2):
                                    dataColumn = searchDataColumn(dataPD, line, column)

                                    # se vier algo, e não for: ':', ',', '[' e ']'
                                    if ((len(dataColumn) > 0) and (len(dataColumn.loc[dataColumn['token'] == 'DOIS_PONTOS']) < 1) and (len(dataColumn.loc[dataColumn['token'] == 'VIRGULA']) < 1) and (len(dataColumn.loc[dataColumn['token'] == 'ABRE_COLCHETE']) < 1) and (len(dataColumn.loc[dataColumn['token'] == 'FECHA_COLCHETE']) < 1)):
                                        dataColumnList.append(dataColumn.values[0])

                                    # caso encontre 2 valores (TIPO e ID)
                                    if len(dataColumnList) == 2:
                                        functionArgs.append([])

                                        for argsInfo in dataColumnList:
                                            functionArgs[paramIdx].append(argsInfo[1])

                                        dataColumnList = []
                                        paramIdx += 1

                            # nome da funcao
                            functionName = function['valor'].values[0]

                            typesReturn = ['INTEIRO', 'FLUTUANTE']
                            functionReturn = 'VAZIO'

                            # tipo de retorno
                            if functionStart['token'].values[0] in typesReturn:
                                functionReturn = functionStart['token'].values[0]
                            
                            # linha de inicio
                            functionLineStart = line

                            # linha final
                            functionLineEnd = max(functionTotal['linha'])
                            
                            # adiciono a função
                            functions.append([functionReturn, functionName, functionArgs, functionLineStart, functionLineEnd])
    
    return functions

def verifyFunctions(dataPD, functionsPD, variablesPD, errors):
    verifyFunctionsLine(dataPD, functionsPD, errors)
    verifyFunctionsRepeat(dataPD, functionsPD, errors)
    verifyFunctionReturn(dataPD, functionsPD, variablesPD, errors)

def verifyFunctionReturn(dataPD, functionsPD, variablesPD, errors):

    # para cada funcao
    for function in functionsPD.values:

        # pego o escopo
        functionEscope = getEscopeByLine(dataPD, function[3], function[4])

        # caso não tenha retorno, mas nao seja vazio
        if ((len(functionEscope.loc[functionEscope['token'] == 'RETORNA']) == 0) and (function[0] != 'VAZIO')):
                errors.append(['ERRO', 'Erro: Função “' + function[1] + '” deveria retornar ' + function[0].lower() + ', mas retorna vazio'])
        
        # caso tenha retorno
        elif ((len(functionEscope.loc[functionEscope['token'] == 'RETORNA']) > 0)):
                
                # pego a linha do retorno
                functionReturn = functionEscope.loc[functionEscope['token'] == 'RETORNA']

                # pego os valores para retornar
                valuesReturn = searchLineByTwoTokenByEnd(dataPD, functionReturn['linha'].values[0], 'ABRE_PARENTESE', 'FECHA_PARENTESE')

                error = False

                # para cada um dos valores
                for values in valuesReturn.values:
                    
                    # caso seja uma variavel ou uma chamada de funcao
                    if values[0] == 'ID':

                        # vejo se e uma variavel
                        valueVariableId = variablesPD.loc[variablesPD['nome'] == values[1]]

                        # caso for
                        if len(valueVariableId) > 0:

                            # pego seu valor
                            valueVariableId = valueVariableId.values[0]

                            # verifico o retorno
                            if valueVariableId[0] != function[0]:
                                errors.append(['ERRO', 'Erro: Função “' + function[1] + '” deveria retornar ' + function[0].lower() + ', mas retorna ' + valueVariableId[0].lower()])

                        else:
                            
                            # pego a funcao
                            valueVariableId = functionsPD.loc[functionsPD['nome'] == values[1]]
                            
                            # caso exista
                            if len(valueVariableId) > 0:

                                # pego seu valor
                                valueVariableId = valueVariableId.values[0]
                                
                                # verifico seu retorno
                                if valueVariableId[0] != function[0]:
                                    errors.append(['ERRO', 'Erro: Função “' + function[1] + '” deveria retornar ' + function[0].lower() + ', mas retorna ' + valueVariableId[0].lower()])
                                    break

                    elif values[0] == 'NUM_INTEIRO':
                        
                        # verifico o retorno
                        if function[0] != 'INTEIRO':
                            errors.append(['ERRO', 'Erro: Função “' + function[1] + '” deveria retornar ' + function[0].lower() + ', mas retorna inteiro'])
                            break
                    
                    elif values[0] == 'NUM_PONTO_FLUTUANTE':
                        
                        # verifico o retorno
                        if function[0] != 'FLUTUANTE':
                            errors.append(['ERRO', 'Erro: Função “' + function[1] + '” deveria retornar ' + function[0].lower() + ', mas retorna flutuante'])
                            break

def verifyFunctionsRepeat(dataPD, functionsPD, errors):
    
    # para cada funcao
    for funcoes in functionsPD.values:

        # procuro recorrencias
        dataSearch = dataPD.loc[(dataPD['token'] == 'ID') & (dataPD['valor'] == funcoes[1])]
        
        # caso apenas encontre uma recorrencia
        if len(dataSearch) == 1:

            # e essa recorrencia nao é da funcao principal
            if len(dataSearch.loc[dataSearch['valor'] == 'principal']) == 0:
                errors.append(['AVISO', 'Aviso: Função “' + funcoes[1] + '” declarada, mas não utilizada'])

def verifyFunctionsLine(dataPD, functionsPD, errors):

    # linha de inicio
    lineStart = dataPD['linha'].min()
    
    # linha final
    lineEnd = dataPD['linha'].max()

    # para cada linha
    for line in range(lineStart, lineEnd+1):

        # busco os dados da linha
        dataLine = searchDataLine(dataPD, line)

        # se existir algum token
        if len(dataLine) > 0:

            # se não for uma função ja definida (como escreva() e leia())
            if ((not searchTokenLineData(dataPD, line, 'ESCREVA')) and (not searchTokenLineData(dataPD, line, 'LEIA') and (not searchTokenLineData(dataPD, line, 'RETORNA')))):

                # vejo se possui o token '(' e se não é uma atribuição
                if ((searchTokenLineData(dataPD, line, 'ABRE_PARENTESE')) and (not searchTokenLineData(dataPD, line, 'ATRIBUICAO'))):
                    
                    # procuro apenas os ID's
                    lineIDs = dataLine.loc[dataLine['token'] == 'ID']
                    qtdParams = len(lineIDs) - 1

                    # caso esteja dentro de uma funcao
                    if(len(lineIDs['linha']) > 0 and isInFunctionDF(functionsPD, lineIDs['linha'].values[0])):
                        
                        # pego o nome da funcao
                        functionName = dataLine.loc[dataLine['token'] == 'ID', 'valor'].values[0]
                        
                        # pego o escopo da funcao
                        functionPD = functionsPD.loc[functionsPD['nome'] == functionName]
                        tamFunctionPD = len(functionPD)
                        
                        # caso esteja chamando a função principal
                        if functionName == 'principal' and tamFunctionPD == 1:

                            # pego o escopo
                            escopeName = findEscope(lineIDs['linha'].values[0], functionsPD.values)

                            # se o escopo nao for na propria funcao principal 
                            if escopeName != 'principal':
                                errors.append(['ERRO', 'Erro: Chamada para a função principal não permitida'])
                        
                        # caso nao ache nenhuma recorrencia
                        if tamFunctionPD == 0:
                            errors.append(['ERRO', 'Erro: Chamada a função “' + functionName + '” que não foi declarada'])
                        else:

                            # linha inicio e fim
                            functionLineStart = functionPD['linha_inicio'].values[0]
                            functionLineEnd = functionPD['linha_fim'].values[0]

                            # se for uma chamada recursiva para a mesma funcao
                            if (functionLineStart < line and line < functionLineEnd):
                                errors.append(['AVISO', 'Aviso: Chamada recursiva para “' + functionName + '”'])

                            # caso a quantidade de parametros seja maior/menor
                            if qtdParams > len(functionPD['parametros'].values[0]):
                                errors.append(['ERRO', 'Erro: Chamada à função “' + functionName + '” com número de parâmetros maior que o declarado'])
                            
                            elif qtdParams < len(functionPD['parametros'].values[0]):
                                errors.append(['ERRO', 'Erro: Chamada à função “' + functionName + '” com número de parâmetros menor que o declarado'])

def verifyVariables(dataPD, functionsPD, variablesPD, errors):
    verifyVariableUse(dataPD, variablesPD, errors)

def verifyVariableUse(dataPD, variablesPD, errors):

    # para cada variavel
    for variable in variablesPD.values:

        # encontro as recorrencias da variavel
        variablePD = dataPD.loc[(dataPD['token'] == 'ID') & (dataPD['valor'] == variable[1])]
        
        # caso so tenha uma recorrência
        if len(variablePD) == 1:
            errors.append(['AVISO', 'Aviso: Variável “' + variable[1] + '” declarada, mas não utilizada'])
        
        # acho declarações em outro escopo de funcao
        anotherDeclarationEscope = variablesPD.loc[(variablesPD['nome'] == variable[1]) & (variablesPD['escope'] == variable[2]) & (variablesPD['linha'] < variable[3])]
        anotherDeclarationGlobal = variablesPD.loc[(variablesPD['nome'] == variable[1]) & (variablesPD['escope'] == 'global') & (variablesPD['linha'] < variable[3])]
        
        # se encontrar no escopo
        if(len(anotherDeclarationEscope) > 0):
            errors.append(['AVISO', 'Aviso: Variável “'+ variable[1] +'” já declarada anteriormente'])

        else:
            
            # se encontrar no escopo global
            if len(anotherDeclarationGlobal) > 0:
                errors.append(['AVISO', 'Aviso: Variável “'+ variable[1] +'” já declarada anteriormente'])

        # caso nenhuma das recorrências tenha sido inicializada
        if (len(variablePD) == (len(anotherDeclarationEscope) + len(anotherDeclarationGlobal) + 1)):
                errors.append(['AVISO', 'Aviso: Variável “' + variable[1] + '” declarada, mas não utilizada'])

def findEscope(line, functions):
    escope = 'global'

    for function in functions:
        if(function[3] <= line and line <= function[4]):
            escope = function[1]
            break
    
    return escope

def findVariable(variables, variableName, escope):
    found = False

    for variable in variables:

        if ((variable[1] == variableName) and (variable[2] == escope)):
            found = True
            break

    return found

def getVariables(dataPD, functions, errors):
    variables = []

    # linha de inicio
    lineStart = dataPD['linha'].min()
    
    # linha final
    lineEnd = dataPD['linha'].max()

    # para cada linha
    for line in range(lineStart, lineEnd+1):
        
        # busco os dados da linha
        dataLine = searchDataLine(dataPD, line)

        # se existir algum token
        if len(dataLine) > 0:
            
            # caso a linha tenha o token ':'
            if len(dataLine.loc[dataLine['token'] == 'DOIS_PONTOS']) >= 1:
                
                # caso a linha tenha o token '('
                if len(dataLine.loc[dataLine['token'] == 'ABRE_PARENTESE']) == 1:

                    # procuro todos os tokens entre os tokens: '(', ')'
                    params = searchLineByTwoToken(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE').values
                    idx = 0

                    # para cada um dos parametros da funcao
                    for param in params: 

                        # se for o token ',' é necessario resetar
                        if param[0] == 'VIRGULA' or param[0] == 'ABRE_COLCHETE' or param[0] == 'FECHA_COLCHETE':
                            idx = 0
                        # pego o nome
                        elif idx == 0:

                            # tipo da variavel
                            variableType = param[0]
                            idx += 1
                        # faço nada (token ':')
                        elif idx == 1:
                            idx += 1
                        # pego o nome, linha e escopo
                        elif idx == 2:

                            # nome da variavel
                            variableName = param[1]

                            # linha da variavel
                            variableLine = param[2]

                            # escopo da variavel
                            escope = findEscope(line, functions)

                            if (findVariable(variables, variableName, escope)):
                                errors.append(['AVISO', 'Aviso: Variável “' + variableName + '” já declarada anteriormente'])

                            # adiciono a variavel
                            variables.append([variableType, variableName, escope, variableLine, False, []])
                            
                
                # caso a linha tenha o token ','
                elif len(dataLine.loc[dataLine['token'] == 'VIRGULA']) >= 1:
                   
                   # pego todas as variaveis
                    dataLineIDs = dataLine.loc[dataLine['token'] == 'ID']
                    detaLineIDs = dataLine.values
                    
                    # o tipo de retorno
                    variableType = dataLine.loc[(dataLine['token'] == 'INTEIRO') | (dataLine['token'] == 'FLUTUANTE'), 'token'].values[0]
                    
                    # a linha de declaracao da variavel
                    variableLine = min(dataLine['linha'])

                    # o escopo da variavel
                    escope = findEscope(line, functions)

                    if(findVariable(variables, variableName, escope)):
                        errors.append(['AVISO', 'Aviso: Variável “' + variableName + '” já declarada anteriormente'])

                    # para cada variavel
                    for declaration in dataLineIDs.values:

                        # nome da variavel
                        variableName = declaration[1]

                        # dimensoes
                        variableDimensions = []

                        # pego o proximo valor
                        nextValueColumn = getColunmValue(dataPD, line, declaration[3]+1)

                        # verifico se possui dimensões
                        if len(nextValueColumn.loc[nextValueColumn['token'] == 'ABRE_COLCHETE']):
                            
                            # pego o indice
                            valueColumn = searchDataColumn(dataPD, line, declaration[3]+2)
                            
                            # se for um token 'NUM_INTEIRO'
                            if len(valueColumn.loc[(valueColumn['token'] == 'NUM_INTEIRO') | (valueColumn['token'] == 'NUM_PONTO_FLUTUANTE')]) == 1:
                                variableDimensions.append(valueColumn['valor'].values[0])

                        # adiciono na lista
                        variables.append([variableType, variableName, escope, variableLine, False, variableDimensions])
                
                else:

                    # tipo da variavel
                    variableType = dataLine.loc[(dataLine['token'] == 'INTEIRO') | (dataLine['token'] == 'FLUTUANTE'), 'token'].values[0]
                    
                    # nome da variavel
                    variableName = dataLine.loc[dataLine['token'] == 'ID', 'valor'].values[0]
                    
                    # linha da variavel
                    variableLine = min(dataLine['linha'])
                    
                    # dimensoes da variavel
                    variableDimensions = []
                    dimensions = dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']

                    # caso possua dimensoes
                    if len(dimensions) > 0:

                        dimensions = dimensions.values

                        # para cada um dos valores
                        for valuesDimension in dimensions:

                            # pego o valor que se encontra depois do '['
                            valueColumn = searchDataColumn(dataPD, line, valuesDimension[3]+1)
                            
                            # se for um token 'NUM_INTEIRO'
                            if len(valueColumn.loc[(valueColumn['token'] == 'NUM_INTEIRO') | (valueColumn['token'] == 'NUM_PONTO_FLUTUANTE')]) == 1:
                                variableDimensions.append(valueColumn['valor'].values[0])
                    
                    # procuro o escopo
                    escope = findEscope(line, functions)

                    if(findVariable(variables, variableName, escope)):
                        errors.append(['AVISO', 'Aviso: Variável “' + variableName + '” já declarada anteriormente'])

                    # salvo a variavel
                    variables.append([variableType, variableName, escope, variableLine, False, variableDimensions])
    
    return variables

def showList(list):
    for item in list:
        print(item)

def createFunctionPD(functions):
    functionsPD = pd.DataFrame(functions, columns=['tipo', 'nome', 'parametros', 'linha_inicio', 'linha_fim'])
    
    return functionsPD

def createVariablePD(variables):
    variablesPD = pd.DataFrame(variables, columns=['tipo', 'nome', 'escope', 'linha', 'using', 'dimensoes'])

    return variablesPD

def verifyAssignment(dataPD, functionsPD, variablesPD, errors):
    verifyAssignmentValues(dataPD, functionsPD, variablesPD, errors)
    #TODO: olhar se uma funcao esta passando os parametros corretos em uma atribuicao

def isFunction(dataPD, line, name):
    function = False

    dataFunction = dataPD.loc[(dataPD['token'] == 'ID') & (dataPD['valor'] == name)]
    
    columnLine = dataFunction['coluna'].values[0]
    continueSearch = True
    idx = 0

    while(continueSearch):
        columnLine += 1
        idx += 1

        dataColumn = dataPD.loc[(dataPD['linha'] == line) & (dataPD['coluna'] == columnLine)]

        if len(dataColumn) > 0:
            dataProx = dataColumn.loc[dataColumn['token'] == 'ABRE_PARENTESE']
            
            if len(dataProx) > 0:
                function = True
                break

        if idx == 20:
            break

    return function

def verifyAssignmentValues(dataPD, functionsPD, variablesPD, errors):

    # para todas as atribuicoes
    assignmentPD = dataPD.loc[dataPD['token'] == 'ATRIBUICAO']

    # para cada atribuicao
    for assignment in assignmentPD.values:

        # pego a linha
        assignmentLine = searchDataLine(dataPD, assignment[2])

        # a variavel da esquerda
        assignmentEsq = searchDataLineBeforeToken(dataPD, assignment[2], 'ATRIBUICAO')
        dataEsq = assignmentEsq.loc[assignmentEsq['token'] == 'ID']
        
        # procuro na tabela
        variable = variablesPD.loc[variablesPD['nome'] == dataEsq['valor'].values[0]]

        # caso ela nao exista
        if len(variable) == 0:
            errors.append(['ERRO', 'Erro: Variável “' + dataEsq['valor'].values[0] + '” não declarada'])
            variableEsqType = ''

        else:
            variableEsqType = variable['tipo'].values[0]
        
        # pego o valor da direita
        assignmentDir = searchDataLineAfterToken(dataPD, assignment[2], 'ATRIBUICAO')

        # caso tenha uma funcao
        if len(assignmentDir.loc[assignmentDir['token'] == 'ABRE_PARENTESE']) > 0:
            
            # pego todos os IDS
            dataDir = assignmentDir.loc[assignmentDir['token'] == 'ID']
            
            # para cada um deles
            for variableAssignmentDir in dataDir.values:
                isVariable = False

                # verifico na tabela de funcoes
                functionDir = functionsPD.loc[functionsPD['nome'] == variableAssignmentDir[1]]
                
                # caso nao encontre
                if len(functionDir) == 0:

                    # procuro na tabela de variaveis
                    variableDir = variablesPD.loc[variablesPD['nome'] == variableAssignmentDir[1]]

                    # caso nao encontre
                    if len(variableDir) == 0:

                        if isFunction(dataPD, variableAssignmentDir[2], variableAssignmentDir[1]):
                            errors.append(['ERRO', 'Erro: Chamada a função “' + variableAssignmentDir[1] + '” que não declarada'])
                        else:
                            errors.append(['ERRO', 'Erro: Variável “' + variableAssignmentDir[1] + '” não declarada'])
                    
                        variableDirType = ''
                    else:
                        isVariable = True
                        variableDirType = variableDir['tipo'].values[0]

                else:
                    variableDirType = functionDir['tipo'].values[0]

                # caso nao tenha nenhum erro
                if variableDirType != '' and variableEsqType != '':

                    # verifico se os tipos sao diferentes
                    if variableEsqType != variableDirType:
                        if not isVariable:
                            errors.append(['AVISO', 'Aviso: Coerção implícita do valor passado para váriavel “' +  dataEsq['valor'].values[0] + '” da função “' + variableAssignmentDir[1] + '”'])
                            break
                        else:
                            errors.append(['AVISO', 'Aviso: Coerção implícita do valor atribuído para “' +  dataEsq['valor'].values[0] + '”'])

        else:
            
            # procuro todos os IDs
            dataDir = assignmentDir.loc[assignmentDir['token'] == 'ID']

            # para cada um deles
            for variableAssignmentDir in dataDir.values:

                # procuro na tabela de variaveis
                variableDir = variablesPD.loc[variablesPD['nome'] == variableAssignmentDir[1]]

                # caso nao encontre
                if len(variableDir) == 0:
                    errors.append(['ERRO', 'Erro: Variável “' + variableAssignmentDir[1] + '” não declarada'])
                    variableDirType = ''
                
                else:
                    variableDirType = variableDir['tipo'].values[0]

                # caso nao tenha nenhum erro
                if variableDirType != '' and variableEsqType != '':

                    # caso os tipos sejam diferentes
                    if variableEsqType != variableDirType:
                        errors.append(['AVISO', 'Aviso: Coerção implícita do valor atribuído para “' +  dataEsq['valor'].values[0] + '”'])
        
def execute():

    # pegar a lista com os tokens
    data = openFile()

    # criar dataframe
    dataPD = createDataFrame(data)

    # criar lista de funções
    functions = getFunctions(dataPD)
    functionsPD = createFunctionPD(functions)

    # criar lista de variaveis
    errors = []
    variables = getVariables(dataPD, functions, errors)
    variablesPD = createVariablePD(variables)

    # verificações
    verifyFunctions(dataPD, functionsPD, variablesPD, errors)
    verifyVariables(dataPD, functionsPD, variablesPD, errors)
    verifyAssignment(dataPD, functionsPD, variablesPD, errors)

    return dataPD, functionsPD, variablesPD, errors