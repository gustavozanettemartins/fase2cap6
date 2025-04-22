from logger_config import logger
from validators import validar_int
from colorama import init, Fore, Style
from core import HarvestReport
from validators import validar_float, validar_str
from datetime import datetime
import os
import platform
from db_config import db_menu
from database import Database
import json

init(autoreset=True)
DATABASE_CONN = None

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
    try:
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
        print(
            Fore.WHITE + Style.BRIGHT + "─" * 60 + "\n" +
            Fore.GREEN + f"🌾 Cultura: {perda.cultura}   🆔 ID: {perda.id}\n" +
            Fore.BLUE + f"📏 Área plantada: {perda.area_plantada_ha} ha\n" +
            Fore.MAGENTA + f"📦 Produção estimada: {perda.prod_estimada_t} t\n" +
            Fore.MAGENTA + f"📦 Produção real:     {perda.prod_real_t} t\n" +
            Fore.YELLOW + f"📅 Data da colheita:  {perda.data_colheita.strftime('%d/%m/%Y')}\n" +
            Fore.LIGHTBLACK_EX + f"📝 Observações: {perda.obs or 'Nenhuma'}"
        )
        perda_abs = round(perda.prod_estimada_t - perda.prod_real_t, 2)
        perda_pct = round(perda_abs / perda.prod_estimada_t * 100, 2)
        print(Fore.RED + f"❗ Perda estimada: {perda_abs} t")
        print(Fore.RED + f"📉 Percentual de perda: {perda_pct}%")
    print(Fore.WHITE + Style.BRIGHT + "─" * 60)

    wait_tela()

def editar_perda() -> None:
    limpar_tela()
    print_menu("✏️ EDITAR OU DELETAR PERDA AGRÍCOLA\n")

    try:
        perdas = HarvestReport.all()
        if not perdas:
            print(Fore.YELLOW + "⚠️ Nenhuma perda registrada.")
            wait_tela()
            return

        for perda in perdas:
            print(Fore.GREEN + f"ID {perda.id}: {perda.cultura} - {perda.data_colheita.strftime('%d/%m/%Y')}")

        escolha = input(Fore.YELLOW + "\n👉 Digite o ID da perda que deseja editar ou deletar: ").strip()
        if not validar_int(escolha):
            print(Fore.RED + "❌ ID inválido.")
            return

        id_escolhido = int(escolha)
        perda = next((p for p in perdas if p.id == id_escolhido), None)

        if not perda:
            print(Fore.RED + f"❌ Nenhum registro encontrado com o ID {id_escolhido}.")
            return

        print_menu(f"Registro selecionado: {perda.cultura} em {perda.data_colheita.strftime('%d/%m/%Y')}")

        acao = input(Fore.YELLOW + "👉 Deseja [E]ditar ou [D]eletar este registro? ").strip().lower()

        if acao == "d":
            confirmar = input(Fore.RED + "❗ Tem certeza que deseja deletar este registro? (s/n): ").strip().lower()
            if confirmar == "s":
                HarvestReport._data = [p for p in HarvestReport._data if p.id != id_escolhido]
                print(Fore.GREEN + f"🗑️ Perda ID {id_escolhido} removida com sucesso.")
            else:
                print("❌ Exclusão cancelada.")
        elif acao == "e":
            print(Fore.CYAN + "\n🔧 Deixe o campo em branco para manter o valor atual.\n")

            cultura = input(f"🪴 Cultura [{perda.cultura}]: ").strip() or perda.cultura
            area_str = input(f"📏 Área plantada [{perda.area_plantada_ha}]: ").strip()
            estimada_str = input(f"📦 Produção estimada [{perda.prod_estimada_t}]: ").strip()
            real_str = input(f"📦 Produção real [{perda.prod_real_t}]: ").strip()
            data_str = input(f"📅 Data da colheita [{perda.data_colheita.strftime('%d/%m/%Y')}]: ").strip()
            obs = input(f"📝 Observações [{perda.obs or 'Nenhuma'}]: ").strip() or perda.obs

            nova_area = float(area_str) if area_str else perda.area_plantada_ha
            nova_estim = float(estimada_str) if estimada_str else perda.prod_estimada_t
            nova_real = float(real_str) if real_str else perda.prod_real_t
            nova_data = datetime.strptime(data_str, "%d/%m/%Y").date() if data_str else perda.data_colheita

            HarvestReport._data = [p for p in HarvestReport._data if p.id != id_escolhido]

            from core import HarvestLoss
            novo = HarvestLoss(
                id=id_escolhido,
                cultura=cultura,
                area_plantada_ha=nova_area,
                prod_estimada_t=nova_estim,
                prod_real_t=nova_real,
                data_colheita=nova_data,
                obs=obs
            )
            HarvestReport._data.append(novo)

            print(Fore.GREEN + f"\n✅ Perda ID {id_escolhido} atualizada com sucesso!")
        else:
            print(Fore.RED + "❌ Ação inválida. Use 'e' para editar ou 'd' para deletar.")

    except Exception as e:
        logger.error(f"Erro ao editar ou deletar perda: {e}")
        print(Fore.RED + "❌ Ocorreu um erro durante a operação.")

    wait_tela()



def load_data() -> None:
    global DATABASE_CONN
    try:
        try:
            db = Database()
            DATABASE_CONN = db
        except Exception as error:
            logger.error(error)
            db = None

        if db is not None:
            limpar_tela()
            print_menu("🌿 CARREGAR DADOS 🌿")
            print_menu("1. Carregar Pelo Json\n2. Carregar Pelo Oracle\n0. Sair")
            response = input(Fore.YELLOW + "\n👉 Escolha uma opção: " + Style.RESET_ALL).strip()

            if validar_int(response):
                option = int(response)

                if option == 1:
                    HarvestReport.load_from_json()
                elif option == 2:
                    HarvestReport.load_from_db(db.read())
                elif option == 0:
                    ...
                else:
                    print(Fore.RED + "❌ Opção inválida." + Style.RESET_ALL)
                    limpar_tela()
            else:
                logger.warning("A opção deve ser um número inteiro.")
                input(Fore.YELLOW + "Pressione Enter para continuar...")
        else:
            HarvestReport.load_from_json()
    except Exception as error:
        logger.error(error)

def menu() -> None:
    try:
        while True:
            limpar_tela()
            print_menu("🌿 MENU PRINCIPAL 🌿")
            print_menu("1. Registrar Perda\n2. Listar Perdas\n3. Editar Perda\n4. Salvar Dados\n"
                       "5. Dados Estatísticos\n6. Registros Salvos\n0. Sair")
            response = input(Fore.YELLOW + "\n👉 Escolha uma opção: " + Style.RESET_ALL).strip()

            if validar_int(response):
                option = int(response)

                if option == 1:
                    registrar_perda()
                    wait_tela()

                elif option == 2:
                    listar_perdas()

                elif option == 3:
                    editar_perda()

                elif option == 4:
                    limpar_tela()
                    print_menu("🌿 SALVAR DADOS 🌿")
                    while True:
                        if DATABASE_CONN is None:
                            print_menu(
                                "1. Salvar JSON\n0. Sair")
                            options = [1, 0]
                        else:
                            print_menu(
                                "1. Salvar JSON\n2. Salvar Oracle\n3. Salvar Ambos\n0. Sair")
                            options = [1, 2, 3, 0]
                        response = input(Fore.YELLOW + "\n👉 Escolha uma opção: " + Style.RESET_ALL).strip()
                        if validar_int(response):
                            option = int(response)
                            if option in options:
                                if option == 1:
                                    HarvestReport.export_to_json()
                                elif option == 2:
                                    HarvestReport.export_to_db(DATABASE_CONN)
                                elif option == 3:
                                    HarvestReport.export_to_json()
                                    HarvestReport.export_to_db(DATABASE_CONN)
                                elif option == 0:
                                    break
                            else:
                                print(Fore.RED + "❌ Opção inválida." + Style.RESET_ALL)
                                limpar_tela()
                        else:
                            logger.warning("A opção deve ser um número inteiro.")
                            input(Fore.YELLOW + "Pressione Enter para continuar...")

                elif option == 5:
                    path_img = HarvestReport.get_statistics()
                    if path_img:
                        abrir_imagem(path_img)
                    wait_tela()

                elif option == 6:
                    while True:
                        limpar_tela()
                        print_menu("🌿 REGISTROS SALVOS🌿")
                        if DATABASE_CONN is None:
                            print_menu(
                                "1. Registros JSON\n0. Sair")
                            options = [1, 0]
                        else:
                            print_menu(
                                "1. Registros JSON\n2. Registros Oracle\n0. Sair")
                            options = [1, 2, 0]
                        response = input(Fore.YELLOW + "\n👉 Escolha uma opção: " + Style.RESET_ALL).strip()
                        if validar_int(response):
                            option = int(response)
                            if option in options:
                                if option == 1:
                                    with open("data.json", "r", encoding="utf-8") as f:
                                        registros = json.load(f)
                                        logger.info(f"🔍 {len(registros)} registros recuperados do json.")
                                        for item in registros:
                                            print(item)
                                elif option == 2:
                                    for item in DATABASE_CONN.read():
                                        print(item)
                                elif option == 0:
                                    break
                            else:
                                print(Fore.RED + "❌ Opção inválida." + Style.RESET_ALL)
                                limpar_tela()
                        else:
                            logger.warning("A opção deve ser um número inteiro.")
                            input(Fore.YELLOW + "Pressione Enter para continuar...")
                        input(Fore.YELLOW + "Pressione Enter para continuar..." + Style.RESET_ALL)

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
        if HarvestReport.updated():
            resposta = input(
                Fore.YELLOW +
                "\n⚠️ Você tem alterações não salvas. Deseja sair sem salvar? (s/n): "
                + Style.RESET_ALL).strip().lower()
            if resposta != "s":
                print("🔁 Retornando ao menu para que você possa salvar.")
                menu()
                return
        logger.info("Saindo do programa...")

def main():
    try:
        db_menu()
        limpar_tela()
        load_data()
        menu()
    except Exception as error:
        logger.error(error)


if __name__ == '__main__':
    logger.info("Programa Inicializado...")
    main()
