import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parametros import FIM_JORNADA, INICIO_JORNADA, PENALIDADE
from problema import simular_rota

CORES = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
         "tab:brown", "tab:pink", "tab:olive", "tab:cyan", "tab:gray"]


def grafico_mapa(inst, rotas, caminho):
    fig, ax = plt.subplots(figsize=(8, 8))
    deposito = inst.pontos[0]
    for numero, rota in enumerate(rotas, start=1):
        detalhe = simular_rota(inst, rota)
        caminho_rota = [deposito] + [inst.pontos[j] for j in rota] + [deposito]
        ax.plot(
            [p.x for p in caminho_rota], [p.y for p in caminho_rota],
            color=CORES[(numero - 1) % len(CORES)], marker="o", markersize=5, linewidth=1.5,
            label=f"Veículo {numero}: {len(rota)} entregas, carga {detalhe.carga}, "
                  f"{detalhe.distancia:.1f} km",
        )
    for p in inst.pontos[1:]:
        ax.annotate(str(p.id), (p.x, p.y), textcoords="offset points", xytext=(5, 5), fontsize=8)
    ax.plot(deposito.x, deposito.y, marker="s", color="black", markersize=12,
            linestyle="none", label="Depósito")
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.set_title("Rotas de entrega encontradas pelo ACO")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=9, frameon=False)
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)


def grafico_convergencia(historico, custo_guloso, caminho):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    pontos = [(i, custo) for i, custo in enumerate(historico, start=1) if custo < PENALIDADE]
    if pontos:
        ax.step([i for i, _ in pontos], [c for _, c in pontos], where="post",
                color="tab:blue", linewidth=2, label="ACO (melhor solução até a iteração)")
    ax.axhline(custo_guloso, color="tab:red", linestyle="--", linewidth=1.5,
               label=f"Solução gulosa ({custo_guloso:.1f} km)")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Distância total (km)")
    ax.set_title("Convergência do ACO")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)


def grafico_horarios(inst, rotas, caminho):
    fig, eixos = plt.subplots(len(rotas), 1, figsize=(9, 2.2 * len(rotas) + 1), sharex=True)
    if len(rotas) == 1:
        eixos = [eixos]
    for numero, (ax, rota) in enumerate(zip(eixos, rotas), start=1):
        detalhe = simular_rota(inst, rota)
        cor = CORES[(numero - 1) % len(CORES)]
        for linha, parada in enumerate(detalhe.paradas):
            cliente = inst.pontos[parada.cliente]
            ax.barh(linha, cliente.fim - cliente.inicio, left=cliente.inicio, height=0.6,
                    color="lightgray", edgecolor="gray", linewidth=0.5)
            if parada.espera > 0:
                ax.plot([parada.chegada, parada.inicio_servico], [linha, linha],
                        color=cor, linestyle=":", linewidth=1.5)
            ax.barh(linha, parada.saida - parada.inicio_servico, left=parada.inicio_servico,
                    height=0.6, color=cor)
        ax.set_yticks(range(len(rota)))
        ax.set_yticklabels([f"Cliente {j}" for j in rota], fontsize=7)
        ax.invert_yaxis()
        ax.set_ylabel(f"Veículo {numero}", fontsize=9)
        ax.grid(True, axis="x", alpha=0.3)
    horas = list(range(INICIO_JORNADA, FIM_JORNADA + 1, 60))
    eixos[-1].set_xticks(horas)
    eixos[-1].set_xticklabels([f"{h // 60}h" for h in horas])
    eixos[-1].set_xlim(INICIO_JORNADA, FIM_JORNADA)
    eixos[-1].set_xlabel("Horário")
    eixos[0].set_title("Atendimento de cada cliente dentro da janela de horário\n"
                       "(cinza: janela do cliente; cor: atendimento; pontilhado: espera)",
                       fontsize=10)
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
