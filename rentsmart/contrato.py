"""Taxa contratual, separada do aluguel mensal."""

from decimal import Decimal

from .utils import arredondar, formatar_moeda


class TaxaContrato:
    """Taxa de contrato de R$ 2.000,00, parcelável em até 5 vezes."""

    VALOR_PADRAO = Decimal("2000.00")
    MAX_PARCELAS = 5

    def __init__(self, parcelas: int, valor: Decimal = VALOR_PADRAO):
        if not (1 <= parcelas <= self.MAX_PARCELAS):
            raise ValueError(f"A taxa contratual pode ser paga de 1 a {self.MAX_PARCELAS} parcelas.")
        self.valor = Decimal(valor)
        self.parcelas = parcelas

    def valores_parcelas(self) -> list[Decimal]:
        """Valor de cada parcela. Se a divisão não for exata, a última ajusta os centavos."""
        parcela = arredondar(self.valor / self.parcelas)
        valores = [parcela] * self.parcelas
        valores[-1] = arredondar(self.valor - parcela * (self.parcelas - 1))
        return valores

    def parcela_do_mes(self, mes: int) -> Decimal:
        """Valor da taxa a pagar no mês informado (1, 2, 3...). Zero depois da última parcela."""
        if 1 <= mes <= self.parcelas:
            return self.valores_parcelas()[mes - 1]
        return Decimal("0.00")

    def descricao(self) -> str:
        if self.parcelas == 1:
            return f"À vista: 1x de {formatar_moeda(self.valor)}"
        valores = self.valores_parcelas()
        if len(set(valores)) == 1:
            return f"{self.parcelas}x de {formatar_moeda(valores[0])}"
        return (
            f"{self.parcelas}x: {self.parcelas - 1}x de {formatar_moeda(valores[0])} "
            f"+ 1x de {formatar_moeda(valores[-1])}"
        )
