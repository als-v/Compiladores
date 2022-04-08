import pandas as pd

def searchScope(data, line):
    # pega todos os valores depois da linha
    dataLine = data.loc[data['linha'] >= line]

    # pego todos os tokens FIM e vejo a linha da primeira ocorrencia
    lineEndScope = min(dataLine.loc[dataLine['token'] == 'FIM', 'linha'].to_list())

    # retorno todos os valores entre a linha e a linha final
    return dataLine.loc[dataLine['linha'] <= lineEndScope]

def searchDataLineBeforeToken(data, line, token):
    dataLine = searchDataLine(data, line)

    columnStart = dataLine['coluna'].min()
    columnEnd = dataLine.loc[dataLine['token'] == token, 'coluna'].values[0]

    return dataLine.loc[(dataLine['coluna'] >= columnStart) & (dataLine['coluna'] <= columnEnd)]

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
    # print(dataPD)

    # retorna o dataframe
    return dataPD

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
        # print(dataLine)

        # se existir algum token
        if len(dataLine) > 0:

            # se não for uma função ja definida (como escreva() e leia())
            if ((not searchTokenLineData(dataPD, line, 'ESCREVA')) and (not searchTokenLineData(dataPD, line, 'LEIA'))):

                # vejo se possui o token '(' e se não é uma atribuição
                if ((searchTokenLineData(dataPD, line, 'ABRE_PARENTESE')) and (not searchTokenLineData(dataPD, line, 'ATRIBUICAO'))):
                    
                    # procuro apenas os ID's
                    lineIDs = dataLine.loc[dataLine['token'] == 'ID']

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
                        functions.append([functionName, functionReturn, functionArgs, functionLineStart, functionLineEnd])
    
    return functions

def showList(list):
    for item in list:
        print(item)

def execute():

    # pegar a lista com os tokens
    data = openFile()

    # criar dataframe
    dataPD = createDataFrame(data)

    # criar lista de funções
    functions = getFunctions(dataPD)
    showList(functions)

execute()
