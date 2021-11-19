from sys import argv
import semantica as sem
from arvore import alteracoesArvore
from anytree.exporter import UniqueDotExporter

def main():
    showTree = False
    detailed = False
    aux = argv[1].split('.')

    if aux[-1] != 'tpp':
      raise IOError("Not a .tpp file!")
    if 'showTree' in argv:
      showTree = True
    if 'detailed' in argv:
      detailed = True

    arvore = sem.main(argv[1], detailed, showTree)

    if None != arvore:
      alteracoesArvore(arvore)
      
      UniqueDotExporter(arvore).to_picture(str(argv[1]) + '.poda.unique.ast.png')
      print('\nPoda na arvore gerada com sucesso!')
    
    else:
      print('\nHouve um erro ao realizar o processo')

if __name__ == "__main__":
    main()

