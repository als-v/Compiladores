import parser
import sintatica 
import subprocess
from sys import argv, exit

def runLex(file):
    subprocess.run(['python3', 'lex.py', file, 'd'])

def mainFunction(dataPD, functionsPD, variablesPD, errors):
    principal = functionsPD.loc[functionsPD['nome'] == 'principal']

    if len(principal) == 0:
        errors.append(['ERRO', 'Erro: Função principal não declarada'])

def arrayVerify(dataPD, variablesPD, errors):
    variableArray = variablesPD.loc[variablesPD['dimensoes'].str.len() != 0]

    if len(variableArray) > 0:
        for variable in variableArray.values:
            for dimensions in variable[5]:
                try:
                    dim = int(dimensions)
                except:
                    errors.append(['ERRO', 'Erro: Índice de array “' + variable[1] + '” não inteiro'])

def variablesVerify(dataPD, functionsPD, variablesPD, errors):
    allID = dataPD.loc[dataPD['token'] == 'ID']

    for id in allID.values:
        # if id[1] not in variablesPD['nome'].values:
        #     errors.append(['ERRO', 'Erro: Variável “' + id[1] + '” não declarada'])
        if id[1] not in functionsPD['nome'].values:
            if id[1] not in variablesPD['nome'].values:
                errors.append(['ERRO', 'Erro: Variável “' + id[1] + '” não declarada'])

def semanticAnalysis(dataPD, functionsPD, variablesPD, errors):
    mainFunction(dataPD, functionsPD, variablesPD, errors)
    arrayVerify(dataPD, variablesPD, errors)
    variablesVerify(dataPD, functionsPD, variablesPD, errors)

def showErrors(errors):

    errosNotRepeat = []

    print('')
    for err in errors:
        if err[0] == 'ERRO':
            if err[1] not in errosNotRepeat:
                print(err[1])
                errosNotRepeat.append(err[1])
    print('')
    for err in errors:
        if err[0] == 'AVISO':
            if err[1] not in errosNotRepeat:
                print(err[1])
                errosNotRepeat.append(err[1])

def showListPD(lista):
    print(lista)

def main():
    
    error, detailedLogs, showTree = False, False, False

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

    runLex(argv[1])
    # error = sintatica.main(argv[1], detailedLogs, showTree)
    error = []
    
    if not error:
        dataPD, functionsPD, variablesPD, errors = parser.execute()

        # showListPD(variablesPD)
        # print('antes de executar')
        # showErrors(errors)
        # showListPD(functionsPD)
        semanticAnalysis(dataPD, functionsPD, variablesPD, errors)
        
        # print('\n\ndepois de executar')
        showErrors(errors)
    else:
        print('Erro')

if __name__ == "__main__":
    main()
