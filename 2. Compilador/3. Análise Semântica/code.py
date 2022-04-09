import parser
import sintatica 
import subprocess
from sys import argv, exit

errors = []

def runLex(file):
    subprocess.run(['python3', 'lex.py', file, 'd'])

def mainFunction(dataPD, functionsPD):
    principal = functionsPD.loc[functionsPD['nome'] == 'principal']

    if len(principal) == 0:
        errors.append(['ERROR', 'Erro: Função principal não declarada'])

    for functions in functionsPD.values:
        lineStart = functions[3] + 1
        lineEnd = parser.searchScope(dataPD, functions[3])['linha'].values[0]

        dataLine = parser.getEscopeByLine(dataPD, lineStart, lineEnd)
        dataLineId = dataLine.loc[dataLine['token'] == 'ID']
        dataLinePrincipal = dataLineId.loc[dataLineId['valor'] == 'principal']

        for principalRecurrence in range(len(dataLinePrincipal)):
            errors.append(['ERROR', 'Erro: Chamada para a função principal não permitida'])

def semanticAnalysis(dataPD, functionsPD, variablesPD):
    mainFunction(dataPD, functionsPD)

def showErrors():
    for err in errors:
        print(err)

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
        dataPD, functionsPD, variablesPD = parser.execute()
        semanticAnalysis(dataPD, functionsPD, variablesPD)
        
        showErrors()
    else:
        print('Erro')

if __name__ == "__main__":
    main()
