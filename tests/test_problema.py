import unittest

from problema import Instancia, Ponto, candidatos, construir_solucao, simular_rota, verificar_solucao, avaliar
from parametros import PENALIDADE


def instancia_pequena(num_veiculos=2, capacidade=20):
    pontos = [
        Ponto(0, 0.0, 0.0, 0, 480, 1080),
        Ponto(1, 3.0, 4.0, 10, 480, 600),
        Ponto(2, 6.0, 8.0, 10, 540, 660),
        Ponto(3, 0.0, 5.0, 15, 900, 1020),
    ]
    return Instancia(pontos, num_veiculos, capacidade, 30.0, 10)


def mais_proximo(inst):
    def escolher(atual, lista):
        return min(lista, key=lambda j: inst.distancias[atual][j])
    return escolher


class TestDistancias(unittest.TestCase):
    def test_distancia_3_4_5(self):
        inst = instancia_pequena()
        self.assertAlmostEqual(inst.distancias[0][1], 5.0)
        self.assertAlmostEqual(inst.tempo_viagem(0, 1), 10.0)

    def test_distancia_zero_nao_quebra(self):
        pontos = [
            Ponto(0, 0.0, 0.0, 0, 480, 1080),
            Ponto(1, 2.0, 2.0, 5, 480, 1080),
            Ponto(2, 2.0, 2.0, 5, 480, 1080),
        ]
        inst = Instancia(pontos, 1, 100, 30.0, 10)
        self.assertEqual(inst.distancias[1][2], 0.0)
        self.assertEqual(inst.clientes(), [1, 2])


class TestCandidatos(unittest.TestCase):
    def test_candidatos_respeita_capacidade(self):
        inst = instancia_pequena(capacidade=20)
        self.assertEqual(candidatos(inst, 0, 10, 480, {1, 2, 3}), [1, 2])

    def test_candidatos_respeita_fim_da_janela(self):
        inst = instancia_pequena()
        self.assertNotIn(1, candidatos(inst, 0, 0, 601, {1, 2, 3}))
        self.assertIn(1, candidatos(inst, 0, 0, 590, {1, 2, 3}))

    def test_candidatos_exige_volta_ate_o_fim_da_jornada(self):
        pontos = [
            Ponto(0, 0.0, 0.0, 0, 480, 1080),
            Ponto(1, 0.0, 10.0, 5, 480, 1080),
        ]
        inst = Instancia(pontos, 1, 100, 30.0, 10)
        self.assertEqual(candidatos(inst, 0, 0, 1030, {1}), [1])
        self.assertEqual(candidatos(inst, 0, 0, 1031, {1}), [])


class TestSimularRota(unittest.TestCase):
    def test_simular_rota_espera_quando_chega_cedo(self):
        inst = instancia_pequena()
        detalhe = simular_rota(inst, [1, 2])
        p1, p2 = detalhe.paradas
        self.assertEqual((p1.cliente, p1.chegada, p1.espera, p1.saida), (1, 490, 0, 500))
        self.assertEqual((p2.chegada, p2.espera, p2.inicio_servico, p2.saida), (510, 30, 540, 550))
        self.assertEqual(detalhe.carga, 20)
        self.assertAlmostEqual(detalhe.distancia, 5.0 + 5.0 + 10.0)
        self.assertAlmostEqual(detalhe.retorno, 570)

    def test_simular_rota_vazia(self):
        detalhe = simular_rota(instancia_pequena(), [])
        self.assertEqual(detalhe.paradas, [])
        self.assertEqual(detalhe.distancia, 0.0)


class TestAvaliar(unittest.TestCase):
    def test_avaliar_solucao_completa(self):
        inst = instancia_pequena(capacidade=20)
        av = avaliar(inst, [[1, 2], [3]])
        self.assertAlmostEqual(av.distancia_total, 20.0 + 10.0)
        self.assertEqual(av.veiculos_usados, 2)
        self.assertEqual(av.nao_atendidos, 0)
        self.assertTrue(av.valida)
        self.assertAlmostEqual(av.custo, 30.0)
        self.assertAlmostEqual(av.espera_total, 30 + 410)

    def test_avaliar_penaliza_nao_atendidos(self):
        inst = instancia_pequena()
        av = avaliar(inst, [[1]])
        self.assertEqual(av.nao_atendidos, 2)
        self.assertFalse(av.valida)
        self.assertAlmostEqual(av.custo, 10.0 + 2 * PENALIDADE)


class TestVerificarSolucao(unittest.TestCase):
    def test_solucao_valida_nao_tem_violacoes(self):
        inst = instancia_pequena(capacidade=20)
        self.assertEqual(verificar_solucao(inst, [[1, 2], [3]]), [])

    def test_verificar_detecta_cliente_repetido(self):
        inst = instancia_pequena(capacidade=100)
        self.assertTrue(any("mais de uma vez" in v for v in verificar_solucao(inst, [[1, 2], [1, 3]])))

    def test_verificar_detecta_cliente_faltando(self):
        inst = instancia_pequena()
        self.assertTrue(any("nao atendido" in v for v in verificar_solucao(inst, [[1, 2]])))

    def test_verificar_detecta_carga_acima_da_capacidade(self):
        inst = instancia_pequena(capacidade=20)
        self.assertTrue(any("capacidade" in v for v in verificar_solucao(inst, [[1, 2, 3]])))

    def test_verificar_detecta_chegada_depois_da_janela(self):
        inst = instancia_pequena(capacidade=100)
        self.assertTrue(any("janela" in v for v in verificar_solucao(inst, [[3, 1], [2]])))

    def test_verificar_detecta_veiculos_demais(self):
        inst = instancia_pequena(num_veiculos=2)
        self.assertTrue(any("veiculos" in v for v in verificar_solucao(inst, [[1], [2], [3]])))

    def test_verificar_detecta_volta_depois_do_fim_da_jornada(self):
        pontos = [
            Ponto(0, 0.0, 0.0, 0, 480, 1080),
            Ponto(1, 0.0, 10.0, 5, 1060, 1080),
        ]
        inst = Instancia(pontos, 1, 100, 30.0, 10)
        self.assertTrue(any("jornada" in v for v in verificar_solucao(inst, [[1]])))


class TestConstruirSolucao(unittest.TestCase):
    def test_construir_abre_novo_veiculo(self):
        inst = instancia_pequena(num_veiculos=2, capacidade=20)
        rotas, nao_atendidos = construir_solucao(inst, mais_proximo(inst))
        self.assertEqual(rotas, [[1, 2], [3]])
        self.assertEqual(nao_atendidos, [])
        self.assertEqual(verificar_solucao(inst, rotas), [])

    def test_construir_sem_veiculos_deixa_nao_atendidos(self):
        inst = instancia_pequena(num_veiculos=1, capacidade=20)
        rotas, nao_atendidos = construir_solucao(inst, mais_proximo(inst))
        self.assertEqual(rotas, [[1, 2]])
        self.assertEqual(nao_atendidos, [3])

    def test_construir_cliente_impossivel_nao_trava(self):
        pontos = [
            Ponto(0, 0.0, 0.0, 0, 480, 1080),
            Ponto(1, 3.0, 4.0, 10, 480, 600),
            Ponto(2, 0.0, 5.0, 500, 480, 1080),
        ]
        inst = Instancia(pontos, 3, 100, 30.0, 10)
        rotas, nao_atendidos = construir_solucao(inst, mais_proximo(inst))
        self.assertEqual(rotas, [[1]])
        self.assertEqual(nao_atendidos, [2])


if __name__ == "__main__":
    unittest.main()
