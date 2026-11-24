"""Classes que representam os imóveis da R.M Imóveis e suas regras de preço.

Hierarquia:

    Imovel (abstrata)
    ├── ImovelComQuartos (abstrata)  -> regras de 2º quarto e garagem
    │   ├── Apartamento              -> desconto de 5% sem crianças
    │   └── Casa
    └── Estudio                      -> pacote de estacionamento
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from .utils import arredondar


@dataclass(frozen=True)
class ItemOrcamento:
    """Uma linha do orçamento (um adicional ou um desconto)."""

    descricao: str
    valor: Decimal


class Imovel(ABC):
    """Classe base de todos os imóveis.

    Cada subclasse define o seu aluguel-base e os seus adicionais.
    O cálculo do valor mensal é igual para todos e fica centralizado aqui.
    """

    TIPO = "Imóvel"
    ALUGUEL_BASE = Decimal("0.00")

    @property
    def aluguel_base(self) -> Decimal:
        return self.ALUGUEL_BASE

    @abstractmethod
    def adicionais(self) -> list[ItemOrcamento]:
        """Lista de acréscimos ao aluguel-base."""

    def descontos(self) -> list[ItemOrcamento]:
        """Lista de descontos. Por padrão, nenhum."""
        return []

    def total_adicionais(self) -> Decimal:
        return sum((item.valor for item in self.adicionais()), Decimal("0.00"))

    def subtotal(self) -> Decimal:
        """Aluguel-base + adicionais (antes dos descontos)."""
        return self.aluguel_base + self.total_adicionais()

    def total_descontos(self) -> Decimal:
        return sum((item.valor for item in self.descontos()), Decimal("0.00"))

    def valor_mensal(self) -> Decimal:
        """Valor final do aluguel mensal."""
        return arredondar(self.subtotal() - self.total_descontos())

    @abstractmethod
    def descricao(self) -> str:
        """Texto curto que descreve o imóvel escolhido."""


class ImovelComQuartos(Imovel):
    """Imóvel que pode ter 1 ou 2 quartos e uma vaga de garagem (casa e apartamento)."""

    QUARTOS_PERMITIDOS = (1, 2)
    ADICIONAL_SEGUNDO_QUARTO = Decimal("0.00")
    VALOR_GARAGEM = Decimal("300.00")

    def __init__(self, quartos: int, garagem: bool):
        if quartos not in self.QUARTOS_PERMITIDOS:
            raise ValueError("O número de quartos deve ser 1 ou 2.")
        self.quartos = quartos
        self.garagem = garagem

    def adicionais(self) -> list[ItemOrcamento]:
        itens = []
        if self.quartos == 2:
            itens.append(ItemOrcamento("Adicional 2º quarto", self.ADICIONAL_SEGUNDO_QUARTO))
        if self.garagem:
            itens.append(ItemOrcamento("Vaga de garagem", self.VALOR_GARAGEM))
        return itens

    def descricao(self) -> str:
        texto_quartos = "1 quarto" if self.quartos == 1 else "2 quartos"
        texto_garagem = "com garagem" if self.garagem else "sem garagem"
        return f"{self.TIPO} - {texto_quartos}, {texto_garagem}"


class Apartamento(ImovelComQuartos):
    TIPO = "Apartamento"
    ALUGUEL_BASE = Decimal("700.00")
    ADICIONAL_SEGUNDO_QUARTO = Decimal("200.00")
    PERCENTUAL_DESCONTO_SEM_CRIANCAS = Decimal("0.05")

    def __init__(self, quartos: int, garagem: bool, possui_criancas: bool):
        super().__init__(quartos, garagem)
        self.possui_criancas = possui_criancas

    def descontos(self) -> list[ItemOrcamento]:
        # O desconto é aplicado sobre o aluguel JÁ com os adicionais.
        if self.possui_criancas:
            return []
        valor = arredondar(self.subtotal() * self.PERCENTUAL_DESCONTO_SEM_CRIANCAS)
        return [ItemOrcamento("Desconto 5% (sem crianças)", valor)]

    def descricao(self) -> str:
        texto_criancas = "com crianças" if self.possui_criancas else "sem crianças"
        return f"{super().descricao()}, {texto_criancas}"


class Casa(ImovelComQuartos):
    TIPO = "Casa"
    ALUGUEL_BASE = Decimal("900.00")
    ADICIONAL_SEGUNDO_QUARTO = Decimal("250.00")


class Estudio(Imovel):
    """Estúdio: estacionamento vendido em pacote de 2 vagas + vagas adicionais."""

    TIPO = "Estúdio"
    ALUGUEL_BASE = Decimal("1200.00")
    VAGAS_PACOTE = 2
    VALOR_PACOTE = Decimal("250.00")
    VALOR_VAGA_ADICIONAL = Decimal("60.00")
    MAX_VAGAS = 10

    def __init__(self, vagas: int):
        if vagas != 0 and not (self.VAGAS_PACOTE <= vagas <= self.MAX_VAGAS):
            raise ValueError(
                f"Informe 0 (sem estacionamento) ou de {self.VAGAS_PACOTE} a "
                f"{self.MAX_VAGAS} vagas. O pacote inicial já inclui {self.VAGAS_PACOTE} vagas."
            )
        self.vagas = vagas

    @property
    def vagas_adicionais(self) -> int:
        return max(0, self.vagas - self.VAGAS_PACOTE)

    def adicionais(self) -> list[ItemOrcamento]:
        if self.vagas == 0:
            return []
        itens = [ItemOrcamento(f"Pacote estacionamento ({self.VAGAS_PACOTE} vagas)", self.VALOR_PACOTE)]
        if self.vagas_adicionais:
            itens.append(
                ItemOrcamento(
                    f"{self.vagas_adicionais} vaga(s) adicional(is) x R$ 60,00",
                    self.VALOR_VAGA_ADICIONAL * self.vagas_adicionais,
                )
            )
        return itens

    def descricao(self) -> str:
        if self.vagas == 0:
            return f"{self.TIPO} - sem estacionamento"
        return f"{self.TIPO} - {self.vagas} vagas de estacionamento"
