from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
import requests

# ---------------------------
# CONFIGURAÇÕES INICIAIS
# ---------------------------
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def ficheiro_valido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------
# ROTAS WEB
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            return "Nenhum ficheiro enviado", 400

        file = request.files["file"]
        nome = request.form.get("nome")
        email = request.form.get("email")

        if file.filename == '':
            return "Nenhum ficheiro selecionado", 400

        if ficheiro_valido(file.filename):
            # Enviar ficheiro diretamente ao n8n
            url = "https://beatrizsilva243.app.n8n.cloud/webhook/teste_cv"
            files = {"file": (file.filename, file.stream, file.mimetype)}
            data = {"nome": nome, "email": email}
            try:
                resposta = requests.post(url, files=files, data=data)
                if resposta.status_code == 200:
                    return "<h3>✅ CV enviado com sucesso!</h3><p><a href='/'>Voltar</a></p>"
                else:
                    return f"Erro ao enviar para o n8n ({resposta.status_code})", 500
            except Exception as e:
                return f"Erro de comunicação com o n8n: {e}", 500
        else:
            return "Extensão de ficheiro não permitida", 400

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
# ARRANQUE LOCAL (para testes)
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
