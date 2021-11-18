from sys import argv
import semantica as sem

def main():
    showTree = False
    detailed = False
    aux = argv[1].split('.')

    if aux[-1] != 'tpp':
      raise IOError("Not a .tpp file!")
    if 'showTree' in argv:
      print("a")
      showTree = True
    if 'detailed' in argv:
      detailed = True

    arvorePoda = sem.main(argv[1], detailed, showTree)

if __name__ == "__main__":
    main()

