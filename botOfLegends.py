# Importa funcionalidades do framework Flask:
# - Flask: cria a aplicação web
# - request: acessa os dados enviados pelo cliente (ex: mensagens do usuário)
# - jsonify: formata a resposta como JSON
# - render_template: permite retornar páginas HTML
from flask import Flask, request, jsonify, render_template

# Importa o módulo sys, que permite interagir com o sistema, como:
# - acessar argumentos de execução
# - encerrar o programa com sys.exit()
import sys

# Importa a biblioteca AIML (Artificial Intelligence Markup Language),
# que permite carregar e interpretar arquivos .aiml para simular inteligência artificial baseada em regras
import aiml

# Importa biblioteca unicodedata, usada para normalizar textos com acentos e símbolos especiais
import unicodedata

# Importa biblioteca re (expressões regulares), usada para remover pontuação e caracteres não desejados
import re

# Importa a biblioteca os, usada para acessar pastas e arquivos do sistema operacional
import os

# Cria uma instância do Flask, que representa a aplicação web
# Essa instância é usada para configurar rotas e executar o servidor
app = Flask(__name__)

# Cria uma instância do kernel AIML
# Esse "kernel" será responsável por processar mensagens e retornar respostas com base nos arquivos .aiml carregados
kernel = aiml.Kernel()


def clean_input(text):
    """
    Função responsável por limpar e normalizar a entrada do usuário.
    Ela executa os seguintes passos:
    - Converte letras acentuadas para sua forma base (ex: "ação" → "acao")
    - Remove todos os sinais de pontuação e símbolos (mantém apenas letras, números e espaços)
    """
    text = unicodedata.normalize("NFKD", text)  # Normaliza acentos
    text = text.encode("ASCII", "ignore").decode(
        "utf-8"
    )  # Remove acentos e caracteres não ASCII
    text = re.sub(
        r"[^\w\s]", "", text
    )  # Remove tudo que não for letra, número ou espaço
    return text


def load_aiml_files(kernel, aiml_path="aiml"):
    """
    Função que carrega todos os arquivos AIML do diretório especificado.

    Parâmetros:
    - kernel: instância do interpretador AIML
    - aiml_path: caminho do diretório onde estão os arquivos .aiml (por padrão: "aiml")

    A função:
    - Verifica se o diretório existe
    - Lista todos os arquivos que terminam com .aiml
    - Carrega cada arquivo usando o método learn() do kernel AIML
    """
    if not os.path.isdir(aiml_path):
        print(f"Diretório AIML não encontrado: {aiml_path}")
        sys.exit(1)  # Encerra o programa caso o diretório não exista

    # Lista todos os arquivos .aiml dentro do diretório informado
    arquivos = [f for f in os.listdir(aiml_path) if f.endswith(".aiml")]
    if not arquivos:
        print(f"Nenhum arquivo .aiml encontrado em {aiml_path}")
        sys.exit(1)  # Encerra o programa se não encontrar nenhum arquivo .aiml

    # Itera sobre os arquivos e os carrega no kernel AIML
    for file in arquivos:
        caminho_completo = os.path.join(aiml_path, file)
        print(f"Carregando: {caminho_completo}")
        kernel.learn(caminho_completo)


# Tenta carregar os arquivos .aiml ao iniciar a aplicação
try:
    load_aiml_files(kernel)
    # Define uma variável (predicate) chamada "personagem_escolhido" com valor "nao"
    # Usado para bloquear o avanço da conversa até que o usuário escolha um personagem
    kernel.setPredicate("personagem_escolhido", "nao")
except FileNotFoundError as e:
    print(e)
    exit(1)  # Encerra o programa se ocorrer algum erro ao carregar os arquivos


@app.route("/chat", methods=["POST"])
def chat():
    """
    Rota principal da API usada para conversar com o chatbot.

    Método: POST
    Espera receber um JSON com a chave "message" contendo a mensagem do usuário:
        Ex: {"message": "Olá"}

    Retorna um JSON com:
    - "response": resposta gerada pelo AIML
    - "encerrar": true se o usuário solicitou sair (detectado no AIML)
    """
    data = request.get_json()  # Lê o JSON enviado pelo front-end
    message = data.get(
        "message", ""
    ).strip()  # Pega o conteúdo da chave "message" e remove espaços

    if not message:
        return jsonify(
            {"response": "Mensagem vazia. Tente novamente."}
        )  # Retorna erro se mensagem for vazia

    cleaned = clean_input(message)  # Limpa a mensagem para evitar erros com acentuação
    response = kernel.respond(
        cleaned
    )  # Envia a mensagem ao motor AIML para obter resposta

    # Verifica se o AIML sinalizou encerramento com <set name="encerrar">sim</set>
    encerrar = kernel.getPredicate(
        "encerrar"
    )  # Lê o valor atual da variável "encerrar"
    should_exit = encerrar.lower() == "sim"  # Converte para minúsculo e compara

    return jsonify(
        {"response": response, "encerrar": should_exit}
    )  # Retorna a resposta e o sinal de encerramento


@app.route("/health-check")
def status():
    """
    Rota simples para testar se a API está no ar.
    Útil para monitoramento e deploy.
    """
    return "🤖 BotOfLegends API está no ar!"


@app.route("/")
def home():
    """
    Rota que exibe a interface HTML do chatbot.
    Espera que exista um arquivo 'index.html' dentro da pasta 'templates/'
    """
    return render_template("index.html")


if __name__ == "__main__":
    # Executa o servidor Flask em modo de desenvolvimento (debug=True)
    # Acessível em: http://localhost:5000
    # host="0.0.0.0" permite que outros dispositivos na rede acessem, se necessário
    app.run(host="0.0.0.0", port=5000, debug=True)
