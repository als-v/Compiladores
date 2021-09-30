inteiro busca_sequencial(inteiro: n, inteiro: size, inteiro: A)
  inteiro: y, res
  y := 0
  res = -1

  repita
    se A[i] == n
      res := 1
    fim

    i := i + 1

  ate i = size

  retorna(res)
fim

principal()
  inteiro: size

  leia(size)

  inteiro: i, A[size], n
  i := 0

  repita
    A[i] := i
    i := i + 1
  ate i = size

  leia(n)
  
  inteiro: resultado
  resultado := busca_sequencial(n, size, A)

  escreva(resultado)
fim