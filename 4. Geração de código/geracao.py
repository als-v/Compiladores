import llvmlite.binding as llvm
import llvmlite.ir as ll


# funcao para criacao do modulo
def iniciaModulo(file):

    # inicializa o modulo LLVM
    llvm.initialize()
    llvm.initialize_all_targets()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # cria o modulo
    modulo = ll.Module(str(file) + '.bc')
    modulo.triple = llvm.get_default_triple()

    target = llvm.Target.from_triple(modulo.triple)
    target_machine = target.create_target_machine()

    modulo.data_layout = target_machine.target_data

    escrevaInteiro = ll.Function(modulo, ll.FunctionType(ll.VoidType(), [ll.IntType(32)]), name="escrevaInteiro")
    leiaInteiro = ll.Function(modulo, ll.FunctionType(ll.IntType(32), []), name="leiaInteiro")
    escrevaFlutuante = ll.Function(modulo, ll.FunctionType(ll.VoidType(), [ll.FloatType()]), name="escrevaFlutuante")
    leiaFlutuante = ll.Function(modulo, ll.FunctionType(ll.FloatType(), []), name="leiaFlutuante")

    return modulo

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
def retorna(no, builder, tipoFuncao, funcao, escopo, variaveis):
    
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

        print(variavelEsquerda, operacao, variavelDireita)
        # se for operacao de soma
        if operacao == '+':
            try:
                builder.ret(builder.add(variavelEsquerda, variavelDireita))
            except:
                # problema ao declarar uma valor que nao é uma variavel
                pass

        # se for operacao de subtração
        elif operacao == '-':
            try:
                builder.ret(builder.sub(variavelEsquerda, variavelDireita))
            except:
                # problema ao declarar uma valor que nao é uma variavel
                pass

        # se for operacao de multiplicação
        elif operacao == '*':
            try:
                builder.ret(builder.mul(variavelEsquerda, variavelDireita))
            except:
                # problema ao declarar uma valor que nao é uma variavel
                pass

        # se for operacao de divisão
        elif operacao == '/':
            try:
                builder.ret(builder.sdiv(variavelEsquerda, variavelDireita))
            except:
                # problema ao declarar uma valor que nao é uma variavel
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

# metodo leia
def leia(no, builder, escopo, variaveis, leiaInteiro, leiaFlutuante):
    variavel = pegarVariavel(no.children[0].name, escopo, variaveis)

    tipoVariavel = variavel.type.pointee.intrinsic_name

    if tipoVariavel == 'i32':
        resultado = builder.call(leiaInteiro, [])
    else:
        resultado = builder.call(leiaFlutuante, [])

    builder.store(resultado, variavel, align=4)

# metodo escreva
def escreva(no, builder, tipoFuncao, funcao, escopo, variaveis, escrevaInteiro, escrevaFlutuante):
    print(no.children)
    variavel = pegarVariavel(no.children[0].name, escopo, variaveis)

    if None != variavel:
        tipo = variavel.type.pointee.intrinsic_name

    if tipo == 'i32':
        try:
            builder.call(escrevaInteiro, [variavel])
        except:
            builder.call(escrevaInteiro, [builder.load(variavel)])
    elif tipo == 'f32':
        try:
            builder.call(escrevaFlutuante, [variavel])
        except:
            builder.call(escrevaFlutuante, [builder.load(variavel)])
        
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