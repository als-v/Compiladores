inteiro e_sempre_dois(inteiro: n)
    n := 2
    escreva(n)
    se n = 2 então
        retorna(1)
    fim

    retorna(0)
fim

principal()
    inteiro: i
    
    leia(i)

    escreva(e_sempre_dois(i))
fim