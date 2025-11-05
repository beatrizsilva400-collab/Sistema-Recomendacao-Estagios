# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 22:38:49 2025

@author: Beatriz Silva
"""

"""
Sistema de Recomendação de Estágios
Autora: Beatriz Silva

MODIFICADO: Utiliza io.BytesIO para processar o PDF em memória, 
evitando salvar no disco local e preparando para o Cloud Storage.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import base64
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pdfplumber
import io  # Importar a biblioteca io
# import os # Já não é necessário para apagar ficheiros
import json

# ===============================================
# ======== INICIALIZAÇÃO DO APP E MODELO ========
# (O código de treino do modelo permanece o mesmo)
# ===============================================
app = FastAPI(title="Sistema de Recomendação de Estágios")

# [Código CORS e Treino de Modelo (dados, df, le, modelo) fica aqui]
# ...

# ======== MODELOS DE INPUT E FUNÇÕES AUXILIARES ========

class FileInput(BaseModel):
    file: str

def recomendar_estagio(cv_limpo):
    # [Função recomendar_estagio() fica aqui, inalterada]
    # ...
    try:
        texto = " ".join(cv_limpo.get("skills", [])) + " " + \
                " ".join([f["curso"] for f in cv_limpo.get("formacao", [])]) + " " + \
                " ".join([e["cargo"] for e in cv_limpo.get("experiencia", [])]) + " " + \
                " ".join([i["idioma"] for i in cv_limpo.get("idiomas", [])])
        
        pred = modelo.predict([texto])[0]
        return le.inverse_transform([pred])[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na recomendação: {str(e)}")


def extract_data_from_pdf_stream(pdf_bytes: bytes) -> dict:
    """Extrai informações cruciais diretamente do stream de bytes do PDF."""
    
    # Abrir o stream de bytes em memória
    file_stream = io.BytesIO(pdf_bytes) 
    full_text = ""
    
    try:
        # pdfplumber consegue abrir um objeto BytesIO
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        
        # 💡 [LÓGICA DE EXTRAÇÃO DE PALAVRAS-CHAVE] 💡
        # Esta parte é a simulação da sua extração de dados do CV.
        # Numa aplicação real, deve ser mais sofisticada (Regex, Spacy, etc.)
        skills = []
        if any(keyword in full_text.lower() for keyword in ["urbanismo", "arquitetura", "projetos"]):
            skills.append("arquitetura e urbanismo")
        if "liderança" in full_text.lower():
            skills.append("liderança")
            
        formacao = []
        if "pós-graduação em planejamento urbano" in full_text.lower():
             formacao.append({"curso": "Pós-Graduação em Planejamento Urbano e Ambiental"})
            
        experiencia = []
        if "gestora de projetos" in full_text.lower():
            experiencia.append({"cargo": "gestora de projetos"})

        idiomas = []
        if "inglês" in full_text.lower():
            idiomas.append({"idioma": "inglês"})
            
        cv_limpo = {
            "skills": skills,
            "formacao": formacao,
            "experiencia": experiencia,
            "idiomas": idiomas
        }
        
        return cv_limpo

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na extração do PDF: {str(e)}")


# ===============================================
# ======== ENDPOINT UNIFICADO PARA O N8N ========
# ===============================================

@app.post("/process_cv_base64")
async def process_cv_base64(payload: FileInput):
    """
    Endpoint Unificado: 
    1. Recebe PDF em Base64.
    2. Decodifica para bytes.
    3. Extrai dados diretamente do stream de bytes (em memória).
    4. Recomenda o estágio.
    5. Devolve o resultado.
    """
    try:
        # 1. Decodificar Base64
        pdf_bytes = base64.b64decode(payload.file)
        
        # 2. Extrair CV Limpo (em memória)
        cv_limpo = extract_data_from_pdf_stream(pdf_bytes)
        
        # 3. Recomendar Estágio
        estagio_sugerido = recomendar_estagio(cv_limpo)
        
        return {
            "status": "ok", 
            "cv_limpo": cv_limpo, 
            "sugestao": estagio_sugerido
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado no processamento: {str(e)}")
        
# [Código de execução do servidor (if __name__ == "__main__":) fica aqui]
# ...

if __name__ == "__main__":
    uvicorn.run("app_main:app", host="0.0.0.0", port=8000, reload=True)
