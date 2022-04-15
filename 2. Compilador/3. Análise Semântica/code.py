import parser
import sintatica 
import subprocess
import podaArvore
from sys import argv, exit
from anytree.exporter import UniqueDotExporter

def runLex(file):
    subprocess.run(['python3', 'lex.py', file, 'd'])

def mainFunction(dataPD, functionsPD, variablesPD, errors):
    principal = functionsPD.loc[functionsPD['nome'] == 'principal']

    if len(principal) == 0:
        errors.append(['ERRO', 'Erro: Função principal não declarada'])

def arrayVerify(dataPD, variablesPD, errors):
    arrayVerifyDimensions(dataPD, variablesPD, errors)
    arrayVerifyRange(dataPD, variablesPD, errors)

def arrayVerifyDimensions(dataPD, variablesPD, errors):

    # procuro todos os arranjos
    variableArray = variablesPD.loc[variablesPD['dimensoes'].str.len() != 0]

    # para cada um deles
    for variable in variableArray.values:

        # passo pelas suas dimensoes
        for dimensions in variable[5]:

            # tento fazer o cast para int
            try:
                dim = int(dimensions)
            except:

                # se der erro, o indice nao e inteiro
                errors.append(['ERRO', 'Erro: Índice de array “' + variable[1] + '” não inteiro'])

def verifyInteger(list):
    notErr = True

    for i in list:
        try:
            int(i)
        except:
            notErr = False
            break
    
    return notErr

def arrayVerifyRange(dataPD, variablesPD, errors):

    # procuro todos os arranjos
    variableArray = variablesPD.loc[variablesPD['dimensoes'].str.len() != 0]

    # passo por todos os arranjos
    for var in variableArray.values:
        
        if verifyInteger(var[5]):

            # pego todas as vezes que foi chamado
            varDimCalls = dataPD.loc[(dataPD['token'] == 'ID') & (dataPD['valor'] == var[1])]
            
            # para cada uma delas
            for varDim in varDimCalls.values:

                # encontro a linha em que ocorreu
                dataLine = parser.searchDataLine(dataPD, varDim[2])

                # pego o token ':='
                dataLineAtt = dataLine.loc[dataLine['token'] == 'ATRIBUICAO']

                # se tiver uma atribuição
                if len(dataLineAtt) > 0:
                    
                    # procuro os valores que vieram apos
                    dataLineAfterAttr = dataLine.loc[dataLine['coluna'] > dataLineAtt['coluna'].values[0]]

                    # para cada um dos ID's
                    for attr in dataLineAfterAttr.loc[dataLineAfterAttr['token'] == 'ID'].values:
                        
                        # vejo se o nome é o mesmo da variavel
                        if var[1] == attr[1]:
                            
                            # procuro os valores apos a declaracao
                            dataLineAttr = dataLineAfterAttr.loc[dataLineAfterAttr['coluna'] > attr[3]]
                            
                            # pego todos os indices
                            dimensionsAttr = dataLineAttr.loc[dataLineAttr['token'] == 'NUM_INTEIRO']
                            
                            # passo pelo range do tamanho do indice da variavel (vetor ou matriz)
                            for idx in range(len(var[5])):

                                # caso a dimensao esteja fora do intervalo
                                if int(dimensionsAttr.values[idx][1]) > int(var[5][idx]):
                                    errors.append(['ERRO', 'Erro: Índice de array “' + var[1] + '” fora do intervalo (out of range)'])
                    
                    # procuro os valores que vieram antes
                    dataLineBeforeAttr = dataLine.loc[dataLine['coluna'] < dataLineAtt['coluna'].values[0]]

                    # para cada um dos ID's
                    for attr in dataLineBeforeAttr.loc[dataLineBeforeAttr['token'] == 'ID'].values:
                        
                        # vejo se o nome é o mesmo da variavel
                        if var[1] == attr[1]:
                            
                            # pego todos os indices
                            dimensionsAttr = dataLineBeforeAttr.loc[dataLineBeforeAttr['token'] == 'NUM_INTEIRO']

                            # passo pelo range do tamanho do indice da variavel (vetor ou matriz)
                            for idx in range(len(var[5])):

                                # caso a dimensao esteja fora do intervalo
                                if int(dimensionsAttr.values[idx][1]) > int(var[5][idx]):
                                    errors.append(['ERRO', 'Erro: Índice de array “' + var[1] + '” fora do intervalo (out of range)'])

def variablesVerify(dataPD, functionsPD, variablesPD, errors):
    allID = dataPD.loc[dataPD['token'] == 'ID']

    for id in allID.values:
        # if id[1] not in variablesPD['nome'].values:
        #     errors.append(['ERRO', 'Erro: Variável “' + id[1] + '” não declarada'])
        if id[1] not in functionsPD['nome'].values:
            if id[1] not in variablesPD['nome'].values:
                errors.append(['ERRO', 'Erro: Variável “' + id[1] + '” não declarada'])

def verifyRead(dataPD, variablesPD, errors):

    # para cada variavel
    for idx, var in enumerate(variablesPD.values):

        # encontro as recorrencias
        recurrency = dataPD.loc[(dataPD['token'] == 'ID') & (dataPD['valor'] == var[1])]
        init = False

        # para cada uma delas
        for rec in recurrency.values:

            # encontro a linha
            dataLine = parser.searchDataLine(dataPD, rec[2])

            # caso seja uma atribuicao
            if len(dataLine.loc[dataLine['token'] == 'ATRIBUICAO']) > 0:
                init = True

            # caso tenha uma funcao 'leia()' e a variavel nao esta inicializada 
            if ((len(dataLine.loc[dataLine['token'] == 'LEIA']) > 0) and (not init)):
                errors.append(['AVISO', 'Aviso: Variável “' + var[1] + '” declarada e não inicializada'])

        # caso ela esteja inicializada, porem nao atualizada na tabela
        if init and not variablesPD.loc[variablesPD['nome'] == var[1]].values[0][4]:
            variablesPD.loc[variablesPD['nome'] == var[1], 'using'] = True

def semanticAnalysis(dataPD, functionsPD, variablesPD, errors):
    mainFunction(dataPD, functionsPD, variablesPD, errors)
    arrayVerify(dataPD, variablesPD, errors)
    variablesVerify(dataPD, functionsPD, variablesPD, errors)
    verifyRead(dataPD, variablesPD, errors)

def showErrors(errors):
    global semanticError

    errosNotRepeat = []

    print('')
    for err in errors:
        if err[0] == 'ERRO':
            semanticError = True
            if err[1] not in errosNotRepeat:
                print(err[1])
                errosNotRepeat.append(err[1])
    print('')
    for err in errors:
        if err[0] == 'AVISO':
            if err[1] not in errosNotRepeat:
                print(err[1])
                errosNotRepeat.append(err[1])

def showListPD(lista, label):
    print('\n{}:\n{}'.format(label, lista))

def main():
    
    global semanticError

    # flags
    error, detailedLogs, showTree, showTables, semanticError = False, False, False, False, False

    # pegar nome do arquivo
    try:
        aux = argv[1].split('.')
    except:
        print('Arquivo inválido!')
        return

     # verificar extensão
    if aux[-1] != 'tpp':
        print('O arquivo selecionado não tem a extensao .tpp!')
        return

    # verficar flag de detalhado
    if 'd' in argv:
        detailedLogs = True
    if 'st' in argv:
        showTree = True
    if 'sta' in argv:
        showTables = True

    runLex(argv[1])
    root, isSintaticErr = sintatica.main(argv[1], detailedLogs, showTree)

    if not isSintaticErr:
        dataPD, functionsPD, variablesPD, errors = parser.execute()
        semanticAnalysis(dataPD, functionsPD, variablesPD, errors)
        showErrors(errors)
        
        if showTables:
            showListPD(functionsPD, 'TABELA DE FUNÇÕES')
            showListPD(variablesPD, 'TABELA DE VARIÁVEIS')

        arv = podaArvore.poda(root)

        # salvar a arvore
        UniqueDotExporter(arv).to_picture(str(argv[1]) + '.poda.ast.png')

    else:
        print('Erro nas analises anteriores')


if __name__ == "__main__":
    main()
