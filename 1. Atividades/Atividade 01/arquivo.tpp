inteiro: TAM_VETOR
TAM_VETOR := 10

inteiro: vetor[TAM_VETOR]
inteiro: numero

{metodo para preencher o vetor com numeros}
preenche_vetor()
	inteiro: auxiliar
	auxiliar = 0
	
	repita

		leia(numero)		
		vetor[auxiliar] = numero

        auxiliar := auxiliar + 1
	ate auxiliar == TAM_VETOR

fim

{metodo que realiza a busca de um determinado valor no vetor}
inteiro busca(inteiro: numero)
	
	inteiro: pos
	pos := 0
	
	repita
		
        se vetor[pos] == numero
            retorna(pos)
        fim

        pos := pos + 1
	
	ate pos == TAM_VETOR
	
	retorna(-1)
fim

{funcao principal do codigo}
inteiro principal()

    {preenche o vetor}
	preenche_vetor()
	
    {pega o numero a ser pesquisado}
	leia(numero)
	
    {realiza a busca}
	posicao = busca_binaria(numero)
	
    {mostra o resultado}
	escreva(posicao)
fim
