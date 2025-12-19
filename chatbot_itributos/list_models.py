"""
Script para listar modelos disponíveis do Google Gemini
"""
from google import genai
from config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

print("🔍 Listando modelos disponíveis do Google Gemini:\n")

try:
    models = client.models.list()
    for model in models:
        print(f"✅ {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"   Suporta: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"❌ Erro ao listar modelos: {e}")
