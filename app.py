# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 11:02:50 2025

@author: Beatriz Silva
"""

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Página inicial
@app.route('/')
def home():
    return render_template('index.html')  # se tiveres templates

# Exemplo de endpoint que devolve JSON
@app.route('/api/recomendar', methods=['POST'])
def recomendar():
    dados = request.json
    # Aqui colocas a tua lógica de recomendação
    recomendacoes = ["Empresa A", "Empresa B"]
    return jsonify({"recomendacoes": recomendacoes})

# Endpoint tipo /docs (podes mostrar info do projeto)
@app.route('/docs')
def docs():
    return "<h2>Documentação do Sistema de Recomendação de Estágios</h2>"
