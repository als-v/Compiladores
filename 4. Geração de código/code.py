import llvmlite.binding as llvm
import llvmlite.ir as ll
import geracao as g

# dic com as variaveis
variaveis = {'global': []}
funcoes = {}

# inicializa o modulo LLVM
llvm.initialize()
llvm.initialize_all_targets()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

# cria o modulo
modulo = ll.Module('modulo.bc')
modulo.triple = llvm.get_default_triple()

target = llvm.Target.from_triple(modulo.triple)
target_machine = target.create_target_machine()

modulo.data_layout = target_machine.target_data

# funcoes previamente declaradas
escrevaInteiro = ll.Function(modulo, ll.FunctionType(ll.VoidType(), [ll.IntType(32)]), name="escrevaInteiro")
leiaInteiro = ll.Function(modulo, ll.FunctionType(ll.IntType(32), []), name="leiaInteiro")
escrevaFlutuante = ll.Function(modulo, ll.FunctionType(ll.VoidType(), [ll.FloatType()]), name="escrevaFlutuante")
leiaFlutuante = ll.Function(modulo, ll.FunctionType(ll.FloatType(), []), name="leiaFlutuante")

# funcao de inicio
def codeGenerator(file, arvore, listaFuncoes, listaVariaveis, listaErros, showModule):

    # para cada no da arvore
    for no in arvore.children:

        # se for uma declaracao de variavel
        if no.name == 'declaracao_variaveis':
            variavel(no, listaVariaveis, modulo)

        # se for uma declaracao de funcao
        if no.name == 'declaracao_funcao':
            function(no, listaFuncoes, listaVariaveis, modulo)
    
    # crio um arquivo de saida
    arquivo = open(str(file)+'.ll', 'w')

    if showModule:
        # mostro o modulo
        print(str(modulo))

    # escrevo o modulo
    arquivo.write(str(modulo))
    arquivo.close()

    # executo funcoes 
    g.run(file)

# funcao para declarar variaveis globais
def variavel(no, listaVariaveis, modulo):

    # variaveis auxiliares
    sucesso = True
    varTipo = no.children[0].name
    varNome = no.children[1].name
    dimensao = 0
    dimensoes = []

    # pego a variavel
    for var in listaVariaveis[varNome]:

        # verifico se ela é global
        if var[1] == varTipo and var[4] == 'global':
            sucesso = True
            varDimensao = var[2]
            dimensoes = var[3]
    
    # caso seja global
    if sucesso:

        # tipo de variavel
        varLLVMTipo = g.tipoLLVM(varTipo)

        # caso tiver mais de uma dimensao
        if dimensao > 0:
            varLLVMTipo = ll.IntType(32)

            # declara cada uma delas
            for dimensao in dimensoes:
                varLLVMTipo = ll.ArrayType(varLLVMTipo, int(dimensao[0]))
            
        # cria a variavel
        var = ll.GlobalVariable(modulo, varLLVMTipo, varNome)

        # se for apenas uma dimensao
        if dimensao == 0:
            
            # se for inteiro/flutuante
            if varTipo == 'inteiro':
                var.initializer = ll.Constant(varLLVMTipo, 0)
            else:
                var.initializer = ll.Constant(varLLVMTipo, 0.0)

        # declarar a variavel como None
        else:
            var.initializer = ll.Constant(varLLVMTipo, None)

        # linkagem/alinhamento
        var.linkage = 'common'
        var.align = 4

        # salvo a variavel nao dic aux
        variaveis['global'].append({varNome: var})

# funcao para declarar variaveis locais
def variavelLocal(var, builder):

    # pega o tipo da variavel
    tipoVar = g.tipoLLVM(var[1])

    if var[2] > 0:
        tipoVar = g.tipoLLVM('inteiro')

        for dimensao in var[3]:
            tipoVar = ll.ArrayType(tipoVar, int(dimensao[0]))

    # cria a variavel
    varLocal = builder.alloca(tipoVar, name=var[0])

    # inicializa 
    if var[2] == 0:

        # se for inteiro
        if var[1] == 'inteiro':
            varLocal.initializer = ll.Constant(tipoVar, 0)
        
        # se for flutuante
        else:
            varLocal.initializer = ll.Constant(tipoVar, 0.0)

    else:
        varLocal.initializer = ll.Constant(tipoVar, None)

    varLocal.align = 4
    
    # caso a variavel nao exista
    if var[4] not in variaveis:
        variaveis[var[4]] = []
    
    # salvo ela
    variaveis[var[4]].append({var[0]: varLocal})

# funcao para verificar as funcoes
def function(no, listaFuncoes, listaVariaveis, modulo):

    # variaveis auxiliares
    global escopo, retorno
    retorno = False
    tipoFuncao = no.children[0].name

    # caso o tipo da funcao nao seja inteiro/flutuante
    if tipoFuncao not in ['inteiro', 'flutuante']:
        tipoFuncao = 'vazio'

    # nome da funcao
    nomeFuncao = no.children[1].name

    # o escopo e a funcao atual
    escopo = nomeFuncao

    # pego o retorno
    tipoRetorno = g.tipoLLVM(tipoFuncao)
    parametros = []

    # try/except para o caso de quando a variavel nao possui tipo de retorno (e necessario pegar o nome em outro filho)
    try:
        # para cada parametro da funcao
        for parametro in listaFuncoes[nomeFuncao][0][3]:

            # para cada um dos parametros
            for var in listaVariaveis[parametro]:

                # caso a varaivel seja da funcao
                if var[4] == nomeFuncao:

                    # pego o tipo dela e salvo nos parametros
                    tipoVar = g.tipoLLVM(var[1])
                    parametros.append(tipoVar)
    except:

        # pego o nome correto da funcao
        nomeFuncao = no.children[2].name

        # o escopo e a funcao atual
        escopo = nomeFuncao

        # pego o retorno
        tipoRetorno = g.tipoLLVM(tipoFuncao)
        parametros = []

        # para cada parametro da funcao
        for parametro in listaFuncoes[nomeFuncao][0][3]:

            # para cada um dos parametros
            for var in listaVariaveis[parametro]:

                # caso a varaivel seja da funcao
                if var[4] == nomeFuncao:

                    # pego o tipo dela e salvo nos parametros
                    tipoVar = g.tipoLLVM(var[1])
                    parametros.append(tipoVar)

    # tipo da funcao
    funcaoLLVM = ll.FunctionType(tipoRetorno, parametros)

    # declara a funcao
    labelNome = nomeFuncao

    # caso o nome da funcao seja principal, tem que alterar o nome para 'main'
    if labelNome == 'principal':
        labelNome = 'main'

    # cria a funcao
    funcao = ll.Function(modulo, funcaoLLVM, name=labelNome)

    # pelos indexs dos parametros
    for idx in range(len(listaFuncoes[nomeFuncao][0][3])):

        # pego o nome do parametro
        funcao.args[idx].name = listaFuncoes[nomeFuncao][0][3][idx]

        # se nao existir a variavel, cria
        if nomeFuncao not in listaVariaveis:
            variaveis[nomeFuncao] = []
            funcoes[nomeFuncao] = []
        
        # salvo
        variaveis[nomeFuncao].append({listaFuncoes[nomeFuncao][0][3][idx]: funcao.args[idx]})
        funcoes[nomeFuncao].append(funcao)

    # bloco inicio
    blocoInicio = funcao.append_basic_block(name='entry')
    builder = ll.IRBuilder(blocoInicio)

    # para nome das variaveis
    for variavel in listaVariaveis:

        # para cada variavel
        for var in listaVariaveis[variavel]:

            # se o escopo que está seja a funcao
            if var[4] == nomeFuncao:

                # se a variavel nao for global
                if var[0] not in listaFuncoes[var[4]][0][3]:

                    # declaro a variavel local
                    variavelLocal(var, builder)
                
                # caso seja global
                else:
                    
                    # verifico as variaveis declaradas na funcao
                    for varFuncao in variaveis[nomeFuncao]:

                        # caso ela nao tenha sido declarada
                        if var[0] not in varFuncao:

                            # declaro a variavel local
                            variavelLocal(var, builder)

    # processar a arvore
    tree(no, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)

    # caso a funcao nao tenha retorno
    if not retorno:
        
        # crio o bloco de saida
        finalBlock = funcao.append_basic_block(name='exit')
        builder.branch(finalBlock)

        builder.position_at_end(finalBlock)

        # caso o tipo da funcao seja inteiro/flutuante
        if tipoFuncao != 'vazio':

            # valor para a saida
            Zero64 = ll.Constant(tipoRetorno, 0)

            # valor de retorno
            valorRetorno = builder.alloca(tipoRetorno, name='retorno')
            builder.store(Zero64, valorRetorno)

            valorRetornoAux = builder.load(valorRetorno, name='ret_temp', align=4)

            # retorno
            builder.ret(valorRetornoAux)

        else:

            # retorno vazio
            builder.ret_void()

        # atualizo as variaveis
        listaFuncoes[nomeFuncao] = funcao
        escopo = 'global'

# andar pela arvore
def tree(no, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao):

    # variavel auxiliar
    global retorno

    # caso seja uma funcao retorna
    if no.name == 'retorna':
        retorno = True
        retorna(no, builder, tipoFuncao, funcao)
        return

    # caso seja uma funcao leia
    elif no.name == 'leia':
        leia(no, builder)
        return

    # caso seja uma funcao escreva
    elif no.name == 'escreva':
        escreva(no, builder, listaFuncoes)
        return

    # caso seja uma atribuicao
    elif no.name == ':=':
        atribuicao(no, builder, listaFuncoes, listaVariaveis)
        return

    # caso seja uma funcao se
    elif no.name == 'se':
        se(no, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)
        return

    # caso seja uma funcao repita
    elif no.name == 'repita':
        repita(no, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)
        return

    # caso seja uma funcao
    elif no.name in listaFuncoes:
        chamadaFuncao(no, builder, listaFuncoes)
        return

    # passo por todos os nos
    for noFilho in no.children:
        tree(noFilho, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)

# chamada de funcoes
def chamadaFuncao(no, builder, listaFuncoes):

    # variaveis auxiliares
    tipoInt = ll.IntType(32)
    nomeFuncao = no.name

    parametros = []
    pai = no.parent

    # passo pela arvore, pegando os parametros
    for noFilho in pai.children:
        if noFilho != no:
            parametros.append(noFilho)

    # caso tenha parametro
    if len(parametros) == 1:

        # nome
        parametro = parametros[0].name

        # se for numerico
        if parametro.isnumeric():

            # pego a funcao e o tipo do parametro
            funcao = listaFuncoes[nomeFuncao]
            tipoParametro = funcao.args[0].type.intrinsic_name

            # se for inteiro/flutuante
            if 'i32' in tipoParametro:
                value = tipoInt(int(parametro))

            else:
                value = ll.Constant(ll.FloatType, float(parametro))
            
            # builda
            builder.call(funcao, [value])

# funcao repita
def repita(no, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao):

    # variaveis auxiliares
    comparacao = []
    comparacao.append(no.children[3].name)

    tipoComparacao = no.children[2].children[0].name
    comparacao.append(no.children[4].name)

    # altero a comparacao para '=='
    if tipoComparacao == '=':
        tipoComparacao = '=='
    
    # variaveis auxiliares
    tipoInt = ll.IntType(32)

    varComper = builder.alloca(ll.IntType(32), name='var_comper')
    valueExists = True

    # para cada um
    for idx in range(len(comparacao)):

        # se ja tiver sido declarado
        if comparacao[idx] in variaveis:
            pass
        
        # caso seja uma valor inteiro/flutuante
        elif pegarVariavel(comparacao[idx]) == None:

            valueExists = False

            # conversao para inteiro/flutuante
            try:
                value = int(comparacao[idx])
            except:
                value = int(comparacao[idx+1])

            # salvo o valor
            builder.store(tipoInt(value), varComper)
            comparacao[idx] = ll.Constant(ll.IntType(32), tipoInt(value))
        
        # caso exista
        else:

            # pego o valor
            comparacao[idx] = pegarVariavel(comparacao[idx])
    
    # bloco de repeticao
    loop = builder.append_basic_block(name='loop')
    loopVal = builder.append_basic_block(name='loop_val')
    loopEnd = builder.append_basic_block(name='loop_end')

    builder.branch(loop)
    builder.position_at_end(loop)

    # passo pela condicao
    tree(no.children[0], builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)
    
    builder.branch(loopVal)
    builder.position_at_end(loopVal)

    # se o valor existe
    if valueExists:

        # caso um dos valores eja ponteiro e outro nao
        if comparacao[0].type.is_pointer and not comparacao[1].type.is_pointer:
            expressao = builder.icmp_signed(tipoComparacao, builder.load(comparacao[0]), comparacao[1], name='expression')

        # caso os dois valores sejam ponteiros
        elif comparacao[0].type.is_pointer and comparacao[1].type.is_pointer:
            expressao = builder.icmp_signed(tipoComparacao, builder.load(comparacao[0]), builder.load(comparacao[1]), name='expression')

        # caso os dois valores nao sejam ponteiros
        else:
            expressao = builder.icmp_signed(tipoComparacao, comparacao[0], comparacao[1], name='expression')
    
    # caso nao exista
    else:

        # caso os valores sejam ponteiros
        if comparacao[0].type.is_pointer and varComper.type.is_pointer:
            expressao = builder.icmp_signed(tipoComparacao, builder.load(comparacao[0]), builder.load(varComper), name='expression')

        # caso um dos valores seja ponteiro e outro nao
        elif not comparacao[0].type.is_pointer and varComper.type.is_pointer:
            expressao = builder.icmp_signed(tipoComparacao, comparacao[0], builder.load(varComper), name='expressionn')

    # caso seja uma comparacao
    if tipoComparacao == '==':
        # builda
        builder.cbranch(expressao, loopEnd, loop)

    else:
        # builda
        builder.cbranch(expressao, loop, loopEnd)

    # bloco
    builder.position_at_end(loopEnd)

# funcao se
def se(no, builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao):
    
    # quantidade de condicoes
    if no.children[0].name == 'corpo' and no.children[0].name == 'corpo':
        condicoes = 1
    elif no.children[1].name == 'corpo':
        condicoes = 2
    else:
        condicoes = 1

    # crio um bloco para cada condicao
    if condicoes == 2:
        seTrue = funcao.append_basic_block('iftrue')
        seFalse = funcao.append_basic_block('iffalse')
        seEnd = funcao.append_basic_block('ifend')
    else:
        seTrue = funcao.append_basic_block('iftrue')
        seEnd = funcao.append_basic_block('ifend')

    comparacoes = []
    comparacoes.append(no.children[3].name)

    tipoComparacao = no.children[2].children[0].name

    # comparacao tem que ser '=='
    if tipoComparacao == '=':
        tipoComparacao = '=='

    # variaveis euxiliares
    comparacoes.append(no.children[4].name)

    tipoInteiro = ll.IntType(32)
    varComperRight = builder.alloca(ll.IntType(32), name='var_comper_right')
    varComperLeft = builder.alloca(ll.IntType(32), name='var_comper_left')

    # passo por cada um
    for idx in range(len(comparacoes)):

        # ignoro caso ela esteja na lista de variaveis
        if comparacoes[idx] in variaveis:
            pass

        # caso seja um valor inteiro/flutuante
        elif pegarVariavel(comparacoes[idx]) == None:
            
            # realizo a conversao para inteiro/flutuante
            try:
                value = int(comparacoes[idx])
            except:
                value = int(comparacoes[idx+1])

            # armazeno o valor na variavel
            builder.store(tipoInteiro(value), varComperRight)
            comparacoes[idx] = ll.Constant(tipoInteiro, tipoInteiro(value))

        # caso a variavel exista
        else:

            # pego seu valor
            comparacoes[idx] = pegarVariavel(comparacoes[idx])

            # armazeno o valor na variavel
            if comparacoes[idx].type.intrinsic_name == 'p0i32':
                varComperLeft = comparacoes[idx]

            else:
                builder.store(comparacoes[idx], varComperLeft)

    # comparacao
    ifState = builder.icmp_signed(tipoComparacao, varComperLeft, varComperRight, name='if_state')

    if condicoes == 2:
        builder.cbranch(ifState, seTrue, seFalse)
    else:
        builder.cbranch(ifState, seTrue, seEnd)

    builder.position_at_end(seTrue)

    # passo pela condicao
    tree(no.children[0], builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)

    try:
        # buildar o bloco de codigo
        builder.branch(seEnd)

    except:
        pass

    # caso tenha mais de uma condicao
    if condicoes == 2:

        # ultimo bloco
        builder.position_at_end(seFalse)

        # passo pela condicao
        tree(no.children[1], builder, tipoFuncao, listaFuncoes, listaVariaveis, funcao)

        try:
            # buildar o bloco de codigo
            builder.branch(seEnd)

        except:
            pass
    
    # ultimo bloco
    builder.position_at_end(seEnd)

# funcao para pegar o valor da variavel
def pegarVariavel(variavel):
    achado = False

    if escopo in variaveis:
        
        if any(variavel in var for var in variaveis[escopo]):
            # variavelAchada = checarVariavel(variavel, variaveis, escopo)
            for var in variaveis[escopo]:
                if variavel in var:
                    variavel = var[variavel]
                    achado = True
                    break

        else:
            # variavelAchada = checarVariavel(variavel, variaveis, 'global')
            for var in variaveis['global']:
                if variavel in var:
                    variavel = var[variavel]
                    achado = True
                    break
    else:
        # variavelAchada = checarVariavel(variavel, variaveis, 'global')
        for var in variaveis['global']:
            if variavel in var:
                variavel = var[variavel]
                achado = True
                break

    if achado:
        return variavel

    return None

# realiza o bloco final do programa
def retorna(no, builder, tipoFuncao, funcao):
    
    # caso seja a funcao principal
    # if funcao.name == 'main':

    # crio o bloco final da funcao
    bloco_final = funcao.append_basic_block('exit')
    builder.branch(bloco_final)
    builder.position_at_end(bloco_final)

    # caso o retorno tenha mais de um parametro
    if len(no.children) > 1:

        # pego os valores do retorno
        variavelEsquerdaLabel = no.children[0].name
        operacao = no.children[1].name
        variavelDireitaLabel = no.children[2].name

        # pego apenas os 2 primeiros valores (deve-se pegar todos de forma recursiva??)
        variavelEsquerda = pegarVariavel(variavelEsquerdaLabel)
        variavelDireita = pegarVariavel(variavelDireitaLabel)

        # se for operacao de soma
        if operacao == '+':
            
            # caso seja um ponteiro
            if 'i32*' in str(variavelDireita.type):
                variavelDireita = builder.load(variavelDireita)

            if 'i32*' in str(variavelEsquerda.type):
                variavelEsquerda = builder.load(variavelEsquerda)

            builder.ret(builder.add(variavelEsquerda, variavelDireita))
        # se for operacao de subtração
        elif operacao == '-':

            # caso seja um ponteiro
            if 'i32*' in str(variavelDireita.type):
                variavelDireita = builder.load(variavelDireita)

            if 'i32*' in str(variavelEsquerda.type):
                variavelEsquerda = builder.load(variavelEsquerda)

            builder.ret(builder.sub(variavelEsquerda, variavelDireita))

        # se for operacao de multiplicação
        elif operacao == '*':

            # caso seja um ponteiro
            if 'i32*' in str(variavelDireita.type):
                variavelDireita = builder.load(variavelDireita)

            if 'i32*' in str(variavelEsquerda.type):
                variavelEsquerda = builder.load(variavelEsquerda)

            builder.ret(builder.mul(variavelEsquerda, variavelDireita))

        # se for operacao de divisão
        elif operacao == '/':

            # caso seja um ponteiro
            if 'i32*' in str(variavelDireita.type):
                variavelDireita = builder.load(variavelDireita)

            if 'i32*' in str(variavelEsquerda.type):
                variavelEsquerda = builder.load(variavelEsquerda)

            builder.ret(builder.sdiv(variavelEsquerda, variavelDireita))
        
        else:

            try:
                variavelDireitaLabel = pegarVariavel(variavelDireitaLabel)
                builder.ret(builder.add(variavelDireitaLabel, variavelDireitaLabel))
            except:
                operacao = pegarVariavel(operacao)
                builder.ret(builder.add(operacao, operacao))

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
            valor = ll.Constant(g.tipoLLVM(tipoFuncao), retorno)

            # builda o valor
            builder.ret(valor)
        
        # caso contrario, encontro o valor da variavel
        else:
            
            try:
                # tento pegar caso ela ja tenha sido declarada
                var = builder.load(pegarVariavel(retorno))

            except:
                # caso ela nao tenha sido declarada
                var = pegarVariavel(retorno)

            # builda o valor
            builder.ret(var)

# metodo leia
def leia(no, builder):

    # variaveis auxiliares
    nome = no.children[0].name
    variavel = pegarVariavel(nome)

    # tipo da variavel
    tipoVariavel = variavel.type.pointee.intrinsic_name

    # caso seja inteiro/flutuante
    if 'i32' in tipoVariavel:
        resultado = builder.call(leiaInteiro, [])
    else:
        resultado = builder.call(leiaFlutuante, [])

    # guardo o valor na variavel
    builder.store(resultado, variavel, align=4)

# metodo escreva
def escreva(no, builder, listaFuncoes):

    # caso tenha apenas um parametro na funcao escreva
    if len(no.children) == 1:

        # pego a variavel
        variavel = pegarVariavel(no.children[0].name)

        # defino variaveis auxiliares
        label = ''
        tipo = ''

        # caso nao seja uma variavel declarada, e sim um numero
        if variavel == None:

            # realizo a conversao para inteiro/flutuante afim de descobrir seu tipo
            try:
                variavel = int(no.children[0].name)
                label = 'inteiro'

            except:
                variavel = float(no.children[0].name)
                label = 'float'

        try:
            # caso seja uma variavel declarada, consigo pegar seu tipo
            tipo = variavel.type.pointee.intrinsic_name
        
        except:
    
            try:
                # caso ainda seja uma variavel declarada, outro metodo para retornar seu tipo
                tipo = variavel.type.intrinsic_name

            except:

                # caso seja um numero inteiro/flutuante, defino seu tipo
                if label == 'inteiro':
                    tipo = ll.IntType(32)

                elif label == 'float':
                    tipo = ll.FloatType()
        
        # caso seja inteiro/flutuante
        if 'i32' in str(tipo):

            try:
                # caso seja uma variavel declarada e carregada
                builder.call(escrevaInteiro, [variavel])

            except:

                try:
                    # carrego a variavel
                    builder.call(escrevaInteiro, [builder.load(variavel)])
                
                except:
                    pass

        elif tipo == 'f32':

            try:
                # caso seja uma variavel declarada e carregada
                builder.call(escrevaFlutuante, [variavel])

            except:
                # carrego a variavel
                builder.call(escrevaFlutuante, [builder.load(variavel)])

    # caso tenha mais de um parametro na funcao escreva (funcao e parametro)
    elif len(no.children) == 2:

        # variaveis auxiliares
        nomeLabel = None
        nome = None
        varCall = None

        # pego o nome caso nao tenha algum erro
        for n in no.children:
            if 'ERROR' not in n.name:
                nomeLabel = n.name
                nome = n.name
        
        # caso tenha seu nome
        if None != nome:

            # pego a variavel
            nome = pegarVariavel(nome)

            # para todas os escopos
            for var in variaveis:

                # verifico se a variavel esta no escopo, ou se ela e global
                if var == escopo or var == 'global':
                    
                    # try/except pois pode ser que o escopo nao exista
                    try:

                        # caso a funcao esteja no escopo
                        if nomeLabel in variaveis[var][0]:

                            # pego seu valor
                            varCall = variaveis[var][0][nomeLabel]

                    except:
                        pass

            try:
                # pego o tipo da variavel
                tipo = varCall.type.pointee.return_type.intrinsic_name

            except:

                try:
                    # pego o tipo da variavel
                    tipo = varCall.type.intrinsic_name

                except:
                    # defino inteiro
                    tipo = 'p0i32'

            # pego a variavel
            variavel = pegarVariavel(no.children[1].name)

            # para todas as funcoes
            for var in variaveis:

                # caso a variavel esteja no escopo ou no escopo global
                if var == escopo or var == 'global':

                    # try/except pois pode ser que o escopo nao exista
                    try:

                        # caso a funcao esteja no escopo
                        if nomeLabel in variaveis[var][0]:

                            # pego seu valor
                            varCall = variaveis[var][0][nomeLabel]

                    except:
                        pass
            
            # problema ao buildar a funcao
            try:

                # crio o valor
                escreva = builder.call(varCall, args=[builder.load(variavel)])

                # caso seja inteiro/flutuante
                if 'i32' in str(tipo):
                    builder.call(escrevaInteiro, args=[escreva])

                else:
                    builder.call(escrevaFlutuante, args=[escreva])

            except:
                pass

    # caso seja um arranjo com uma posicao especifica
    elif len(no.children) == 4:

        # variaveis auxiliares
        tipoInt = ll.IntType(32)

        nome = no.children[0].name
        indexLabel = no.children[2].name

        variavel = pegarVariavel(nome)
        index = builder.load(pegarVariavel(indexLabel))
        
        # problema ao buildar uma variavel em uma posicao especifica
        try:
            valorExp = builder.gep(variavel, [tipoInt(0), tipoInt(index)], name=str(nome)+'['+str(indexLabel)+']')
        except:
            valorExp = builder.gep(variavel, [index], name=str(nome)+'['+str(indexLabel)+']')
        
        # expressao
        expressao = builder.load(valorExp, align=4)

        try:
            # pego o tipo da variavel
            tipo = variavel.type.pointee.return_type.intrinsic_name

        except:

            try:
                # pego o tipo da variavel
                tipo = variavel.type.intrinsic_name

            except:
                # defino inteiro
                tipo = 'i32'
        
        # caso seja inteiro/flutuante
        try:
            builder.call(escrevaFlutuante, args=[expressao])
        except:
            builder.call(escrevaInteiro, args=[expressao])

# atribuicao
def atribuicao(no, builder, listaFuncoes, listaVariaveis):

    # variaveis auxiliares
    tipoFloat = ll.FloatType()
    tipoInt = ll.IntType(32)

    recebeu = True
    direita, esquerda = g.auxArrays(no.parent)
    variavel = None

    # caso tenha apenas uma variavel/valor a esquerda
    if len(esquerda) == 1:
        variavel = pegarVariavel(esquerda[0])

    # caso tenha mais de uma variavel/valor a esquerda
    else:
        
        # pego a variavel
        variavelEsquerda = pegarVariavel(esquerda[0])

        # tamanho
        if len(esquerda) == 4:

            # variavel a esquerda
            var = pegarVariavel(esquerda[2])

            # caso nao seja um numero
            if None != var:

                try:
                    # expressao e variavel
                    expressao = builder.load(var)
                    variavel = builder.gep(variavelEsquerda, [tipoInt(0), expressao])

                except:
                    # expressao e variavel
                    expressao = builder.load(var)
                    variavel = builder.gep(variavelEsquerda, [expressao])

        # temanho
        else:

            # variavel auxiliar
            expressoes = []

            # para todas as variaveis
            for idx in [esquerda[2], esquerda[4]]:

                # caso seja numerico
                if idx.isnumeric():

                    # adiciono a variavel
                    expressoes.append(tipoInt(idx))

                # caso seja uma variavel
                else:

                    # pego a variavel
                    var = pegarVariavel(idx)
                    
                    # se ela existir
                    if var != None:

                        # carrego seu valor
                        expressoes.append(builder.load(var))

            # pego a operacao
            operacao = esquerda[3]

            # se for soma
            if operacao == '+':
                expressao = builder.add(expressoes[0], expressoes[1], name=esquerda[0]+'_'+esquerda[2]+esquerda[3]+esquerda[4], flags=())
            
            # se for subtracao
            if operacao == '-':
                expressao = builder.sub(expressoes[0], expressoes[1], name=esquerda[0]+'_'+esquerda[2]+esquerda[3]+esquerda[4], flags=())

    try:
        # pego o tipo da variavel
        tipo = variavel.type.pointee.return_type.intrinsic_name

    except:

        try:
            # pego o tipo da variavel
            tipo = variavel.type.intrinsic_name

        except:
            # defino inteiro
            tipo = 'i32'

    # caso seja inteiro/flutuante
    if 'i32' in str(tipo):
        expressao = ll.Constant(ll.IntType(32), 0)
        valorE = 0

    else:
        expressao = ll.Constant(ll.FloatType(), 0.0)
        valorE = 0.0

    # variaveis auxiliares
    idx = 0
    next_operation = 'add'

    # enquanto tiver 'operacoes'
    while idx < len(direita):

        # verifico se e inteiro/flutuante
        if 'i32' in str(tipo):
            expressaoT = ll.Constant(ll.IntType(32), 0)
            valorT = 0
        else:
            expressaoT = ll.Constant(ll.FloatType(), 0.0)
            valorT = 0.0

        # caso nao for operacao
        if direita[idx] != '+' and direita[idx] != '-' and direita[idx] != '*':

            # caso nao for inteiro
            if 'i32' not in str(tipo):

                # se o valor nao tiver nas variaveis
                if direita[idx] not in variaveis and pegarVariavel(direita[idx]) == None:

                    try:
                        # pego seu valor
                        valor = float(direita[idx])
                        expressaoT = ll.Constant(ll.FloatType(), valor)
                        valorT = valor

                    except:
                        pass

            # caso seja inteiro
            if direita[idx].isnumeric():

                # pego seu valor
                valor = int(direita[idx])
                expressaoT = ll.Constant(ll.IntType(32), valor)
                valorT = valor
            
            # caso seja funcao
            elif direita[idx] in variaveis:

                # variaveis auxiliares para a funcao
                numVar = listaFuncoes[direita[idx]][0][2]
                funcao = funcoes[direita[idx]][0]
                args = []
                aux  = 0

                # pera todas as variaveis
                for nxtIdx in range(idx+1, idx+numVar+1):

                    # se for inteiro
                    if direita[nxtIdx].isnumeric():

                        # pego seus parametros
                        nomeParam = listaFuncoes[direita[idx]][0][3][aux]
                        tipoParam = listaVariaveis[nomeParam][0][1]

                        # se for inteiro/flutuante
                        if tipoParam == 'inteiro':
                            valorParam = int(direita[nxtIdx])
                            args.append(ll.Constant(ll.IntType(32), valorParam))
                        else:
                            valorParam = float(direita[nxtIdx])
                            args.append(ll.Constant(ll.FloatType(), valorParam))

                    # caso nao existe
                    elif pegarVariavel(direita[nxtIdx]) == None:

                        try:
                            # pego seu valor
                            valorParam = float(direita[nxtIdx])
                            args.append(ll.Constant(ll.FloatType(), valorParam))

                        except:
                            pass

                    # caso exista
                    else:
                        # pego seu valor
                        args.append(builder.load(pegarVariavel(direita[nxtIdx])))
                    
                    # incremento
                    aux += 1
                
                tipo = listaFuncoes[direita[idx]][0][1]
                
                if tipo == 'inteiro':
                    tipo = ll.IntType(32)
                else:
                    tipo = ll.FloatType()
                
                try:
                    expressaoT = builder.call(funcao, args)
                except:
                    pass

                # incremento
                idx += idx + numVar
            
            elif pegarVariavel(direita[idx]) != None:
                expressaoT = pegarVariavel(direita[idx])

                if 'i32' in str(tipo):
                    
                    try:
                        expressaoT = builder.load(expressaoT)

                    except:
                        pass

                valorT = direita[idx]

        # caso não for variavel, e sim valor
        elif pegarVariavel(direita[idx]) != None:

            # se for inteiro
            if 'i32' in str(tipo):

                # arranjo
                if len(direita) > idx and direita[idx+1] == '[':

                    # variaveis auxiliriares
                    arrVar = direita[idx]
                    idxVar = direita[idx+2]

                    # pego o arranjo
                    arrVar = pegarVariavel(arrVar)
                    idxVarLoad = builder.load(pegarVariavel(idxVar))

                    # salvo o valor
                    arrVarPos = builder.gep(arrVar, [tipoInt(0), idxVarLoad], name=str(direita[idx])+'['+str(direita[idx+2])+']')
                    expressaoT = builder.load(arrVarPos, align=4)

                    # incremento
                    idx += 3
                
                # caso nao seja arranjo
                else:
                    
                    try:
                        # carrego o valor da variavel
                        expressaoT = builder.load(pegarVariavel(direita[idx+1]))

                    except:
                        # carrego o valor da variavel
                        expressaoT = pegarVariavel(direita[idx+1])

                        # caso nao exista
                        if None == expressaoT:
                            label = '' 

                            # converto para inteiro/flutuante para descobrir seu tipo
                            try:
                                valor = int(direita[idx+1])
                                label = 'inteiro'
                            except:
                                valor = float(direita[idx+1])
                                label = 'flutuante'
                            
                            # crio a variavel inteiro/flutuante
                            if label == 'inteiro':
                                expressaoT = ll.Constant(ll.IntType(32), valor)
                                valorT = valor

                            else:
                                expressaoT = ll.Constant(ll.FloatType(), valor)
                                valorT = valor
        
        # caso seja soma
        if next_operation == 'add':
            
            # caso ambos forem flutuantes
            if 'i32' not in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                
                try:
                    expressao = builder.fadd(expressao, expressaoT, name='expressao', flags=())
                
                except:

                    try:
                        expressao = builder.fadd(builder.load(expressao), expressaoT, name='expressao', flags=())
                    
                    except:

                        try:
                            expressao = builder.fadd(expressao, builder.load(expressaoT), name='expressao', flags=())
                        
                        except:

                            try:
                                expressao = builder.fadd(builder.load(expressao), builder.load(expressaoT), name='expressao', flags=())

                            except:
                                print('Erro ao somar')
                                pass

            # caso ambos forem inteiros
            elif 'i32' in expressao.type.intrinsic_name and 'i32' in expressaoT.type.intrinsic_name:
                expressao = builder.add(expressao, expressaoT, name='expressao', flags=())

            # caso tenha os dois tipos
            else:
                
                # se um for flutuante e outro inteiro
                if 'i32' in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                    valorAlt = float(valorT)
                    expressaoT = ll.Constant(ll.FloatType(), valorAlt)
                    expressao = builder.fadd(expressao, expressaoT, name='expressao', flags=())

                # se um for inteiro e outro flutuante
                elif 'i32' in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                    valorAlt = float(valorE)
                    expressao = ll.Constant(ll.FloatType(), valorAlt)
                    expressao = builder.fadd(expressao, expressaoT, name='expressao', flags=())

        # caso seja subtracao
        if next_operation == 'sub':
            
            # caso ambos forem flutuantes
            if 'i32' not in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                expressao = builder.fsub(expressao, expressaoT, name='expressao', flags=())

            # caso ambos forem inteiros
            elif 'i32'  in expressao.type.intrinsic_name and  'i32' in expressaoT.type.intrinsic_name:
                expressao = builder.sub(expressao, expressaoT, name='expressao', flags=())

            # caso tenha os dois tipos
            else:

                # se um for flutuante e outro inteiro
                if 'i32' not in expressao.type.intrinsic_name and 'i32' in expressaoT.type.intrinsic_name:
                    valorAlt = float(valorT)
                    expressaoT = ll.Constant(ll.FloatType(), valorAlt)
                    expressao = builder.fsub(expressao, expressaoT, name='expressao', flags=())

                # se um for inteiro e outro flutuante
                elif 'i32' in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                    valorAlt = float(valorE)
                    expressao = ll.Constant(ll.FloatType(), valorAlt)
                    expressao = builder.fsub(expressao, expressaoT, name='expressao', flags=())

        # caso seja multiplicacao
        elif next_operation == 'mul':

            # caso ambos forem flutuantes
            if 'i32' not in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                expressao = builder.fmul(expressao, expressaoT, name='expressao', flags=())

            # caso ambos forem inteiros
            elif 'i32' in expressao.type.intrinsic_name and 'i32' in expressaoT.type.intrinsic_name:
                expressao = builder.mul(expressao, expressaoT, name='expressao', flags=())

            # caso tenha os dois tipos
            else:

                # se um for flutuante e outro inteiro
                if 'i32' not in expressao.type.intrinsic_name and 'i32' in expressaoT.type.intrinsic_name:
                    valorAlt = float(valorT)
                    expressaoT = ll.Constant(ll.FloatType(), valorAlt)
                    expressao = builder.fmul(expressao, expressaoT, name='expressao', flags=())

                # se um for inteiro e outro flutuante
                elif 'i32' in expressao.type.intrinsic_name and 'i32' not in expressaoT.type.intrinsic_name:
                    valorAlt = float(valorE)
                    expressao = ll.Constant(ll.FloatType(), valorAlt)
                    expressao = builder.fmul(expressao, expressaoT, name='expressao', flags=())
        
        # caso nao seja nenhum dos casos acima
        else:
            
            # try/except pois em alguns casos direita[idx] nao existe
            try:
                # soma
                if direita[idx] == '+':
                    next_operation = 'add'
                
                # subtracao
                elif direita[idx] == '-':
                    next_operation = 'sub'

                # multiplicacao
                elif direita[idx] == '*':
                    next_operation = 'mul'

            except:
                pass

        # incremento
        idx+=1
    
    try:
        # salvo
        builder.store(expressao, variavel)
    except:
        # erro aqui **
        pass