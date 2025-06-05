from flask import Flask, request, jsonify, render_template

# Importa o módulo sys para acessar argumentos da linha de comando e sair do programa se necessário
import sys

# Importa a biblioteca AIML (Artificial Intelligence Markup Language)
import aiml

# Bibliotecas para normalização e limpeza de texto (remoção de acentos e símbolos)
import unicodedata
import re

# Biblioteca para interagir com o sistema de arquivos
import os

# Inicializa app Flask
app = Flask(__name__)

# Inicializa kernel AIML
kernel = aiml.Kernel()


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


def load_aiml_files(kernel, aiml_path="aiml"):
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


# Carrega os arquivos AIML ao iniciar a API
try:
    load_aiml_files(kernel)
    kernel.setPredicate("personagem_escolhido", "nao")
except FileNotFoundError as e:
    print(e)
    exit(1)


@app.route("/chat", methods=["POST"])
def chat():
    """
    Rota POST /chat
    Recebe: {"message": "texto"}
    Retorna: {"response": "resposta do bot"}
    """
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Mensagem vazia. Tente novamente."})

    cleaned = clean_input(message)
    response = kernel.respond(cleaned)

    # Detecta se AIML marcou o encerramento
    encerrar = kernel.getPredicate("encerrar")
    should_exit = encerrar.lower() == "sim"

    return jsonify({"response": response, "encerrar": should_exit})


@app.route("/health-check")
def status():
    return "🤖 BotOfLegends API está no ar!"


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    # Roda o servidor Flask localmente
    app.run(host="0.0.0.0", port=5000, debug=True)
