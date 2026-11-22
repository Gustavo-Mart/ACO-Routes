import csv
import os
import tempfile
import unittest

from dados import gerar_instancia, salvar_clientes_csv
from guloso import solucao_gulosa
from problema import verificar_solucao
from parametros import FIM_JORNADA, INICIO_JORNADA


class TestGerarInstancia(unittest.TestCase):
    def setUp(self):
        self.inst = gerar_instancia()

    def test_mesma_semente_mesma_instancia(self):
        outra = gerar_instancia()
        self.assertEqual(self.inst.pontos, outra.pontos)
        self.assertEqual(self.inst.semente, outra.semente)

    def test_sementes_diferentes_dao_instancias_diferentes(self):
        outra = gerar_instancia(semente=self.inst.semente + 1000)
        self.assertNotEqual(self.inst.pontos, outra.pontos)

    def test_quarenta_clientes_e_deposito_no_centro(self):
        self.assertEqual(len(self.inst.clientes()), 40)
        deposito = self.inst.pontos[0]
        self.assertEqual((deposito.x, deposito.y, deposito.demanda), (10.0, 10.0, 0))
        self.assertEqual(self.inst.num_veiculos, 5)
        self.assertEqual(self.inst.capacidade, 100)

    def test_clientes_dentro_da_area_e_demanda_entre_5_e_15(self):
        for p in self.inst.pontos[1:]:
            self.assertTrue(0 <= p.x <= 20 and 0 <= p.y <= 20)
            self.assertTrue(5 <= p.demanda <= 15)

    def test_janelas_dentro_da_jornada_e_duracao_valida(self):
        for p in self.inst.pontos[1:]:
            self.assertGreaterEqual(p.inicio, INICIO_JORNADA)
            self.assertLessEqual(p.fim, FIM_JORNADA)
            self.assertIn(p.fim - p.inicio, (120, 150, 180))
            self.assertEqual(p.inicio % 30, 0)

    def test_demanda_total_entre_350_e_450(self):
        total = sum(p.demanda for p in self.inst.pontos)
        self.assertTrue(350 <= total <= 450, total)

    def test_gulosa_atende_todos_e_e_valida(self):
        rotas, nao_atendidos = solucao_gulosa(self.inst)
        self.assertEqual(nao_atendidos, [])
        self.assertEqual(verificar_solucao(self.inst, rotas), [])

    def test_csv_tem_cabecalho_e_40_linhas(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "clientes.csv")
            salvar_clientes_csv(self.inst, caminho)
            with open(caminho, encoding="utf-8", newline="") as arquivo:
                linhas = list(csv.reader(arquivo))
        self.assertEqual(linhas[0], ["id", "x_km", "y_km", "demanda", "inicio_janela", "fim_janela"])
        self.assertEqual(len(linhas), 41)
        self.assertEqual(linhas[1][0], "1")


if __name__ == "__main__":
    unittest.main()
