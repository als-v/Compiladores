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

    for functions in functionsPD.values:
        lineStart = functions[3] + 1
        lineEnd = parser.searchScope(dataPD, functions[3])['linha'].values[0]

        dataLine = parser.getEscopeByLine(dataPD, lineStart, lineEnd)
        dataLineId = dataLine.loc[dataLine['token'] == 'ID']

        dataLinePrincipal = dataLineId.loc[dataLineId['valor'] == 'principal']

        for principalRecurrence in range(len(dataLinePrincipal)):
            # errors.append(['ERROR', 'Erro: Chamada para a função principal não permitida'])
            pass
def declarations(dataPD, functionsPD, variablesPD):
    # for idLine in dataLineId.values:
    #             isFunction = True
    #             isVariable = True

    #             if(len(functionsPD.loc[functionsPD['nome'] == idLine[1]]) > 0):
    #                 isFunction = False

    #             if(len(variablesPD.loc[variablesPD['nome'] == idLine[1]]) > 0):
    #                 isVariable = False

    #             if(isFunction and isVariable):
    #                 lineIdData = parser.searchDataLine(dataPD, idLine[2])
    #                 print(idLine)
    #                 print(lineIdData)
                    # errors.append(['ERROR', 'Erro: Variável ou função não declarada'])
    pass
def semanticAnalysis(dataPD, functionsPD, variablesPD, errors):
    mainFunction(dataPD, functionsPD, variablesPD, errors)

def showErrors(errors):
    for err in errors:
        if err[0] == 'ERRO':
            print(err[1])
    for err in errors:
        if err[0] == 'AVISO':
            print(err[1])

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
    error = sintatica.main(argv[1], detailedLogs, showTree)
    
    if not error:
        dataPD, functionsPD, variablesPD, errors = parser.execute()

        showListPD(variablesPD)
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
