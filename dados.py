import csv
import random

from guloso import solucao_gulosa
from parametros import NUM_CLIENTES, NUM_VEICULOS, CAPACIDADE, TAMANHO_AREA, SEMENTE_INSTANCIA
from parametros import INICIO_JORNADA, FIM_JORNADA, VELOCIDADE_KMH, TEMPO_SERVICO
from parametros import DEMANDA_MIN, DEMANDA_MAX
from problema import Instancia, Ponto

DURACOES_JANELA = (120, 150, 180)
DEMANDA_TOTAL_MIN = 350
DEMANDA_TOTAL_MAX = 450


def horario(minutos):
    minutos = int(round(minutos))
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def sortear_clientes(semente):
    rng = random.Random(semente)
    centro = TAMANHO_AREA / 2
    pontos = [Ponto(0, centro, centro, 0, INICIO_JORNADA, FIM_JORNADA)]
    for i in range(1, NUM_CLIENTES + 1):
        x = round(rng.uniform(0, TAMANHO_AREA), 1)
        y = round(rng.uniform(0, TAMANHO_AREA), 1)
        demanda = rng.randint(DEMANDA_MIN, DEMANDA_MAX)
        duracao = rng.choice(DURACOES_JANELA)
        ultimo_inicio = FIM_JORNADA - duracao
        inicio = rng.randrange(INICIO_JORNADA, ultimo_inicio + 1, 30)
        pontos.append(Ponto(i, x, y, demanda, inicio, inicio + duracao))
    return Instancia(pontos, NUM_VEICULOS, CAPACIDADE, VELOCIDADE_KMH, TEMPO_SERVICO, semente)


def gerar_instancia(semente=SEMENTE_INSTANCIA):
    while True:
        inst = sortear_clientes(semente)
        demanda_total = sum(p.demanda for p in inst.pontos)
        if DEMANDA_TOTAL_MIN <= demanda_total <= DEMANDA_TOTAL_MAX:
            _, nao_atendidos = solucao_gulosa(inst)
            if not nao_atendidos:
                return inst
        semente += 1


def salvar_clientes_csv(inst, caminho):
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["id", "x_km", "y_km", "demanda", "inicio_janela", "fim_janela"])
        for p in inst.pontos[1:]:
            escritor.writerow([p.id, p.x, p.y, p.demanda, horario(p.inicio), horario(p.fim)])
