"""Orçamento: junta o imóvel e a taxa contratual, gera o resumo e a projeção."""

from dataclasses import dataclass
from decimal import Decimal

from .contrato import TaxaContrato
from .imoveis import Imovel
from .utils import formatar_moeda


@dataclass(frozen=True)
class LinhaProjecao:
    """Valores previstos para um mês do contrato."""

    mes: int
    aluguel: Decimal
    parcela_taxa: Decimal
    total_mes: Decimal
    total_acumulado: Decimal


class Orcamento:
    MESES_PROJECAO = 12

    def __init__(self, imovel: Imovel, taxa: TaxaContrato):
        self.imovel = imovel
        self.taxa = taxa

    @property
    def aluguel_mensal(self) -> Decimal:
        return self.imovel.valor_mensal()

    def projecao(self, meses: int = MESES_PROJECAO) -> list[LinhaProjecao]:
        """Gera a previsão de pagamentos mês a mês."""
        linhas = []
        acumulado = Decimal("0.00")
        for mes in range(1, meses + 1):
            parcela = self.taxa.parcela_do_mes(mes)
            total = self.aluguel_mensal + parcela
            acumulado += total
            linhas.append(LinhaProjecao(mes, self.aluguel_mensal, parcela, total, acumulado))
        return linhas

    def resumo(self) -> str:
        """Texto detalhado mostrando como o valor final foi formado."""
        largura = 56
        im = self.imovel

        def linha(rotulo: str, valor: Decimal, sinal: str = " ") -> str:
            texto_valor = f"{sinal}{formatar_moeda(valor)}"
            return f"  {rotulo:<{largura - len(texto_valor) - 4}}  {texto_valor}"

        partes = [
            "=" * largura,
            "ORÇAMENTO DE LOCAÇÃO - R.M IMÓVEIS".center(largura),
            "=" * largura,
            f"Imóvel: {im.descricao()}",
            "-" * largura,
            "ALUGUEL MENSAL",
            linha(f"Aluguel-base ({im.TIPO})", im.aluguel_base),
        ]
        partes += [linha(item.descricao, item.valor, "+") for item in im.adicionais()]
        if im.descontos():
            partes.append(linha("Subtotal", im.subtotal()))
            partes += [linha(item.descricao, item.valor, "-") for item in im.descontos()]
        partes += [
            linha(">> VALOR MENSAL DO ALUGUEL", self.aluguel_mensal),
            "-" * largura,
            "TAXA CONTRATUAL (cobrada à parte do aluguel)",
            linha("Valor total da taxa", self.taxa.valor),
            f"  Parcelamento: {self.taxa.descricao()}",
            "-" * largura,
            "PRIMEIRO ANO (12 meses)",
        ]
        projecao = self.projecao()
        total_aluguel = sum((l.aluguel for l in projecao), Decimal("0.00"))
        partes += [
            linha("Total de aluguéis", total_aluguel),
            linha("Total da taxa contratual", self.taxa.valor),
            linha(">> TOTAL PREVISTO NO 1º ANO", projecao[-1].total_acumulado),
            "=" * largura,
        ]
        return "\n".join(partes)
