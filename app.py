from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename

# ---------------------------
# CONFIGURAÇÕES INICIAIS
# ---------------------------
app = Flask(__name__)

# Pasta onde os CVs serão guardados
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Extensões permitidas (PDF, DOCX, etc.)
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def ficheiro_valido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------
# ROTAS WEB
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'cv' not in request.files:
            return "Nenhum ficheiro enviado", 400

        file = request.files['cv']
        if file.filename == '':
            return "Nenhum ficheiro selecionado", 400

        if ficheiro_valido(file.filename):
            filename = secure_filename(file.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho)
            # Aqui podes chamar tua função de processamento/recomendação
            return redirect(url_for('sucesso', filename=filename))
        else:
            return "Extensão de ficheiro não permitida", 400

    return render_template('upload.html')

@app.route('/sucesso/<filename>')
def sucesso(filename):
    return f"CV '{filename}' carregado com sucesso!"

@app.route('/api/recomendar', methods=['POST'])
def recomendar():
    dados = request.json
    # Exemplo de lógica simples (substituir pela tua)
    nome = dados.get("nome", "Utilizador")
    recomendacoes = ["Empresa A", "Empresa B", "Empresa C"]
    return jsonify({
        "mensagem": f"Olá {nome}, aqui estão as tuas recomendações!",
        "recomendacoes": recomendacoes
    })

@app.route('/docs')
def docs():
    return render_template('docs.html')

# ---------------------------
# ARRANQUE LOCAL (para testes)
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
