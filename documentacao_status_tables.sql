-- ============================================================================
-- DOCUMENTAÇÃO: TABELAS DE STATUS CRIADAS NO SISTEMA iTributos
-- ============================================================================
-- Data de criação: 18/12/2025
-- Objetivo: Normalizar e documentar os códigos de status do sistema
-- ============================================================================

-- ============================================================================
-- 1. TABELA: payment_status
-- ============================================================================
-- Descrição: Status para pagamentos (payments, payment_parcels, etc)
-- Tabelas relacionadas: 7 tabelas

SELECT 'PAYMENT_STATUS' as tabela, * FROM payment_status ORDER BY id;

-- Relacionamentos criados:
-- • payment_parcels.status → payment_status.id
-- • payments.status → payment_status.id
-- • grouped_payments.status → payment_status.id
-- • payment_duplicates.status → payment_status.id
-- • payment_extensions.status → payment_status.id
-- • payment_parcel_revenues.status → payment_status.id

-- ============================================================================
-- 2. TABELA: active_debt_status
-- ============================================================================
-- Descrição: Status específicos para dívida ativa
-- Tabelas relacionadas: 1 tabela

SELECT 'ACTIVE_DEBT_STATUS' as tabela, * FROM active_debt_status ORDER BY id;

-- Relacionamentos criados:
-- • active_debts.status → active_debt_status.id

-- ============================================================================
-- CONSULTAS ÚTEIS
-- ============================================================================

-- Ver todos os relacionamentos de foreign key criados:
SELECT 
    tc.table_name AS tabela,
    tc.constraint_name AS constraint,
    ccu.table_name AS tabela_referenciada,
    kcu.column_name AS coluna,
    ccu.column_name AS coluna_referenciada
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND (ccu.table_name = 'payment_status' OR ccu.table_name = 'active_debt_status')
ORDER BY tc.table_name;

-- Ver status de pagamentos em uso com valores:
SELECT 
    ps.id,
    ps.description AS status,
    COUNT(DISTINCT p.id) as qtd_pagamentos,
    COUNT(DISTINCT pp.id) as qtd_parcelas,
    TO_CHAR(SUM(pp.total::numeric), 'FM999,999,999,999.00') as valor_total
FROM payment_status ps
LEFT JOIN payments p ON p.status = ps.id
LEFT JOIN payment_parcels pp ON pp.status = ps.id
GROUP BY ps.id, ps.description
HAVING COUNT(DISTINCT p.id) > 0 OR COUNT(DISTINCT pp.id) > 0
ORDER BY ps.id;

-- Ver status de dívida ativa em uso:
SELECT 
    ads.id,
    ads.description AS status,
    COUNT(ad.id) as qtd_dividas_ativas
FROM active_debt_status ads
LEFT JOIN active_debts ad ON ad.status = ads.id
GROUP BY ads.id, ads.description
HAVING COUNT(ad.id) > 0
ORDER BY ads.id;

-- Consultar TLLF com descrição do status:
SELECT 
    td.id,
    p.name AS contribuinte,
    td.year AS ano,
    td.parcel_number AS parcela,
    td.due_date AS vencimento,
    td.value AS valor,
    ps.description AS status
FROM taxable_debts td
JOIN unico_people p ON p.id = td.person_id
JOIN payment_status ps ON ps.id = td.status
WHERE td.revenue_acronym = 'TLLF'
AND td.year IN (2024, 2025)
ORDER BY td.year DESC, p.name, td.parcel_number;

-- ============================================================================
-- ÍNDICES CRIADOS PARA PERFORMANCE
-- ============================================================================
-- • idx_payment_parcels_status ON payment_parcels(status)
-- • idx_payments_status ON payments(status)
-- • idx_grouped_payments_status ON grouped_payments(status)
-- • idx_payment_duplicates_status ON payment_duplicates(status)
-- • idx_payment_extensions_status ON payment_extensions(status)
-- • idx_payment_parcel_revenues_status ON payment_parcel_revenues(status)
-- • idx_active_debts_status ON active_debts(status)

-- ============================================================================
-- TABELAS QUE REQUEREM ANÁLISE MANUAL
-- ============================================================================
-- As seguintes tabelas possuem coluna 'status' mas requerem análise para
-- determinar se devem usar payment_status ou ter sua própria tabela de status:
--
-- 1. dte_user_requests
-- 2. educacao_bibliographic_collection_borrowings
-- 3. educacao_bibliographic_collection_reservations
-- 4. educacao_deletions
-- 5. frotas_vehicle_shutdowns
-- 6. legal_cases
-- 7. mailbox_message_generators
-- 8. payment_import_logs (tem dados: status 1)
-- 9. personal_financial_positions (tem dados: status 1)
-- 10. saude_reception_tfds
-- 11. saude_suppressed_demand_withdrawals
-- 12. saude_suppressed_demands
-- 13. saude_travel_closings
-- 14. saude_travels
-- 15. subjects
-- ============================================================================
