# RentSmart — Orçamento de Locação (R.M Imóveis)

Aplicação em Python, orientada a objetos, que calcula o orçamento mensal de locação de
apartamentos, casas e estúdios da R.M Imóveis, mostra um resumo detalhado e gera um
arquivo CSV com a projeção dos 12 primeiros meses do contrato.

Trabalho da disciplina **Algorithmic Thinking & Introduction to Object-Oriented Programming**.

## Requisitos

- Python **3.10 ou superior** (testado no 3.13)
- Nenhuma biblioteca externa — só a biblioteca padrão (`csv`, `decimal`, `abc`, `dataclasses`, `pathlib`)

## Como executar

```bash
git clone https://github.com/claraguiar/RentSmart.git
cd RentSmart
python main.py
```

O programa pergunta, passo a passo:

1. Tipo de imóvel (1 = Apartamento, 2 = Casa, 3 = Estúdio)
2. Apartamento/Casa: quantidade de quartos (1 ou 2) e se deseja vaga de garagem
3. Apartamento: se possui crianças (sem crianças = 5% de desconto)
4. Estúdio: se deseja estacionamento e quantas vagas no total (2 a 10)
5. Em quantas parcelas deseja pagar a taxa contratual (1 a 5)

Respostas inválidas são recusadas e a pergunta é repetida.
Ao final, o orçamento é exibido no terminal e o CSV é salvo na pasta `orcamentos/`
com o nome `projecao_<tipo>_<data>_<hora>.csv`.

## Como executar os testes

```bash
python -m unittest discover tests
```

## Regras de negócio implementadas

| Item | Valor |
|---|---|
| Aluguel-base apartamento (1 quarto) | R$ 700,00 |
| Aluguel-base casa (1 quarto) | R$ 900,00 |
| Aluguel-base estúdio | R$ 1.200,00 |
| 2º quarto — apartamento | + R$ 200,00 |
| 2º quarto — casa | + R$ 250,00 |
| Vaga de garagem (casa/apartamento) | + R$ 300,00 |
| Estúdio — pacote de 2 vagas | + R$ 250,00 |
| Estúdio — cada vaga além de 2 | + R$ 60,00 |
| Apartamento sem crianças | − 5% sobre (base + adicionais) |
| Taxa contratual (separada do aluguel) | R$ 2.000,00 em 1 a 5 parcelas |

Premissas adotadas: o limite de 10 vagas para estúdio é uma regra de validação da aplicação;
quando a taxa não divide em centavos exatos (ex.: 3x), a última parcela ajusta a diferença
(666,67 + 666,67 + 666,66 = 2.000,00); as parcelas da taxa são cobradas nos primeiros meses do contrato.

## Formato do CSV

Separador `;` e vírgula decimal (abre direto no Excel em português). Colunas:

`Mes ; Aluguel (R$) ; Parcela taxa contratual (R$) ; Total do mes (R$) ; Total acumulado (R$)`

A última linha traz os totais do ano. Exemplos prontos estão na pasta [`exemplos/`](exemplos/).

## Estrutura do projeto

```
RentSmart/
├── main.py                 # ponto de entrada
├── rentsmart/
│   ├── imoveis.py          # Imovel, ImovelComQuartos, Apartamento, Casa, Estudio, ItemOrcamento
│   ├── contrato.py         # TaxaContrato
│   ├── orcamento.py        # Orcamento, LinhaProjecao
│   ├── exportador.py       # ExportadorCSV
│   ├── interface.py        # InterfaceConsole (entradas, validação, exibição)
│   └── utils.py            # arredondamento e formatação de moeda
├── tests/test_regras.py    # testes automatizados das regras
├── exemplos/               # CSVs de exemplo gerados pelo sistema
└── docs/                   # parte teórica (PDF)
```
