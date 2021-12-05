import llvmlite.binding as llvm
import llvmlite.ir as ll

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
