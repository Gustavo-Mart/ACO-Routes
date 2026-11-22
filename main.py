import csv
import json
import os
import statistics

import parametros
from aco import executar_aco
from dados import gerar_instancia, horario, salvar_clientes_csv
from graficos import grafico_convergencia, grafico_horarios, grafico_mapa
from guloso import solucao_gulosa
from problema import avaliar, simular_rota, verificar_solucao


def detalhar_veiculos(inst, rotas):
    veiculos = []
    for numero, rota in enumerate(rotas, start=1):
        detalhe = simular_rota(inst, rota)
        paradas = []
        for ordem, parada in enumerate(detalhe.paradas, start=1):
            cliente = inst.pontos[parada.cliente]
            paradas.append({
                "ordem": ordem,
                "cliente": parada.cliente,
                "demanda": cliente.demanda,
                "janela": f"{horario(cliente.inicio)}-{horario(cliente.fim)}",
                "chegada": horario(parada.chegada),
                "espera_min": round(parada.espera, 1),
                "inicio_atendimento": horario(parada.inicio_servico),
                "saida": horario(parada.saida),
            })
        veiculos.append({
            "numero": numero,
            "entregas": len(rota),
            "carga": detalhe.carga,
            "distancia_km": round(detalhe.distancia, 2),
            "espera_min": round(sum(p.espera for p in detalhe.paradas), 1),
            "retorno": horario(detalhe.retorno),
            "rota": rota,
            "paradas": paradas,
        })
    return veiculos


def gravar_rotas_csv(veiculos, caminho):
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["veiculo", "ordem", "cliente", "demanda", "janela", "chegada",
        "espera_min", "inicio_atendimento", "saida"])
        for veiculo in veiculos:
            for p in veiculo["paradas"]:
                escritor.writerow([veiculo["numero"], p["ordem"], p["cliente"], p["demanda"],
                p["janela"], p["chegada"], p["espera_min"],
                p["inicio_atendimento"], p["saida"]])


def gravar_resumo(dados, caminho):
    melhor, inst = dados["melhor"], dados["instancia"]
    linhas = [
        "RESUMO DA MELHOR SOLUCAO ENCONTRADA PELO ACO",
        "",
        f"Instancia: {inst['num_clientes']} clientes, {inst['num_veiculos']} veiculos de capacidade "
        f"{inst['capacidade']}, demanda total {inst['demanda_total']} (semente {inst['semente']})",
        f"Execucao escolhida: semente {melhor['semente']} ({melhor['iteracoes']} iteracoes)",
        "",
        f"Distancia total:      {melhor['distancia_km']:.2f} km",
        f"Veiculos usados:      {melhor['veiculos_usados']}",
        f"Clientes atendidos:   {melhor['clientes_atendidos']} de {inst['num_clientes']}",
        f"Espera total:         {melhor['espera_min']:.0f} min",
        f"Solucao valida:       {'sim' if melhor['valida'] else 'NAO'}",
    ]
    for violacao in melhor["violacoes"]:
        linhas.append(f"  VIOLACAO: {violacao}")
    linhas.append("")
    for v in melhor["veiculos"]:
        rota = " -> ".join(["deposito"] + [str(j) for j in v["rota"]] + ["deposito"])
        linhas.append(f"Veiculo {v['numero']}: {v['entregas']} entregas, carga {v['carga']}, "
        f"{v['distancia_km']:.2f} km, volta as {v['retorno']}")
        linhas.append(f"  {rota}")
    linhas += ["", "Parametros do ACO:"]
    linhas += [f"  {nome} = {valor}" for nome, valor in dados["parametros"].items()]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")


def gravar_comparacao(dados, caminho):
    gulosa, aco = dados["gulosa"], dados["aco"]
    linhas = [
        "COMPARACAO: SOLUCAO GULOSA x ACO",
        "",
        f"Solucao gulosa (vizinho mais proximo): {gulosa['distancia_km']:.2f} km, "
        f"{gulosa['veiculos_usados']} veiculos",
        "",
        "ACO, uma execucao por semente:",
        "semente  distancia_km  veiculos  iteracoes  segundos  valida",
    ]
    for e in dados["execucoes"]:
        linhas.append(f"{e['semente']:>7}  {e['distancia_km']:>12.2f}  {e['veiculos_usados']:>8}  "
        f"{e['iteracoes']:>9}  {e['segundos']:>8.2f}  {'sim' if e['valida'] else 'NAO'}")
    linhas += [
        "",
        f"Melhor: {aco['melhor_km']:.2f} km   Media: {aco['media_km']:.2f} km   "
        f"Pior: {aco['pior_km']:.2f} km   Desvio padrao: {aco['desvio_km']:.2f} km",
        f"Reducao da melhor execucao em relacao a gulosa: {aco['reducao_melhor_pct']:.1f}%",
        f"Reducao media em relacao a gulosa:              {aco['reducao_media_pct']:.1f}%",
    ]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")


def main(pasta_saida="resultados", mostrar=True):
    def avisar(texto):
        if mostrar:
            print(texto)

    os.makedirs(pasta_saida, exist_ok=True)

    def caminho(nome):
        return os.path.join(pasta_saida, nome)

    inst = gerar_instancia()
    salvar_clientes_csv(inst, caminho("clientes.csv"))
    demanda_total = sum(p.demanda for p in inst.pontos)
    avisar(f"Instancia: {len(inst.clientes())} clientes, {inst.num_veiculos} veiculos, "
    f"demanda total {demanda_total}")

    rotas_gulosa, _ = solucao_gulosa(inst)
    av_gulosa = avaliar(inst, rotas_gulosa)
    avisar(f"Solucao gulosa: {av_gulosa.distancia_total:.2f} km")

    resultados = []
    for semente in parametros.SEMENTES_ACO:
        resultado = executar_aco(inst, semente)
        resultados.append((semente, resultado))
        avisar(f"ACO semente {semente}: {resultado.avaliacao.distancia_total:.2f} km "
            f"em {resultado.iteracoes} iteracoes ({resultado.segundos:.1f} s)")

    semente_melhor, melhor = min(resultados, key=lambda r: r[1].avaliacao.custo)
    violacoes = verificar_solucao(inst, melhor.rotas)
    veiculos = detalhar_veiculos(inst, melhor.rotas)
    distancias = [r.avaliacao.distancia_total for _, r in resultados]

    dados = {
        "parametros": {
            "ALFA": parametros.ALFA, "BETA": parametros.BETA, "RHO": parametros.RHO,
            "Q": parametros.Q, "TAU0": parametros.TAU0,
            "NUM_FORMIGAS": parametros.NUM_FORMIGAS,
            "MAX_ITERACOES": parametros.MAX_ITERACOES,
            "LIMITE_ESTAGNACAO": parametros.LIMITE_ESTAGNACAO,
        },
        "instancia": {
            "semente": inst.semente,
            "num_clientes": len(inst.clientes()),
            "num_veiculos": inst.num_veiculos,
            "capacidade": inst.capacidade,
            "demanda_total": demanda_total,
            "velocidade_kmh": inst.velocidade_kmh,
            "tempo_servico_min": inst.tempo_servico,
            "clientes": [
                {"id": p.id, "x": p.x, "y": p.y, "demanda": p.demanda,
                "janela": f"{horario(p.inicio)}-{horario(p.fim)}"}
                for p in inst.pontos[1:]
            ],
        },
        "gulosa": {
            "distancia_km": av_gulosa.distancia_total,
            "veiculos_usados": av_gulosa.veiculos_usados,
            "espera_min": av_gulosa.espera_total,
            "valida": av_gulosa.valida,
            "rotas": rotas_gulosa,
        },
        "execucoes": [
            {
                "semente": semente,
                "distancia_km": r.avaliacao.distancia_total,
                "veiculos_usados": r.avaliacao.veiculos_usados,
                "espera_min": r.avaliacao.espera_total,
                "iteracoes": r.iteracoes,
                "segundos": r.segundos,
                "valida": r.avaliacao.valida,
                "formigas_validas_pct": 100 * sum(r.validas_por_iteracao)
                                        / (r.iteracoes * parametros.NUM_FORMIGAS),
            }
            for semente, r in resultados
        ],
        "aco": {
            "melhor_km": min(distancias),
            "media_km": statistics.mean(distancias),
            "pior_km": max(distancias),
            "desvio_km": statistics.stdev(distancias) if len(distancias) > 1 else 0.0,
            "reducao_melhor_pct": 100 * (1 - min(distancias) / av_gulosa.distancia_total),
            "reducao_media_pct": 100 * (1 - statistics.mean(distancias) / av_gulosa.distancia_total),
            "segundos_total": sum(r.segundos for _, r in resultados),
        },
        "melhor": {
            "semente": semente_melhor,
            "distancia_km": melhor.avaliacao.distancia_total,
            "veiculos_usados": melhor.avaliacao.veiculos_usados,
            "espera_min": melhor.avaliacao.espera_total,
            "clientes_atendidos": len(inst.clientes()) - melhor.avaliacao.nao_atendidos,
            "valida": melhor.avaliacao.valida,
            "violacoes": violacoes,
            "iteracoes": melhor.iteracoes,
            "historico": melhor.historico,
            "validas_por_iteracao": melhor.validas_por_iteracao,
            "veiculos": veiculos,
        },
    }

    with open(caminho("resultados.json"), "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    gravar_rotas_csv(veiculos, caminho("rotas.csv"))
    gravar_resumo(dados, caminho("resumo.txt"))
    gravar_comparacao(dados, caminho("comparacao.txt"))
    grafico_mapa(inst, melhor.rotas, caminho("mapa_rotas.png"))
    grafico_convergencia(melhor.historico, av_gulosa.distancia_total, caminho("convergencia.png"))
    grafico_horarios(inst, melhor.rotas, caminho("horarios_veiculos.png"))

    avisar("")
    avisar(f"Melhor solucao do ACO: {melhor.avaliacao.distancia_total:.2f} km "
        f"(semente {semente_melhor}), {dados['aco']['reducao_melhor_pct']:.1f}% abaixo da gulosa")
    if violacoes:
        avisar("ATENCAO: a melhor solucao viola restricoes:")
        for violacao in violacoes:
            avisar(f"  {violacao}")
    else:
        avisar("Todos os clientes atendidos dentro da janela, da capacidade e da jornada.")
    avisar(f"Arquivos gravados em: {os.path.abspath(pasta_saida)}")
    return dados


if __name__ == "__main__":
    main()
