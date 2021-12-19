import llvmlite.ir as ll
import subprocess

# funcao auxiliar para retornar os nos a partir de um nome
def auxArrays(pai):

    # variaveis auxiliares
    recebeu = True
    direita, esquerda = [], []

    # para cada um dos filhos
    for no in pai.children:

        # se tiver atribuicao
        if no.name != ':=':

            # esquerda/direita
            if recebeu:
                esquerda.append(no.name)
            else:
                direita.append(no.name)

        # caso nao tenha
        else:
            recebeu = False

    # retorna os valores
    return direita, esquerda

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
