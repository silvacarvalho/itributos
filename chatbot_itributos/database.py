"""
Database Module - Conexão e operações no banco iTributos
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from config import DB_CONFIG
import pandas as pd


class DatabaseService:
    """Serviço de banco de dados para iTributos"""
    
    def __init__(self):
        """Inicializa conexão com o banco"""
        self.config = DB_CONFIG
        self.connection = None
        self.schema_cache = None
        
    def connect(self) -> bool:
        """
        Estabelece conexão com o banco
        
        Returns:
            True se conectado com sucesso
        """
        try:
            self.connection = psycopg2.connect(**self.config)
            print(f"✅ Conectado ao banco: {self.config['database']}")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            return False
    
    def disconnect(self):
        """Fecha conexão com o banco"""
        if self.connection:
            self.connection.close()
            print("🔌 Conexão fechada")
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executa query SQL e retorna resultados
        
        Args:
            sql: Query SQL
            params: Parâmetros da query (opcional)
        
        Returns:
            Lista de dicionários com os resultados
        """
        if not self.connection or self.connection.closed:
            self.connect()
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                
                # Converte RealDictRow para dict comum
                return [dict(row) for row in results]
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Erro ao executar query: {e}")
    
    def execute_to_dataframe(self, sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """
        Executa query e retorna como DataFrame pandas
        
        Args:
            sql: Query SQL
            params: Parâmetros da query (opcional)
        
        Returns:
            DataFrame pandas com os resultados
        """
        results = self.execute_query(sql, params)
        return pd.DataFrame(results)
    
    def get_schema_context(self, tables: Optional[List[str]] = None) -> str:
        """
        Retorna contexto do schema para o LLM
        
        Args:
            tables: Lista de tabelas específicas (se None, retorna tabelas principais)
        
        Returns:
            String formatada com schema do banco
        """
        if self.schema_cache and not tables:
            return self.schema_cache
        
        # Tabelas principais do iTributos
        main_tables = tables or [
            'unico_people',
            'payments',
            'payment_parcels',
            'payment_status',
            'active_debts',
            'active_debt_status',
            'agreements',
            'agreement_operations',
            'other_debts_agreement_operations',
            'taxable_debts',
            'revenues',
            'payment_entries',
            'graphic_files',
            'graphic_files_payment_parcels'
        ]
        
        schema_parts = []
        
        for table in main_tables:
            try:
                columns_query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """
                columns = self.execute_query(columns_query, (table,))
                
                if columns:
                    schema_parts.append(f"\nTabela: {table}")
                    schema_parts.append("Colunas:")
                    for col in columns:
                        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                        schema_parts.append(
                            f"  - {col['column_name']}: {col['data_type']} {nullable}"
                        )
            except Exception as e:
                print(f"Erro ao obter schema de {table}: {e}")
        
        # Adiciona informações importantes sobre relacionamentos
        schema_parts.append("\n=== RELACIONAMENTOS (CRÍTICO) ===")
        schema_parts.append("agreements:")
        schema_parts.append("  - agreements.agreement_operation_id → agreement_operations.id")
        schema_parts.append("  - agreements.id ← payments.payable_id (quando payable_type='Agreement')")
        schema_parts.append("")
        schema_parts.append("agreement_operations:")
        schema_parts.append("  - agreement_operations.id ← agreements.agreement_operation_id")
        schema_parts.append("  - agreement_operations.person_id → unico_people.id")
        schema_parts.append("")
        schema_parts.append("payments:")
        schema_parts.append("  - payments.person_id → unico_people.id")
        schema_parts.append("  - payments.id ← payment_parcels.payment_id")
        schema_parts.append("  - payments.payable_id → agreements.id (quando payable_type='Agreement')")
        schema_parts.append("")
        schema_parts.append("payment_parcels:")
        schema_parts.append("  - payment_parcels.payment_id → payments.id")
        schema_parts.append("  - payment_parcels.status → payment_status.id")
        
        schema_parts.append("\n=== VALORES DE STATUS ===")
        schema_parts.append("payment_parcels.status:")
        schema_parts.append("  - 0 = Cancelado")
        schema_parts.append("  - 1 = Aberto (em aberto, não pago)")
        schema_parts.append("  - 5 = Pago")
        schema_parts.append("")
        schema_parts.append("active_debts.status:")
        schema_parts.append("  - É um INTEGER que referencia active_debt_status.id")
        schema_parts.append("  - NÃO existe coluna 'active_debt_status' na tabela active_debts")
        schema_parts.append("  - Use: ad.status para filtrar, NÃO ad.active_debt_status")
        
        schema_parts.append("\n=== CAMPOS IMPORTANTES ===")
        schema_parts.append("unico_people:")
        schema_parts.append("  - cpf_cnpj: CPF/CNPJ do contribuinte")
        schema_parts.append("  - name: Nome do contribuinte")
        schema_parts.append("")
        schema_parts.append("payments:")
        schema_parts.append("  - payable_type: 'Agreement' (parcelamento) ou outros")
        schema_parts.append("  - payable_id: ID do acordo quando type='Agreement'")
        schema_parts.append("  - person_id: ID do contribuinte")
        schema_parts.append("")
        schema_parts.append("agreements:")
        schema_parts.append("  - protocol_number: Número do protocolo do parcelamento")
        schema_parts.append("  - agreement_operation_id: FK para agreement_operations")
        schema_parts.append("")
        schema_parts.append("payment_entries:")
        schema_parts.append("  - barcode: Código de barras do boleto")
        
        context = "\n".join(schema_parts)
        
        # Cache apenas se for schema completo
        if not tables:
            self.schema_cache = context
        
        return context
    
    def get_contributor_by_cpf_cnpj(self, cpf_cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Busca contribuinte por CPF/CNPJ
        
        Args:
            cpf_cnpj: CPF ou CNPJ do contribuinte
        
        Returns:
            Dados do contribuinte ou None
        """
        sql = """
            SELECT id, cpf_cnpj, name, email, phone
            FROM unico_people
            WHERE cpf_cnpj = %s
            LIMIT 1
        """
        results = self.execute_query(sql, (cpf_cnpj,))
        return results[0] if results else None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão e retorna informações do banco
        
        Returns:
            Dict com informações do banco
        """
        try:
            result = self.execute_query("SELECT version()")
            tables_count = self.execute_query(
                "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public'"
            )
            
            return {
                'connected': True,
                'database': self.config['database'],
                'host': self.config['host'],
                'postgres_version': result[0]['version'],
                'tables_count': tables_count[0]['count']
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }


# Exemplo de uso e testes
if __name__ == '__main__':
    db = DatabaseService()
    
    # Teste de conexão
    info = db.test_connection()
    print(f"Informações do banco: {info}")
    
    # Teste de schema
    if info['connected']:
        schema = db.get_schema_context(['payments', 'payment_parcels'])
        print(f"\n{schema}")
    
    db.disconnect()
