# 💬 Chatbot iTributos

Sistema de consulta inteligente ao banco de dados iTributos usando IA (Google Gemini ou Ollama) para converter perguntas em linguagem natural para SQL.

## 🎯 Funcionalidades

- ✅ **Consultas em linguagem natural** - Faça perguntas como "histórico do contribuinte X"
- 🤖 **Dois provedores de IA**:
  - **Google Gemini** (gratuito, 15 req/min)
  - **Ollama** (local, offline)
- 💾 **Cache inteligente** - Respostas rápidas para consultas repetidas
- 📊 **Visualização de dados** - Tabelas e gráficos interativos
- 📥 **Exportação** - Download de resultados em CSV
- 🔍 **SQL transparente** - Veja a query gerada
- 📈 **Histórico** - Acompanhe suas consultas

## 🚀 Instalação

### 1. Requisitos

- Python 3.10+
- PostgreSQL (banco iTributos configurado)
- Conexão com internet (para Gemini) OU Ollama instalado (para uso offline)

### 2. Instalar dependências

```powershell
cd C:\Users\Fiscal\PROJETOS\mcp.local\chatbot_itributos

# Ativar ambiente virtual
..\.venv\Scripts\Activate.ps1

# Instalar pacotes
pip install -r requirements.txt
```

### 3. Configurar API Key do Google Gemini (RECOMENDADO)

#### Obter API Key (Gratuita):
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

#### Configurar no projeto:
A chave já está configurada no arquivo `.env`:
```
GOOGLE_API_KEY=AIzaSyCq_xGXfc05bNrOOOa3VWaeynKwptQeHfo
```

### 4. (OPCIONAL) Instalar Ollama para uso offline

Se preferir usar IA local sem depender de internet:

1. Baixe: https://ollama.ai
2. Instale o Ollama
3. Baixe um modelo:
```powershell
ollama pull llama3.1
```

4. Altere no arquivo `.env`:
```
LLM_PROVIDER=ollama
```

## ▶️ Como Usar

### Iniciar o chatbot:

```powershell
# Certifique-se de estar no diretório correto
cd C:\Users\Fiscal\PROJETOS\mcp.local\chatbot_itributos

# Ativar ambiente virtual
..\.venv\Scripts\Activate.ps1

# Executar aplicação
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em: `http://localhost:8501`

### Alternar entre Gemini e Ollama:

Na barra lateral esquerda, você pode alternar entre os provedores:
- 🌐 **Gemini**: API Google (requer internet, gratuito)
- 🏠 **Ollama**: Local (offline, requer instalação)

## 💡 Exemplos de Perguntas

### Histórico de Contribuinte
```
Me dê um histórico financeiro completo do contribuinte 34.019.100/0001-81
```

### Parcelamentos
```
Quais são todos os parcelamentos ativos?
Mostre parcelamentos com reparcelamento do contribuinte X
```

### Pagamentos
```
Mostre os pagamentos realizados em dezembro de 2024
Quais débitos estão em aberto?
```

### Dívida Ativa
```
Contribuintes com débitos em dívida ativa
```

### Análises
```
Total arrecadado por tipo de receita em 2024
Contribuintes inadimplentes com mais de 3 parcelas atrasadas
```

## 📁 Estrutura do Projeto

```
chatbot_itributos/
├── app.py                 # Interface Streamlit (main)
├── config.py              # Configurações e variáveis de ambiente
├── database.py            # Conexão e operações no PostgreSQL
├── llm_service.py         # Integração com Gemini/Ollama
├── cache_manager.py       # Sistema de cache
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (com API key configurada)
├── .env.example           # Exemplo de configuração
└── cache/                 # Diretório de cache (criado automaticamente)
```

## ⚙️ Configurações

Edite o arquivo `.env` para personalizar:

```bash
# Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=itributos
DB_USER=postgres
DB_PASSWORD=postgres

# Google Gemini (JÁ CONFIGURADO)
GOOGLE_API_KEY=AIzaSyCq_xGXfc05bNrOOOa3VWaeynKwptQeHfo

# Ollama (para uso local)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Escolha o provedor: 'ollama'
LLM_PROVIDER=ollama

# Cache (1 hora = 3600 segundos)
CACHE_TTL_SECONDS=3600
```

## 🔧 Troubleshooting

### Erro: "GOOGLE_API_KEY não configurada"
- Verifique se o arquivo `.env` existe
- A API key já está configurada: `AIzaSyCq_xGXfc05bNrOOOa3VWaeynKwptQeHfo`

### Erro: "Não foi possível conectar ao Ollama"
- Certifique-se de que o Ollama está rodando
- Execute: `ollama serve` em outro terminal
- Baixe o modelo: `ollama pull llama3.1`

### Erro de conexão com PostgreSQL
- Verifique se o PostgreSQL está rodando
- Confirme credenciais no arquivo `.env`
- Teste conexão: `psql -U postgres -d itributos`

### Query SQL incorreta
- O LLM pode gerar SQL inválido ocasionalmente
- Tente reformular a pergunta de forma mais específica
- Use exemplos de perguntas fornecidos como referência

## 📊 Limites e Performance

### Google Gemini (Gratuito):
- ✅ 15 requisições/minuto
- ✅ 1.500 requisições/dia
- ✅ Sem necessidade de GPU
- ⚠️ Requer conexão com internet

### Ollama (Local):
- ✅ Ilimitado
- ✅ Offline
- ✅ Privacidade total
- ⚠️ Requer 8GB+ RAM
- ⚠️ GPU recomendada para melhor performance

### Cache:
- Consultas idênticas retornam instantaneamente do cache
- TTL padrão: 1 hora
- Cache pode ser limpo manualmente na interface

## 🛡️ Segurança

- ⚠️ **Nunca compartilhe sua GOOGLE_API_KEY publicamente**
- ✅ Adicione `.env` ao `.gitignore`
- ✅ Use `.env.example` para documentar configurações sem expor credenciais
- ✅ O banco é acessado apenas em modo leitura (SELECT)

## 📝 Próximas Melhorias

- [ ] Suporte a múltiplos bancos
- [ ] Histórico persistente de conversas
- [ ] Sugestões automáticas de perguntas
- [ ] Export para Excel com formatação
- [ ] Autenticação de usuários
- [ ] API REST para integração

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de **Troubleshooting**
2. Consulte os logs no terminal
3. Revise as configurações do `.env`

## 📄 Licença

Uso interno - Prefeitura

---

**Desenvolvido para o setor de Fiscalização Tributária** 💰🏛️
