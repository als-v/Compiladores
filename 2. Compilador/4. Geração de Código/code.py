import semantica as sem
import geracaoCodigo as gc
from sys import argv, exit

def main():

    # flags
    detailedLogs, showTree, showTables, showModule = False, False, False, False

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
    if 'sm' in argv:
        showModule = True

    semanticError, root, dataPD, functionsPD, variablesPD = sem.execute(argv[1], detailedLogs, showTree, showTables)

    if not semanticError:
        modulo = gc.codeGenerator(argv[1], root, dataPD, functionsPD, variablesPD)
    
        if showModule:
            print('\n\n', str(modulo))

    else:
        print('Houve um erro nas etapas anteriores')

if __name__ == "__main__":
    main()