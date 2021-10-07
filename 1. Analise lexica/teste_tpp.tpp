inteiro: a[10]
flutuante: b

inteiro func1(inteiro:x, flutuante:y)
  inteiro: res
  se (x > y) então
    res := x + y
  senão
    res := x * y
  fim
  retorna(res)
fim

func2(inteiro:z, flutuante:w)
  a := z
  b := w
fim

inteiro principal()
  inteiro: x,y
  flutuante: w
  a := 10 + 2
  leia(x)
  leia(w)
  w := .6 + 1.
  func2(1, 2.5)
  b := func1(x,w)
  escreva(b)
  retorna(0)
fim