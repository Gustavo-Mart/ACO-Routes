from problema import construir_solucao


def solucao_gulosa(inst):
    def mais_proximo(atual, lista_candidatos):
        return min(lista_candidatos, key=lambda j: inst.distancias[atual][j])

    return construir_solucao(inst, mais_proximo)
