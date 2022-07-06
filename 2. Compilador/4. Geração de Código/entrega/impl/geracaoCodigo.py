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
                tipoLLVM = ll.ArrayType(tipoLLVM, int(var[5][0]))
                indices = int(var[5][0])
            else:
                indices = 0

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
            varModule.append(['global', var[0], var[1], varLLVM, indices])

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
                varModule.append([func[1], param[0], param[1], funcLLVM.args[idx], 0])

        funcModule.append([func[1], funcLLVM, func[0]])

        funcInit = funcLLVM.append_basic_block('entry')
        builder = ll.IRBuilder(funcInit)

        for var in varModule:
            if var[0] == func[1]:
                param = builder.alloca(ll.IntType(32), name='param')
                builder.store(var[3], param)
                var[3] = param

        declareAll(builder, dataPD, func[1], func[3], func[4], functionsPD)

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
    idsLine = dataLine.loc[dataLine['token'] == 'ID']

    for nameVar in idsLine['valor'].values:

        varFunction = builder.alloca(typeLLVM, name=nameVar)
        
        if typeVar.lower() == 'inteiro':
            varFunction.initializer = ll.Constant(typeLLVM, 0)
        else:
            varFunction.initializer = ll.Constant(typeLLVM, 0.0)

        varFunction.align = 4
        varModule.append([functionName, typeVar, nameVar, varFunction, 0])

def returnValueArray(dataLine):
    dataLineIDS = dataLine.loc[dataLine['token'] == 'ID']
    dataResult = []
    
    for dataIds in dataLineIDS.values:
        nextValue = dataLine.loc[dataLine['coluna'] == dataIds[3] + 1, 'token']

        if len(nextValue) > 0:
            if nextValue.values[0] == 'ABRE_COLCHETE':
                tamArray = dataLine.loc[dataLine['coluna'] == dataIds[3] + 2, 'valor'].values[0]
                dataResult.append([dataIds[1], int(tamArray)])
            else:
                dataResult.append([dataIds[1], 0])
        else:
            dataResult.append([dataIds[1], 0])

    return dataResult

def declareVarArray(builder, functionName, dataLine):
    typeVar = dataLine.values[0][0]
    typeLLVM = returnLLVMType(typeVar)
    idsLine = dataLine.loc[dataLine['token'] == 'ID']
    allIds = returnValueArray(dataLine)

    for var in allIds:

        if var[1] > 0:
            varFunction = builder.alloca(ll.ArrayType(typeLLVM, var[1]), name=var[0])
            varFunction.initializer = ll.Constant(typeLLVM, None)
        else:

            varFunction = builder.alloca(typeLLVM, name=var[0])
            
            if typeVar.lower() == 'inteiro':
                varFunction.initializer = ll.Constant(typeLLVM, 0)
            else:
                varFunction.initializer = ll.Constant(typeLLVM, 0.0)

        varFunction.align = 4
        varModule.append([functionName, typeVar, var[0], varFunction, var[1]])

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
                if str(varAttrLLVM[3].type) == 'i32*' or str(varAttrLLVM[3].type) == 'float*':
                    loadAttr.append(builder.load(varAttrLLVM[3]))
                else:
                    loadAttr.append(varAttrLLVM[3])
            else:
                loadAttr.append('FUNCAO;;' + str(attr[idx][1]))

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

def isArray(variable):
    for var in varModule:
        if var[2] == variable:

            if var[4] > 0:
                return True
            else:
                return False

    return False

def atribuition(builder, function, dataLine, line, functionsPD):

    tipoInt = ll.IntType(32)

    # variavel a esquerda da atribuicao
    varEsq = dataLine.values[0][1]

    # variaveis a direita da atribuicao
    varDir = p.searchDataLineAfterToken2(dataLine, line, 'ATRIBUICAO')

    if isArray(varEsq):
        var = getLLVMVar(varEsq, function)[3]

        exp = False
        expBefore = False

        if dataLine.values[2][0] != 'ID':
            indice = int(dataLine.values[2][1])
        else:
            expBefore = True
            indice = builder.load(getLLVMVar(dataLine.values[2][1], function)[3])

        if (dataLine.values[4][0] == 'ID' or dataLine.values[4][0] == 'NUM_INTEIRO' or dataLine.values[4][0] == 'NUM_PONTO_FLUTUANTE'):
            exp = True
            op = dataLine.values[3][0]
            varOp = getLLVMVar(dataLine.values[4][1], function)[3]

            if op == 'MENOS':
                expressao = builder.sub(tipoInt(indice), builder.load(varOp), name='sub_temp')

        if exp:
            varLLVMDir = builder.gep(var, [tipoInt(0), expressao], name='ptr_A_'+varEsq)
        else:
            if expBefore:
                varLLVMDir = builder.gep(var, [tipoInt(0), indice], name='ptr_A_'+varEsq)
            else:
                varLLVMDir = builder.gep(var, [tipoInt(0), tipoInt(indice)], name='ptr_A_'+varEsq)
    else:
        varLLVMDir = getLLVMVar(varEsq, function)[3]


    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(varDir)
    attr = listAttr(varDir)
    op = listOp(varDir)

    loadAttr = returnLoadAttr(builder, qtdAttr, attr, function)

    # se tiver apenas uma atribuicao
    if qtdAttr == 1:

        if 'FUNCAO' not in str(loadAttr[0]):

            if 'i32' in str(loadAttr[0].type) and 'i32' in str(varLLVMDir.type):
                builder.store(loadAttr[0], varLLVMDir)

            elif 'i32' in str(loadAttr[0].type) and 'float' in str(varLLVMDir.type):
                temp = builder.sitofp(loadAttr[0], ll.FloatType(), name="temp")
                builder.store(temp, varLLVMDir)
        else:
            functionLLVM = getLLVMFunction(attr[0][1])[1]
            chamadaFuncao = builder.call(functionLLVM, [])

            builder.store(chamadaFuncao, varLLVMDir)

    # se tiver 2 atribuicoes
    elif qtdAttr > 1:

        if not isArray(attr[0][1]):
            if 'FUNCAO' not in str(loadAttr[0]):

                if op[0][0] == 'MAIS':
                    expressao = builder.add(loadAttr[0], loadAttr[1], name='add_temp')

                elif op[0][0] == 'MENOS':
                    expressao = builder.sub(loadAttr[0], loadAttr[1], name='sub_temp')

                elif op[0][0] == 'MULTIPLICACAO':
                    expressao = builder.mul(loadAttr[0], loadAttr[1], name='mul_temp')

                elif op[0][0] == 'DIVISAO':
                    expressao = builder.sdiv(loadAttr[0], loadAttr[1], name='div_temp')

                if 'i32' in str(expressao.type) and 'i32' in str(varLLVMDir.type):
                        
                        builder.store(expressao, varLLVMDir)

                elif 'float' in str(expressao.type) and 'float' in str(varLLVMDir.type):
                    builder.store(expressao, varLLVMDir)
                elif 'i32' in str(expressao.type) and 'float' in str(varLLVMDir.type):
                    temp = builder.sitofp(expressao, ll.FloatType(), name="temp")
                    builder.store(temp, varLLVMDir)

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
            
            else:
                
                indexGeral = 0
                function = []
                result = []

                while(indexGeral < len(loadAttr)):
                    
                    if 'FUNCAO' in str(loadAttr[indexGeral]):
                        
                        funcName = loadAttr[indexGeral].split(';;')[1]
                        functionPD = functionsPD.loc[functionsPD['nome'] == funcName]

                        function.append([len(functionPD.values[0][2]), getLLVMFunction(funcName), [], functionPD.values[0][0]])

                    else:
                        
                        isParam = function[-1]

                        if isParam[0] > 0:
                            function[-1][0] -= 1
                            function[-1][2].append(loadAttr[indexGeral])

                        if function[-1][0] == 0:
                            functionAtual = function.pop()

                            chamadaFuncao = builder.call(functionAtual[1][1], functionAtual[2])
                            result.append(chamadaFuncao)

                    indexGeral += 1

                if len(function) > 0:
                    
                    if function[-1][0] == len(result):
                        functionAtual = function.pop()

                        chamadaFuncao = builder.call(functionAtual[1][1], result)
                        builder.store(chamadaFuncao, varLLVMDir)
                
                elif len(result) > 0:
                    builder.store(result[0], varLLVMDir)

        else:

            arrayVar = attr[0][1]

            if isArray(arrayVar):

                if len(attr) == 2:
                    
                    isId = False

                    if attr[1][0] != 'ID':
                        indice = int(attr[1][1])
                    else:
                        isId = True
                        indice = loadAttr[1]

                    if isId:
                        posicaoArray = builder.gep(loadAttr[0], [tipoInt(0), indice], name='ptr_A_'+str(attr[1][1]))

                    else:
                        posicaoArray = builder.gep(loadAttr[0], [tipoInt(0), tipoInt(indice)], name='ptr_A_'+str(attr[1][1]))
                    
                    builder.store(builder.load(posicaoArray), varLLVMDir)

                elif len(attr) == 4:

                    isId1 = False
                    isId2 = False

                    if attr[1][0] != 'ID':
                        indice1 = int(attr[1][1])
                    else:
                        isId1 = True
                        indice1 = loadAttr[1]

                    if attr[3][0] != 'ID':
                        indice2 = int(attr[3][1])
                    else:
                        isId2 = True
                        indice2 = loadAttr[3]

                    if isId1:
                        posicaoArray1 = builder.gep(loadAttr[0], [tipoInt(0), indice1], name='ptr_A_'+str(attr[0][1]) + '[' + str(attr[1][1]) + ']')

                    else:
                        posicaoArray1 = builder.gep(loadAttr[0], [tipoInt(0), tipoInt(indice1)], name='ptr_A_'+str(attr[0][1]) + '[' + str(attr[1][1]) + ']')

                    if isId2:
                        posicaoArray2 = builder.gep(loadAttr[2], [tipoInt(0), indice2], name='ptr_A_'+str(attr[2][1])+'['+str(attr[3][1] + ']'))

                    else:
                        posicaoArray2 = builder.gep(loadAttr[2], [tipoInt(0), tipoInt(indice2)], name='ptr_A_'+str(attr[2][1])+'['+str(attr[3][1] + ']'))

                    if op[0][0] == 'MAIS':
                        posicaoArray1 = builder.load(posicaoArray1)
                        posicaoArray2 = builder.load(posicaoArray2)

                    if str(posicaoArray1.type) == 'float' and str(posicaoArray2.type) == 'float':
                        expressao = builder.fadd(posicaoArray1, posicaoArray2, name='add_A_temp')
                    
                    else:
                        expressao = builder.add(posicaoArray1, posicaoArray2, name='add_A_temp')

                    builder.store(expressao, varLLVMDir)

def escreva(builder, dataPD, funcName, dataLine, line, functionsPD):

    tipoInt = ll.IntType(32)

    dataLineAttr = p.searchLineByTwoToken(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE')
    
    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(dataLineAttr)
    attr = listAttr(dataLineAttr)
    op = listOp(dataLineAttr)

    loadAttr = returnLoadAttr(builder, qtdAttr, attr, funcName)

    if qtdAttr == 1:
        
        if 'FUNCAO' not in str(loadAttr[0]):
            if str(loadAttr[0].type) == 'i32':
                builder.call(escrevaInteiro, [loadAttr[0]])

            elif str(loadAttr[0].type) == 'float':
                builder.call(escrevaFlutuante, [loadAttr[0]])
        else:

            funcName = loadAttr[0].split(';;')[1]
            functionAtual = getLLVMFunction(funcName)

            chamadaFuncao = builder.call(functionAtual[1], [])
            if functionAtual[2].lower() == 'inteiro':
                builder.call(escrevaInteiro, [chamadaFuncao])
            else:
                builder.call(escrevaFlutuante, [chamadaFuncao])

    else:
        
        if len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) == 0:
            indexGeral = 0
            function = []

            while(indexGeral < len(loadAttr)):
                
                if 'FUNCAO' in str(loadAttr[indexGeral]):
                    
                    funcName = loadAttr[indexGeral].split(';;')[1]
                    functionPD = functionsPD.loc[functionsPD['nome'] == funcName]

                    function.append([len(functionPD.values[0][2]), getLLVMFunction(funcName), [], functionPD.values[0][0]])

                else:
                    
                    isParam = function[-1]

                    if isParam[0] > 0:
                        function[-1][0] -= 1
                        function[-1][2].append(loadAttr[indexGeral])

                    if function[-1][0] == 0:
                        functionAtual = function.pop()

                        chamadaFuncao = builder.call(functionAtual[1][1], functionAtual[2])

                        if functionAtual[3].lower() == 'inteiro':
                            builder.call(escrevaInteiro, [chamadaFuncao])

                        elif functionAtual[3].lower() == 'flutuante':
                            builder.call(escrevaFlutuante, [chamadaFuncao])

                indexGeral += 1
        
        else:

            arrayVar = attr[0][1]

            if isArray(arrayVar):

                if len(attr) == 2:
                    isId = False

                    if attr[1][0] != 'ID':
                        indice = int(attr[1][1])
                    else:
                        isId = True
                        indice = loadAttr[1]

                    if isId:
                        posicaoArray = builder.gep(loadAttr[0], [tipoInt(0), indice], name='ptr_A_'+str(attr[1][1]))
                    else:
                        posicaoArray = builder.gep(loadAttr[0], [tipoInt(0), tipoInt(indice)], name='ptr_A_'+str(attr[1][1]))
                    
                    posicaoArray = builder.load(posicaoArray, align=4)
                    varEscope = getLLVMVar(arrayVar, funcName)

                    if varEscope[1].lower() == 'inteiro':
                        builder.call(escrevaInteiro, [posicaoArray])
                    elif varEscope[1].lower() == 'flutuante':
                        builder.call(escrevaFlutuante, [posicaoArray])

def retorna(builder, dataPD, funcName, funcLLVM, dataLine, line, typeFunc, seRepitaBlock, functionsPD):

    global moreOneReturn

    if len(seRepitaBlock) == 0:

        if not moreOneReturn:
            bloco_final = funcLLVM.append_basic_block('exit')
            builder.branch(bloco_final)
            builder.position_at_end(bloco_final)
    else:
        moreOneReturn = True

    dataLineAttr = p.searchLineByTwoTokenByEnd(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE')
    
    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(dataLineAttr)
    attr = listAttr(dataLineAttr)
    op = listOp(dataLineAttr)
    loadAttr = returnLoadAttr(builder, qtdAttr, attr, funcName)

    if qtdAttr == 1:
        builder.ret(loadAttr[0])

    # se tiver 2 atribuicoes
    elif qtdAttr > 1:
        
        valueReturn = builder.alloca(ll.IntType(32), name='return')

        if 'FUNCAO' not in str(loadAttr[0]):

            if op[0][0] == 'MAIS':
                expressao = builder.add(loadAttr[0], loadAttr[1], name='add_temp')

            elif op[0][0] == 'MENOS':
                expressao = builder.sub(loadAttr[0], loadAttr[1], name='sub_temp')

            elif op[0][0] == 'MULTIPLICACAO':
                expressao = builder.mul(loadAttr[0], loadAttr[1], name='sub_temp')

            elif op[0][0] == 'DIVISAO':
                expressao = builder.sdiv(loadAttr[0], loadAttr[1], name='sub_temp')

            builder.store(expressao, valueReturn)

            canRepeat = False

            if len(op) > 1:

                expressao2 = None
                idxGeral = 1
                idxMais = 0
                idxMenos = 0
                idxMul = 0
                idxDiv = 0

                for idx, operacoes in enumerate(op[1:]):
                    idxGeral += 1

                    if operacoes[0] == 'MAIS':
                        expressao2 = builder.add(loadAttr[idxGeral], expressao, name='add_temp')
                        idxMais += 1
                    elif operacoes[0] == 'MENOS':
                        expressao2 = builder.sub(loadAttr[idxGeral], expressao, name='sub_temp')
                        idxMenos += 1
                    elif operacoes[0] == 'MULTIPLICACAO':
                        expressao2 = builder.mul(loadAttr[idxGeral], expressao, name='mul_temp')
                        idxMul += 1
                    elif operacoes[0] == 'DIVISAO':
                        expressao2 = builder.sdiv(loadAttr[idxGeral], expressao, name='div_temp')
                        idxDiv += 1
                    
                    builder.store(expressao2, valueReturn)
            
            builder.ret(builder.load(valueReturn))

        else:

            if len(op) != 3:
                
                indexGeral = 0
                function = []
                result = []

                while(indexGeral < len(loadAttr)):
                    
                    if 'FUNCAO' in str(loadAttr[indexGeral]):
                        
                        funcName = loadAttr[indexGeral].split(';;')[1]
                        functionPD = functionsPD.loc[functionsPD['nome'] == funcName]

                        function.append([len(functionPD.values[0][2]), getLLVMFunction(funcName), [], functionPD.values[0][0]])

                    else:
                        
                        isParam = function[-1]

                        if isParam[0] > 0:
                            function[-1][0] -= 1
                            function[-1][2].append(loadAttr[indexGeral])
            
                        if function[-1][0] == 0:
                            functionAtual = function.pop()

                            chamadaFuncao = builder.call(functionAtual[1][1], functionAtual[2])
                            result.append(chamadaFuncao)

                    indexGeral += 1

                if len(function) > 0:
                    
                    if function[-1][0] == len(result):
                        functionAtual = function.pop()

                        chamadaFuncao = builder.call(functionAtual[1][1], result)
                        builder.store(chamadaFuncao, valueReturn)
                
                elif len(result) > 0:
                    builder.store(result[0], valueReturn)

                builder.ret(builder.load(valueReturn))

            else:

                # print('aqui: ', loadAttr)

                funcName = loadAttr[0].split(';;')[1]
                funcaoLLVMPD = getLLVMFunction(funcName)

                if op[0][0] == 'MENOS':
                    expressao1 = builder.sub(loadAttr[1], loadAttr[2], name='sub_temp')

                chamadaFuncao1 = builder.call(funcaoLLVMPD[1], [expressao1])

                funcName = loadAttr[3].split(';;')[1]
                funcaoLLVMPD = getLLVMFunction(funcName)

                if op[2][0] == 'MENOS':
                    expressao2 = builder.sub(loadAttr[4], loadAttr[5], name='sub_temp')

                chamadaFuncao2 = builder.call(funcaoLLVMPD[1], [expressao2])

                if op[1][0] == 'MAIS':
                    expressao = builder.add(chamadaFuncao1, chamadaFuncao2, name='add_temp')
                
                builder.store(expressao, valueReturn)
                builder.ret(builder.load(valueReturn))

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

def getCompare(dataLine):

    if len(dataLine.loc[dataLine['token'] == 'E_LOGICO']) == 0:
        if len(dataLine.loc[dataLine['token'] == 'MAIOR']) > 0:
            return '>', 'MAIOR'
        
        if len(dataLine.loc[dataLine['token'] == 'MAIOR_IGUAL']) > 0:
            return '>=', 'MAIOR_IGUAL'
        
        if len(dataLine.loc[dataLine['token'] == 'MENOR']) > 0:
            return '<', 'MENOR'

        if len(dataLine.loc[dataLine['token'] == 'MENOR_IGUAL']) > 0:
            return '<=', 'MENOR_IGUAL'

        if len(dataLine.loc[dataLine['token'] == 'IGUAL']) > 0:
            return '==', 'IGUAL'
    else:

        if len(dataLine.loc[dataLine['token'] == 'E_LOGICO']) == 1:
            return '==' 'E_LOGICO'
            
        # exemplo 11
        return '&&', 'E_LOGICO'
    
    return ''

def returnType(tipo, value):
    tipoInteiro = ll.IntType(32)
    tipoFlutuante = ll.FloatType()

    if tipo == 'inteiro':
        return tipoInteiro(value)
    elif tipo == 'flutuante':
        return tipoFlutuante(value)

def verifyQtdComparation(dataLine):
    qtdIgual = len(dataLine.loc[dataLine['token'] == 'IGUAL'])
    qtdNot = len(dataLine.loc[dataLine['token'] == 'NEGACAO'])
    qtdMaior = len(dataLine.loc[dataLine['token'] == 'MAIOR'])
    qtdMaiorIgual = len(dataLine.loc[dataLine['token'] == 'MAIOR_IGUAL'])
    qtdMenor = len(dataLine.loc[dataLine['token'] == 'MENOR'])
    qtdMenorIgual = len(dataLine.loc[dataLine['token'] == 'MENOR_IGUAL'])
    qtdELogico = len(dataLine.loc[dataLine['token'] == 'E_LOGICO'])
    qtdOULogico = len(dataLine.loc[dataLine['token'] == 'OU_LOGICO'])

    return qtdIgual + qtdNot + qtdMaior + qtdMaiorIgual + qtdMenor + qtdMenorIgual + qtdELogico + qtdOULogico

def getSecondCompare(dataLine):
    returnSecond = False

    for values in dataLine.values:

        if values[0] == 'MAIOR':
            if returnSecond: return '>', None
            returnSecond = True

        elif values[0] == 'MAIOR_IGUAL':
            if returnSecond: return '>=', None
            returnSecond = True
 
        elif values[0] == 'MENOR':
            if returnSecond: return '<', None
            returnSecond = True

        elif values[0] == 'MENOR_IGUAL':
            if returnSecond: return '<=', None
            returnSecond = True

        elif values[0] == 'E_LOGICO':
            if returnSecond: return '&&', 'E_LOGICO'
            returnSecond = True

        elif values[0] == 'OU_LOGICO':
            if returnSecond: return '||', 'OU_LOGICO'
            returnSecond = True

def getCompares(dataLine):
    compares = []
    pegar = False

    for values in dataLine.values:

        if values[0] == 'MAIOR':
            if pegar: 
                compares.append([values[1], 'MAIOR'])
                pegar = False
            else:
                pegar = True

        elif values[0] == 'MAIOR_IGUAL':
            if pegar: 
                compares.append([values[1], 'MAIOR_IGUAL'])
                pegar = False
            else:
                pegar = True
 
        elif values[0] == 'MENOR':
            if pegar: 
                compares.append([values[1], 'MENOR'])
                pegar = False
            else:
                pegar = True

        elif values[0] == 'MENOR_IGUAL':
            if pegar: 
                compares.append([values[1], 'MENOR_IGUAL'])
                pegar = False
            else:
                pegar = True

        elif values[0] == 'E_LOGICO':
            if pegar: 
                compares.append([values[1], 'E_LOGICO'])
                pegar = False
            else:
                pegar = True

        elif values[0] == 'OU_LOGICO':
            if pegar: 
                compares.append([values[1], 'OU_LOGICO'])
                pegar = False
            else:
                pegar = True

        elif values[0] == 'IGUAL':
            if pegar: 
                compares.append([values[1], 'IGUAL'])
                pegar = False
            else:
                pegar = True

        elif values[0] == 'NEGACAO':
            compares.append([values[1], 'NEGACAO'])
    
    return compares

def se(builder, dataPD, funcName, dataLine, line, seRepitaBlock, idxBlock, seTrue, seFalse, seEnd):
    
    qtdComper = verifyQtdComparation(dataLine)

    if qtdComper == 3:
        secondCompare = getSecondCompare(dataLine)

        if secondCompare[0] == '&&':

            # comparacao, token = getCompare(dataLine)
            dataLine1 = p.searchLineByTwoToken(dataPD, line, 'SE', secondCompare[1])

            # pego a comparacao
            comparacao, token = getCompare(dataLine1)

            # quantidade de atributos e atributos
            dataSeEsq = p.searchLineByTwoToken(dataPD, line, 'SE', token)
            qtdAttrEsq = p.checkAttr(dataSeEsq)
            attrEsq = listAttr(dataSeEsq)

            # pegar as variaveis inicializadas
            loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

            # quantidade de atributos e atributos
            dataSeDir = p.searchLineByTwoToken(dataPD, line, token, secondCompare[1])
            qtdAttrDir = p.checkAttr(dataSeDir)
            attrDir = listAttr(dataSeDir)
            
            # pegar as variaveis inicializadas
            loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

            # crio a comparacao
            comperRight = builder.alloca(ll.IntType(32), name='var_comp_if_r')
            comperLeft = builder.alloca(ll.IntType(32), name='var_comp_if_l')
            
            if qtdAttrEsq == 1 and qtdAttrDir == 1:

                # carrego os valores para ambos os lados da comparacao
                for attrEsq in loadAttrEsq:
                    builder.store(attrEsq, comperLeft, align=4)

                for attrDir in loadAttrDir:
                    builder.store(attrDir, comperRight, align=4)

            funcaoLLVM = getLLVMFunction(funcName)[1]
            verifyBlock = funcaoLLVM.append_basic_block('verify')

            # crio o bloco do if
            ifState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='if_state')
            builder.cbranch(ifState, verifyBlock, seFalse)

            builder.position_at_end(verifyBlock)

            # comparacao, token = getCompare(dataLine)
            dataLine2 = p.searchLineByTwoToken(dataPD, line, secondCompare[1], 'ENTAO')

            # pego a comparacao
            comparacao, token = getCompare(dataLine2)

            # quantidade de atributos e atributos
            dataSeEsq = p.searchLineByTwoToken(dataPD, line, secondCompare[1], token)
            qtdAttrEsq = p.checkAttr(dataSeEsq)
            attrEsq = listAttr(dataSeEsq)

            # pegar as variaveis inicializadas
            loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

            # quantidade de atributos e atributos
            dataSeDir = p.searchLineByTwoToken(dataPD, line, token, 'ENTAO')
            qtdAttrDir = p.checkAttr(dataSeDir)
            attrDir = listAttr(dataSeDir)
            
            # pegar as variaveis inicializadas
            loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

            if qtdAttrEsq == 1 and qtdAttrDir == 1:

                # carrego os valores para ambos os lados da comparacao
                for attrEsq in loadAttrEsq:
                    builder.store(attrEsq, comperLeft, align=4)

                for attrDir in loadAttrDir:
                    builder.store(attrDir, comperRight, align=4)
            
            # crio o bloco do if
            ifState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='if_state')
            builder.cbranch(ifState, seTrue, seFalse)

            builder.position_at_end(seTrue)

    elif qtdComper == 6:
        compares = getCompares(dataLine)

        # comparacao, token = getCompare(dataLine)
        dataLine1 = p.searchLineByTwoToken(dataPD, line, 'SE', compares[0][1])
        
        # pego a comparacao
        comparacao, token = getCompare(dataLine1)

        # quantidade de atributos e atributos
        dataSeEsq = p.searchLineByTwoToken(dataPD, line, 'SE', token)
        qtdAttrEsq = p.checkAttr(dataSeEsq)
        attrEsq = listAttr(dataSeEsq)

        # pegar as variaveis inicializadas
        loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

        # quantidade de atributos e atributos
        dataSeDir = p.searchLineByTwoToken(dataPD, line, token, compares[0][1])
        qtdAttrDir = p.checkAttr(dataSeDir)
        attrDir = listAttr(dataSeDir)
        
        # pegar as variaveis inicializadas
        loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

        # crio a comparacao
        comperRight = builder.alloca(ll.IntType(32), name='var_comp_if_r')
        comperLeft = builder.alloca(ll.IntType(32), name='var_comp_if_l')

        if qtdAttrEsq == 3 and qtdAttrDir == 1:
            
            loadEsq = []
            attr = []

            for attrEsq in loadAttrEsq:
                if 'FUNCAO' in str(attrEsq):
                    funcNameA = attrEsq.split(';;')[1]
                    functionLLVM = getLLVMFunction(funcNameA)

                    loadEsq.append(functionLLVM[1])
                else:
                    attr.append(attrEsq)

            funcCall = builder.call(loadEsq[0], attr, name='call_func')
            builder.store(funcCall, comperLeft, align=4)
            builder.store(loadAttrDir[0], comperRight, align=4)
            
            llvmFunc = getLLVMFunction(funcName)[1]
            verify = llvmFunc.append_basic_block('verify')

            # crio o bloco do if
            ifState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='if_state')
            builder.cbranch(ifState, seTrue, verify)

            builder.position_at_end(verify)

        # comparacao, token = getCompare(dataLine)
        dataLine1 = p.searchLineByTwoToken(dataPD, line, 'SE', compares[1][1])
        
        # pego a comparacao
        comparacao, token = getCompare(dataLine1)
        
        # quantidade de atributos e atributos
        dataSeEsq = p.searchLineByTwoToken3(dataPD, line, compares[0][1], token, 1)
        qtdAttrEsq = p.checkAttr(dataSeEsq)
        attrEsq = listAttr(dataSeEsq)

        # pegar as variaveis inicializadas
        loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

        # quantidade de atributos e atributos
        dataSeDir = p.searchLineByTwoToken2(dataPD, line, token, 1, compares[1][1])
        qtdAttrDir = p.checkAttr(dataSeDir)
        attrDir = listAttr(dataSeDir)
        
        # pegar as variaveis inicializadas
        loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

        # crio a comparacao
        comperRight = builder.alloca(ll.IntType(32), name='var_comp_if_r')
        comperLeft = builder.alloca(ll.IntType(32), name='var_comp_if_l')

        if qtdAttrEsq == 3 and qtdAttrDir == 1:
           
            loadEsq = []
            attr = []

            for attrEsq in loadAttrEsq:
                if 'FUNCAO' in str(attrEsq):
                    funcNameA = attrEsq.split(';;')[1]
                    functionLLVM = getLLVMFunction(funcNameA)

                    loadEsq.append(functionLLVM[1])
                else:
                    attr.append(attrEsq)

            funcCall = builder.call(loadEsq[0], [attr[0], attr[1]], name='call_func')
            builder.store(funcCall, comperLeft, align=4)
            builder.store(loadAttrDir[0], comperRight, align=4)
            
            funcaoEscopoLLVM = getLLVMFunction(funcName)[1]
            verifyBlock = funcaoEscopoLLVM.append_basic_block('verify.1')

            # crio o bloco do if
            ifState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='if_state')
            builder.cbranch(ifState, verifyBlock, seEnd)

            builder.position_at_end(verifyBlock)

        # comparacao, token = getCompare(dataLine)
        dataLine1 = p.searchLineByTwoToken(dataPD, line, compares[2][1], 'ENTAO')
        
        # pego a comparacao
        comparacao, token = getCompare(dataLine1)

        # quantidade de atributos e atributos
        dataSeEsq = p.searchLineByTwoToken3(dataPD, line, compares[2][1], token, 2)
        qtdAttrEsq = p.checkAttr(dataSeEsq)
        attrEsq = listAttr(dataSeEsq)

        # pegar as variaveis inicializadas
        loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

        # quantidade de atributos e atributos
        dataSeDir = p.searchLineByTwoToken2(dataPD, line, token, 2, 'ENTAO')
        qtdAttrDir = p.checkAttr(dataSeDir)
        attrDir = listAttr(dataSeDir)
        
        # pegar as variaveis inicializadas
        loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

        # crio a comparacao
        comperRight = builder.alloca(ll.IntType(32), name='var_comp_if_r')
        comperLeft = builder.alloca(ll.IntType(32), name='var_comp_if_l')

        if qtdAttrEsq == 3 and qtdAttrDir == 1:
           
            loadEsq = []
            attr = []

            for attrEsq in loadAttrEsq:
                if 'FUNCAO' in str(attrEsq):
                    funcNameA = attrEsq.split(';;')[1]
                    functionLLVM = getLLVMFunction(funcNameA)

                    loadEsq.append(functionLLVM[1])
                else:
                    attr.append(attrEsq)

            funcCall = builder.call(loadEsq[0], [attr[0], attr[1]], name='call_func')
            builder.store(funcCall, comperLeft, align=4)
            builder.store(loadAttrDir[0], comperRight, align=4)
            
            # crio o bloco do if
            ifState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='if_state')
            builder.cbranch(ifState, seEnd, seTrue)

            builder.position_at_end(seTrue)
    else:

        # pego a comparacao
        comparacao, token = getCompare(dataLine)
        
        # quantidade de atributos e atributos
        dataSeEsq = p.searchLineByTwoToken(dataPD, line, 'SE', token)
        qtdAttrEsq = p.checkAttr(dataSeEsq)
        attrEsq = listAttr(dataSeEsq)
        
        # pegar as variaveis inicializadas
        loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

        # quantidade de atributos e atributos
        dataSeDir = p.searchLineByTwoToken(dataPD, line, token, 'ENTAO')
        qtdAttrDir = p.checkAttr(dataSeDir)
        attrDir = listAttr(dataSeDir)

        # pegar as variaveis inicializadas
        loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

        # crio a comparacao
        comperRight = builder.alloca(ll.IntType(32), name='var_comp_if_r')
        comperLeft = builder.alloca(ll.IntType(32), name='var_comp_if_l')

        # verifico se possuo apenas 1 variavel para verificar
        if qtdAttrEsq == 1 and qtdAttrDir == 1:

            # carrego os valores para ambos os lados da comparacao
            for attrEsq in loadAttrEsq:
                builder.store(attrEsq, comperLeft, align=4)

            for attrDir in loadAttrDir:
                builder.store(attrDir, comperRight, align=4)

        else:
            # exemplo 11
            pass
        
        # crio o bloco do if
        ifState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='if_state')
        
        # se for um se sem o senão
        if seFalse == None:

            # crio a condicao, onde se for falso, nao executa o bloco e pula direto para o bloco fim
            builder.cbranch(ifState, seTrue, seEnd)

        else:
            # crio a condicao, onde se for falso, pula direto para o bloco falso
            builder.cbranch(ifState, seTrue, seFalse)

        # o escopo agora e do bloco 'verdade'
        builder.position_at_end(seTrue)

def repita(builder, dataPD, dataLine, line, funcName, loop, loopEnd):
    
    # pego a comparacao
    comparacao, token = getCompare(dataLine)

    # quantidade de atributos e atributos
    dataRepitaEsq = p.searchLineByTwoToken(dataPD, line, 'ATE', token)
    qtdAttrEsq = p.checkAttr(dataRepitaEsq)
    attrEsq = listAttr(dataRepitaEsq)

    # pegar as variaveis inicializadas
    loadAttrEsq = returnLoadAttr(builder, qtdAttrEsq, attrEsq, funcName)

    # quantidade de atributos e atributos
    dataRepitaDir = p.searchDataLineAfterToken2(dataPD, line, token)
    qtdAttrDir = p.checkAttr(dataRepitaDir)
    attrDir = listAttr(dataRepitaDir)

    # pegar as variaveis inicializadas
    loadAttrDir = returnLoadAttr(builder, qtdAttrDir, attrDir, funcName)

    # crio a comparacao
    comperRight = builder.alloca(ll.IntType(32), name='var_comp_loop_r')
    comperLeft = builder.alloca(ll.IntType(32), name='var_comp_loop_l')

    # verifico se possuo apenas 1 variavel para verificar
    if qtdAttrEsq == 1 and qtdAttrDir == 1:

        # carrego os valores para ambos os lados da comparacao
        for attrEsq in loadAttrEsq:
            builder.store(attrEsq, comperLeft, align=4)

        for attrDir in loadAttrDir:
            builder.store(attrDir, comperRight, align=4)

    # crio o bloco do if
    loopState = builder.icmp_signed(comparacao, builder.load(comperLeft), builder.load(comperRight), name='loop_state')

    # caso seja uma comparacao (se nao fizer isso, sempre que o valor nao seja igual ao esperado ele sai do loop)
    if comparacao == '==':
        builder.cbranch(loopState, loopEnd, loop)
    
    else:
        builder.cbranch(loopState, loop, loopEnd)

    builder.position_at_end(loopEnd)

def callFunction(builder, dataPD, dataLine, line, funcName, funcArray):
    dataLineAttr = p.searchLineByTwoToken(dataPD, line, 'ABRE_PARENTESE', 'FECHA_PARENTESE')

    # quantidade de atributos e atributos
    qtdAttr = p.checkAttr(dataLineAttr)
    attr = listAttr(dataLineAttr)
    op = listOp(dataLineAttr)

    loadAttr = returnLoadAttr(builder, qtdAttr, attr, funcName)

    if qtdAttr == 1:
        builder.call(funcArray[1], loadAttr, name='call_func')

def findReturns(dataPD, functionPD, funcName):
    fPD = functionPD.loc[functionPD['nome'] == funcName]
    lineStart = fPD['linha_inicio'].values[0]
    lineEnd = fPD['linha_fim'].values[0]

    escopoPD = dataPD.loc[(dataPD['linha'] >= lineStart) & (dataPD['linha'] <= lineEnd)]

    return len(escopoPD.loc[escopoPD['token'] == 'RETORNA'])

def declareAll(builder, dataPD, funcName, lineStart, lineEnd, functionsPD):

    global moreOneReturn
    moreOneReturn = False

    lineStart = lineStart + 1
    funcLLVM = getLLVMFunction(funcName)
    valueReturn = False

    func = getLLVMFunction(funcName)
    funcLLVM = func[1]
    typeFunc = func[2]

    seRepitaBlock = []
    idxBlock = 0

    for line in range(lineStart, (lineEnd + 1)):
        dataLine = p.searchDataLine(dataPD, line)

        if len(dataLine) > 0:
            if dataLine.values[0][0] == 'ID':
                funcLine = getLLVMFunction(dataLine.values[0][1])

                if funcLine:
                    callFunction(builder, dataPD, dataLine, line, funcName, funcLine)

        if len(dataLine.loc[dataLine['token'] == 'DOIS_PONTOS']) > 0:
            if len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) > 0:
                declareVarArray(builder, funcName, dataLine)
            # elif len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) == 2:
            #     declareVarMatrix(builder, funcName, dataLine)
            else:
                declareVarEscope(builder, funcName, dataLine)

        if len(dataLine.loc[dataLine['token'] == 'ATRIBUICAO']) > 0:
            atribuition(builder, funcName, dataLine, line, functionsPD)

        if len(dataLine.loc[dataLine['token'] == 'ESCREVA']) > 0:
            escreva(builder, dataPD, funcName, dataLine, line, functionsPD)
    
        if len(dataLine.loc[dataLine['token'] == 'LEIA']) > 0:
            leia(builder, dataPD, funcName, dataLine, line)
        
        if len(dataLine.loc[dataLine['token'] == 'SE']) > 0:
            
            # verifico se possui um senao
            senao = p.verifySeAndSenao(dataPD, line)

            # se possuir o senao
            if senao:
                
                returns = findReturns(dataPD, functionsPD, funcName)
                
                # crio os blocos: verdade, falso e fim
                seTrue = funcLLVM.append_basic_block('if_true')
                seFalse = funcLLVM.append_basic_block('if_false')
                seEnd = None

                if returns == 2:
                    moreOneReturn = True
                else:
                    seEnd = funcLLVM.append_basic_block('if_end')
                

                # adiciono na lista: [TIPO, se possui senao, se ja executou o senao, bloco verdade, bloco falso, bloco fim]
                seRepitaBlock.append(['SE', senao, False, seTrue, seFalse, seEnd])

                # chamo a funcao
                se(builder, dataPD, funcName, dataLine, line, seRepitaBlock, idxBlock, seTrue, seFalse, seEnd)
                idxBlock += 1

            else:

                # caso nao possui senao, entao crio apenas os blocos: verdade e fim
                seTrue = funcLLVM.append_basic_block('if_true')
                seEnd = funcLLVM.append_basic_block('if_end')
                
                # adiciono na lista: [TIPO, se possui senao, se ja executou o senao, bloco verdade, bloco falso, bloco fim]
                seRepitaBlock.append(['SE', senao, False, seTrue, None, seEnd])
                
                # chamo a funcao
                se(builder, dataPD, funcName, dataLine, line, seRepitaBlock, idxBlock, seTrue, None, seEnd)
                idxBlock += 1
        
        # caso seja um senao
        if len(dataLine.loc[dataLine['token'] == 'SENAO']) > 0:

            # precaucao para nao dar erro
            if len(seRepitaBlock) > 0:
                
                blockCompare = seRepitaBlock[-1]

                # pego o ultimo bloco criado
                block = seRepitaBlock.pop()

                # seto a flag para indicar que estou no senao
                block[2] = True
                seRepitaBlock.append(block)

                if not moreOneReturn:
                    # vai para o if end
                    builder.branch(block[5])

                # continua no senao
                builder.position_at_end(block[4])

        if len(dataLine.loc[dataLine['token'] == 'REPITA']) > 0:
            loop = builder.append_basic_block('loop')
            loppVal = builder.append_basic_block('loop_val')
            loopEnd = builder.append_basic_block('loop_end')

            seRepitaBlock.append(['REPITA', False, False, loop, loppVal, loopEnd])

            builder.branch(loop)
            builder.position_at_end(loop)

        if len(dataLine.loc[dataLine['token'] == 'ATE']) > 0:
            
            block = seRepitaBlock[-1]

            if block[0] == 'REPITA':

                # pego o bloco
                block = seRepitaBlock.pop()
                builder.branch(block[4])
                builder.position_at_end(block[4])

                repita(builder, dataPD, dataLine, line, funcName, block[3], block[5])

        if len(dataLine.loc[dataLine['token'] == 'FIM']) > 0:
            
            if len(seRepitaBlock) > 0:

                # pego o bloco
                block = seRepitaBlock.pop()
                
                if not moreOneReturn:    
                    # vai para o fim
                    builder.branch(block[5])

                if block[5]:
                    builder.position_at_end(block[5])


        if len(dataLine.loc[dataLine['token'] == 'RETORNA']) > 0:
            valueReturn = True
            retorna(builder, dataPD, funcName, funcLLVM, dataLine, line, typeFunc, seRepitaBlock, functionsPD)

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