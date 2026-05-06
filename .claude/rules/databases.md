---
description: Карта баз данных компании «Моё дело» — хосты, порты, DBMS, логины. Применяется при работе с SQL, Python-скриптами подключения, dbt.
paths:
  - "**/*.sql"
  - "**/*.py"
  - "**/dbt_project.yml"
  - "**/profiles.yml"
  - "**/sources.yml"
---

# Базы данных «Моё дело»

10 источников данных. Креденшалы (полные пароли): `C:\Users\User\Downloads\Доступы (1) (1).xlsx`

## Источники

| # | Хост:порт | База | DBMS | Логин | Назначение |
|---|-----------|------|------|-------|-----------|
| 1 | 10.0.0.111:5432 | dialer | PostgreSQL | zinin | Колл-центр продаж |
| 2 | 10.0.0.59:3306 | asteriskcdrdb | MySQL | zinin | Телефония CDR |
| 3 | 172.16.172.102:1433 | moedelo | MSSQL | viewer | Основная БД продукта |
| 4 | 172.16.172.106:1433 | PBIRS | MSSQL | viewer | Power BI Report Server |
| 5 | 172.16.172.175:6432 | owox | PostgreSQL | dev | OWOX-аналитика, маркетинг |
| 6 | 172.16.172.199:3306 | crm_prod | MySQL | power_bi | CRM (сделки, лиды) |
| 7 | 172.16.172.216:6432 | backoffice_Reports | PostgreSQL | dev | Продажи, продления, клиенты |
| 8 | 172.16.172.216:6432 | mindbox | PostgreSQL | dev | Рассылки |
| 9 | 172.16.172.223:6432 | backofficeBilling_Bills | PostgreSQL | dev | Биллинг |
| 10 | 192.168.226.125 | mdtech | PostgreSQL | dev | Техподдержка |

## Группы отчётов по источникам

- **Сквозная отчётность** (6 отчётов) — owox, backoffice, crm_prod, moedelo
- **Отчётность КЦ Продаж** (3) — dialer, owox, backoffice, crm_prod
- **Отчётность Маркетинг** (4) — owox, crm_prod, mindbox, moedelo
- **Отчётность ССК** (5) — backoffice, asteriskcdrdb, crm_prod, mdtech
- **Продуктовые метрики** (3) — owox, backoffice
- **Отчётность WL** (2) — owox, moedelo, backoffice
- **Клиентская база** — owox, backoffice

## Шаблоны подключения (Python)

```python
import psycopg2, pymysql, pymssql

# PostgreSQL (backoffice, owox, dialer, mindbox, billing, mdtech)
conn = psycopg2.connect(host="172.16.172.216", port=6432,
                       dbname="backoffice_Reports", user="dev", password="...")

# MySQL (crm_prod, asteriskcdrdb)
conn = pymysql.connect(host="172.16.172.199", port=3306,
                      database="crm_prod", user="power_bi", password="...")

# MSSQL (moedelo, PBIRS)
conn = pymssql.connect(server="172.16.172.102", port=1433,
                      database="moedelo", user="viewer", password="...")
```

## Правила безопасности

- Никогда не хардкодить пароли — читать из xlsx или env
- Production-БД: только SELECT + sandbox схемы
- DROP / TRUNCATE / DELETE / UPDATE заблокированы в settings.json deny-листе
- При подозрительных операциях — спросить пользователя
