"""
Sistema de Recomendação de Estágios
Autora: Beatriz Silva

Modificado para integração com n8n (FastAPI + Base64 + pdfplumber)
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
import os # Para lidar com ficheiros temporários
import json

# ===============================================
# ======== INICIALIZAÇÃO DO APP E MODELO ========
# ===============================================
app = FastAPI(title="Sistema de Recomendação de Estágios")

# ======== CORS PARA INTEGRAÇÃO COM N8N =========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # permite chamadas de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== EXEMPLO DE DADOS DE TREINO =========
dados = [
    {
        "skills": ["python", "machine learning"],
        "formacao": "Engenharia Informática",
        "experiencia": ["programador", "analista de dados"],
        "idiomas": ["inglês"],
        "estagio": "Data Science"
    },
    {
        "skills": ["excel", "logística"],
        "formacao": "Engenharia e Gestão Industrial",
        "experiencia": ["assistente logístico"],
        "idiomas": ["português", "inglês"],
        "estagio": "Supply Chain"
    },
    {
        "skills": ["marketing", "comunicação", "vendas"],
        "formacao": "Gestão e Marketing",
        "experiencia": ["assistente comercial"],
        "idiomas": ["português", "inglês"],
        "estagio": "Marketing"
    },
    {
        "skills": ["arquitetura", "urbanismo", "liderança", "gestão de projetos"],
        "formacao": "Arquitetura e Urbanismo",
        "experiencia": ["gestora de projetos"],
        "idiomas": ["inglês", "espanhol"],
        "estagio": "Gestão de Projetos de Construção"
    }
]

df = pd.DataFrame(dados)
df["texto"] = df["skills"].apply(lambda x: " ".join(x)) + " " + \
              df["formacao"] + " " + \
              df["experiencia"].apply(lambda x: " ".join(x)) + " " + \
              df["idiomas"].apply(lambda x: " ".join(x))

le = LabelEncoder()
df["estagio_cod"] = le.fit_transform(df["estagio"])

modelo = Pipeline([
    ("vetor", TfidfVectorizer()),
    ("classificador", RandomForestClassifier(random_state=42))
])
modelo.fit(df["texto"], df["estagio_cod"])

# ===============================================
# ======== MODELOS DE INPUT E FUNÇÕES AUXILIARES ========
# ===============================================

class CVInput(BaseModel):
    raw: dict

class FileInput(BaseModel):
    file: str

def clean_text(text):
    if not text:
        return None
    text = text.strip()
    if text.endswith(',') or text.endswith('e'):
        text = text[:-1].strip()
    return text if text else None

def recomendar_estagio(cv_limpo):
    """Recebe o JSON limpo do CV e usa o modelo treinado para recomendar o estágio."""
    try:
        # Cria a string de texto para o modelo
        texto = " ".join(cv_limpo.get("skills", [])) + " " + \
                " ".join([f["curso"] for f in cv_limpo.get("formacao", [])]) + " " + \
                " ".join([e["cargo"] for e in cv_limpo.get("experiencia", [])]) + " " + \
                " ".join([i["idioma"] for i in cv_limpo.get("idiomas", [])])
        
        # Previsão
        pred = modelo.predict([texto])[0]
        return le.inverse_transform([pred])[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na recomendação: {str(e)}")


def extract_data_from_pdf(pdf_path: str) -> dict:
    """Extrai informações cruciais do PDF para o modelo."""
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        
        # Lógica de Extração Simplificada (Exemplo)
        
        # 1. Habilidades (Simplesmente lista de keywords para teste)
        # Numa aplicação real, usaria NLP para extrair entidades
        skills = []
        if any(keyword in full_text.lower() for keyword in ["urbanismo", "arquitetura", "projetos"]):
            skills.append("arquitetura e urbanismo")
        if "liderança" in full_text.lower():
            skills.append("liderança")
        if "sustentabilidade" in full_text.lower():
            skills.append("sustentabilidade")
            
        # 2. Formação (Assumindo que há cursos chave)
        formacao = []
        if "pós-graduação em planejamento urbano" in full_text.lower():
             formacao.append({"curso": "Pós-Graduação em Planejamento Urbano e Ambiental"})
        if "arquitetura e urbanismo" in full_text.lower():
             formacao.append({"curso": "Arquitetura e Urbanismo"})

        # 3. Experiência (Assumindo que há cargos chave)
        experiencia = []
        if "gestora de projetos" in full_text.lower() or "gestão de projetos" in full_text.lower():
            experiencia.append({"cargo": "gestora de projetos"})

        # 4. Idiomas
        idiomas = []
        if "inglês" in full_text.lower():
            idiomas.append({"idioma": "inglês"})
        if "espanhol" in full_text.lower():
            idiomas.append({"idioma": "espanhol"})
            
        # O modelo espera esta estrutura:
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
    2. Salva o PDF localmente.
    3. Extrai o texto e converte para JSON de CV limpo.
    4. Recomenda o estágio.
    5. Devolve o resultado.
    """
    file_name = "cv_recebido_temp.pdf"
    
    try:
        # 1. Receber e Salvar PDF
        pdf_bytes = base64.b64decode(payload.file)
        with open(file_name, "wb") as f:
            f.write(pdf_bytes)
        
        # 2. Extrair CV Limpo
        cv_limpo = extract_data_from_pdf(file_name)
        
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
        
    finally:
        # 4. Limpar o ficheiro
        if os.path.exists(file_name):
            os.remove(file_name)


# ===============================================
# ======== ENDPOINTS ORIGINAIS (MANTIDOS) ========
# ===============================================

# Mantidos para compatibilidade com o seu código anterior, 
# mas o /process_cv_base64 é o recomendado para o n8n.

@app.post("/upload_pdf/")
async def upload_pdf(payload: FileInput):
    """Recebe PDF em base64 e salva localmente (apenas para salvar)"""
    try:
        pdf_bytes = base64.b64decode(payload.file)
        with open("cv_recebido.pdf", "wb") as f:
            f.write(pdf_bytes)
        return {"status": "ok", "message": "PDF recebido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao salvar PDF: {str(e)}")

@app.post("/extract_cv")
async def extract_cv(payload: CVInput):
    """
    Recebe JSON do CV (já extraído por um parser externo) e devolve-o limpo.
    (Neste fluxo, o JSON seria o 'cv_limpo' da função 'extract_data_from_pdf').
    """
    try:
        # Se quiser usar este endpoint, teria de chamar a função 
        # extract_data_from_pdf noutro lugar
        dados_limpos = payload.raw
        return {"status": "ok", "data": dados_limpos}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/recommend_stage")
async def recommend_stage(payload: CVInput):
    """Recebe CV limpo (JSON) e recomenda estágio"""
    estagio = recomendar_estagio(payload.raw)
    return {"status": "ok", "sugestao": estagio}

# ===============================================
# ======== EXECUÇÃO DO SERVIDOR ========
# ===============================================
# No final do seu novo ficheiro 'app_main.py'
if __name__ == "__main__":
    # Garanta que o nome do ficheiro está correto aqui
    uvicorn.run("app_main:app", host="0.0.0.0", port=8000, reload=True)