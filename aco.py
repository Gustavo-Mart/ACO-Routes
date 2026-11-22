import random
import time
from dataclasses import dataclass

from parametros import ALFA, BETA, RHO, Q, TAU0, NUM_FORMIGAS, MAX_ITERACOES, LIMITE_ESTAGNACAO
from problema import avaliar, construir_solucao


@dataclass
class ResultadoACO:
    rotas: list
    avaliacao: object
    historico: list
    iteracoes: int
    segundos: float
    validas_por_iteracao: list


def roleta(pesos, rng):
    total = sum(pesos)
    sorteio = rng.random() * total
    acumulado = 0.0
    for indice, peso in enumerate(pesos):
        acumulado += peso
        if peso > 0 and sorteio <= acumulado:
            return indice
    return max(i for i, peso in enumerate(pesos) if peso > 0)


def arestas_da_solucao(rotas):
    arestas = []
    for rota in rotas:
        caminho = [0] + rota + [0]
        for i, j in zip(caminho, caminho[1:]):
            arestas.append((i, j))
    return arestas


def atualizar_feromonio(feromonio, solucoes, rho, q):
    n = len(feromonio)
    for i in range(n):
        for j in range(n):
            feromonio[i][j] = (1 - rho) * feromonio[i][j]
    for rotas, avaliacao in solucoes:
        if not avaliacao.valida:
            continue
        deposito = q / avaliacao.distancia_total
        for i, j in arestas_da_solucao(rotas):
            feromonio[i][j] += deposito
            if i != j:
                feromonio[j][i] += deposito


def executar_aco(inst, semente, alfa=ALFA, beta=BETA, rho=RHO, q=Q, tau0=TAU0, num_formigas=NUM_FORMIGAS,
                 max_iteracoes=MAX_ITERACOES, limite_estagnacao=LIMITE_ESTAGNACAO):
    inicio = time.time()
    rng = random.Random(semente)
    n = len(inst.pontos)

    heuristica = [[1.0 / max(d, 0.001) for d in linha] for linha in inst.distancias]

    feromonio = [[tau0] * n for _ in range(n)]

    def escolher(atual, lista_candidatos):
        pesos = [
            (feromonio[atual][j] ** alfa) * (heuristica[atual][j] ** beta)
            for j in lista_candidatos
        ]
        return lista_candidatos[roleta(pesos, rng)]

    melhor_rotas, melhor_avaliacao = None, None
    historico = []
    validas_por_iteracao = []
    sem_melhora = 0

    for _ in range(max_iteracoes):
        solucoes = []
        for _ in range(num_formigas):
            rotas, _ = construir_solucao(inst, escolher)
            solucoes.append((rotas, avaliar(inst, rotas)))

        rotas_iteracao, avaliacao_iteracao = min(solucoes, key=lambda s: s[1].custo)
        if melhor_avaliacao is None or avaliacao_iteracao.custo < melhor_avaliacao.custo:
            melhor_rotas, melhor_avaliacao = rotas_iteracao, avaliacao_iteracao
            sem_melhora = 0
        else:
            sem_melhora += 1
        historico.append(melhor_avaliacao.custo)
        validas = 0
        for _, avaliacao in solucoes:
            if avaliacao.valida:
                validas += 1
        validas_por_iteracao.append(validas)

        atualizar_feromonio(feromonio, solucoes, rho, q)

        if sem_melhora >= limite_estagnacao:
            break

    segundos = time.time() - inicio
    return ResultadoACO(melhor_rotas, melhor_avaliacao, historico, len(historico), segundos,
                        validas_por_iteracao)
