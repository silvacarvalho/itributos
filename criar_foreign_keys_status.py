import psycopg2
from datetime import datetime

# Conectar ao banco
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="itributos",
    user="postgres",
    password="postgres"
)
conn.autocommit = True
cursor = conn.cursor()

print("=" * 80)
print("CRIANDO FOREIGN KEYS PARA TABELAS COM STATUS")
print("=" * 80)

# Tabelas relacionadas a pagamentos (usam payment_status)
payment_tables = [
    'grouped_payments',
    'payment_duplicates',
    'payment_extensions',
    'payment_parcel_revenues',
    'payments'
]

# Tabela de dívida ativa (usa active_debt_status)
active_debt_tables = [
    'active_debts'
]

# Outras tabelas que precisam de análise manual
other_tables = [
    'dte_user_requests',
    'educacao_bibliographic_collection_borrowings',
    'educacao_bibliographic_collection_reservations',
    'educacao_deletions',
    'frotas_vehicle_shutdowns',
    'legal_cases',
    'mailbox_message_generators',
    'payment_import_logs',
    'personal_financial_positions',
    'saude_reception_tfds',
    'saude_suppressed_demand_withdrawals',
    'saude_suppressed_demands',
    'saude_travel_closings',
    'saude_travels',
    'subjects'
]

success_count = 0
error_count = 0
skipped_count = 0

# Processar tabelas de pagamento
print("\n📊 TABELAS DE PAGAMENTO (payment_status):")
print("-" * 80)
for table in payment_tables:
    constraint_name = f"fk_{table}_payment_status"
    
    # Verificar se a constraint já existe
    cursor.execute("""
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = %s AND table_name = %s
    """, (constraint_name, table))
    
    if cursor.fetchone():
        print(f"⏭️  {table:<40} [JÁ EXISTE]")
        skipped_count += 1
        continue
    
    try:
        # Criar foreign key
        cursor.execute(f"""
            ALTER TABLE {table}
            ADD CONSTRAINT {constraint_name}
            FOREIGN KEY (status)
            REFERENCES payment_status(id)
        """)
        
        # Criar índice
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{table}_status 
            ON {table}(status)
        """)
        
        print(f"✅ {table:<40} [OK]")
        success_count += 1
        
    except Exception as e:
        print(f"❌ {table:<40} [ERRO: {str(e)[:40]}]")
        error_count += 1

# Processar tabela de dívida ativa
print("\n💰 TABELAS DE DÍVIDA ATIVA (active_debt_status):")
print("-" * 80)
for table in active_debt_tables:
    constraint_name = f"fk_{table}_active_debt_status"
    
    # Verificar se a constraint já existe
    cursor.execute("""
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = %s AND table_name = %s
    """, (constraint_name, table))
    
    if cursor.fetchone():
        print(f"⏭️  {table:<40} [JÁ EXISTE]")
        skipped_count += 1
        continue
    
    try:
        # Criar foreign key
        cursor.execute(f"""
            ALTER TABLE {table}
            ADD CONSTRAINT {constraint_name}
            FOREIGN KEY (status)
            REFERENCES active_debt_status(id)
        """)
        
        # Criar índice
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{table}_status 
            ON {table}(status)
        """)
        
        print(f"✅ {table:<40} [OK]")
        success_count += 1
        
    except Exception as e:
        print(f"❌ {table:<40} [ERRO: {str(e)[:40]}]")
        error_count += 1

# Relatório de outras tabelas
print("\n⚠️  OUTRAS TABELAS (requerem análise manual):")
print("-" * 80)
for table in other_tables:
    # Contar registros por status
    cursor.execute(f"""
        SELECT status, COUNT(*) as qtd 
        FROM {table} 
        WHERE status IS NOT NULL
        GROUP BY status 
        ORDER BY status
        LIMIT 5
    """)
    
    status_info = cursor.fetchall()
    if status_info:
        status_str = ", ".join([f"{s[0]}({s[1]})" for s in status_info])
        print(f"📋 {table:<40} Status: {status_str}")
    else:
        print(f"📋 {table:<40} [Sem dados de status]")

# Resumo final
print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)
print(f"✅ Sucesso:        {success_count}")
print(f"⏭️  Já existentes:  {skipped_count}")
print(f"❌ Erros:          {error_count}")
print(f"⚠️  Análise manual: {len(other_tables)}")
print("=" * 80)

cursor.close()
conn.close()

print("\n✓ Processo concluído!")
