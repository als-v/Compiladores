from sys import argv
import semantica as sem
from code import codeGenerator

def main():

  # flag para mostrar a arvore
  showTree = False

  # flag para mostrar a tabela
  showTable = False

  # flag para mostrar os erros detalhados
  detailed = False

  # arquivo .tpp
  aux = argv[1].split('.')
  if aux[-1] != 'tpp':
    raise IOError("Not a .tpp file!")
  if 'showTree' in argv:
    showTree = True
  if 'showTable' in argv:
    showTable = True
  if 'detailed' in argv:
    detailed = True

  # analise semantica
  try:
    arvore, listaFuncoes, listaVariaveis, listaErros = sem.main(argv[1], detailed, showTree, showTable)
  except Exception as e:
    print('Aconteceu um erro:', e)
    return
    
  if None != arvore:
    err = False

    for err in listaErros:
      if 'ERROR' in listaErros[0]:
        print('\nNão é possível gerar código, devido a erros na análise semântica!')
        err = True
        break

    if not err:
      codeGenerator(argv[1], arvore, listaFuncoes, listaVariaveis, listaErros)
  
  else:
    print('\nHouve um erro ao realizar o processo')

if __name__ == "__main__":
  main()

