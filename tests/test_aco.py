import random
import unittest

from aco import atualizar_feromonio, executar_aco, roleta
from dados import gerar_instancia
from problema import Instancia, Ponto, avaliar, verificar_solucao


class TestRoleta(unittest.TestCase):
    def test_roleta_peso_zero_nunca_sai(self):
        rng = random.Random(0)
        sorteios = {roleta([0.0, 2.0, 0.0], rng) for _ in range(200)}
        self.assertEqual(sorteios, {1})

    def test_roleta_proporcional(self):
        rng = random.Random(0)
        vezes = sum(roleta([1.0, 3.0], rng) for _ in range(10000))
        self.assertTrue(7200 <= vezes <= 7800, vezes)


def instancia_quadrado():
    pontos = [
        Ponto(0, 0.0, 0.0, 0, 480, 1080),
        Ponto(1, 0.0, 10.0, 5, 480, 1080),
        Ponto(2, 10.0, 10.0, 5, 480, 1080),
        Ponto(3, 10.0, 0.0, 5, 480, 1080),
    ]
    return Instancia(pontos, 1, 100, 30.0, 10)


class TestAtualizarFeromonio(unittest.TestCase):
    def test_evaporacao_e_deposito(self):
        inst = instancia_quadrado()
        rotas = [[1, 2, 3]]
        avaliacao = avaliar(inst, rotas)
        self.assertAlmostEqual(avaliacao.distancia_total, 40.0)
        feromonio = [[1.0] * 4 for _ in range(4)]
        atualizar_feromonio(feromonio, [(rotas, avaliacao)], rho=0.1, q=100.0)
        for i, j in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            self.assertAlmostEqual(feromonio[i][j], 3.4)
            self.assertAlmostEqual(feromonio[j][i], 3.4)
        self.assertAlmostEqual(feromonio[0][2], 0.9)
        self.assertAlmostEqual(feromonio[1][3], 0.9)

    def test_solucao_invalida_nao_deposita(self):
        inst = instancia_quadrado()
        rotas = [[1, 2]]
        avaliacao = avaliar(inst, rotas)
        self.assertFalse(avaliacao.valida)
        feromonio = [[1.0] * 4 for _ in range(4)]
        atualizar_feromonio(feromonio, [(rotas, avaliacao)], rho=0.1, q=100.0)
        for linha in feromonio:
            for valor in linha:
                self.assertAlmostEqual(valor, 0.9)


class TestExecutarAco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inst = gerar_instancia()
        cls.resultado = executar_aco(cls.inst, semente=1, max_iteracoes=30)

    def test_aco_devolve_solucao_valida(self):
        self.assertEqual(verificar_solucao(self.inst, self.resultado.rotas), [])
        self.assertTrue(self.resultado.avaliacao.valida)

    def test_mesma_semente_mesmo_resultado(self):
        outro = executar_aco(self.inst, semente=1, max_iteracoes=30)
        self.assertEqual(outro.rotas, self.resultado.rotas)
        self.assertEqual(outro.historico, self.resultado.historico)

    def test_historico_nunca_piora(self):
        historico = self.resultado.historico
        self.assertEqual(len(historico), self.resultado.iteracoes)
        for anterior, atual in zip(historico, historico[1:]):
            self.assertLessEqual(atual, anterior)
        self.assertAlmostEqual(historico[-1], self.resultado.avaliacao.custo)

    def test_conta_formigas_com_solucao_valida(self):
        validas = self.resultado.validas_por_iteracao
        self.assertEqual(len(validas), self.resultado.iteracoes)
        self.assertTrue(all(0 <= v <= 20 for v in validas))
        self.assertGreater(sum(validas), 0)

    def test_para_por_estagnacao(self):
        inst = instancia_quadrado()
        resultado = executar_aco(inst, semente=1, max_iteracoes=200, limite_estagnacao=5)
        self.assertLess(resultado.iteracoes, 200)
        self.assertAlmostEqual(resultado.avaliacao.distancia_total, 40.0)

    def test_instancia_impossivel_nao_quebra(self):
        pontos = [
            Ponto(0, 0.0, 0.0, 0, 480, 1080),
            Ponto(1, 0.0, 5.0, 10, 480, 1080),
            Ponto(2, 5.0, 5.0, 10, 480, 1080),
            Ponto(3, 5.0, 0.0, 10, 480, 1080),
        ]
        inst = Instancia(pontos, 1, 10, 30.0, 10)
        resultado = executar_aco(inst, semente=1, max_iteracoes=10)
        self.assertFalse(resultado.avaliacao.valida)
        self.assertEqual(resultado.avaliacao.nao_atendidos, 2)
        self.assertEqual(resultado.validas_por_iteracao, [0] * resultado.iteracoes)

    def test_pontos_na_mesma_coordenada_nao_quebram(self):
        pontos = [
            Ponto(0, 0.0, 0.0, 0, 480, 1080),
            Ponto(1, 4.0, 4.0, 5, 480, 1080),
            Ponto(2, 4.0, 4.0, 5, 480, 1080),
        ]
        inst = Instancia(pontos, 1, 100, 30.0, 10)
        resultado = executar_aco(inst, semente=1, max_iteracoes=5)
        self.assertTrue(resultado.avaliacao.valida)


if __name__ == "__main__":
    unittest.main()
