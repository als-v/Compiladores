from sys import argv
import semantica as sem
from arvore import alteracoesArvore
from anytree.exporter import UniqueDotExporter
from anytree import RenderTree, AsciiStyle

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
  arvore = sem.main(argv[1], detailed, showTree, showTable)

  # caso de tudo certo
  if None != arvore:

    # arteracoes na arvore
    alteracoesArvore(arvore)
    
    # salvar a arvore
    UniqueDotExporter(arvore).to_picture(str(argv[1]) + '.poda.ast.png')
    
    if showTree:
      print('\nArvore sintatica podada:\n')
      print(RenderTree(arvore, style=AsciiStyle()).by_attr())
    
    print('\nPoda na arvore gerada com sucesso!\nArquivo: ' + argv[1] + '.poda.ast.png')
  
  else:
    print('\nHouve um erro ao realizar o processo')

if __name__ == "__main__":
  main()

