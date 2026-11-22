import math
from dataclasses import dataclass

from parametros import FIM_JORNADA, INICIO_JORNADA, PENALIDADE


@dataclass
class Ponto:
    id: int
    x: float
    y: float
    demanda: int
    inicio: int
    fim: int


@dataclass
class Instancia:
    pontos: list
    num_veiculos: int
    capacidade: int
    velocidade_kmh: float
    tempo_servico: int
    semente: int = 0

    def __post_init__(self):
        self.distancias = []
        for a in self.pontos:
            linha = []
            for b in self.pontos:
                linha.append(math.dist((a.x, a.y), (b.x, b.y)))
            self.distancias.append(linha)

    def tempo_viagem(self, i, j):
        return self.distancias[i][j] / self.velocidade_kmh * 60

    def clientes(self):
        return [p.id for p in self.pontos[1:]]


@dataclass
class Parada:
    cliente: int
    chegada: float
    espera: float
    inicio_servico: float
    saida: float


@dataclass
class DetalheRota:
    paradas: list
    carga: int
    distancia: float
    retorno: float


@dataclass
class Avaliacao:
    distancia_total: float
    veiculos_usados: int
    espera_total: float
    nao_atendidos: int
    valida: bool
    custo: float


def candidatos(inst, atual, carga, relogio, nao_atendidos):
    lista = []
    for j in sorted(nao_atendidos):
        cliente = inst.pontos[j]
        if carga + cliente.demanda > inst.capacidade:
            continue
        chegada = relogio + inst.tempo_viagem(atual, j)
        if chegada > cliente.fim:
            continue
        saida = max(chegada, cliente.inicio) + inst.tempo_servico
        if saida + inst.tempo_viagem(j, 0) > FIM_JORNADA:
            continue
        lista.append(j)
    return lista


def construir_solucao(inst, escolher):
    nao_atendidos = set(inst.clientes())
    rotas = []
    while nao_atendidos and len(rotas) < inst.num_veiculos:
        rota = []
        atual, carga, relogio = 0, 0, INICIO_JORNADA
        while True:
            lista = candidatos(inst, atual, carga, relogio, nao_atendidos)
            if not lista:
                break
            proximo = escolher(atual, lista)
            cliente = inst.pontos[proximo]
            chegada = relogio + inst.tempo_viagem(atual, proximo)
            relogio = max(chegada, cliente.inicio) + inst.tempo_servico
            carga += cliente.demanda
            rota.append(proximo)
            nao_atendidos.remove(proximo)
            atual = proximo
        if not rota:
            break
        rotas.append(rota)
    return rotas, sorted(nao_atendidos)


def simular_rota(inst, rota):
    paradas = []
    atual, carga, relogio, distancia = 0, 0, INICIO_JORNADA, 0.0
    for j in rota:
        cliente = inst.pontos[j]
        chegada = relogio + inst.tempo_viagem(atual, j)
        inicio_servico = max(chegada, cliente.inicio)
        saida = inicio_servico + inst.tempo_servico
        paradas.append(Parada(j, chegada, inicio_servico - chegada, inicio_servico, saida))
        distancia += inst.distancias[atual][j]
        carga += cliente.demanda
        atual, relogio = j, saida
    distancia += inst.distancias[atual][0]
    retorno = relogio + inst.tempo_viagem(atual, 0)
    return DetalheRota(paradas, carga, distancia, retorno)


def verificar_solucao(inst, rotas):
    violacoes = []
    if len(rotas) > inst.num_veiculos:
        violacoes.append(f"usa {len(rotas)} veiculos, mas so ha {inst.num_veiculos} veiculos")
    visitas = [j for rota in rotas for j in rota]
    for j in inst.clientes():
        if visitas.count(j) == 0:
            violacoes.append(f"cliente {j} nao atendido")
        elif visitas.count(j) > 1:
            violacoes.append(f"cliente {j} atendido mais de uma vez")
    for numero, rota in enumerate(rotas, start=1):
        detalhe = simular_rota(inst, rota)
        if detalhe.carga > inst.capacidade:
            violacoes.append(f"veiculo {numero}: carga {detalhe.carga} acima da capacidade {inst.capacidade}")
        for parada in detalhe.paradas:
            if parada.chegada > inst.pontos[parada.cliente].fim:
                violacoes.append(f"veiculo {numero}: chega ao cliente {parada.cliente} depois do fim da janela")
        if detalhe.retorno > FIM_JORNADA:
            violacoes.append(f"veiculo {numero}: volta ao deposito depois do fim da jornada")
    return violacoes


def avaliar(inst, rotas):
    detalhes = [simular_rota(inst, rota) for rota in rotas]
    distancia_total = sum(d.distancia for d in detalhes)
    espera_total = sum(p.espera for d in detalhes for p in d.paradas)
    atendidos = {j for rota in rotas for j in rota}
    nao_atendidos = len(set(inst.clientes()) - atendidos)
    valida = not verificar_solucao(inst, rotas)
    custo = distancia_total + PENALIDADE * nao_atendidos
    return Avaliacao(distancia_total, len(rotas), espera_total, nao_atendidos, valida, custo)
