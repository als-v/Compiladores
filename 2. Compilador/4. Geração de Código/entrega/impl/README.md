# Geração de código da linguagem TPP

## Bibliotecas utilizadas:
- ply.lex: é um módulo da biblioteca ply, que é usado para o processo da análise léxica.
- sys: Este módulo fornece acesso a algumas variáveis usadas ou mantidas pelo interpretador e a funções que interagem fortemente com o interpretador.
- mytree: Este módulo fornece estruturas de dados: arvores prontas para serem utilizadas. 
- anytree: Este módulo fornece estruturas de dados: arvores prontas para serem utilizadas. 
- logging: Este módulo define funções e classes que implementam um sistema de logs flexíveis.
- llvmlite: Este módulo é necessário para escrever compiladores JIT.

## Para rodar deve-se executar o comando:
```python3 main.py [arquivo.tpp] [d] [st] [sta] [sm] [ar]```

Onde, o arquivo.tpp é o arquivo para a análise, e os parâmetros:
- 'd' é um parâmetro opcional que indica se a saída deve ser detalhada ou não.
- 'st' é um parâmetro opcional que indica se a saída deve apresentar a arvore sintatática e a arvore sintática abstrata.
- 'sta' é um parâmetro opcional que indica se a saída deve apresentar a tabela de símbulos.
- 'sm' é um parâmetro opcional que indica se a saída deve apresentar o modulo gerado.
- 'ar' é um parâmetro opcional que indica se após gerar o módulo deve ser compilado automaticamente.