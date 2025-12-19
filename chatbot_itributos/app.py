"""
Chatbot iTributos - Interface Streamlit
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Dict, Any
import sys

# Importar módulos locais
from database import DatabaseService
from llm_service import LLMService
from cache_manager import CacheManager


# Configuração da página
st.set_page_config(
    page_title="Chatbot iTributos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado inspirado no Gemini
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .assistant-message {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .sql-code {
        background-color: #263238;
        color: #aed581;
        padding: 10px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    
    /* Estilo Gemini para input */
    .stTextArea textarea {
        border-radius: 24px !important;
        border: 1.5px solid #dadce0 !important;
        padding: 16px 20px !important;
        font-size: 16px !important;
        transition: all 0.2s ease !important;
        background-color: #f8f9fa !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #1a73e8 !important;
        box-shadow: 0 1px 6px rgba(26, 115, 232, 0.3) !important;
        background-color: white !important;
    }
    
    /* Botão elegante estilo Gemini */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 24px !important;
        padding: 12px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Dica de CTRL+ENTER */
    .shortcut-hint {
        color: #5f6368;
        font-size: 12px;
        margin-top: 8px;
        font-style: italic;
    }
    
    /* Botão de parar */
    .stButton > button[kind="secondary"] {
        background-color: #ea4335 !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #d33426 !important;
    }
</style>
""", unsafe_allow_html=True)


# Inicialização de serviços no session_state
def init_services():
    """Inicializa serviços se ainda não estiverem no session_state"""
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseService()
        st.session_state.db.connect()
    
    if 'cache' not in st.session_state:
        st.session_state.cache = CacheManager()
    
    if 'llm_provider' not in st.session_state:
        st.session_state.llm_provider = 'gemini'
    
    if 'llm' not in st.session_state:
        try:
            st.session_state.llm = LLMService(provider=st.session_state.llm_provider)
        except Exception as e:
            st.error(f"Erro ao inicializar LLM: {e}")
            st.session_state.llm = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    if 'stop_requested' not in st.session_state:
        st.session_state.stop_requested = False


def render_sidebar():
    """Renderiza barra lateral com configurações"""
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        # Seletor de LLM
        st.subheader("🤖 Modelo de IA")
        llm_option = st.radio(
            "Selecione o provedor:",
            options=['gemini', 'ollama'],
            index=['gemini', 'ollama'].index(st.session_state.llm_provider),
            help="Gemini: Google AI, grátis até 15 req/min, rápido e preciso\nOllama: Local, gratuito, privado"
        )
        
        # Atualiza LLM se mudou
        if llm_option != st.session_state.llm_provider:
            st.session_state.llm_provider = llm_option
            try:
                st.session_state.llm = LLMService(provider=llm_option)
                st.success(f"✅ {llm_option.capitalize()} ativado!")
            except Exception as e:
                st.error(f"❌ Erro ao ativar {llm_option}: {e}")
        
        # Info do provedor ativo
        if st.session_state.llm:
            if st.session_state.llm_provider == 'ollama':
                st.success("✅ Ollama Ativo")
                if hasattr(st.session_state.llm, 'ollama_model'):
                    st.info(f"📦 Modelo: {st.session_state.llm.ollama_model}")
            elif st.session_state.llm_provider == 'gemini':
                st.success("✅ Google Gemini Ativo")
                from config import GEMINI_MODEL
                st.info(f"🌐 Modelo: {GEMINI_MODEL}")
        else:
            st.error("❌ LLM não conectado")
        
        st.divider()
        
        # Status do banco
        st.subheader("💾 Banco de Dados")
        db_info = st.session_state.db.test_connection()
        if db_info['connected']:
            st.success("✅ Conectado")
            st.text(f"Database: {db_info['database']}")
            st.text(f"Tabelas: {db_info['tables_count']}")
        else:
            st.error(f"❌ Erro: {db_info.get('error', 'Desconectado')}")
        
        st.divider()
        
        # Cache
        st.subheader("📦 Cache")
        cache_stats = st.session_state.cache.get_stats()
        st.text(f"Consultas em cache: {cache_stats['size']}")
        st.text(f"TTL: {cache_stats['ttl_hours']:.1f}h")
        
        if st.button("🗑️ Limpar Cache", use_container_width=True):
            st.session_state.cache.clear()
            st.success("Cache limpo!")
            st.rerun()
        
        st.divider()
        
        # Histórico
        st.subheader("📊 Estatísticas")
        st.text(f"Conversas: {len(st.session_state.chat_history)}")
        st.text(f"Consultas SQL: {len(st.session_state.query_history)}")
        
        if st.button("🔄 Nova Conversa", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.query_history = []
            st.success("Conversa reiniciada!")
            st.rerun()


def process_question(question: str) -> Dict[str, Any]:
    """
    Processa pergunta do usuário
    
    Args:
        question: Pergunta em linguagem natural
    
    Returns:
        Dict com sql, results, explanation
    """
    try:
        st.session_state.processing = True
        st.session_state.stop_requested = False
        
        # Verificar se foi solicitada interrupção
        if st.session_state.stop_requested:
            st.session_state.processing = False
            return {
                'error': True,
                'message': '⛔ Processamento interrompido pelo usuário',
                'sql': None,
                'results': []
            }
        
        # Obter schema do banco
        schema_context = st.session_state.db.get_schema_context()
        
        # Gerar SQL com LLM
        with st.spinner("🤖 Gerando consulta SQL..."):
            if st.session_state.stop_requested:
                st.session_state.processing = False
                return {'error': True, 'message': '⛔ Interrompido', 'sql': None, 'results': []}
            llm_response = st.session_state.llm.generate_sql(question, schema_context)
        
        if 'error' in llm_response or not llm_response.get('sql'):
            return {
                'error': True,
                'message': llm_response.get('explanation', 'Erro ao gerar SQL'),
                'sql': None,
                'results': []
            }
        
        sql = llm_response['sql']
        explanation = llm_response.get('explanation', '')
        
        # Verificar cache
        cached_results = st.session_state.cache.get(sql)
        if cached_results is not None:
            st.session_state.processing = False
            return {
                'error': False,
                'sql': sql,
                'results': cached_results,
                'explanation': explanation,
                'from_cache': True
            }
        
        # Verificar interrupção antes de executar
        if st.session_state.stop_requested:
            st.session_state.processing = False
            return {'error': True, 'message': '⛔ Interrompido', 'sql': None, 'results': []}
        
        # Executar query
        with st.spinner("💾 Executando consulta no banco..."):
            results = st.session_state.db.execute_query(sql)
        
        # Armazenar no cache
        st.session_state.cache.set(sql, results)
        
        # Salvar no histórico
        st.session_state.query_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'sql': sql,
            'results_count': len(results)
        })
        
        st.session_state.processing = False
        return {
            'error': False,
            'sql': sql,
            'results': results,
            'explanation': explanation,
            'from_cache': False
        }
    
    except Exception as e:
        st.session_state.processing = False
        return {
            'error': True,
            'message': f"Erro ao processar consulta: {str(e)}",
            'sql': None,
            'results': []
        }


def render_results(response: Dict[str, Any], message_id: str = "main"):
    """Renderiza resultados da consulta"""
    if response['error']:
        st.error(f"❌ {response['message']}")
        return
    
    # Explicação
    if response.get('explanation'):
        st.info(f"💡 **Explicação:** {response['explanation']}")
    
    # Aviso de fallback
    if response.get('fallback_used'):
        provider_name = response.get('fallback_provider', 'alternativo').capitalize()
        st.warning(f"⚠️ Limite do modelo principal atingido. Usando **{provider_name}** automaticamente para continuar.")
    
    # SQL
    with st.expander("📄 Ver SQL", expanded=False):
        st.code(response['sql'], language='sql')
        if response.get('from_cache'):
            st.caption("✅ Resultado obtido do cache")
    
    # Resultados
    results = response['results']
    if not results:
        st.warning("⚠️ Nenhum resultado encontrado")
        return
    
    st.success(f"✅ {len(results)} registro(s) encontrado(s)")
    
    # Tabela
    df = pd.DataFrame(results)
    
    # Formatação automática de valores monetários
    def format_currency_columns(dataframe):
        """Detecta e formata colunas monetárias automaticamente"""
        df_formatted = dataframe.copy()
        
        # Palavras-chave que indicam valores monetários (mais abrangente)
        money_keywords = [
            'valor', 'value', 'price', 'preco', 'total', 'amount', 'quantia',
            'saldo', 'credito', 'debito', 'taxa', 'multa', 'juros',
            'desconto', 'acrescimo', 'pagamento', 'recebimento', 'pago',
            'receita', 'despesa', 'custo', 'tarifa', 'montante',
            'principal', 'restante', 'devido', 'cobrado', 'recebido', 'due', 'paid',
            'fee', 'payment', 'income', 'expense', 'cost'
        ]
        
        for col in df_formatted.columns:
            col_lower = str(col).lower()
            
            # Verificar se é coluna numérica
            if df_formatted[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                # Verificar se o nome da coluna contém palavras-chave monetárias
                is_money_column = any(keyword in col_lower for keyword in money_keywords)
                
                if is_money_column:
                    # Formatar como moeda brasileira diretamente
                    def format_br_currency(value):
                        if pd.isna(value) or value is None:
                            return "-"
                        try:
                            # Formatar com separadores brasileiros
                            valor_formatado = f"{float(value):,.2f}"
                            # Substituir: 1,234.56 -> 1.234,56
                            valor_formatado = valor_formatado.replace(',', '#TEMP#')
                            valor_formatado = valor_formatado.replace('.', ',')
                            valor_formatado = valor_formatado.replace('#TEMP#', '.')
                            return f"R$ {valor_formatado}"
                        except:
                            return "-"
                    
                    df_formatted[col] = df_formatted[col].apply(format_br_currency)
        
        return df_formatted
    
    df_display = format_currency_columns(df)
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Opções de exportação
    col1, col2 = st.columns([1, 1])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f"consulta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    
    with col2:
        # Tentar criar gráfico se houver dados numéricos
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if len(numeric_cols) >= 1 and len(df.columns) >= 2:
            with st.expander("📊 Visualização", expanded=False):
                chart_type = st.selectbox("Tipo de gráfico:", ["Barras", "Linha", "Pizza"], key=f"chart_type_{message_id}")
                
                if len(df) > 0:
                    if chart_type == "Barras" and len(df.columns) >= 2:
                        x_col = st.selectbox("Eixo X:", df.columns, key=f"x_col_{message_id}")
                        y_col = st.selectbox("Eixo Y:", numeric_cols, key=f"y_col_{message_id}")
                        fig = px.bar(df.head(20), x=x_col, y=y_col)
                        st.plotly_chart(fig, use_container_width=True)


def render_chat_interface():
    """Renderiza interface de chat"""
    st.title("💬 Chatbot iTributos")
    st.caption("Faça perguntas sobre o banco de dados em linguagem natural")
    
    # Container de chat
    chat_container = st.container()
    
    # Histórico de conversa
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>🙋 Você:</strong><br/>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 Assistente:</strong>
                </div>
                """, unsafe_allow_html=True)
                render_results(message['response'], message_id=f"msg_{i}")
    
    # Input de pergunta
    st.divider()
    
    # Exemplos rápidos
    st.subheader("💡 Exemplos de perguntas:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Histórico de contribuinte", use_container_width=True):
            st.session_state.example_question = "Me dê um histórico financeiro do contribuinte 34.019.100/0001-81"
    
    with col2:
        if st.button("💰 Parcelamentos ativos", use_container_width=True):
            st.session_state.example_question = "Quais são os parcelamentos ativos?"
    
    with col3:
        if st.button("📈 Pagamentos do mês", use_container_width=True):
            st.session_state.example_question = "Mostre os pagamentos realizados em dezembro de 2024"
    
    # Campo de input elegante estilo Gemini
    st.markdown("### 💬 Faça sua pergunta")
    question = st.text_area(
        label="Pergunta",
        value=st.session_state.get('example_question', ''),
        placeholder="Digite sua pergunta sobre o sistema tributário...\n\nExemplo: Me dê um histórico financeiro do contribuinte 34.019.100/0001-81",
        height=120,
        key="question_input",
        label_visibility="collapsed"
    )
    
    # Dica de atalho
    st.markdown('<p class="shortcut-hint">💡 Dica: Pressione <strong>Ctrl + Enter</strong> para enviar</p>', unsafe_allow_html=True)
    
    # Limpar exemplo após usar
    if 'example_question' in st.session_state:
        del st.session_state.example_question
    
    # Botões de enviar e parar lado a lado
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        submit_clicked = st.button(
            "🚀 Enviar", 
            type="primary", 
            use_container_width=True, 
            disabled=st.session_state.get('processing', False)
        )
    
    with col_btn2:
        # Botão parar sempre visível, mas só funcional durante processamento
        stop_clicked = st.button(
            "⛔ Parar", 
            type="secondary", 
            use_container_width=True,
            disabled=not st.session_state.get('processing', False)
        )
        
        if stop_clicked and st.session_state.get('processing', False):
            st.session_state.stop_requested = True
            st.warning("⚠️ Solicitação de parada enviada...")
            st.rerun()
    
    # JavaScript para CTRL+ENTER
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        let interval = setInterval(function() {
            const textareas = parent.document.querySelectorAll('textarea');
            if (textareas.length > 0) {
                textareas.forEach(textarea => {
                    if (!textarea.hasAttribute('data-listener-added')) {
                        textarea.setAttribute('data-listener-added', 'true');
                        textarea.addEventListener('keydown', function(e) {
                            if (e.ctrlKey && e.key === 'Enter') {
                                e.preventDefault();
                                const buttons = parent.document.querySelectorAll('button');
                                buttons.forEach(btn => {
                                    const text = btn.textContent;
                                    if (text && text.includes('Enviar') && !btn.disabled) {
                                        btn.click();
                                    }
                                });
                            }
                        });
                    }
                });
            }
        }, 500);
        
        setTimeout(function() { clearInterval(interval); }, 5000);
    })();
    </script>
    """, height=0)
    
    if submit_clicked:
        if question.strip():
            # Adicionar pergunta ao histórico
            st.session_state.chat_history.append({
                'role': 'user',
                'content': question
            })
            
            # Processar pergunta
            response = process_question(question)
            
            # Adicionar resposta ao histórico
            st.session_state.chat_history.append({
                'role': 'assistant',
                'response': response
            })
            
            # Resetar flag de processamento e recarregar
            st.session_state.processing = False
            st.session_state.stop_requested = False
            st.rerun()
        else:
            st.warning("⚠️ Digite uma pergunta primeiro")


def main():
    """Função principal"""
    # Inicializar serviços
    init_services()
    
    # Renderizar sidebar
    render_sidebar()
    
    # Renderizar interface principal
    render_chat_interface()


if __name__ == '__main__':
    main()
