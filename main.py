"""Ponto de entrada do RentSmart. Execute com:  python main.py"""

from rentsmart.interface import InterfaceConsole


def main() -> None:
    InterfaceConsole().executar()


if __name__ == "__main__":
    main()
