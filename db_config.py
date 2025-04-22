import os
from dotenv import set_key, load_dotenv
import oracledb
from pathlib import Path

ENV_PATH = Path(".env")

DATA = {
    "ORACLE_USER": "Nome de usuário Oracle",
    "ORACLE_PASSWORD": "Senha do usuário",
    "ORACLE_HOST": "Host (ex: localhost)",
    "ORACLE_PORT": "Porta (padrão: 1521)",
    "ORACLE_SERVICE": "Serviço ou SID (ex: xe)"
}


def update_env():
    if not ENV_PATH.exists():
        with open(ENV_PATH, "w") as f:
            f.write("# Configuração do Banco Oracle\n")

    for key, value in DATA.items():
        valor_atual = os.getenv(key, "")
        print(f"\n{value}:")
        print(f"📌 Valor atual: {valor_atual or '[não definido]'}")
        novo_valor = input(f"👉 Novo valor para {key} (pressione Enter para manter): ").strip()
        if novo_valor:
            set_key(str(ENV_PATH), key, novo_valor)


def test_connect():
    print("\n🔌 Testando conexão com o banco Oracle...")
    load_dotenv()

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    host = os.getenv("ORACLE_HOST")
    port = os.getenv("ORACLE_PORT", "1521")
    service = os.getenv("ORACLE_SERVICE")

    dsn = f"{host}:{port}/{service}"

    try:
        with oracledb.connect(user=user, password=password, dsn=dsn) as conn:
            print("✅ Conexão bem-sucedida!")
            return True
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return False


def db_menu():
    while True:
        print("\n⚙️  MENU DE CONFIGURAÇÃO DO BANCO ORACLE")
        print("1. Configurar arquivo .env")
        print("2. Testar conexão com o banco")
        print("0. Sair")

        option = input("\n👉 Escolha uma opção: ").strip()

        if option == "1":
            update_env()
        elif option == "2":
            test_connect()
        elif option == "0":
            print("👋 Saindo da configuração.")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    db_menu()
