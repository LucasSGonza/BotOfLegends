# Importa o módulo sys para acessar argumentos da linha de comando e sair do programa se necessário
import sys

# Importa a biblioteca AIML (Artificial Intelligence Markup Language)
import aiml

# Bibliotecas para normalização e limpeza de texto (remoção de acentos e símbolos)
import unicodedata
import re

# Biblioteca para interagir com o sistema de arquivos
import os


def clean_input(text):
    """
    Função que limpa o texto digitado pelo usuário:
    - Remove acentos (ex: "ação" → "acao")
    - Remove pontuação e caracteres especiais (ex: "Olá!" → "Ola")
    """
    text = unicodedata.normalize(
        "NFKD", text
    )  # Normaliza os acentos para caracteres base
    text = text.encode("ASCII", "ignore").decode("utf-8")  # Remove os acentos
    text = re.sub(
        r"[^\w\s]", "", text
    )  # Remove tudo que não for letra, número ou espaço
    return text


def load_aiml_files(kernel, aiml_path):
    """
    Função que carrega todos os arquivos .aiml encontrados em um diretório:
    - Verifica se o caminho é válido
    - Lista os arquivos com extensão .aiml
    - Usa o método kernel.learn() para cada um deles
    """
    if not os.path.isdir(aiml_path):
        print(f"Diretório AIML não encontrado: {aiml_path}")
        sys.exit(1)  # Encerra o programa se o diretório não existir

    # Filtra apenas os arquivos que terminam com .aiml
    arquivos = [f for f in os.listdir(aiml_path) if f.endswith(".aiml")]
    if not arquivos:
        print(f"Nenhum arquivo .aiml encontrado em {aiml_path}")
        sys.exit(1)  # Encerra se nenhum AIML for encontrado

    # Itera sobre os arquivos e carrega cada um no kernel
    for file in arquivos:
        caminho_completo = os.path.join(aiml_path, file)
        print(f"Carregando: {caminho_completo}")
        kernel.learn(caminho_completo)


def main():
    """
    Função principal:
    - Lê argumentos da linha de comando
    - Inicializa o interpretador AIML
    - Entra em um loop para processar mensagens do usuário
    """
    if len(sys.argv) < 2:
        print("Uso: python botOfLegends.py aiml/")
        sys.exit(1)  # Se nenhum argumento for passado, finaliza com erro

    aiml_dir = sys.argv[
        1
    ]  # Primeiro argumento da linha de comando: pasta com arquivos .aiml
    k = aiml.Kernel()  # Cria uma instância do motor AIML

    load_aiml_files(k, aiml_dir)  # Carrega os arquivos .aiml no kernel

    print("🤖 Chatbot iniciado. Digite 'sair' para encerrar.\n")
    print("Olá, bem vindo ao 'BotOfLegends'! Qual qual desses personagens você deseja conversar?")
    print("1 - Garen\n2 - Braum\n3 - Gnar\n4 - Rammus\n")

    # Loop principal do chatbot
    while True:
        message = input("> ")  # Lê a mensagem digitada pelo usuário no terminal

        # Condição de parada do chatbot
        if message.lower() in ("sair", "exit", "quit"):
            print("Encerrando chatbot.")
            break

        message = clean_input(message)  # Limpa a mensagem com a função definida
        response = k.respond(
            message
        )  # Envia a mensagem para o kernel AIML e obtém resposta
        print(response)  # Exibe a resposta no terminal


# Garante que a função main só será executada se o script for rodado diretamente
if __name__ == "__main__":
    main()
