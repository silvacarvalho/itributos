# Tabelas de Status - Sistema iTributos
## Criadas em: 18/12/2025

## 📊 Estrutura Criada

### 1️⃣ payment_status (21 status)
Tabela de referência para status de pagamentos

| ID | Descrição PT | Descrição EN |
|----|--------------|--------------|
| 0 | Simulado | simulated |
| 1 | Aberto | opened |
| 2 | Cancelado | canceled |
| 3 | Isento | exempt |
| 4 | Dívida Ativa | active_debt |
| 5 | Pago | paid |
| 6 | Anulado | annulled |
| 7 | Excluído | excluded |
| 8 | Isenção | exemption |
| 9 | Imunidade | immunity |
| 10 | Incentivo | incentive |
| 11 | Remissão | remission |
| 12 | Suspenso | suspended |
| 13 | Parcelado | parceled |
| 14 | ISS | iss |
| 15 | Sem Movimento | without_movement |
| 16 | Supervisionado | supervised |
| 17 | Doação em Pagamento | donation_in_payments |
| 18 | Prescrito | prescribed |
| 19 | Transferido | transferred |
| 20 | Anistiado | amnistied |

**Tabelas relacionadas (7):**
- ✅ payment_parcels
- ✅ payments
- ✅ grouped_payments
- ✅ payment_duplicates
- ✅ payment_extensions
- ✅ payment_parcel_revenues

---

### 2️⃣ active_debt_status (10 status)
Tabela de referência para status de dívida ativa

| ID | Descrição PT | Descrição EN |
|----|--------------|--------------|
| 0 | Aberto | opened |
| 1 | Suspenso | suspended |
| 2 | Cancelado | canceled |
| 3 | Parcelado | parceled |
| 4 | Resgatado | redeemed |
| 5 | Prescrito | prescribed |
| 6 | Anistiado | amnistied |
| 7 | Pago | paid |
| 8 | Supervisionado | supervised |
| 9 | Doação em Pagamento | donation_in_payment |

**Tabelas relacionadas (1):**
- ✅ active_debts

---

## 🔗 Relacionamentos (Foreign Keys)

```
payment_status (id)
    ├── payment_parcels.status
    ├── payments.status
    ├── grouped_payments.status
    ├── payment_duplicates.status
    ├── payment_extensions.status
    └── payment_parcel_revenues.status

active_debt_status (id)
    └── active_debts.status
```

---

## 📈 Estatísticas de Uso

### Payment Status em Uso:
- **Status 1 (Aberto)**: 1.853 pagamentos, 1.731 parcelas
- **Status 2 (Cancelado)**: 2.567 pagamentos, 2.927 parcelas
- **Status 5 (Pago)**: 25.325 pagamentos, 25.607 parcelas ✨
- **Status 6 (Anulado)**: 4.753 pagamentos, 4.858 parcelas
- **Status 13 (Parcelado)**: 181 pagamentos, 221 parcelas
- **Status 18 (Prescrito)**: 628 pagamentos, 543 parcelas

### Active Debt Status em Uso:
- **Status 0 (Aberto)**: 6 dívidas ativas

---

## 🎯 Benefícios

1. **Normalização**: Dados centralizados e consistentes
2. **Integridade**: Foreign keys garantem dados válidos
3. **Performance**: Índices criados em todas as colunas status
4. **Documentação**: Sistema autodocumentado
5. **Manutenção**: Fácil adicionar novos status se necessário
6. **Consultas**: JOIN simples para obter descrições legíveis

---

## 📝 Exemplo de Uso

```sql
-- ANTES (sem relacionamento):
SELECT year, parcel_number, status, value
FROM taxable_debts
WHERE revenue_acronym = 'TLLF';

-- DEPOIS (com relacionamento):
SELECT 
    td.year,
    td.parcel_number,
    ps.description AS status_descricao,
    td.value
FROM taxable_debts td
JOIN payment_status ps ON ps.id = td.status
WHERE td.revenue_acronym = 'TLLF';
```

---

## ⚠️ Tabelas Pendentes (15)

Requerem análise para determinar estrutura de status apropriada:

1. dte_user_requests
2. educacao_bibliographic_collection_borrowings
3. educacao_bibliographic_collection_reservations
4. educacao_deletions
5. frotas_vehicle_shutdowns
6. legal_cases
7. mailbox_message_generators
8. payment_import_logs ⚡ (com dados)
9. personal_financial_positions ⚡ (com dados)
10. saude_reception_tfds
11. saude_suppressed_demand_withdrawals
12. saude_suppressed_demands
13. saude_travel_closings
14. saude_travels
15. subjects

---

## 🛠️ Scripts Criados

1. **criar_foreign_keys_status.py** - Script automatizado para criar relacionamentos
2. **documentacao_status_tables.sql** - Documentação SQL completa
3. **relatorio_completo_tllf.py** - Relatório Excel atualizado com status

---

## ✅ Validação

Todos os relacionamentos foram testados e estão funcionando corretamente:
- ✅ Foreign keys criadas
- ✅ Índices criados
- ✅ Consultas com JOIN funcionando
- ✅ Integridade referencial garantida
