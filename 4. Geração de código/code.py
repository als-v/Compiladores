import llvmlite.binding as llvm
import llvmlite.ir as ll
import geracao as g

variaveis = {'global': []}

def codeGenerator(file, arvore, listaFuncoes, listaVariaveis, listaErros):

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

    # gera o codigo
    generate(arvore, listaVariaveis, listaFuncoes, modulo)

# funcao para declarar variaveis globais
def variavel(no, listaVariaveis, modulo):
    sucesso = True
    varTipo = no.children[0].name
    varNome = no.children[1].name
    dimensao = 0
    dimensoes = []

    for var in listaVariaveis[varNome]:
        if var[1] == varTipo and var[4] == 'global':
            sucesso = True
            varDimensao = var[2]
            dimensoes = var[3]
    
    if sucesso:

        # tipo de variavel
        varLLVMTipo = g.tipoLLVM(varTipo)

        if dimensao > 0:
            varLLVMTipo = ll.IntType(32)

            for dimensao in dimensoes:
                varLLVMTipo = ll.ArrayType(varLLVMTipo, int(dimensao[0]))
            
        # cria a variavel
        var = ll.GlobalVariable(modulo, varLLVMTipo, varNome)

        # vejo a dimensão
        if dimensao == 0:

            if varTipo == 'inteiro':
                var.initializer = ll.Constant(varLLVMTipo, 0)
            else:
                var.initializer = ll.Constant(varLLVMTipo, 0.0)

        else:
            var.initializer = ll.Constant(varLLVMTipo, None)

        var.linkage = 'common'
        var.align = 4
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
        listaVariaveis[var[4]] = []
    
    # salvo ela
    variaveis[var[4]].append({var[0]: varLocal})

# funcao para verificar as funcoes
def function(no, listaFuncoes, listaVariaveis, modulo):
    global escopo, retorno
    retorno = False
    tipoFuncao = no.children[0].name
    
    if tipoFuncao not in ['inteiro', 'flutuante']:
        tipoFuncao = 'vazio'
        print('ENTROU AQUI')
        nomeFuncao = no.children[1].name
    else:
        # nomeFuncao = no.children[-2].name
        nomeFuncao = no.children[1].name

    escopo = nomeFuncao

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

    funcaoLLVM = ll.FunctionType(tipoRetorno, parametros)

    # declara a funcao
    labelNome = nomeFuncao

    # caso o nome da funcao seja principal, tem que alterar o nome
    if labelNome == 'principal':
        labelNome = 'main'

    # cria a funcao
    funcao = ll.Function(modulo, funcaoLLVM, name=nomeFuncao)

    # pelos indexs dos parametros
    for idx in range(len(listaFuncoes[nomeFuncao][0][3])):

        # pego o nome do parametro
        funcao.args[idx].name = listaFuncoes[nomeFuncao][0][3][idx]

        # se nao existir a variavel, cria
        if nomeFuncao not in listaVariaveis:
            listaVariaveis[nomeFuncao] = []
        
        # salvo
        listaVariaveis[nomeFuncao].append({listaFuncoes[nomeFuncao][0][3][idx]: funcao.args[idx]})

    # bloco inicio
    blocoInicio = funcao.append_basic_block(name='entry')
    builder = ll.IRBuilder(blocoInicio)

    for variavel in listaVariaveis:
        for var in listaVariaveis[variavel]:
            if var[4] == nomeFuncao:
                if var[0] not in listaFuncoes[var[4]][0][3]:
                    variavelLocal(var, builder)

    # passo pela arvore
    tree(no, builder, tipoFuncao, funcao, escopo, variaveis)

# andar pela arvore
def tree(no, builder, tipoFuncao, funcao, escopo, variaveis):
    global retorno

    if no.name == 'retorna':
        retorno = True
        g.retorna_code(no, builder, tipoFuncao, funcao, escopo, variaveis)
        # gen_retorna_code(node, builder, type_func, func)
        return

    for noFilho in no.children:
        tree(noFilho, builder, tipoFuncao, funcao, escopo, variaveis)

# funcao para gerar o codigo
def generate(arvore, listaVariaveis, listaFuncoes, modulo):

    # para cada no da arvore
    for no in arvore.children:

        # se for uma declaracao de variavel
        if no.name == 'declaracao_variaveis':
            variavel(no, listaVariaveis, modulo)

        # se for uma declaracao de funcao
        if no.name == 'declaracao_funcao':
            function(no, listaFuncoes, listaVariaveis, modulo)