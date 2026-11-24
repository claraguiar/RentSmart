"""Testes das regras comerciais. Execute com:  python -m unittest discover tests"""

import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from rentsmart import Apartamento, Casa, Estudio, ExportadorCSV, Orcamento, TaxaContrato

D = Decimal


class TestApartamento(unittest.TestCase):
    def test_um_quarto_com_criancas(self):
        self.assertEqual(Apartamento(1, False, True).valor_mensal(), D("700.00"))

    def test_dois_quartos(self):
        self.assertEqual(Apartamento(2, False, True).valor_mensal(), D("900.00"))

    def test_desconto_aplicado_apos_adicionais(self):
        # 700 + 200 + 300 = 1200 ; 5% = 60 ; total 1140
        self.assertEqual(Apartamento(2, True, False).valor_mensal(), D("1140.00"))

    def test_um_quarto_sem_criancas(self):
        self.assertEqual(Apartamento(1, False, False).valor_mensal(), D("665.00"))


class TestCasa(unittest.TestCase):
    def test_um_quarto(self):
        self.assertEqual(Casa(1, False).valor_mensal(), D("900.00"))

    def test_dois_quartos_com_garagem(self):
        self.assertEqual(Casa(2, True).valor_mensal(), D("1450.00"))

    def test_casa_nao_tem_desconto(self):
        self.assertEqual(Casa(1, False).descontos(), [])


class TestEstudio(unittest.TestCase):
    def test_sem_estacionamento(self):
        self.assertEqual(Estudio(0).valor_mensal(), D("1200.00"))

    def test_pacote_duas_vagas(self):
        self.assertEqual(Estudio(2).valor_mensal(), D("1450.00"))

    def test_vagas_adicionais(self):
        # 1200 + 250 + 3 x 60
        self.assertEqual(Estudio(5).valor_mensal(), D("1630.00"))

    def test_vagas_invalidas(self):
        for vagas in (1, -1, 11):
            with self.assertRaises(ValueError):
                Estudio(vagas)


class TestValidacoes(unittest.TestCase):
    def test_quartos_invalidos(self):
        with self.assertRaises(ValueError):
            Casa(3, False)
        with self.assertRaises(ValueError):
            Apartamento(0, False, True)

    def test_parcelas_invalidas(self):
        for parcelas in (0, 6):
            with self.assertRaises(ValueError):
                TaxaContrato(parcelas)


class TestTaxaContrato(unittest.TestCase):
    def test_cinco_parcelas(self):
        self.assertEqual(TaxaContrato(5).valores_parcelas(), [D("400.00")] * 5)

    def test_divisao_nao_exata_soma_2000(self):
        valores = TaxaContrato(3).valores_parcelas()
        self.assertEqual(valores, [D("666.67"), D("666.67"), D("666.66")])
        self.assertEqual(sum(valores), D("2000.00"))

    def test_parcela_fora_do_prazo_e_zero(self):
        self.assertEqual(TaxaContrato(2).parcela_do_mes(3), D("0.00"))


class TestOrcamento(unittest.TestCase):
    def setUp(self):
        self.orcamento = Orcamento(Casa(2, True), TaxaContrato(4))

    def test_projecao_tem_12_meses(self):
        self.assertEqual(len(self.orcamento.projecao()), 12)

    def test_taxa_separada_do_aluguel(self):
        projecao = self.orcamento.projecao()
        self.assertEqual(projecao[0].aluguel, D("1450.00"))
        self.assertEqual(projecao[0].parcela_taxa, D("500.00"))
        self.assertEqual(projecao[0].total_mes, D("1950.00"))
        self.assertEqual(projecao[4].parcela_taxa, D("0.00"))

    def test_total_primeiro_ano(self):
        # 12 x 1450 + 2000
        self.assertEqual(self.orcamento.projecao()[-1].total_acumulado, D("19400.00"))

    def test_exporta_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = ExportadorCSV(pasta).exportar(self.orcamento, Path(pasta) / "teste.csv")
            with open(caminho, encoding="utf-8-sig") as arquivo:
                linhas = list(csv.reader(arquivo, delimiter=";"))
        self.assertEqual(len(linhas), 14)  # cabeçalho + 12 meses + total
        self.assertEqual(linhas[1], ["1", "1.450,00", "500,00", "1.950,00", "1.950,00"])
        self.assertEqual(linhas[-1][3], "19.400,00")


if __name__ == "__main__":
    unittest.main()
