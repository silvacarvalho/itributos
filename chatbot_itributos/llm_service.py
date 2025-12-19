"""
LLM Service - Ollama e Google Gemini
"""
import requests
import json
from typing import Optional, Dict, Any
from config import OLLAMA_HOST, OLLAMA_MODEL, GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FALLBACK_MODELS, LLM_PROVIDER
from google import genai
from google.genai import types


class LLMService:
    """Serviço de LLM com Ollama e Google Gemini"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or LLM_PROVIDER
        self.ollama_model = None
        self.gemini_model = None
        
        if self.provider == 'ollama':
            self._init_ollama()
        elif self.provider == 'gemini':
            self._init_gemini()
        else:
            raise ValueError(f"Provider '{self.provider}' não suportado. Use 'ollama' ou 'gemini'")
    
    def _init_ollama(self):
        """Inicializa Ollama"""
        try:
            # Testa conexão com Ollama
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = response.json().get('models', [])
                model_names = [m['name'] for m in available_models]
                
                if not model_names:
                    raise ConnectionError(
                        f"Nenhum modelo instalado no Ollama.\n"
                        f"Instale um modelo: ollama pull llama3.2"
                    )
                
                # Verificar se o modelo configurado existe
                if OLLAMA_MODEL not in model_names:
                    # Usar o primeiro modelo disponível
                    self.ollama_model = model_names[0]
                    print(f"⚠️  Modelo {OLLAMA_MODEL} não encontrado, usando: {self.ollama_model}")
                else:
                    self.ollama_model = OLLAMA_MODEL
                
                print(f"✅ Ollama conectado em {OLLAMA_HOST}")
                print(f"📦 Modelo ativo: {self.ollama_model}")
                print(f"📋 Modelos disponíveis: {', '.join(model_names)}")
            else:
                raise ConnectionError("Ollama não respondeu corretamente")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Não foi possível conectar ao Ollama em {OLLAMA_HOST}. "
                f"Certifique-se de que o Ollama está rodando.\n"
                f"Instale: https://ollama.ai\n"
                f"Execute: ollama pull llama3.2\n"
                f"Erro: {e}"
            )
    
    def _init_gemini(self):
        """Inicializa Google Gemini"""
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não configurada no .env.\n"
                "Obtenha em: https://aistudio.google.com/app/apikey\n"
                "Gemini oferece uso gratuito com limites generosos"
            )
        
        try:
            # Criar cliente Gemini
            self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            self.gemini_model_name = GEMINI_MODEL
            self.gemini_fallback_models = GEMINI_FALLBACK_MODELS.copy()
            self.gemini_current_model_index = 0
            
            print(f"✅ Google Gemini conectado")
            print(f"🎯 Modelo principal: {GEMINI_MODEL}")
            if len(self.gemini_fallback_models) > 1:
                print(f"🔄 Modelos de fallback: {', '.join(self.gemini_fallback_models[1:])}")
            
        except Exception as e:
            raise ConnectionError(
                f"Não foi possível conectar ao Google Gemini.\n"
                f"Verifique sua API key e conexão.\n"
                f"Erro: {e}"
            )
    
    def generate_sql(self, user_question: str, schema_context: str) -> Dict[str, Any]:
        """
        Gera SQL a partir da pergunta do usuário
        
        Args:
            user_question: Pergunta do usuário em linguagem natural
            schema_context: Contexto do schema do banco de dados
        
        Returns:
            Dict com 'sql', 'explanation' e 'tables_used'
        """
        prompt = self._build_sql_prompt(user_question, schema_context)
        
        if self.provider == 'ollama':
            return self._generate_sql_ollama(prompt)
        elif self.provider == 'gemini':
            return self._generate_sql_gemini(prompt)
    
    def _build_sql_prompt(self, user_question: str, schema_context: str) -> str:
        """Constrói o prompt para geração de SQL"""
        return f"""Você é um especialista em SQL para o sistema iTributos - sistema de gestão tributária municipal.

CONTEXTO DO BANCO DE DADOS:
{schema_context}

REGRAS IMPORTANTES:
1. agreements.agreement_operation_id → agreement_operations.id (NÃO use ao.agreement_operation_id)
2. agreement_operations.person_id → unico_people.id
3. payments.payable_id = agreements.id quando payable_type = 'Agreement'
4. payments.id → payment_parcels.payment_id
5. payment_parcels.status: 5=Pago, 1=Aberto, 0=Cancelado
6. SEMPRE use aliases curtos e claros (p, pm, pp, a, ao, up)
7. SEMPRE inclua WHERE clauses apropriadas
8. Não limitar resultados sem solicitação explícita do usuário
9. Use JOINs corretos para relacionar tabelas
10. VALORES MONETÁRIOS: Use nomes de colunas claros (ex: valor_total, valor_pago) para facilitar formatação automática em R$

EXEMPLOS DE QUERIES CORRETAS:

-- Parcelamentos ativos:
SELECT 
    a.protocol_number,
    up.name,
    up.cpf_cnpj,
    ao.date_agreement,
    COUNT(pp.id) as total_parcelas
FROM agreements a
JOIN agreement_operations ao ON a.agreement_operation_id = ao.id
JOIN unico_people up ON ao.person_id = up.id
JOIN payments pm ON pm.payable_id = a.id AND pm.payable_type = 'Agreement'
JOIN payment_parcels pp ON pp.payment_id = pm.id
WHERE pp.status = 1
GROUP BY a.protocol_number, up.name, up.cpf_cnpj, ao.date_agreement
LIMIT 100;

-- Débitos em aberto:
SELECT 
    pp.id,
    up.name,
    up.cpf_cnpj,
    pp.value,
    pp.due_date,
    ps.description as status_descricao
FROM payment_parcels pp
JOIN payments pm ON pm.id = pp.payment_id
JOIN unico_people up ON up.id = pm.person_id
JOIN payment_status ps ON ps.id = pp.status
WHERE pp.status = 1
ORDER BY pp.due_date DESC
LIMIT 100;

-- Histórico de contribuinte:
SELECT 
    pm.id,
    pm.payable_type,
    pm.value,
    pm.created_at
FROM payments pm
JOIN unico_people up ON up.id = pm.person_id
WHERE up.cpf_cnpj = '00.000.000/0000-00'
ORDER BY pm.created_at DESC
LIMIT 100;

ERROS COMUNS A EVITAR:
❌ ad.active_debt_status (NÃO EXISTE)
✅ ad.status (CORRETO - é um INTEGER, não uma coluna de tabela)
❌ ao.agreement_operation_id (ERRADO)
✅ a.agreement_operation_id (CORRETO)

PERGUNTA DO USUÁRIO:
{user_question}

RESPONDA NO FORMATO JSON (sem markdown):
{{
    "sql": "query SQL completa",
    "explanation": "explicação da query em português",
    "tables_used": ["tabela1", "tabela2"]
}}"""
    
    def _generate_sql_ollama(self, prompt: str) -> Dict[str, Any]:
        """Gera SQL usando Ollama"""
        try:
            model_to_use = getattr(self, 'ollama_model', OLLAMA_MODEL)
            print(f"⏳ Processando com {model_to_use} (pode demorar 1-2 minutos)...")
            
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    'model': model_to_use,
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json',
                    'options': {
                        'temperature': 0.1,
                        'num_predict': 500
                    }
                },
                timeout=180  # 3 minutos
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"Ollama retornou status {response.status_code}. "
                    f"Verifique se o modelo '{model_to_use}' está instalado. "
                    f"Execute: ollama pull {model_to_use}"
                )
            
            result_text = response.json()['response'].strip()
            
            # Remove markdown se presente
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            return result
        except requests.exceptions.Timeout:
            return {
                'sql': None,
                'explanation': (
                    'Timeout: O modelo demorou mais de 3 minutos para responder. '
                    'Tente: 1) Usar um modelo menor (qwen2.5:3b), '
                    '2) Reformular a pergunta de forma mais simples, '
                    '3) Verificar se o Ollama tem recursos suficientes.'
                ),
                'tables_used': [],
                'error': 'timeout'
            }
        except json.JSONDecodeError as e:
            return {
                'sql': None,
                'explanation': f'Erro ao processar resposta do Ollama: {e}. Resposta recebida: {result_text[:200]}',
                'tables_used': [],
                'error': str(e)
            }
        except Exception as e:
            return {
                'sql': None,
                'explanation': f'Erro ao gerar SQL com Ollama: {e}',
                'tables_used': [],
                'error': str(e)
            }
    
    def _generate_sql_gemini(self, prompt: str) -> Dict[str, Any]:
        """Gera SQL usando Google Gemini com fallback automático"""
        result_text = ""
        
        # Tentar cada modelo da lista em sequência até ter sucesso
        for attempt, model_name in enumerate(self.gemini_fallback_models):
            try:
                if attempt > 0:
                    print(f"🔄 Tentando modelo de fallback: {model_name}...")
                else:
                    print(f"⏳ Processando com Gemini ({model_name})...")
                
                # Gerar resposta
                response = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
                
                # Verificar se há resposta
                if not response or not response.text:
                    raise Exception("Gemini retornou resposta vazia")
                
                result_text = response.text.strip()
                
                # Remove markdown se presente
                if result_text.startswith('```json'):
                    result_text = result_text.split('```json')[1].split('```')[0].strip()
                elif result_text.startswith('```'):
                    result_text = result_text.split('```')[1].split('```')[0].strip()
                
                result = json.loads(result_text)
                
                # Sucesso! Atualizar modelo atual
                if attempt > 0:
                    print(f"✅ Sucesso com modelo de fallback: {model_name}")
                    self.gemini_model_name = model_name
                    self.gemini_current_model_index = attempt
                
                return result
                
            except json.JSONDecodeError as e:
                # Erro de parsing - não tentar fallback, retornar erro
                return {
                    'sql': None,
                    'explanation': (
                        f'❌ Erro ao processar resposta do Gemini: {e}\n\n'
                        f'Resposta recebida:\n{result_text[:500]}\n\n'
                        f'Tente reformular a pergunta.'
                    ),
                    'tables_used': [],
                    'error': str(e)
                }
            
            except Exception as e:
                error_message = str(e).lower()
                
                # Verificar se é erro de rate limit ou quota
                is_rate_limit = any(keyword in error_message for keyword in [
                    'rate limit',
                    'quota',
                    'resource exhausted',
                    'resource_exhausted',
                    '429',
                    'too many requests',
                    'limit exceeded',
                    'quota exceeded'
                ])
                
                # Se for rate limit e tiver mais modelos, tentar próximo
                if is_rate_limit and attempt < len(self.gemini_fallback_models) - 1:
                    print(f"⚠️  Limite atingido no modelo {model_name}")
                    print(f"🔄 Mudando para próximo modelo...")
                    continue  # Tentar próximo modelo
                
                # Se não for rate limit ou for último modelo, retornar erro
                if attempt == len(self.gemini_fallback_models) - 1:
                    return {
                        'sql': None,
                        'explanation': (
                            f'❌ Todos os modelos Gemini atingiram o limite ou falharam.\n'
                            f'Último erro ({model_name}): {e}\n\n'
                            f'Aguarde alguns minutos ou configure um modelo diferente no .env'
                        ),
                        'tables_used': [],
                        'error': str(e)
                    }
                else:
                    return {
                        'sql': None,
                        'explanation': f'❌ Erro ao gerar SQL com Gemini: {e}',
                        'tables_used': [],
                        'error': str(e)
                    }
        
        # Caso nenhum modelo funcione
        return {
            'sql': None,
            'explanation': '❌ Nenhum modelo Gemini disponível no momento.',
            'tables_used': [],
            'error': 'all_models_failed'
        }
    
    def explain_results(self, question: str, results: list, sql: str) -> str:
        """Gera explicação em linguagem natural dos resultados"""
        if not results:
            return "Nenhum resultado encontrado para esta consulta."
        
        prompt = f"""Você é um assistente tributário que explica resultados de consultas.

PERGUNTA ORIGINAL: {question}

SQL EXECUTADO:
{sql}

QUANTIDADE DE RESULTADOS: {len(results)}

PRIMEIROS RESULTADOS (até 5):
{json.dumps(results[:5], indent=2, default=str, ensure_ascii=False)}

TAREFA:
Explique os resultados em linguagem simples e objetiva para um funcionário da prefeitura.
Destaque informações importantes e padrões encontrados.
Seja conciso e direto.

RESPOSTA:"""
        
        try:
            if self.provider == 'gemini':
                # Tentar com modelo atual primeiro, depois fallback
                for attempt, model_name in enumerate([self.gemini_model_name] + 
                    [m for m in self.gemini_fallback_models if m != self.gemini_model_name]):
                    try:
                        response = self.gemini_client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.3,
                                max_output_tokens=500
                            )
                        )
                        if attempt > 0:
                            print(f"✅ Explicação gerada com modelo de fallback: {model_name}")
                        return response.text
                    except Exception as e:
                        error_msg = str(e).lower()
                        is_rate_limit = any(k in error_msg for k in [
                            'rate limit', 'quota', '429', 'resource exhausted', 
                            'resource_exhausted', 'limit exceeded'
                        ])
                        if is_rate_limit and attempt < len(self.gemini_fallback_models) - 1:
                            continue
                        elif attempt == len(self.gemini_fallback_models) - 1:
                            return f"Não foi possível gerar explicação: todos os modelos atingiram o limite."
                        else:
                            return f"Não foi possível gerar explicação: {e}"
            else:  # ollama
                model_to_use = getattr(self, 'ollama_model', OLLAMA_MODEL)
                response = requests.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        'model': model_to_use,
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'temperature': 0.3,
                            'num_predict': 300
                        }
                    },
                    timeout=120  # 2 minutos
                )
                return response.json()['response']
        except Exception as e:
            return f"Não foi possível gerar explicação: {e}"


# Exemplo de uso e testes
if __name__ == '__main__':
    # Teste com Ollama
    try:
        llm = LLMService(provider='ollama')
        print("✅ Ollama Service inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar Ollama: {e}")
    
    # Teste com Gemini
    try:
        llm = LLMService(provider='gemini')
        print("✅ Gemini Service inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar Gemini: {e}")
