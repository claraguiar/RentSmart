"""Interface de terminal: faz as perguntas, valida as respostas e mostra o resultado."""

from .contrato import TaxaContrato
from .exportador import ExportadorCSV
from .imoveis import Apartamento, Casa, Estudio, Imovel
from .orcamento import Orcamento


class InterfaceConsole:
    def __init__(self, exportador: ExportadorCSV | None = None):
        self.exportador = exportador or ExportadorCSV()
        # Cada opção do menu aponta para o método que coleta os dados daquele imóvel.
        self.opcoes_imovel = {
            "1": ("Apartamento (a partir de R$ 700,00)", self._coletar_apartamento),
            "2": ("Casa (a partir de R$ 900,00)", self._coletar_casa),
            "3": ("Estúdio (a partir de R$ 1.200,00)", self._coletar_estudio),
        }

    # ---------- leitura e validação de entradas ----------

    @staticmethod
    def ler_opcao(pergunta: str, opcoes: list[str]) -> str:
        while True:
            resposta = input(pergunta).strip()
            if resposta in opcoes:
                return resposta
            print(f"  Opção inválida. Escolha entre: {', '.join(opcoes)}.")

    @staticmethod
    def ler_sim_nao(pergunta: str) -> bool:
        while True:
            resposta = input(f"{pergunta} (s/n): ").strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("  Resposta inválida. Digite 's' para sim ou 'n' para não.")

    @staticmethod
    def ler_inteiro(pergunta: str, minimo: int, maximo: int) -> int:
        while True:
            resposta = input(pergunta).strip()
            try:
                numero = int(resposta)
            except ValueError:
                print("  Digite um número inteiro.")
                continue
            if minimo <= numero <= maximo:
                return numero
            print(f"  Valor fora do intervalo permitido ({minimo} a {maximo}).")

    # ---------- coleta de dados de cada tipo de imóvel ----------

    def _ler_quartos(self) -> int:
        return int(self.ler_opcao("Quantidade de quartos (1 ou 2): ", ["1", "2"]))

    def _coletar_apartamento(self) -> Imovel:
        quartos = self._ler_quartos()
        garagem = self.ler_sim_nao("Deseja vaga de garagem (+R$ 300,00)?")
        criancas = self.ler_sim_nao("Possui crianças? (sem crianças = 5% de desconto)")
        return Apartamento(quartos, garagem, criancas)

    def _coletar_casa(self) -> Imovel:
        quartos = self._ler_quartos()
        garagem = self.ler_sim_nao("Deseja vaga de garagem (+R$ 300,00)?")
        return Casa(quartos, garagem)

    def _coletar_estudio(self) -> Imovel:
        if not self.ler_sim_nao("Deseja estacionamento? (pacote de 2 vagas por R$ 250,00)"):
            return Estudio(vagas=0)
        vagas = self.ler_inteiro(
            f"Quantidade total de vagas ({Estudio.VAGAS_PACOTE} a {Estudio.MAX_VAGAS}; "
            "cada vaga além de 2 custa R$ 60,00): ",
            Estudio.VAGAS_PACOTE,
            Estudio.MAX_VAGAS,
        )
        return Estudio(vagas)

    # ---------- fluxo principal ----------

    def escolher_imovel(self) -> Imovel:
        print("\nTipos de imóvel:")
        for chave, (rotulo, _) in self.opcoes_imovel.items():
            print(f"  [{chave}] {rotulo}")
        opcao = self.ler_opcao("Escolha o tipo de imóvel: ", list(self.opcoes_imovel))
        _, coletar = self.opcoes_imovel[opcao]
        return coletar()

    def escolher_taxa(self) -> TaxaContrato:
        print("\nTaxa contratual: R$ 2.000,00 (pode ser parcelada em até 5x).")
        parcelas = self.ler_inteiro("Em quantas parcelas deseja pagar (1 a 5)? ", 1, TaxaContrato.MAX_PARCELAS)
        return TaxaContrato(parcelas)

    def novo_orcamento(self) -> None:
        imovel = self.escolher_imovel()
        taxa = self.escolher_taxa()
        orcamento = Orcamento(imovel, taxa)

        print()
        print(orcamento.resumo())

        caminho = self.exportador.exportar(orcamento)
        print(f"\nProjeção de 12 meses salva em: {caminho}")

    def executar(self) -> None:
        print("=" * 56)
        print("RentSmart - Orçamento de Locação | R.M Imóveis".center(56))
        print("=" * 56)
        try:
            while True:
                self.novo_orcamento()
                if not self.ler_sim_nao("\nDeseja fazer outro orçamento?"):
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\nAtendimento interrompido.")
        print("Obrigado por usar o RentSmart!")
