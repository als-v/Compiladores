{Condicional}
inteiro: idx

principal()
    inteiro: a
    idx := 0

	repita
        leia(a)

        se a > 0 então
            escreva(100)
        senão
            escreva(1)
        fim

        idx := idx + 1
    até idx < 10

fim
