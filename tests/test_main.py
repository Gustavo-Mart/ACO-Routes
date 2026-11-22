import json
import os
import tempfile
import unittest

from main import main

ARQUIVOS = ["clientes.csv", "rotas.csv", "resumo.txt", "comparacao.txt", "resultados.json",
            "mapa_rotas.png", "convergencia.png", "horarios_veiculos.png"]


class TestMain(unittest.TestCase):
    def test_main_gera_todos_os_arquivos(self):
        with tempfile.TemporaryDirectory() as base:
            pasta = os.path.join(base, "resultados")
            dados = main(pasta, mostrar=False)
            for nome in ARQUIVOS:
                caminho = os.path.join(pasta, nome)
                self.assertTrue(os.path.exists(caminho), nome)
                self.assertGreater(os.path.getsize(caminho), 0, nome)

            de_novo = main(pasta, mostrar=False)
            self.assertEqual(de_novo["melhor"]["distancia_km"], dados["melhor"]["distancia_km"])

            with open(os.path.join(pasta, "resultados.json"), encoding="utf-8") as arquivo:
                gravado = json.load(arquivo)

        self.assertTrue(gravado["melhor"]["valida"])
        self.assertEqual(gravado["melhor"]["violacoes"], [])
        self.assertEqual(len(gravado["execucoes"]), 5)
        self.assertEqual(gravado["melhor"]["clientes_atendidos"], 40)
        menor = min(e["distancia_km"] for e in gravado["execucoes"])
        self.assertAlmostEqual(gravado["melhor"]["distancia_km"], menor)
        self.assertAlmostEqual(gravado["aco"]["melhor_km"], menor)
        clientes = [p["cliente"] for v in gravado["melhor"]["veiculos"] for p in v["paradas"]]
        self.assertEqual(sorted(clientes), list(range(1, 41)))


if __name__ == "__main__":
    unittest.main()
