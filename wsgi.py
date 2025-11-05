# wsgi.py
import sys
from pathlib import Path

# Adiciona o caminho da sua aplicação ao PATH
# Substitua 'Sistema-Recomendacao-Estagios' pelo nome exato da sua pasta de projeto no GitHub
path_para_a_app = Path(__file__).parent.absolute()
if str(path_para_a_app) not in sys.path:
    sys.path.append(str(path_para_a_app))

# Importa a instância 'app' do seu ficheiro principal (app_main.py)
# IMPORTANTE: Garante que está a usar a app do app_main.py
from app_main import app as application
