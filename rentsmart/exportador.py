"""Exporta a projeção de 12 meses para um arquivo CSV."""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .orcamento import Orcamento
from .utils import formatar_numero


class ExportadorCSV:
    """Grava a projeção em CSV no padrão brasileiro (separador ';' e vírgula decimal),
    que abre corretamente no Excel em português."""

    CABECALHO = [
        "Mes",
        "Aluguel (R$)",
        "Parcela taxa contratual (R$)",
        "Total do mes (R$)",
        "Total acumulado (R$)",
    ]

    def __init__(self, pasta_saida: str | Path = "orcamentos"):
        self.pasta_saida = Path(pasta_saida)

    def gerar_nome_arquivo(self, orcamento: Orcamento) -> Path:
        tipo = orcamento.imovel.TIPO.lower().replace("ú", "u")
        carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.pasta_saida / f"projecao_{tipo}_{carimbo}.csv"

    def exportar(self, orcamento: Orcamento, caminho: str | Path | None = None) -> Path:
        caminho = Path(caminho) if caminho else self.gerar_nome_arquivo(orcamento)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        projecao = orcamento.projecao()

        # utf-8-sig: o Excel reconhece os acentos corretamente.
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(self.CABECALHO)
            for l in projecao:
                escritor.writerow([
                    l.mes,
                    formatar_numero(l.aluguel),
                    formatar_numero(l.parcela_taxa),
                    formatar_numero(l.total_mes),
                    formatar_numero(l.total_acumulado),
                ])
            escritor.writerow([
                "TOTAL",
                formatar_numero(sum((l.aluguel for l in projecao), Decimal("0"))),
                formatar_numero(sum((l.parcela_taxa for l in projecao), Decimal("0"))),
                formatar_numero(projecao[-1].total_acumulado),
                "",
            ])
        return caminho
