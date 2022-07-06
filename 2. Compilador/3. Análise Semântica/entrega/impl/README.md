# Análise sintática da linguagem TPP

## Bibliotecas utilizadas:
- ply.lex: é um módulo da biblioteca ply, que é usado para o processo da análise léxica.
- sys: Este módulo fornece acesso a algumas variáveis usadas ou mantidas pelo interpretador e a funções que interagem fortemente com o interpretador.
- mytree: Este módulo fornece estruturas de dados: arvores prontas para serem utilizadas. 
- anytree: Este módulo fornece estruturas de dados: arvores prontas para serem utilizadas. 
- logging: Este módulo define funções e classes que implementam um sistema de logs flexíveis.

## Para instalar as dependencias:
```pip install -r requirements.txt ```

## Para rodar deve-se executar o comando:
```python3 code.py [arquivo.tpp] [d] [st] [sta]```

Onde, o arquivo.tpp é o arquivo para a análise que deve ser passado obrigatoriamente, e os parâmetros opcionais:
- 'd' é um parâmetro opcional que indica se a saída deve ser detalhada ou não.
- 'st' é um parâmetro opcional que indica se a saída deve apresentar a arvore sintatática.
- 'sta' é um parâmetro opcional que indica se a saída deve apresentar a tabela de símbulos.