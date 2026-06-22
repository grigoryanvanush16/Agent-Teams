# -*- coding: utf-8 -*-
"""Контент: Roadmap, CTE, Витрины, ТЗ, Реестр дашбордов, Топ-10."""

# ============== ЛИСТ 2: Roadmap витрин ==============
# (vitrina, status, prior, owner, source, impl, purpose)
ROADMAP = [
 ('int_leads_base','Нужна, не делалась',0,'DE',
  'marts._32_lead_info (лиды) + marts._33_opportunities (преобразование/контакт/брак) + marts._38_calls (дозвон АО)',
  'пересобрать',
  'Ядро лидов КД: firm_id × дата регистрации с типом лида, направлением, продуктом регистрации, флагами «загружен в АО», «дозвон», «преобразован», подкатегорией брака. База воронки КД. Питает «Сквозную отчётность», «Расшифровку по каналам КД», «Квалификацию по каналам КД».'),
 ('dm_kd_funnel','Нужна, не делалась',0,'DE',
  'int_leads_base + int_sales_base_kd + dim_kd_cost',
  'пересобрать',
  'Ядро сквозной воронки КД: дата лида × канал × продукт × тип лида - лиды→дозвон→квал→продажи→выручка, конверсии и юнит-экономика (CPL, CPLq, CPO, CAC) в одной грануляции. Сводит в одно то, что сейчас размазано по «Сквозной отчётности» и листам «исходник лиды/продажи».'),
 ('int_sales_base_kd','Нужна, не делалась',0,'DE',
  'marts._23_sale (продажи) + привязка к лиду по firm_id',
  'пересобрать',
  'База платежей КД: платёж × позиция с продуктом, типом оплаты (Новый/Продление), is_option/is_one_time, скидками по 3 каналам (менеджер/Пригласи друга/Лояльность) и реальным периодом. Логика дисконтов и ARPU переиспользуется из эталона int_sales_base v58.'),
 ('dim_date','Нужна / переиспользовать',0,'DE',
  'recursive CTE 2020-2030 + производственный календарь',
  'авто в DWH',
  'Календарь (date / year / quarter / month / week / рабочий день). Общий с эталоном v58. Нужен для отчётности по дате лида и по дате оплаты и для time-intelligence (YoY/MoM).'),
 ('dim_lead_type','Нужна, не делалась',1,'DE',
  'int_leads_base (lead_gen_responsible, direction, Альфа-бандл)',
  'авто в DWH',
  'Справочник типа лида: Лиды КД / Лиды маркетинга / WL / C проектов КД / С прочих источников. Единый срез «тип лида» на всех дашбордах. Бизнес-правило SWITCH уже зашито в DAX-колонку.'),
 ('dim_kd_cost','Нужна, не делалась',1,'DE',
  'CostMarketing (Google Sheet / файл xls с расходами): статья расходов × месяц × направление',
  'пересобрать',
  'Расходы КД: КВ партнёра + Сертификаты (переменные, для CPL/CPO), ФОТ КД, Прочие. Питает CPL, CPLq, CPO, CAC. Жёлтая правка: CPL/CPO считаются только от КВ+сертификаты, ФОТ и прочие - лишь в CAC.'),
 ('dm_kd_invoices','Нужна, не делалась',1,'DE',
  'marts._55_payment_history_ex / marts._33_opportunities.invoice_date + dim_partner',
  'пересобрать',
  'Выставленные счета: шт и руб по дате счёта и по дате лида, разрез по партнёрам. Питает «Динамику показателей → выставленные счета по партнёрам» и «Когорты счёт на оплату».'),
 ('dim_partner','Нужна, не делалась',1,'DE',
  'marts._23_sale (regional_partner_name) + marts._55_payment_history_ex',
  'авто в DWH',
  'Справочник партнёров (RegionalPartnerName), в т.ч. «Партнёр Мой бизнес». Разрез «партнёр» для счетов, ARPU и выручки. Питает дашборды «Партнёры», «Партнёр Мой бизнес».'),
 ('plan_kd_monthly','Нужна, не делалась',1,'DE + КД',
  'Plans (Google Sheet «Планы pbi»): месячный план по метрикам/менеджерам',
  'пересобрать',
  'Месячный план КД по лидам/продажам/выручке и менеджерам. Питает блок план/факт (Факт/План на дату/% плана). Заменяет ручную сборку плана из Google-таблицы.'),
 ('dm_kd_cohort_conversion','Частично есть (модель в PBI)',1,'Кирилл / DE',
  'marts._32_lead_info + marts._33_opportunities (ca_change_date)',
  'пересобрать',
  'Когортная преобразованность лидов нарастающим итогом по дням дозревания (через 0/1/2/.../>7 дней). Дашборд «Квалификация и преобразование лида по каналам КД» уже есть - перенести логику из PBI в витрину.'),
 ('dm_kd_calls_status','Остаётся в PBI поверх dialer',2,'Кирилл',
  'marts._38_calls + marts._45_asterisk_call (статусы/подстатусы звонков)',
  'BI-сторона',
  'Статусы и подстатусы звонков АО (КЦ Продаж БИЗ). Операционка телефонии, считается на стороне BI поверх dialer - в DWH КД не переносим.'),
 ('dm_kd_retention','Нужна, не делалась',2,'DE',
  'marts._23_sale + событие продления (аналог int_sales_base ИБ/АУТ)',
  'пересобрать',
  'Удержание КД: churn, % переподписки, Upsell в АУТ (шт/руб = клиенты ИБ→АУТ и сумма их оплат), Upsell Сбербанк (WL), LTV = ARPU × LT (срок жизни), Gross margin. Сейчас метрик нет (GAP) - требуется событийная витрина продлений, как в эталоне v58.'),
]

# ============== ЛИСТ 3: CTE ==============
CTE_RULES = """-- Бизнес-правила сборки воронки КД (аналог листа CTE в ИБ метрики v58)
-- ВСЁ собирается ВНУТРИ moedelo_marts (как эталон строит из _23_sale), а не из сырых owox/dialer/crm.
-- Проверено на marts (май 2026): Лиды КД 9116, преобразовано (ca_status) 4639, дозвон (talk>0) 8744, продажи нов. тариф 103.
--
-- 1. ЛИД КД. marts._32_lead_info (зеркало owox lead_info), is_deleted = 0.
--    Лид КД: lead_gen_responsible ∈ (N'Коммерческая дирекция',N'Коммерческая дирекция.Проект')
--            AND direction ∈ (N'КЦ',N'МД 2',N'Freemium'). Кириллица матчится на varchar/CP1251.
--    ВНИМАНИЕ (GAP): «Альфа-бандл» в marts колонкой НЕ хранится (PBI calc-column). До переноса в DWH
--    исключение бандла из «Лиды КД» не воспроизводится - нужно вынести правило бандла в источник/витрину.
-- 2. ТИП ЛИДА (срез) - SWITCH по lead_gen_responsible + direction (+ Альфа-бандл, см. GAP п.1):
--    Маркетинг*/Не распределено → 'Лиды маркетинга'; КД + {КЦ,МД2,Freemium} → 'Лиды КД';
--    КД + direction 'WL' → 'WL'; lead_gen_responsible ∈ ('КД 2.0','КД 3.0') → 'C проектов КД'; иначе 'С прочих'.
-- 3. ФАКТ-ЛИДЫ (база дозвона/конверсии). registration_product (raw в marts) ∈ ('BIZ','IB-ACC','IB-BIZ') → ИБ,
--    ('OUT','OUT-ACC','OUT-BIZ') → Аут. «Должен быть отгружен в АО» = is_loaded (из extra_data/_33). Проверено: ИБ=IB-ACC, Аут=OUT-ACC.
-- 4. ДОЗВОН. Прокси из marts._33_opportunities на уровне фирмы: max_call_talk_duration_seconds > 0
--    (или call_attempt_count > 0 / was_contact = 1). Детальный дозвон по статусам - marts._38_calls.disposition
--    ∈ ('DROP','ANSWER','ABANDON','FAST_DROP'), но в _38_calls нет firm_id (мост lead_external_id→firm).
-- 5. КВАЛИФИКАЦИЯ (преобразование). marts._33_opportunities.ca_status = 1 (валовое);
--    мес-в-мес: МЕСЯЦ(ca_change_date) = МЕСЯЦ(user_registration_date). JOIN o.md_firm_id_c = li.firm_id, o.deleted=0.
-- 6. ПОДКАТЕГОРИЯ БРАКА - из marts._33_opportunities: decline_reason / reason_by_decline / decline_case_c + satisfaction_c (эмоц.):
--    'Брак лида - недозвон', 'Брак лида - не давал согласия', 'Не целевой - ОПФ'.
-- 7. ПРОДАЖА. marts._23_sale → JOIN к лиду по firm_id. PayType = 'Новый' (operator_department='КЦ Продаж БИЗ').
--    is_one_time=1 → разовая; is_option по tariff_name (NOT LIKE '%опция%' → тариф); тариф = is_reselling=0 AND is_one_time=0 AND is_option=0.
-- 8. ВЫРУЧКА = payment_sum (реально оплачено = full_sum − скидки), НЕ full_sum (прейскурант).
-- 9. ДВЕ ДАТЫ. «По дате лида» - продажа агрегируется на месяц регистрации лида (когорта).
--    «По дате оплаты» - на payment_date (ALL(dimCalendar[Date]) в DAX).
-- 10. РАСХОД (CostMarketing, вне marts). УТОЧНЕНО жёлтой пометкой «Описание метрик_1»:
--     переменные для CPL/CPO = КВ партнёра (комиссионное вознаграждение) + Сертификаты (БЕЗ прочих и БЕЗ ФОТ).
--     CPL = (КВ+серт)/лиды; CPLq = CPL/%квал; CPO = (КВ+серт)/продажи (без ФОТ и прочих); CAC = ВСЕ расходы/продажи.
--     Правка относительно текущего DAX: там CPL = {Комиссия,Прочие}/лиды, CPO = {ФОТ,Комиссия,Прочие}/продажи.
-- 11. СКИДКИ (3 канала, спека Кирилла, см. эталон int_sales_base v58): discount_manager / discount_friend / discount_loyalty,
--     % = Скидка (Общая) ÷ номинальная стоимость из реального периода. Исключаются Бюро/возвраты/рассрочки/переходы."""

CTE_SQL_TITLE = "Полная сборка ядра воронки dm_kd_funnel (по дате лида):"
CTE_SQL = """DROP TABLE IF EXISTS dm_kd_funnel;

WITH leads AS (                         -- лиды КД с типом и продуктом (источник marts._32_lead_info)
  SELECT l.firm_id,
         l.lead_date,
         l.source_channel_group, l.source_channel,
         l.product,
         l.lead_type,                             -- из dim_lead_type (SWITCH)
         l.is_fact_lead,                          -- ИБ/Аут И «загружен в АО»
         l.is_called,                             -- есть звонок CallsAC (DROP/ANSWER/ABANDON/FAST_DROP)
         l.is_converted_gross,                    -- преобразован валово
         l.is_converted_mom                       -- преобразован мес-в-мес
  FROM int_leads_base l
  WHERE l.lead_type = N'Лиды КД'
), pays AS (                            -- ОПТИМИЗАЦИЯ: предагрегируем продажи до (firm_id, год, месяц) - убирает fan-out
  SELECT s.firm_id,                     -- (1 лид × N платежей превращался в N строк; теперь 1 строка на фирму-месяц)
         YEAR(s.payment_date)  AS pay_year,
         MONTH(s.payment_date) AS pay_month,
         MAX(CASE WHEN s.is_one_time = 0 AND s.is_option = 0 THEN 1 ELSE 0 END)            AS has_tariff,
         SUM(CASE WHEN s.is_one_time = 0 AND s.is_option = 0 THEN s.payment_sum ELSE 0 END) AS tariff_sum
  FROM int_sales_base_kd s
  WHERE s.pay_type = N'Новый' AND s.is_deleted = 0
  GROUP BY s.firm_id, YEAR(s.payment_date), MONTH(s.payment_date)
), cost AS (                            -- расходы КД по месяцу/направлению (CostMarketing). Жёлтая правка: var_cost = КВ + сертификаты.
  SELECT month, direction,
         SUM(CASE WHEN cost_item IN (N'КВ партнёра', N'Сертификаты') THEN value ELSE 0 END) AS var_cost,  -- для CPL и CPO
         SUM(CASE WHEN cost_item = N'ФОТ КД' THEN value ELSE 0 END)                          AS fot_kd,
         SUM(value)                                                                          AS cost_total -- для CAC (все статьи)
  FROM dim_kd_cost GROUP BY month, direction
)
SELECT
  ld.lead_date,
  ld.source_channel_group                                          AS channel_group,
  ld.source_channel                                                AS channel,
  ld.product,
  COUNT(DISTINCT ld.firm_id)                                       AS leads,
  COUNT(DISTINCT CASE WHEN ld.is_fact_lead = 1 THEN ld.firm_id END)        AS fact_leads_ao,
  COUNT(DISTINCT CASE WHEN ld.is_called = 1 THEN ld.firm_id END)           AS reached,         -- дозвон
  COUNT(DISTINCT CASE WHEN ld.is_converted_mom = 1 THEN ld.firm_id END)    AS qleads_mom,
  COUNT(DISTINCT CASE WHEN pa.has_tariff = 1 THEN ld.firm_id END)          AS sales_tariff_by_lead,
  SUM(pa.tariff_sum)                                                       AS revenue_tariff_by_lead
FROM leads ld
-- join по фирме И месяцу регистрации = месяц оплаты (продажа «по дате лида»); pays уже без дублей
LEFT JOIN pays pa ON pa.firm_id = ld.firm_id
                 AND pa.pay_year  = YEAR(ld.lead_date)
                 AND pa.pay_month = MONTH(ld.lead_date)
GROUP BY ld.lead_date, ld.source_channel_group, ld.source_channel, ld.product;
-- Экономика (CPL, CPLq, CPO, CAC) и конверсии считаются как расчётные поля на агрегате (см. лист «Витрины и таблицы»).
-- ОПТИМИЗАЦИЯ: month-match вынесен в условие JOIN (раньше был в CASE по фан-аут таблице) - меньше промежуточных строк."""

# ============== ЛИСТ 4: Витрины и таблицы ==============
# Каждая витрина: dict с title, table, sql, fields[(поле,описание,комментарий,пример,ключ,sql)]
VITRINY = [
 {'title':'Витрина 1. Ядро лидов КД: firm_id × дата регистрации с типом лида, флагами дозвона, квалификации и брака.',
  'table':'Таблица: int_leads_base  [расчётная (owox + dialer + crm)]',
  'sql':"""DROP TABLE IF EXISTS int_leads_base;

-- Источники - moedelo_marts (как эталон строит из _23_sale). Проверено на marts, май 2026.
WITH base AS (   -- лиды из marts._32_lead_info (зеркало owox lead_info)
  SELECT li.firm_id,
         CAST(li.user_registration_date AS date)  AS lead_date,
         li.registration_product,                 -- raw: IB-ACC / OUT-ACC / UU / SPS / WL-*
         li.direction, li.lead_gen_responsible,
         li.source_channel_group, li.source_channel,
         li.partner_id, li.sale_stage, li.crm_refuse_reason
  FROM _32_lead_info li
  WHERE li.is_deleted = 0
), typed AS (    -- тип лида + продукт-категория + флаг факт-лида
  SELECT b.*,
    CASE
      WHEN b.lead_gen_responsible IN (N'Маркетинг',N'Маркетинг. Пригласи друга',N'Не распределено') THEN N'Лиды маркетинга'
      WHEN b.lead_gen_responsible IN (N'Коммерческая дирекция',N'Коммерческая дирекция.Проект')
           AND b.direction IN (N'КЦ',N'МД 2',N'Freemium')                                          THEN N'Лиды КД'
      WHEN b.lead_gen_responsible IN (N'Коммерческая дирекция',N'Коммерческая дирекция.Проект')
           AND b.direction = N'WL'                                                                  THEN N'WL'
      WHEN b.lead_gen_responsible IN (N'КД 2.0',N'КД 3.0')                                          THEN N'C проектов КД'
      ELSE N'С прочих источников'
    END                                                              AS lead_type,
    CASE WHEN b.registration_product IN ('BIZ','IB-ACC','IB-BIZ') THEN N'ИБ'
         WHEN b.registration_product IN ('OUT','OUT-ACC','OUT-BIZ') THEN N'Аут'
         ELSE N'Прочее' END                                         AS product
  FROM base b
), opp AS (      -- преобразование/дозвон/брак из marts._33_opportunities (агрегат по фирме)
  SELECT o.md_firm_id_c                                            AS firm_id,
         MAX(CASE WHEN o.ca_status = 1 THEN 1 ELSE 0 END)          AS is_converted_gross,
         MAX(CASE WHEN o.ca_status = 1
                   AND DATEDIFF(MONTH, o.registration_date_c, o.ca_change_date) = 0
                  THEN 1 ELSE 0 END)                               AS is_converted_mom,
         MAX(CASE WHEN o.max_call_talk_duration_seconds > 0 OR o.was_contact = 1
                  THEN 1 ELSE 0 END)                               AS is_called,   -- дозвон-прокси (talk>0)
         MAX(ISNULL(o.decline_reason, o.reason_by_decline))        AS lead_subcategory
  FROM _33_opportunities o
  WHERE o.deleted = 0
  GROUP BY o.md_firm_id_c
)
SELECT t.*,
       CASE WHEN t.product IN (N'ИБ',N'Аут') THEN 1 ELSE 0 END AS is_fact_lead,  -- + признак загрузки в АО
       ISNULL(op.is_called,0)            AS is_called,
       ISNULL(op.is_converted_gross,0)   AS is_converted_gross,
       ISNULL(op.is_converted_mom,0)     AS is_converted_mom,
       op.lead_subcategory
INTO int_leads_base
FROM typed t
LEFT JOIN opp op ON op.firm_id = t.firm_id;
-- GAP: «Альфа-бандл» (исключение из Лиды КД) - PBI calc-column, в marts нет. Дозвон по статусам
-- (DROP/ANSWER/ABANDON/FAST_DROP) - через marts._38_calls (мост lead_external_id→firm), пока прокси из _33.""",
  'fields':[
   ('firm_id','ид фирмы','_32_lead_info.firm_id = _33_opportunities.md_firm_id_c','1070037','PK','firm_id'),
   ('lead_date','дата регистрации лида','CAST(user_registration_date AS date)','2026-06-01','PK','user_registration_date'),
   ('lead_type','тип лида','РАСЧЁТНОЕ - SWITCH (Лиды КД / маркетинга / WL / C проектов КД / С прочих). GAP: без Альфа-бандла','Лиды КД','','CASE ... END'),
   ('product','категория продукта','РАСЧЁТНОЕ - ИБ (IB-ACC/IB-BIZ/BIZ) / Аут (OUT-*) / Прочее','ИБ','','CASE registration_product'),
   ('source_channel_group','группа канала','raw _32_lead_info.source_channel_group','КЦ','','source_channel_group'),
   ('source_channel','канал','raw _32_lead_info.source_channel','Входящий','','source_channel'),
   ('partner_id','ид партнёра','raw _32_lead_info.partner_id','—','FK','partner_id'),
   ('is_fact_lead','факт-лид (ИБ/Аут, в АО)','РАСЧЁТНОЕ - продукт ИБ/Аут (+ признак загрузки в АО)','1','','CASE WHEN product IN (ИБ,Аут)'),
   ('is_called','дозвон','РАСЧЁТНОЕ - _33_opportunities.max_call_talk_duration_seconds>0 OR was_contact=1','1','','MAX(CASE WHEN talk>0 OR was_contact=1)'),
   ('is_converted_gross','преобразован валово','РАСЧЁТНОЕ - _33_opportunities.ca_status=1','1','','MAX(CASE WHEN ca_status=1)'),
   ('is_converted_mom','преобразован мес-в-мес','РАСЧЁТНОЕ - ca_status=1 И месяц(ca_change_date)=месяц(регистрации)','1','','DATEDIFF(MONTH,reg,ca_change_date)=0'),
   ('lead_subcategory','подкатегория брака','РАСЧЁТНОЕ - _33_opportunities.decline_reason / reason_by_decline','Недозвон','','ISNULL(decline_reason,reason_by_decline)'),
  ]},
 {'title':'Витрина 2. Сквозная воронка КД: лиды→дозвон→квалификация→продажи→выручка с экономикой. Ядро.',
  'table':'Таблица: dm_kd_funnel  [расчётная (int_leads_base + int_sales_base_kd + dim_kd_cost)]',
  'sql':"См. полный SQL на листе «CTE». Грануляция: дата лида × канал × продукт. Экономика (CPL/CPLq/CPO/CAC) и конверсии - расчётные поля на агрегате.",
  'fields':[
   ('lead_date','дата лида','день регистрации лида (когорта продажи по дате лида)','2026-06-01','PK','lead_date'),
   ('channel_group','группа канала','raw int_leads_base.source_channel_group','КЦ','PK','source_channel_group'),
   ('channel','канал','raw int_leads_base.source_channel','Входящий','PK','source_channel'),
   ('product','продукт','raw int_leads_base.product','ИБ','PK','product'),
   ('leads','лиды КД','COUNT(DISTINCT firm_id) где lead_type=Лиды КД','1649','','COUNT(DISTINCT firm_id)'),
   ('fact_leads_ao','факт-лиды (ИБ/Аут в АО)','COUNT(DISTINCT firm_id) где is_fact_lead=1','1320','','COUNT(DISTINCT CASE WHEN is_fact_lead=1)'),
   ('reached','дозвон','COUNT(DISTINCT firm_id) где is_called=1','980','','COUNT(DISTINCT CASE WHEN is_called=1)'),
   ('reach_rate','% дозвона','РАСЧЁТНОЕ: reached / fact_leads_ao','0.74','','reached / NULLIF(fact_leads_ao,0)'),
   ('qleads_mom','квал-лиды (мес-в-мес)','COUNT(DISTINCT firm_id) где is_converted_mom=1','610','','COUNT(DISTINCT CASE WHEN is_converted_mom=1)'),
   ('qual_rate','% квалификации (мес-в-мес)','РАСЧЁТНОЕ: qleads_mom / leads','0.37','','qleads_mom / NULLIF(leads,0)'),
   ('sales_tariff_by_lead','продажи тарифы (по дате лида)','оплаты-тарифы в месяц регистрации лида','140','','COUNT(DISTINCT CASE WHEN sale_type=тариф AND месяц совпал)'),
   ('revenue_tariff_by_lead','выручка тарифы (по дате лида)','SUM payment_sum тарифов в месяц лида','9446061','','SUM(CASE WHEN sale_type=тариф AND месяц совпал)'),
   ('conv_by_lead','конверсия по дате лида','РАСЧЁТНОЕ: sales_tariff_by_lead / leads','0.085','','sales_tariff_by_lead / NULLIF(leads,0)'),
   ('cpl','CPL (расч.)','РАСЧЁТНОЕ: (КВ+сертификаты) / лиды. Жёлтая правка - без прочих расходов','620','','var_cost / NULLIF(leads,0)'),
   ('cplq','CPLq (расч.)','РАСЧЁТНОЕ: CPL / % квалификации','1680','','cpl / NULLIF(qual_rate,0)'),
   ('cpo','CPO (расч.)','РАСЧЁТНОЕ: (КВ+сертификаты) / продажи. Жёлтая правка - без ФОТ и прочих','7300','','var_cost / NULLIF(sales,0)'),
   ('cac','CAC (расч.)','РАСЧЁТНОЕ: ВСЕ расходы / продажи','9100','','cost_total / NULLIF(sales,0)'),
  ]},
 {'title':'Витрина 3. База платежей КД: продукт, тип оплаты, опции/разовые, скидки по 3 каналам, реальный период.',
  'table':'Таблица: int_sales_base_kd  [расчётная (marts._23_sale + дисконты как в int_sales_base v58)]',
  'sql':"""DROP TABLE IF EXISTS int_sales_base_kd;
-- Источник - marts._23_sale (та же таблица, что и эталон ИБ v58). Фильтры как в источнике Sales дашборда:
--   payment_method NOT IN ('freemium','oneTime_tech','granted for partner','DeloBank','rnkbpay','tech_pay','profbuh'),
--   is_deleted = 0. Блок дисконтов (discount_manager/friend/loyalty, real_full_sum) переиспользуется
--   1:1 из эталона int_sales_base v58 (лист «CTE» файла ИБ метрики v58). Проверено на marts (май 2026): 103 нов. тарифа / 3,12 млн ₽.
SELECT
  s.firm_id, s.payment_id, s.position_number,
  s.payment_date, s.start_date, s.end_date,
  s.product_group,
  CASE WHEN s.product_group IN ('BIZ','IB-ACC','IB-BIZ') THEN N'ИБ'
       WHEN s.product_group IN ('OUT','OUT-ACC','OUT-BIZ') THEN N'Аут'
       WHEN s.product_group = 'SPS' THEN N'Бюро' ELSE N'Прочее' END        AS product,
  CASE WHEN s.tariff_name LIKE N'%опция%' THEN 1 ELSE 0 END                AS is_option,
  s.is_one_time, s.is_reselling, s.is_deleted,
  CASE WHEN s.operator_department = N'КЦ Продаж БИЗ' THEN N'Новый'
       WHEN s.has_prev_paid_subscription = 1 OR s.operator_department = N'Сопровождение УУ' THEN N'Продление'
       ELSE N'Новый' END                                                  AS pay_type,
  s.payment_sum, s.full_sum, s.normative_period,
  s.regional_partner_name, s.manager, s.operator_department,
  s.loyalty_program_month, s.friendinvite_discount, s.promo_code
INTO int_sales_base_kd
FROM _23_sale s
WHERE s.is_deleted = 0
  AND s.payment_method NOT IN ('freemium','oneTime_tech','granted for partner','DeloBank','rnkbpay','tech_pay','profbuh');""",
  'fields':[
   ('firm_id','ид фирмы','FK на лид (int_leads_base.firm_id)','1070037','PK','firm_id'),
   ('payment_id','ид платежа','raw _23_sale','16284347','PK','payment_id'),
   ('position_number','позиция в платеже','raw','1','PK','position_number'),
   ('payment_date','дата оплаты','payment_date::date','2026-06-06','','payment_date'),
   ('product','категория продукта','РАСЧЁТНОЕ - ИБ/Аут/Бюро/Прочее','ИБ','','CASE product_group'),
   ('is_option','опция (1) / тариф (0)','РАСЧЁТНОЕ - tariff_name LIKE %опция%','0','','CASE WHEN tariff_name LIKE %опция%'),
   ('is_one_time','разовая услуга','raw (с поправками на УУ-внедрение и консультации)','0','','is_one_time'),
   ('pay_type','тип оплаты','РАСЧЁТНОЕ - Новый / Продление по operator_department','Новый','','CASE operator_department'),
   ('payment_sum','сумма оплаты, руб','raw (реально оплачено)','6270','','payment_sum'),
   ('full_sum','номинальная сумма, руб','raw (прейскурант)','8000','','full_sum'),
   ('regional_partner_name','партнёр','raw - для разреза по партнёрам','Мой бизнес','FK','regional_partner_name'),
   ('discount_total','общая скидка, руб','РАСЧЁТНОЕ - 3 канала (менеджер+друг+лояльность), логика int_sales_base v58','1243','','disc.manager+friend+loyalty'),
   ('real_full_sum','номинал из реального периода, руб','РАСЧЁТНОЕ - база для % скидки (как в v58)','8704','','full_sum/normative_period*real_months'),
  ]},
 {'title':'Витрина 4. Расходы КД: статья × месяц × направление. Питает CPL, CPLq, CPO, CAC.',
  'table':'Таблица: dim_kd_cost  [справочник (выгрузка файла расходов CostMarketing)]',
  'sql':"""DROP TABLE IF EXISTS dim_kd_cost;
-- Источник: CostMarketing (Google Sheet / файл xls с расходами КД).
-- Статьи (жёлтая правка «Описание метрик_1»): КВ партнёра + Сертификаты = переменные (CPL/CPO); ФОТ КД и Прочие - отдельно (только в CAC).
SELECT
  date_trunc('month', period)::date AS month,
  direction,
  cost_item,                              -- 'КВ партнёра' / 'Сертификаты' / 'ФОТ КД' / 'Прочие расходы'
  SUM(value) AS value
INTO dim_kd_cost
FROM stg_kd_cost
GROUP BY date_trunc('month', period)::date, direction, cost_item;""",
  'fields':[
   ('month','месяц','date_trunc(month, period)','2026-06-01','PK','date_trunc(month,period)'),
   ('direction','направление КД','raw','КЦ','PK','direction'),
   ('cost_item','статья расходов','КВ партнёра (комиссионное вознагр.) / Сертификаты / ФОТ КД / Прочие расходы','КВ партнёра','PK','cost_item'),
   ('value','сумма, руб','SUM(value)','450000','','SUM(value)'),
   ('var_cost','переменные (расч.)','РАСЧЁТНОЕ: КВ партнёра + Сертификаты (для CPL и CPO). Жёлтая правка - без прочих и ФОТ','520000','','SUM CASE IN (КВ,Сертификаты)'),
   ('fot_kd','ФОТ КД (расч.)','РАСЧЁТНОЕ: статья = ФОТ КД (только в CAC)','1200000','','SUM CASE = ФОТ КД'),
   ('cost_total','все расходы (расч.)','РАСЧЁТНОЕ: SUM(value) всех статей - для CAC','1900000','','SUM(value)'),
  ]},
 {'title':'Витрина 5. Выставленные счета КД: шт и руб по дате счёта/лида, разрез по партнёрам.',
  'table':'Таблица: dm_kd_invoices  [расчётная (marts._33_opportunities.invoice_date + dim_partner)]',
  'sql':"""DROP TABLE IF EXISTS dm_kd_invoices;
-- Факт выставления счёта по фирме - marts._33_opportunities.invoice_date (проверено: 122 фирмы КД с invoice_date за май 2026).
-- Сумма счёта и разрез по партнёру: marts._55_payment_history_ex (BillNumber/BillDate, но БЕЗ firm_id/суммы)
-- ИЛИ кастомный запрос InvoicePayment к moedelo (mssql02, PaymentHistory) - в нём есть PaymentSum и партнёр.
-- GAP: marts-native суммы счёта по фирме нет, нужен JOIN _55 ↔ _23_sale по PrimaryPaymentId либо запрос к moedelo.
SELECT
  CAST(o.invoice_date AS date)               AS invoice_date,
  CAST(li.user_registration_date AS date)    AS lead_date,
  s.regional_partner_name                    AS partner_name,
  COUNT(DISTINCT o.md_firm_id_c)             AS invoices_cnt
INTO dm_kd_invoices
FROM _33_opportunities o
JOIN _32_lead_info li ON li.firm_id = o.md_firm_id_c
LEFT JOIN _23_sale s ON s.firm_id = o.md_firm_id_c
WHERE o.deleted = 0 AND o.invoice_date IS NOT NULL
GROUP BY CAST(o.invoice_date AS date), CAST(li.user_registration_date AS date), s.regional_partner_name;""",
  'fields':[
   ('invoice_date','дата счёта','CAST(_33_opportunities.invoice_date AS date)','2026-06-03','PK','invoice_date'),
   ('lead_date','дата лида','_32_lead_info.user_registration_date (альтернативная привязка к календарю)','2026-06-01','PK','user_registration_date'),
   ('partner_name','партнёр','_23_sale.regional_partner_name / dim_partner','Мой бизнес','PK','regional_partner_name'),
   ('invoices_cnt','счетов (фирм), шт','COUNT(DISTINCT md_firm_id_c) с invoice_date','122','','COUNT(DISTINCT md_firm_id_c)'),
   ('invoices_sum','счетов, руб','GAP: суммы в marts нет на уровне фирмы - из moedelo InvoicePayment (PaymentSum)','4800000','','SUM(PaymentSum) - moedelo'),
  ]},
 {'title':'Витрина 6. Когортная преобразованность лидов КД нарастающим итогом по дням дозревания.',
  'table':'Таблица: dm_kd_cohort_conversion  [расчётная (когорта лида × день преобразования)]',
  'sql':"""DROP TABLE IF EXISTS dm_kd_cohort_conversion;
-- Дашборд «Квалификация и преобразование лида по каналам КД»: преобразование через 0/1/2/.../>7 дней.
WITH leads AS (
  SELECT firm_id, lead_date, source_channel_group, product
  FROM int_leads_base WHERE lead_type = N'Лиды КД'
), conv AS (
  SELECT md_firm_id_c AS firm_id, CAST(MIN(ca_change_date) AS date) AS conv_date
  FROM _33_opportunities WHERE deleted = 0 AND ca_status = 1
  GROUP BY md_firm_id_c
)
SELECT
  l.lead_date, l.source_channel_group, l.product,
  COUNT(DISTINCT l.firm_id)                                                          AS leads_in_cohort,
  COUNT(DISTINCT CASE WHEN DATEDIFF(DAY, l.lead_date, c.conv_date) = 0 THEN l.firm_id END)         AS conv_d0,
  COUNT(DISTINCT CASE WHEN DATEDIFF(DAY, l.lead_date, c.conv_date) BETWEEN 1 AND 7 THEN l.firm_id END) AS conv_d1_7,
  COUNT(DISTINCT CASE WHEN DATEDIFF(DAY, l.lead_date, c.conv_date) > 7 THEN l.firm_id END)         AS conv_d7plus,
  CAST(COUNT(DISTINCT CASE WHEN c.conv_date IS NOT NULL THEN l.firm_id END) AS float)
    / NULLIF(COUNT(DISTINCT l.firm_id),0)                                            AS conv_rate_cum
INTO dm_kd_cohort_conversion
FROM leads l LEFT JOIN conv c ON c.firm_id = l.firm_id
GROUP BY l.lead_date, l.source_channel_group, l.product;""",
  'fields':[
   ('lead_date','дата (когорта) лида','день регистрации','2026-06-01','PK','lead_date'),
   ('source_channel_group','группа канала','raw','КЦ','PK','source_channel_group'),
   ('product','продукт','raw','ИБ','PK','product'),
   ('leads_in_cohort','лидов в когорте','COUNT(DISTINCT firm_id)','1500','','COUNT(DISTINCT firm_id)'),
   ('conv_d0','преобразовано в день 0','distinct лидов с conv в день регистрации','420','','COUNT(DISTINCT CASE conv-lead=0)'),
   ('conv_d1_7','преобразовано за 1-7 дней','distinct лидов с conv 1..7 дн','310','','COUNT(DISTINCT CASE 1..7)'),
   ('conv_d7plus','преобразовано позже 7 дней','distinct лидов с conv >7 дн','90','','COUNT(DISTINCT CASE >7)'),
   ('conv_rate_cum','преобразованность накопит., %','РАСЧЁТНОЕ: все преобразованные / лиды когорты','0.55','','converted / NULLIF(leads,0)'),
  ]},
 {'title':'Витрина 7. План КД на месяц: лиды/продажи/выручка по метрике и менеджеру. Питает блок план/факт.',
  'table':'Таблица: plan_kd_monthly  [справочник (Google Sheet «Планы pbi»)]',
  'sql':"""DROP TABLE IF EXISTS plan_kd_monthly;
-- Источник: Plans (Google Sheet, опубликованный xlsx). Месячный план по метрикам и менеджерам.
SELECT
  plan_month::date AS month,
  metric,                                 -- лиды / продажи / выручка
  manager_group,
  manager,
  plan_value
INTO plan_kd_monthly
FROM stg_kd_plans;""",
  'fields':[
   ('month','месяц плана','plan_month::date','2026-06-01','PK','plan_month'),
   ('metric','метрика','лиды / продажи / выручка','выручка','PK','metric'),
   ('manager_group','группа менеджеров','raw plan_manager_group','КЦ Продаж БИЗ','PK','manager_group'),
   ('manager','менеджер (ФИО)','raw','Иванов И.','','manager'),
   ('plan_value','план на месяц','raw','12000000','','plan_value'),
   ('plan_to_date','план на дату (расч.)','РАСЧЁТНОЕ: plan_value / дней в месяце × прошедших дней','7200000','','plan_value/days_in_month*days_passed'),
  ]},
]

# ============== ЛИСТ 5: ТЗ для разработки ==============
# (#, задача, ответственный, витрина есть?, что построить, какие метрики, источник)
TZ = [
 (1,'Ядро int_leads_base','DE','Нет',
  'Витрина лидов КД из marts: _32_lead_info (лид) + _33_opportunities (преобразование ca_status, дозвон-прокси, брак) + _38_calls (дозвон по статусам). Тип лида - SWITCH (Лиды КД / маркетинга / WL / проекты / прочее).',
  'Лиды КД, Тип лида, Факт-лиды в АО, Дозвон, % дозвона, Квал-лиды, брак',
  'marts: _32_lead_info + _38_calls + _33_opportunities. Связь по md_firm_id_c = firm_id.'),
 (2,'Ядро dm_kd_funnel','DE','Нет',
  'Сквозная витрина воронки КД: дата лида × канал × продукт - лиды→дозвон→квал→продажи→выручка + экономика (CPL/CPLq/CPO/CAC) в одной грануляции.',
  'Вся воронка КД + конверсии + юнит-экономика',
  'int_leads_base + int_sales_base_kd + dim_kd_cost. Сводит «Сквозную отчётность» в одну витрину.'),
 (3,'База платежей int_sales_base_kd','DE','Источник есть (Sales в PBI), витрины нет',
  'Витрина платежей КД на sales_report_row с расчётом типа оплаты, опций/разовых и блока скидок (3 канала). Переиспользовать логику дисконтов и реального периода из эталона int_sales_base v58.',
  'Продажи/Выручка тарифы и итого, Средний чек, ARPU, Скидки',
  'marts._23_sale + спека дисконтов Кирилла (как в ИБ v58).'),
 (4,'Витрина расходов dim_kd_cost','DE + КД','Нет',
  'dim_kd_cost из файла расходов CostMarketing: статья (КВ партнёра / Сертификаты / ФОТ КД / Прочие) × месяц × направление. Жёлтая правка: переменные для CPL/CPO = КВ + сертификаты (без прочих и ФОТ); ФОТ и прочие - только в CAC. Уточнить у КД состав статьи «Сертификаты».',
  'Переменные расходы (КВ+серт), ФОТ КД, CPL, CPLq, CPO, CAC',
  'CostMarketing (Google Sheet / xls). Получить актуальный файл расходов и состав статей у руководителя КД.'),
 (5,'Дедупликация мер воронки','DE / Аналитик','Частично (меры есть в дашбордах)',
  'Свести дубли мер «Сквозной отчётности» (две версии «по дате лида»/«по дате оплаты», WL-копии) к базовым с time-intelligence. Единые [Лиды КД]/[Продажи]/[Выручка]/[Конверсия].',
  'Единые меры воронки вместо десятков копий',
  'Корень расхождений цифр между листами отчёта.'),
 (6,'Когортная преобразованность','Кирилл / DE','Частично (модель в PBI)',
  'dm_kd_cohort_conversion: преобразование лидов нарастающим итогом по дням (0/1-7/>7 дн). Перенести логику дашборда «Квалификация и преобразование лида по каналам КД» из PBI в витрину.',
  'Преобразованность накопленная %, преобразование через N дней',
  'marts._32_lead_info + marts._33_opportunities (ca_change_date).'),
 (7,'Счета и партнёры','DE','Нет',
  'dm_kd_invoices (InvoicePayment) + dim_partner (regional_partner_name). Счета шт/руб по дате счёта и дате лида, ARPU и выручка в разрезе партнёров (Партнёр Мой бизнес).',
  'Выставленные счета шт/руб, счета и ARPU по партнёрам',
  'marts._55_payment_history_ex / _33_opportunities.invoice_date + marts._23_sale.regional_partner_name.'),
 (8,'План КД','DE + КД','Нет',
  'plan_kd_monthly: месячный план по лидам/продажам/выручке и менеджерам для расчёта Факт/План на дату и % плана. Заменяет ручную сборку из Google-таблицы.',
  'Факт на дату, План на дату, % выполнения плана',
  'Plans (Google Sheet «Планы pbi»). План у руководителя КД.'),
 (9,'Событийная витрина удержания','DE','Нет (GAP)',
  'dm_kd_retention: построить событие продления для клиентов КД (аналог int_sales_base ИБ/АУТ v58) для расчёта churn, % переподписки, Upsell в АУТ/Сбербанк, LTV. Сейчас этих метрик нет.',
  'Churn, % переподписки, Upsell АУТ, Upsell Сбербанк (WL), LTV, Gross margin',
  'marts._23_sale + LEAD по платежам (логика prolong_success v58).'),
 (10,'Статусы звонков АО','Кирилл','Остаётся в PBI',
  'Уточнить словарь статусов/подстатусов звонков dialer для дашборда «Статусы и подстатусы звонков». Считается на стороне BI поверх dialer - в DWH КД не переносим.',
  'Статусы и подстатусы звонков, % дозвона по операторам',
  'marts._38_calls + marts._45_asterisk_call. Документация по статусам колл-центра.'),
]

# ============== ЛИСТ 6: Реестр дашбордов ==============
# (dashboard, engine, folder, used, purpose, key_metrics, sources, impl)
DASH = [
 ('Сквозная отчётность','Power BI','Сквозная отчётность','Да',
  'Главный сквозной отчёт КД: воронка лиды→дозвон→квал→продажи→выручка (листы «исходник лиды»/«исходник продажи»), конверсия источников, динамика дня КЦ, партнёры, оплаченные месяцы, спец. тарифы, воронка по лидам, когорты «счёт на оплату»',
  'Лиды КД, Дозвон, % дозвона, Квал-лиды, Продажи, Выручка, Конверсия, ARPU, Средний чек, План/Факт',
  'marts (_32_lead_info, _23_sale, _38_calls, _33_opportunities, _55_payment_history_ex), Plans, CostMarketing',
  'пересобрать'),
 ('Расшифровка по каналам КД','Power BI','Сквозная отчётность','Да',
  'Детализация воронки КД в разрезе каналов и направлений лидогенерации',
  'Лиды КД, преобразование, продажи, выручка по каналам',
  'marts._32_lead_info + marts._23_sale',
  'авто в DWH'),
 ('Квалификация и преобразование лида по каналам КД','Power BI','Сквозная отчётность','Да',
  'Когортная преобразованность лидов КД нарастающим итогом по дням (0/1/2/.../>7 дн) в разрезе каналов',
  'Факт-лиды, Преобразовано через N дней (шт/%), преобразованность накопленная',
  'marts._32_lead_info + marts._33_opportunities',
  'пересобрать'),
 ('Партнёр Мой бизнес','Power BI','КД','Да',
  'Отчётность по партнёру «Мой бизнес»: лиды, продажи, выручка, счета',
  'Лиды, продажи, выручка, выставленные счета по партнёру',
  'marts._23_sale (regional_partner_name) + marts._55_payment_history_ex',
  'пересобрать'),
 ('Отчётность КЦ Продаж БИЗ - Статусы и подстатусы звонков','Power BI','Отчётность КЦ Продаж БИЗ','Да',
  'Статусы и подстатусы звонков колл-центра продаж БИЗ',
  'Статусы/подстатусы звонков, % дозвона, попытки',
  'marts._38_calls + marts._33_opportunities',
  'BI-сторона'),
 ('Отчёты продаж 2.0 - Общая конверсия','Power BI','Отчётность КЦ Продаж БИЗ','Да',
  'Общая конверсия продаж КЦ Продаж БИЗ',
  'Лиды, продажи, общая конверсия',
  'marts._23_sale + marts._32_lead_info',
  'авто в DWH'),
 ('Отчёты продаж 2.1 - Общая конверсия ООП','Power BI','Отчётность КЦ Продаж БИЗ','Да',
  'Общая конверсия отдела online-продаж (ООП)',
  'Лиды, продажи, конверсия ООП',
  'marts._23_sale + marts._32_lead_info',
  'авто в DWH'),
 ('Отчётность WL - Upsell Сбербанк','Power BI','Главная','Да',
  'Апсейл по WL-направлению Сбербанк',
  'Upsell Сбербанк (руб/шт), WL-продажи',
  'marts._23_sale (WL)',
  'пересобрать'),
]

# ============== ЛИСТ 7: Топ-10 дашбордов ==============
# (rank, dashboard, use, value, ready, score, why, metrics, vitrины, action)
TOP10 = [
 (1,'Сквозная отчётность',3,3,2,8,
  'Главный сквозной отчёт КД лиды→продажи; листы «исходник лиды»/«исходник продажи» - прямая основа ядра воронки. Максимум использования и ценности.',
  'Лиды КД, дозвон, квал, продажи, выручка, конверсия, план/факт','dm_kd_funnel + int_leads_base','пересобрать'),
 (2,'Квалификация и преобразование лида по каналам КД',3,3,3,9,
  'Когортная преобразованность по дням - ключевой отчёт качества лидов КД; модель в PBI уже готова, логику легко перенести в витрину.',
  'Преобразованность накопленная %, через N дней','dm_kd_cohort_conversion','пересобрать'),
 (3,'Расшифровка по каналам КД',3,3,2,8,
  'Воронка КД в разрезе каналов лидогенерации - основа для оценки эффективности каналов КД.',
  'Лиды, преобразование, продажи, выручка по каналам','dm_kd_funnel + dim_lead_type','авто в DWH'),
 (4,'Отчёты продаж 2.0 - Общая конверсия',3,3,2,8,
  'Общая конверсия КЦ Продаж БИЗ - операционный отчёт продаж, ядро конверсионной воронки.',
  'Лиды, продажи, общая конверсия','dm_kd_funnel','авто в DWH'),
 (5,'Партнёр Мой бизнес',2,3,2,7,
  'Партнёрское направление: лиды/продажи/выручка/счета по партнёру. Ценен для оценки партнёрского канала.',
  'Лиды, продажи, выручка, счета по партнёру','dm_kd_invoices + dim_partner','пересобрать'),
 (6,'Отчёты продаж 2.1 - Общая конверсия ООП',2,2,2,6,
  'Конверсия отдела online-продаж - смежная конверсионная воронка КД.',
  'Лиды, продажи, конверсия ООП','dm_kd_funnel','авто в DWH'),
 (7,'Отчётность WL - Upsell Сбербанк',2,2,2,6,
  'Апсейл по WL Сбербанк - отдельное направление выручки КД.',
  'Upsell Сбербанк руб/шт','dm_kd_retention','пересобрать'),
 (8,'Отчётность КЦ Продаж БИЗ - Статусы и подстатусы звонков',2,2,2,6,
  'Статусы звонков колл-центра - операционка телефонии. Остаётся в PBI поверх dialer.',
  'Статусы/подстатусы звонков, % дозвона','dm_kd_calls_status','оставить в PBI'),
 (9,'Когорты счёт на оплату (Сквозная отчётность)',2,2,2,6,
  'Когорты по выставленным счетам - конверсия счёта в оплату. Часть «Сквозной отчётности».',
  'Выставленные счета, конверсия счёт→оплата','dm_kd_invoices','пересобрать'),
 (10,'Динамика показателей - счета и ARPU по партнёрам',2,2,2,6,
  'Выставленные счета и ARPU в разрезе партнёров. Питается счетами и продажами по партнёру.',
  'Счета по партнёрам, ARPU по партнёрам','dm_kd_invoices + dim_partner','пересобрать'),
]
TOP10_NOTE = ('Не вошли в топ-10: служебные и узкие листы «Сквозной отчётности» (Спец. тарифы, Оплаченные месяцы, '
  'Конверсия источников, Воронка по лидам) - они срезы ядра воронки и закрываются витриной dm_kd_funnel.')

# ============== Эталон-конформность: частоты обновления (Roadmap) и вопросы к DE (Витрины) ==============
# Частота обновления по эталону ИБ v58: (Желаемая, Мин. допустимая, Инкрементальное обновление)
REFRESH = {
 'int_leads_base':          ('Раз в час', 'Раз в сутки', 'Да - инкремент по lead_date'),
 'dm_kd_funnel':            ('Раз в сутки', 'Раз в сутки', 'Да - инкремент по lead_date'),
 'int_sales_base_kd':       ('Раз в час', 'Раз в сутки', 'Да - инкремент по payment_date'),
 'dim_date':                ('Раз в год', 'Раз в год', 'Нет - статика'),
 'dim_lead_type':           ('Раз в неделю', 'Раз в месяц', 'Нет - full refresh (справочник)'),
 'dim_kd_cost':             ('Раз в сутки', 'Раз в неделю', 'Нет - full refresh (файл расходов)'),
 'dm_kd_invoices':          ('Раз в сутки', 'Раз в сутки', 'Да - инкремент по invoice_date'),
 'dim_partner':             ('Раз в неделю', 'Раз в месяц', 'Нет - full refresh (справочник)'),
 'plan_kd_monthly':         ('Раз в сутки', 'Раз в неделю', 'Нет - full refresh (план из Google Sheet)'),
 'dm_kd_cohort_conversion': ('Раз в сутки (ночью)', 'Раз в неделю', 'Нет - full refresh (когорта × день)'),
 'dm_kd_calls_status':      ('-', '-', '-'),
 'dm_kd_retention':         ('Раз в сутки', 'Раз в неделю', 'Да - инкремент по событию продления'),
}

# Открытые вопросы к DE по полям витрин (колонка «вопросы» эталона). Ключ: имя витрины → {поле: вопрос}
QUESTIONS = {
 'int_leads_base': {
   'lead_type': '«Альфа-бандл» в marts нет (PBI calc-column) - где зафиксировать правило исключения бандла из «Лиды КД»?',
   'is_called': 'Дозвон по статусам (DROP/ANSWER/ABANDON/FAST_DROP) - нужен мост _38_calls.lead_external_id → firm_id; пока прокси talk>0.',
   'is_converted_mom': 'Мес-в-мес считать по DATEDIFF(MONTH, registration_date_c, ca_change_date)=0 - подтвердить с КД.',
 },
 'int_sales_base_kd': {
   'discount_total': 'Воспроизвести блок дисконтов Кирилла (3 канала) на продажах КД, как в int_sales_base v58?',
   'pay_type': 'Полный перечень operator_department для «Продление» (кроме КЦ Продаж БИЗ) - сверить с КД.',
 },
 'dm_kd_invoices': {
   'invoices_sum': 'Сумма счёта по фирме: в marts на уровне фирмы нет - брать из moedelo InvoicePayment (PaymentSum) или JOIN _55 ↔ _23 по PrimaryPaymentId?',
 },
 'dim_kd_cost': {
   'cost_item': 'Состав статьи «Сертификаты» (ЭЦП или подарочные клиентам)? Точные названия статей сверить с файлом расходов КД.',
 },
 'dm_kd_cohort_conversion': {
   'conv_d0': 'Дозревание по дням считать от ca_change_date? Сверить раскладку 0/1-7/>7 дн с дашбордом «через N дней».',
 },
}
