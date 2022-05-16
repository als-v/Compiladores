inteiro: A[10]
inteiro: B[10]

inteiro principal()
    inteiro: a
    inteiro: i
    i := 0

    repita
        leia(a)
        A[i] := a
        i := i + 1
    até i = 10

    i := 0
    repita
        B[9 - i] := A[i]
        i := i + 1
    até i = 10

    i := 0
    repita
        escreva(B[i])
        i := i + 1
    até i = 10    

    retorna(0)
fim
