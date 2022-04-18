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

        funcModule.append([func[1], funcLLVM, func[0]])

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

def listOp(varDir):
    listOp = []

    for var in varDir.values:

        if var[0] == 'MENOS' or var[0] == 'MAIS' or var[0] == 'MULTIPLICACAO' or var[0] == 'DIVISAO':
            listOp.append(var)

    return listOp 

def findAttr(varDir, attrLLVM, token, idx):
    columnValue = varDir.loc[varDir['token'] == token]['coluna'].values[idx]
    dataAfterToken = varDir.loc[varDir['coluna'] > columnValue]
    var = dataAfterToken.values[0]
    varName = var[1]
    idxVar = None

    if var[0] == 'ID':
            for idx, a in enumerate(attrLLVM):
                gambiarra = str(a).split('%"')[-1].split('"')[0]
                
                if varName == gambiarra:
                    idxVar = idx
    else:

        if var[0] == 'NUM_INTEIRO':
            intType = ll.IntType(32)
            return intType(var[1])

        elif var[0] == 'NUM_PONTO_FLUTUANTE':
            floatType = ll.FloatType()
            return floatType(var[1])
    
    if idxVar == None:
        return None
    
    return attrLLVM[idxVar]
    
def returnLoadAttr(builder, qtdAttr, attr, function):
    intType = ll.IntType(32)
    floatType = ll.FloatType()
    loadAttr = []
    
    # para cada um deles
    for idx in range(qtdAttr):

        # se for um numero flutuante
        if attr[idx][0] == 'NUM_PONTO_FLUTUANTE':
            loadAttr.append(floatType(float(attr[idx][1])))

        # se for inteiro
        elif attr[idx][0] == 'NUM_INTEIRO':
            tipoAttr = returnLLVMType('inteiro')
            loadAttr.append(intType(int(attr[idx][1])))

        # se for um id
        elif attr[idx][0] == 'ID':
            varAttrLLVM = getLLVMVar(attr[idx][1], function)
           
            if None != varAttrLLVM:
                tipoAttr = returnLLVMType(varAttrLLVM[1])
                loadAttr.append(builder.load(varAttrLLVM[3]))

    return loadAttr

def returnNotLoadAttr(builder, qtdAttr, attr, function):
    intType = ll.IntType(32)
    floatType = ll.FloatType()
    notLoadAttr = []
    
    # para cada um deles
    for idx in range(qtdAttr):

        # se for um numero flutuante
        if attr[idx][0] == 'NUM_PONTO_FLUTUANTE':
            notLoadAttr.append(floatType(attr[idx][1]))

        # se for inteiro
        elif attr[idx][0] == 'NUM_INTEIRO':
            tipoAttr = returnLLVMType('inteiro')
            notLoadAttr.append(intType(attr[idx][1]))

        # se for um id
        elif attr[idx][0] == 'ID':
            varAttrLLVM = getLLVMVar(attr[idx][1], function)
           
            if None != varAttrLLVM:
                tipoAttr = returnLLVMType(varAttrLLVM[1])
                notLoadAttr.append(varAttrLLVM[3])

    return notLoadAttr

def atribuition(builder, function, dataLine, line):

    # variavel a esquerda da atribuicao
    varEsq = dataLine.values[0][1]

    # variaveis a direita da atribuicao
    varDir = p.searchDataLineAfterToken2(dataLine, line, 'ATRIBUICAO')
    varLLVMDir = getLLVMVar(varEsq, function)[3]

    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(varDir)
    attr = listAttr(varDir)
    op = listOp(varDir)

    loadAttr = returnLoadAttr(builder, qtdAttr, attr, function)

    # se tiver apenas uma atribuicao
    if qtdAttr == 1:
        builder.store(loadAttr[0], varLLVMDir)

    # se tiver 2 atribuicoes
    elif qtdAttr > 1:
        if op[0][0] == 'MAIS':
            expressao = builder.add(loadAttr[0], loadAttr[1], name='add_temp')

        elif op[0][0] == 'MENOS':
            expressao = builder.sub(loadAttr[0], loadAttr[1], name='sub_temp')

        elif op[0][0] == 'MULTIPLICACAO':
            expressao = builder.mul(loadAttr[0], loadAttr[1], name='sub_temp')

        elif op[0][0] == 'DIVISAO':
            expressao = builder.sdiv(loadAttr[0], loadAttr[1], name='sub_temp')

        builder.store(expressao, varLLVMDir)

        canRepeat = False

        if len(op) > 1:

            expressao2 = None
            idxMais = 0
            idxMenos = 0
            idxMul = 0
            idxDiv = 0

            for idx, operacoes in enumerate(op[1:]):

                if operacoes[0] == 'MAIS':
                    expressao = builder.add(findAttr(varDir, loadAttr, 'MAIS', idxMais), expressao, name='add_temp')
                    idxMais += 1
                elif operacoes[0] == 'MENOS':
                    expressao = builder.sub(findAttr(varDir, loadAttr, 'MENOS', idxMenos), expressao, name='sub_temp')
                    idxMenos += 1
                elif operacoes[0] == 'MULTIPLICACAO':
                    expressao = builder.mul(findAttr(varDir, loadAttr, 'MULTIPLICACAO', idxMul), expressao, name='mul_temp')
                    idxMul += 1
                elif operacoes[0] == 'DIVISAO':
                    expressao = builder.sdiv(findAttr(varDir, loadAttr, 'DIVISAO', idxDiv), expressao, name='div_temp')
                    idxDiv += 1
                
                builder.store(expressao, varLLVMDir)

def escreva(builder, dataPD, funcName, dataLine, line):
    dataLineAttr = p.searchLineByTwoToken(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE')
    
    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(dataLineAttr)
    attr = listAttr(dataLineAttr)
    op = listOp(dataLineAttr)

    loadAttr = returnLoadAttr(builder, qtdAttr, attr, funcName)

    if qtdAttr == 1:

        if str(loadAttr[0].type) == 'i32':
            builder.call(escrevaInteiro, [loadAttr[0]])

        elif str(loadAttr[0].type) == 'float':
            builder.call(escrevaFlutuante, [loadAttr[0]])

def retorna(builder, dataPD, funcName, funcLLVM, dataLine, line, typeFunc):
    bloco_final = funcLLVM.append_basic_block('exit')
    builder.branch(bloco_final)
    builder.position_at_end(bloco_final)

    dataLineAttr = p.searchLineByTwoToken(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE')

    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(dataLineAttr)
    attr = listAttr(dataLineAttr)
    op = listOp(dataLineAttr)
    loadAttr = returnLoadAttr(builder, qtdAttr, attr, funcName)

    if qtdAttr == 1:
        builder.ret(loadAttr[0])

def leia(builder, dataPD, funcName, dataLine, line):
    dataLineAttr = p.searchLineByTwoToken(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE')
    
    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(dataLineAttr)
    attr = listAttr(dataLineAttr)

    # pegar as variaveis nao inicializadas (ponteiros)
    loadAttr = returnNotLoadAttr(builder, qtdAttr, attr, funcName)

    # verificacao de segurança
    if qtdAttr == 1:
        
        # verificacao de segurança
        if attr[0][0] == 'ID':

            # se for int
            if (str(loadAttr[0].type) == 'i32*'):
                leiaReturn = builder.call(leiaInteiro, [])

            # se for float
            elif str(loadAttr[0].type) == 'float*':
                leiaReturn = builder.call(leiaFlutuante, [])

            # guardar o valor lido
            builder.store(leiaReturn, loadAttr[0], align=4)
        
        else:
            print('Erro na função leia: lendo um valor')
    else:
        print('Erro na função leia: lendo mais de um valor')

def declareAll(builder, dataPD, funcName, lineStart, lineEnd):

    lineStart = lineStart + 1
    funcLLVM = getLLVMFunction(funcName)
    valueReturn = False

    func = getLLVMFunction(funcName)
    funcLLVM = func[1]
    typeFunc = func[2]

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

        if len(dataLine.loc[dataLine['token'] == 'ESCREVA']) > 0:
            escreva(builder, dataPD, funcName, dataLine, line)
    
        if len(dataLine.loc[dataLine['token'] == 'LEIA']) > 0:
            leia(builder, dataPD, funcName, dataLine, line)
        
        if len(dataLine.loc[dataLine['token'] == 'RETORNA']) > 0:
            valueReturn = True
            retorna(builder, dataPD, funcName, funcLLVM, dataLine, line, typeFunc)


    if not valueReturn:
        finalBlock = funcLLVM.append_basic_block(name='exit')
        builder.branch(finalBlock)

        builder.position_at_end(finalBlock)
        
        if func[2] == 'VAZIO':
            builder.ret_void()
        else:
            print('err')
            # if func[2] == 'INTEIRO':
            #     typeReturnFunc = ll.IntType(32)
            # elif func[2] == 'FLUTUANTE':
            #     typeReturnFunc = ll.FloatType()
            
            # value = ll.Constant(typeReturnFunc, 0)
            # valueReturn = builder.alloca(typeReturnFunc, name='return')
            # builder.store(value, valueReturn)

            # valueReturn = builder.load(valueReturn, name='ret_temp', align=4)
            # builder.ret(valueReturn)

def codeGenerator(file, root, dataPD, functionsPD, variablesPD):
    
    declareVarGlobal(variablesPD)
    declareFunctions(dataPD, functionsPD)
    return modulo