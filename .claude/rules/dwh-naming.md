---
description: Naming convention для DWH «Моё дело» — слои Raw/ODS/Star/Marts. Применяется при создании dbt-моделей, написании ТЗ, SQL DDL.
paths:
  - "**/models/**/*.sql"
  - "**/models/**/*.yml"
  - "**/dbt_project.yml"
  - "**/Desktop/МД/2.DWH/**"
  - "**/Desktop/МД/3.ТЗ_DWH/**"
  - "**/Desktop/МД/4.DWH_Production/**"
---

# DWH Naming Convention

Эталонный регистр имён: `C:\Users\User\Desktop\МД\2.DWH\TZ\T008_Names_Registry.md`

## Слои

```
L0 (Raw/Staging)    — as-is из источников
L1 (ODS)            — очистка, дедупликация, SCD2
L2 (Star Schema)    — факты + измерения по Kimball
L3 (Marts)          — бизнес-витрины для Power BI
```

## Префиксы и паттерны

```
L0: raw_{source}_{table}          — raw_crm_deals, raw_backoffice_payments
L1: ods_{source}_{entity}         — ods_crm_deals, ods_backoffice_clients
L2: fact_{process}                — fact_sales, fact_renewals, fact_payments
    dim_{entity}                  — dim_client, dim_tariff, dim_date
L3: mart_{domain}_{metric_group}  — mart_sales_daily, mart_renewals_cohort
```

## Источники в именах

| Источник | Префикс |
|----------|---------|
| backoffice_Reports | `backoffice` |
| crm_prod | `crm` |
| moedelo | `moedelo` |
| owox | `owox` |
| dialer | `dialer` |
| mindbox | `mindbox` |
| backofficeBilling_Bills | `billing` |

## dbt структура

```
models/
├── staging/          ← raw_*, ods_*
│   └── stg_{source}__{entity}s.sql
├── intermediate/     ← вспомогательные таблицы для marts
│   └── int_{purpose}.sql
└── marts/
    ├── core/         ← fact_*, dim_*
    └── {domain}/     ← mart_*
```

## Тесты dbt

Минимум для каждой модели:
- `unique` на PK
- `not_null` на обязательных
- `relationships` для FK
- `accepted_values` для статусов/категорий

## Валидация имён

Перед созданием новых имён — запустить:
```bash
python "C:/Users/User/Desktop/МД/0.AI_Hub/scripts/validate_naming.py" <имя1> <имя2> ...
```

## Правила DDL

- Все колонки snake_case
- Даты: `created_at`, `updated_at`, `valid_from`, `valid_to` (для SCD2)
- ID: `{entity}_id` (например, `client_id`, `deal_id`)
- Метрики в фактах: `_amount` для сумм, `_count` для количества, `_rate` для долей
- Описания таблиц обязательны в schema.yml
