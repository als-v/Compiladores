from sys import argv
import semantica as sem

def main():
    aux = argv[1].split('.')

    if aux[-1] != 'tpp':
      raise IOError("Not a .tpp file!")

    arvorePoda = sem.main(argv[1])

if __name__ == "__main__":
    main()

