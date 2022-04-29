inteiro: ano

inteiro modulo(inteiro:a,b)
	inteiro: numerador, denominador
	numerador := a
	denominador := b
	se (numerador < denominador) então
	  retorna (numerador)
	fim

	repita
		numerador := numerador - denominador
	até (numerador <= denominador)

	retorna(numerador)
fim

inteiro principal()
   leia(ano)

   se (modulo(ano,400) = 0) || (modulo(ano,4) = 0) && (!(modulo(ano,100) = 0)) então
      escreva(ano)
      escreva(1) {Verdadeiro}
   fim

   retorna(0)
fim
