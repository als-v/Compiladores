import llvmlite.binding as llvm
import llvmlite.ir as ll

# checa a variavel, e retorna ela
def checarVariavel(variavel, variaveis, escopo):
    for var in variaveis['global']:
        if variavel in var:
            variavel = var[variavel]
            return variavel

    return None

# funcao para pegar o valor da variavel
def pegarVariavel(variavel, escopo, variaveis):

    if escopo in variaveis:
        
        if any(variavel in var for var in variaveis[escopo]):
            variavelAchada = checarVariavel(variavel, variaveis, escopo)

        else:
            variavelAchada = checarVariavel(variavel, variaveis, escopo)
    else:
        variavelAchada = checarVariavel(variavel, variaveis, escopo)

    return variavelAchada

# realiza o bloco final do programa
def retorna_code(no, builder, tipoFuncao, funcao, escopo, variaveis):
    
    # bloco final
    bloco_final = funcao.append_basic_block('exit')
    builder.branch(bloco_final)
    builder.position_at_end(bloco_final)

    # caso o retorno tenha mais de um parametro
    if len(no.children) > 1:

        # pego os valores do retorno
        variavelEsquerda = no.children[0].name
        operacao = no.children[1].name
        variavelDireita = no.children[2].name

        # pego os valores
        variavelEsquerda = pegarVariavel(variavelEsquerda, escopo, variaveis)
        variavelDireita = pegarVariavel(variavelDireita, escopo, variaveis)

        # se for operacao de soma
        if operacao == '+':
            try:
                builder.ret(builder.add(variavelEsquerda, variavelDireita))
            except:
                pass

    # se nao tiver mais de um parametro  
    else:

        # flag para numerico
        num = False

        # caso o no seja um numero
        if no.children[0].name.isnumeric():
            num = True

            # se for inteiro ou flutuante
            if tipoFuncao == 'inteiro':
                retorno = int(no.children[0].name)
            else:
                retorno = float(no.children[0].name)
        
        # caso seja uma variavel
        else:
            retorno = no.children[0].name

        # se for inteiro ou flutuante
        if num:

            # pego o valor da variavel
            valor = ll.Constant(tipoLLVM(tipoFuncao), retorno)
            builder.ret(valor)
        
        # caso contrario, encontro o valor da variavel
        else:

            try:
                var = builder.load(pegarVariavel(retorno, escopo, variaveis))
            except:
                var = pegarVariavel(retorno, escopo, variaveis)

            builder.ret(var)

# funcao que retorna o tipo da variavel
def tipoLLVM(tipo):

    # se for inteiro
    if tipo == "inteiro":
        default_type = ll.IntType(32)
    
    # se for flutuante
    elif tipo == "flutuante":
        default_type = ll.FloatType()

    # se for void
    else:
        default_type = ll.VoidType()

    return default_type