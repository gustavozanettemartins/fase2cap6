from logger_config import logger
from validators import validar_int
from colorama import Fore, Style
from core import HarvestReport
from validators import validar_float, validar_str
from datetime import datetime
import os
import platform


def abrir_imagem(caminho: str) -> None:
    sistema = platform.system()

    try:
        if os.path.exists(caminho):
            if sistema == "Windows":
                os.startfile(caminho)
            elif sistema == "Darwin":
                os.system(f"open '{caminho}'")
            else:
                os.system(f"xdg-open '{caminho}'")
        else:
            print(f"❌ O caminho da imagem não foi encontrado")
    except Exception as e:
        print(f"❌ Não foi possível abrir a imagem automaticamente: {e}")

def limpar_tela() -> None:
    from time import sleep

    try:
        sleep(0.7)
        os.system("cls" if os.name == "nt" else "clear")
        print(f"\nSistema Controle Agrícola v1.0\n")
    except Exception as error:
        logger.error(error)


def wait_tela() -> None:
    input(Fore.YELLOW + "\n🔙 Pressione Enter para voltar ao menu..." + Style.RESET_ALL)


def print_menu(data: str) -> None:
    from colorama import init, Fore, Style

    try:
        init(autoreset=True)

        print(Fore.BLUE + Style.BRIGHT + f"{data}" + Style.RESET_ALL)
    except Exception as error:
        logger.error(error)

def registrar_perda() -> None:
    limpar_tela()
    print_menu("🌾 REGISTRAR NOVA PERDA AGRÍCOLA 🌾\n")

    try:
        cultura = input("🪴  Cultura: ").strip()
        while not validar_str(cultura):
            print(Fore.RED + "❌ Cultura inválida. Tente novamente.")
            cultura = input("🪴  Cultura: ").strip()

        while True:
            area = input("📏  Área plantada (ha): ").strip()
            if not validar_float(area):
                print(Fore.RED + "❌ Valor inválido para área.")
                continue
            if float(area) <= 0:
                print(Fore.RED + "❌  A área deve ser maior que zero.")
                continue
            break

        while True:
            estimada = input("📦  Produção estimada (t): ").strip()
            if not validar_float(estimada):
                print(Fore.RED + "❌ Valor inválido para produção estimada.")
                continue
            if float(estimada) <= 0:
                print(Fore.RED + "❌ A produção estimada deve ser maior que zero.")
                continue
            break

        while True:
            real = input("📦  Produção real obtida (t): ").strip()
            if not validar_float(real):
                print(Fore.RED + "❌ Valor inválido para produção real.")
                continue
            if float(real) < 0:
                print(Fore.RED + "❌ A produção real não pode ser negativa.")
                continue
            break

        data_str = input("📅  Data da colheita (dd/mm/aaaa): ").strip()
        while True:
            try:
                datetime.strptime(data_str, "%d/%m/%Y")
                break
            except ValueError:
                print(Fore.RED + "❌ Formato inválido. Use dd/mm/aaaa.")
                data_str = input("📅  Data da colheita (dd/mm/aaaa): ").strip()

        obs = input("📝  Observações (opcional): ").strip()

        perda = HarvestReport.register_loss(
            cultura=cultura,
            area_plantada_ha=float(area),
            prod_estimada_t=float(estimada),
            prod_real_t=float(real),
            data_colheita_str=data_str,
            obs=obs
        )

        print(Fore.GREEN + Style.BRIGHT + f"\n✅ Perda registrada com sucesso: ID {perda.id}!\n")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⚠️ Operação cancelada pelo usuário.\n")


def listar_perdas() -> None:
    limpar_tela()
    print_menu("📋 LISTAGEM DE PERDAS AGRÍCOLAS\n")
    print_menu("1. Listar todas as perdas\n2. Filtrar por cultura\n0. Voltar ao menu principal")

    escolha = input(Fore.YELLOW + "\n👉 Escolha uma opção: " + Style.RESET_ALL).strip()

    if escolha == "1":
        perdas = HarvestReport.all()
        titulo = "📋 TODAS AS PERDAS REGISTRADAS"
    elif escolha == "2":
        cultura = input("🌾 Digite o nome da cultura: " + Style.RESET_ALL).strip()
        while not validar_str(cultura):
            print(Fore.RED + "❌ Cultura inválida.")
            cultura = input("🌾 Digite o nome da cultura: ").strip()
        perdas = HarvestReport.filter_by_culture(cultura)
        titulo = f"📋 PERDAS PARA A CULTURA: {cultura.upper()}"
    elif escolha == "0":
        return
    else:
        print(Fore.RED + "❌ Opção inválida.")
        return

    limpar_tela()
    print_menu(titulo + "\n")

    if not perdas:
        print(Fore.YELLOW + "⚠️  Nenhuma perda encontrada.")
        return

    for perda in perdas:
        print(Fore.WHITE + Style.BRIGHT + "─" * 60)
        print(Fore.GREEN + f"🌾 Cultura: {perda.cultura}   🆔 ID: {perda.id}")
        print(Fore.BLUE + f"📏 Área plantada: {perda.area_plantada_ha} ha")
        print(Fore.MAGENTA + f"📦 Produção estimada: {perda.prod_estimada_t} t")
        print(Fore.MAGENTA + f"📦 Produção real:     {perda.prod_real_t} t")
        print(Fore.YELLOW + f"📅 Data da colheita:  {perda.data_colheita.strftime('%d/%m/%Y')}")
        print(Fore.LIGHTBLACK_EX + f"📝 Observações: {perda.obs or 'Nenhuma'}")
        perda_abs = round(perda.prod_estimada_t - perda.prod_real_t, 2)
        perda_pct = round(perda_abs / perda.prod_estimada_t * 100, 2)
        print(Fore.RED + f"❗ Perda estimada: {perda_abs} t")
        print(Fore.RED + f"📉 Percentual de perda: {perda_pct}%")
    print(Fore.WHITE + Style.BRIGHT + "─" * 60)

    wait_tela()

def menu() -> None:
    try:
        HarvestReport.load_from_json()

        while True:
            limpar_tela()
            print_menu("🌿 MENU PRINCIPAL 🌿")
            print_menu("1. Registrar Perda\n2. Listar Perdas\n3. Exportar Dados\n4. Dados Estatísticos\n0. Sair")
            response = input(Fore.YELLOW + "\n👉 Escolha uma opção: " + Style.RESET_ALL).strip()

            if validar_int(response):
                option = int(response)

                if option == 1:
                    registrar_perda()
                elif option == 2:
                    listar_perdas()
                elif option == 3:
                    HarvestReport.export_to_json()
                    wait_tela()
                elif option == 4:
                    abrir_imagem(HarvestReport.get_statistics())
                    wait_tela()
                elif option == 0:
                    break
                else:
                    print(Fore.RED + "❌ Opção inválida." + Style.RESET_ALL)
            else:
                logger.warning("A opção deve ser um número inteiro.")
                input(Fore.YELLOW + "Pressione Enter para continuar...")

    except KeyboardInterrupt:
        logger.info("Interrompido com sucesso.")
    except Exception as error:
        logger.error(error)
    finally:
        logger.info("Saindo do programa...")

def main():
    try:
        menu()
    except Exception as error:
        logger.error(error)


if __name__ == '__main__':
    logger.info("Programa Inicializado...")
    main()
