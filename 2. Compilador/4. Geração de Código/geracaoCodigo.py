import llvmlite.binding as llvm
import llvmlite.ir as ll
import parser as p

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

varModule = []
funcModule = []

def returnLLVMType(type):
    if type.lower() == 'inteiro':
        return ll.IntType(32)
    elif type.lower() == 'flutuante':
        return ll.FloatType()

    return ll.VoidType()

def declareVarGlobal(variablesPD):

    # para cada uma das variaveis globais
    for var in variablesPD.values:
        if var[2] == 'global':

            # pego o tipo
            tipoLLVM = returnLLVMType(var[0])

            # se for um arranjo
            if len(var[5]) > 0:
                tipoLLVM = ll.ArrayType(tipoLLVM, len(var[5]))

            # crio a variavel
            varLLVM = ll.GlobalVariable(modulo, tipoLLVM, var[1])

            # caso seja um arranjo
            if len(var[5]) > 0:
                varLLVM.initializer = ll.Constant(tipoLLVM, None)
            
            # caso nao seja, verifico o tipo da variavel
            else:

                if var[0].lower() == 'inteiro':
                    varLLVM.initializer = ll.Constant(tipoLLVM, 0)
                else:
                    varLLVM.initializer = ll.Constant(tipoLLVM, 0.0)

            # linkagem/alinhamento
            varLLVM.linkage = 'common'
            varLLVM.align = 4
            
            # salvo a variavel
            varModule.append(['global', var[0], var[1], varLLVM])

def declareFunctions(dataPD, functionsPD):

    # para cada funcao
    for func in functionsPD.values:

        # variaveis auxiliares
        tipoLLVM = returnLLVMType(func[0])
        params = []

        # se tiver parametros
        if len(func[2]) > 0:

            # para cada parametro
            for param in func[2]:
                params.append(returnLLVMType(param[0]))

        funcLLVM = ll.FunctionType(tipoLLVM, params)

        functionName = func[1]

        if func[1] == 'principal':
            functionName = 'main'
        
        funcLLVM = ll.Function(modulo, funcLLVM, name=functionName)

        if len(func[2]) > 0:

            for idx, param in enumerate(func[2]):
                varModule.append([func[1], param[0], param[1], funcLLVM.args[idx]])

        funcModule.append([func[1], funcLLVM])

        funcInit = funcLLVM.append_basic_block('entry')
        builder = ll.IRBuilder(funcInit)

        declareAll(builder, dataPD, func[1], func[3], func[4])

def getLLVMFunction(funcName):
    for func in funcModule:
        if func[0] == funcName:
            return func
    
    return None

def getLLVMVarAux(varName, function):
    for var in varModule:
        if var[0] == function and var[2] == varName:
            return var
    
    return None

def getLLVMVar(varName, function):
    var = getLLVMVarAux(varName, function)

    if var is None:
        var = getLLVMVarAux(varName, 'global')

    return var

def declareVarEscope(builder, functionName, dataLine):
    typeVar = dataLine.values[0][0]
    typeLLVM = returnLLVMType(typeVar)
    nameVar = dataLine.values[2][1]

    varFunction = builder.alloca(typeLLVM, name=nameVar)
    
    if typeVar.lower() == 'inteiro':
        varFunction.initializer = ll.Constant(typeLLVM, 0)
    else:
        varFunction.initializer = ll.Constant(typeLLVM, 0.0)

    varFunction.align = 4
    varModule.append([functionName, typeVar, nameVar, varFunction])

def declareVarArray(builder, functionName, dataLine):
    print('NAO IMPLEMENTADO: declaracao array')

def declareVarMatrix(builder, functionName, dataLine):
    print('NAO IMPLEMENTADO: declaracao matrix')

def listAttr(varDir):
    listAttr = []

    for var in varDir.values:

        if var[0] == 'NUM_PONTO_FLUTUANTE' or var[0] == 'NUM_INTEIRO' or var[0] == 'ID':
            listAttr.append(var)

    return listAttr

def atribuition(builder, function, dataLine, line):

    intType = ll.IntType(32)
    floatType = ll.FloatType()

    # variavel a esquerda da atribuicao
    varEsq = dataLine.values[0][1]

    # variaveis a direita da atribuicao
    varDir = p.searchDataLineAfterToken2(dataLine, line, 'ATRIBUICAO')
    varLLVMDir = getLLVMVar(varEsq, function)[3]

    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(varDir)
    attr = listAttr(varDir) 
    loadAttr = []

    # para cada um deles
    for idx in range(qtdAttr):

        # se for um numero flutuante
        if attr[idx][0] == 'NUM_PONTO_FLUTUANTE':
            loadAttr.append(floatType(attr[idx][1]))

        # se for inteiro
        elif attr[idx][0] == 'NUM_INTEIRO':
            tipoAttr = returnLLVMType('inteiro')
            loadAttr.append(intType(attr[idx][1]))

        # se for um id
        elif attr[idx][0] == 'ID':
            varAttrLLVM = getLLVMVar(attr[idx][1], function)
           
            if None != varAttrLLVM:
                tipoAttr = returnLLVMType(varAttrLLVM[1])
                loadAttr.append(builder.load(varAttrLLVM[3]))
    
    if qtdAttr == 1:
        builder.store(loadAttr[0], varLLVMDir)
    elif qtdAttr == 2:
        if len(varDir.loc[varDir['token'] == 'MAIS']) > 0:
            expressao = builder.add(loadAttr[0], loadAttr[1])

        elif len(varDir.loc[varDir['token'] == 'MENOS']) > 0:
            expressao = builder.sub(loadAttr[0], loadAttr[1])

        builder.store(expressao, varLLVMDir)
    
    elif qtdAttr > 2:
        print('NAO IMPLEMENTADO: atribuicao com mais de 2 atributos')

def declareAll(builder, dataPD, funcName, lineStart, lineEnd):

    lineStart = lineStart + 1
    funcLLVM = getLLVMFunction(funcName)

    for line in range(lineStart, (lineEnd + 1)):
        dataLine = p.searchDataLine(dataPD, line)
        
        if len(dataLine.loc[dataLine['token'] == 'DOIS_PONTOS']) > 0:
            if len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) == 1:
                declareVarArray(builder, funcName, dataLine)
            elif len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) == 2:
                declareVarMatrix(builder, funcName, dataLine)
            else:
                declareVarEscope(builder, funcName, dataLine)

        if len(dataLine.loc[dataLine['token'] == 'ATRIBUICAO']) > 0:
            atribuition(builder, funcName, dataLine, line)

def codeGenerator(file, root, dataPD, functionsPD, variablesPD):
    
    declareVarGlobal(variablesPD)
    declareFunctions(dataPD, functionsPD)
    return modulo