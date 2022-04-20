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

                if 'alloca' in str(varAttrLLVM[3]):
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

def atribuition(builder, function, dataLine, line, functionsPD):

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

        if 'FUNCAO' not in loadAttr[0]:
            builder.store(loadAttr[0], varLLVMDir)
        
        else:
            functionLLVM = getLLVMFunction(attr[0][1])[1]
            chamadaFuncao = builder.call(functionLLVM, [])

            builder.store(chamadaFuncao, varLLVMDir)

    # se tiver 2 atribuicoes
    elif qtdAttr > 1:
        
        if 'FUNCAO' not in str(loadAttr[0]):

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
        
        else:

            funcName = attr[0][1].split(';;')[0]
            functionPD = functionsPD.loc[functionsPD['nome'] == funcName]

            if len(functionPD) > 0:
                funcPD = functionsPD.values[0]

                haveParams = False
                attrIdx = 0

                if len(funcPD[2]) > 0:
                    haveParams = True

                funcParams = []

                while(haveParams):
                    attrIdx += 1

                    funcParams.append(loadAttr[attrIdx])

                    if attrIdx == len(funcPD[2]):
                        haveParams = False
                
                print('params: ', funcParams)

                print(getLLVMFunction(funcName))

                chamadaFuncao = builder.call(getLLVMFunction(funcName)[1], funcParams)
                builder.store(chamadaFuncao, varLLVMDir)

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
        if len(dataLine.loc[dataLine['token'] == 'OU_LOGICO']) == 0:
            # exemplo 12
            pass
        else:
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

def se(builder, dataPD, funcName, dataLine, line, seRepitaBlock, idxBlock, seTrue, seFalse, seEnd):
    
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


def declareAll(builder, dataPD, funcName, lineStart, lineEnd, functionsPD):

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

        if len(dataLine.loc[dataLine['token'] == 'DOIS_PONTOS']) > 0:
            if len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) == 1:
                declareVarArray(builder, funcName, dataLine)
            elif len(dataLine.loc[dataLine['token'] == 'ABRE_COLCHETE']) == 2:
                declareVarMatrix(builder, funcName, dataLine)
            else:
                declareVarEscope(builder, funcName, dataLine)

        if len(dataLine.loc[dataLine['token'] == 'ATRIBUICAO']) > 0:
            atribuition(builder, funcName, dataLine, line, functionsPD)

        if len(dataLine.loc[dataLine['token'] == 'ESCREVA']) > 0:
            escreva(builder, dataPD, funcName, dataLine, line)
    
        if len(dataLine.loc[dataLine['token'] == 'LEIA']) > 0:
            leia(builder, dataPD, funcName, dataLine, line)
        
        if len(dataLine.loc[dataLine['token'] == 'SE']) > 0:
            
            # verifico se possui um senao
            senao = p.verifySeAndSenao(dataPD, line)

            # se possuir o senao
            if senao:

                # crio os blocos: verdade, falso e fim
                seTrue = funcLLVM.append_basic_block('if_true')
                seFalse = funcLLVM.append_basic_block('if_false')
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

                # vai para o fim
                builder.branch(block[5])
                builder.position_at_end(block[5])

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