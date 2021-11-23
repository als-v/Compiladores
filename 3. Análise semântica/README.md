# Análise semântica da linguagem TPP

## Bibliotecas utilizadas:
- ply.lex: é um módulo da biblioteca ply, que é usado para o processo da análise léxica.
- sys: Este módulo fornece acesso a algumas variáveis usadas ou mantidas pelo interpretador e a funções que interagem fortemente com o interpretador.
- mytree: Este módulo fornece estruturas de dados: arvores prontas para serem utilizadas. 
- anytree: Este módulo fornece estruturas de dados: arvores prontas para serem utilizadas. 
- logging: Este módulo define funções e classes que implementam um sistema de logs flexíveis.

## Para rodar deve-se executar o comando:
```python3 tppparser.py [arquivo.tpp] [detailed] [showTree] [showTable]```

Onde, o arquivo.tpp é o arquivo para a análise, e os parâmetros:
- 'detailed' é um parâmetro opcional que indica se a saída deve ser detalhada ou não.
- 'showTree' é um parâmetro opcional que indica se a saída deve apresentar a arvore sintatática e a arvore sintática abstrata.
- 'showTable' é um parâmetro opcional que indica se a saída deve apresentar a tabela de símbulos.