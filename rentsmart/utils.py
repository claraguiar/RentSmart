"""Funções utilitárias para trabalhar com valores monetários."""

from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda um valor para 2 casas decimais (centavos)."""
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def formatar_numero(valor: Decimal) -> str:
    """Formata um número no padrão brasileiro: 1.234,56"""
    texto = f"{arredondar(valor):,.2f}"  # 1,234.56
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_moeda(valor: Decimal) -> str:
    """Formata um valor como moeda brasileira: R$ 1.234,56"""
    return f"R$ {formatar_numero(valor)}"
