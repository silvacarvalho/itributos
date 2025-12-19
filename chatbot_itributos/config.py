import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'itributos'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Ollama Configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')

# Lista de modelos Gemini para fallback (em ordem de preferência)
# Quando um modelo atingir o limite, tenta o próximo automaticamente
GEMINI_FALLBACK_MODELS = [
    'gemini-3-flash-preview',                   # Modelo experimental mais novo
    'gemini-2.0-flash-exp',                     # Mais rápido, mais requisições gratuitas
    'gemini-2.5-flash',                         # Modelo mais novo, bom equilíbrio
    'gemini-2.5-pro',                           # Mais capaz, mas mais lento e com menos requisições gratuitas
    'gemini-2.5-flash-preview-09-2025',         # Último modelo disponível
    'gemini-2.5-flash-lite',                    # Versão leve do 2.5
    'gemini-2.5-flash-lite-preview-09-2025',    # Versão leve do 2.5 preview
    'gemini-2.0-flash',                         # Modelo estável, mas mais antigo
    'gemini-2.0-flash-lite',                    # Versão leve do 2.0
    'gemini-1.5-flash',                         # Rápido, bom para tarefas simples
    'gemini-1.5-pro',                           # Mais capaz, limite menor
]

# Configurar qual modelo inicial usar (se GEMINI_MODEL não estiver configurado)
if GEMINI_MODEL not in GEMINI_FALLBACK_MODELS:
    GEMINI_FALLBACK_MODELS.insert(0, GEMINI_MODEL)

# Configurações de LLM
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')

# Configurações do Cache
CACHE_DIR = os.getenv('CACHE_DIR', './cache')
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '3600'))

# Configurações do Streamlit
STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', '8501'))

# Validação de configuração
if LLM_PROVIDER == 'gemini' and not GEMINI_API_KEY:
    print("⚠️ AVISO: GEMINI_API_KEY não configurada!")
    print("Configure no arquivo .env para usar Gemini")
    print("Obtenha sua chave em: https://aistudio.google.com/app/apikey")
else:
    print(f"✅ LLM Provider: {LLM_PROVIDER}")
    print(f"📦 Ollama: {OLLAMA_HOST} ({OLLAMA_MODEL})")
    if GEMINI_API_KEY:
        print(f"🔑 Gemini configurado")
        print(f"🎯 Modelo principal: {GEMINI_MODEL}")
        print(f"🔄 Fallback habilitado: {', '.join(GEMINI_FALLBACK_MODELS[1:] if len(GEMINI_FALLBACK_MODELS) > 1 else ['Nenhum'])}")
