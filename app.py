from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import requests

# ---------------------------
# CONFIGURAÇÕES INICIAIS
# ---------------------------
app = Flask(__name__)

# Pasta local para uploads (opcional — apenas se quiseres guardar)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Extensões permitidas
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def ficheiro_valido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------
# ROTAS PRINCIPAIS
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        try:
            # Obter ficheiro e campos do formulário
            file = request.files.get("file")
            nome = request.form.get("nome")
            email = request.form.get("email")

            if not file or file.filename == '':
                return "❌ Nenhum ficheiro selecionado", 400

            if not ficheiro_valido(file.filename):
                return "❌ Extensão de ficheiro não permitida", 400

            # Enviar ficheiro diretamente para o webhook do n8n
            url = "https://beatrizsilva243.app.n8n.cloud/webhook/teste_cv"
            files = {"file": (file.filename, file.stream, file.mimetype)}
            data = {"nome": nome, "email": email}

            resposta = requests.post(url, files=files, data=data)

            if resposta.status_code == 200:
                return "<h3>✅ CV enviado com sucesso!</h3><p><a href='/'>Voltar</a></p>"
            else:
                return f"⚠️ Erro ao enviar para o n8n (código {resposta.status_code})", 500

        except Exception as e:
            return f"❌ Erro interno: {e}", 500

    # Se for GET, mostra a página upload.html (opcional)
    return render_template("upload.html")


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/api/recomendar', methods=['POST'])
def recomendar():
    dados = request.json
    nome = dados.get("nome", "Utilizador")
    recomendacoes = ["Empresa A", "Empresa B", "Empresa C"]
    return jsonify({
        "mensagem": f"Olá {nome}, aqui estão as tuas recomendações!",
        "recomendacoes": recomendacoes
    })


# ---------------------------
# EXECUÇÃO LOCAL (para testes)
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
