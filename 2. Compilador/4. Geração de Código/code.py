import subprocess
import semantica as sem
from sys import argv, exit
import geracaoCodigo as gc

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

        # crio um arquivo de saida 
        arquivo = open(str(argv[1])+'.ll', 'w')

        # escrevo o modulo
        arquivo.write(str(modulo))
        arquivo.close()

        run(argv[1])

    else:
        print('Houve um erro nas etapas anteriores')

def run(file):
    file = str(file)

    # comandos necessarios para gerar o codigo
    commands = [
        'clang -emit-llvm -S io.c', 
        'llc -march=x86-64 -filetype=obj io.ll -o io.o', 
        'llvm-link ' + file + '.ll io.ll -o ' + file + '.bc', 
        'clang ' + file + '.bc -o ' + file + '.o', 
        'rm ' + file + '.bc'
    ]
    
    # rodo os comandos
    for command in commands:
        subprocess.run(command.split(' '))


if __name__ == "__main__":
    main()