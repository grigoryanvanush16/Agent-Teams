---
description: Conventions для Power BI проектов «Моё дело» — TMDL, DAX, relationships, source SQL.
paths:
  - "**/*.tmdl"
  - "**/*.pbip"
  - "**/Dashboard.SemanticModel/**"
  - "**/renewals-powerbi/**"
---

# Power BI Conventions

## Формат проектов

PBIP (Power BI Project) — `.tmdl` файлы под VCS. Структура:

```
{Dashboard}.SemanticModel/definition/
├── model.tmdl              ← настройки модели, datasource
├── relationships.tmdl      ← связи между таблицами
├── tables/
│   ├── fact_*.tmdl
│   ├── dim_*.tmdl
│   └── _Measures.tmdl      ← все DAX меры
└── cultures/
    └── ru-RU.tmdl
```

## Star schema

- Один факт = один бизнес-процесс
- `fact_*` всегда связан с `dim_date` через MonthKey или DateKey
- Тип relationship: many-to-one (fact → dim)
- Cross-filter: single direction по умолчанию, both directions только при необходимости

## DAX правила

```dax
// DIVIDE с защитой от деления на 0
Доля = DIVIDE([Числитель], [Знаменатель], 0)

// ALLEXCEPT — сохранить фильтры только по указанным
Метрика по тарифу =
CALCULATE([Базовая метрика],
  ALLEXCEPT(dim_tariff, dim_tariff[tariff_group])
)

// Running total — корректный pattern
Накопительно =
CALCULATE([Метрика],
  FILTER(ALL(dim_date[MonthKey]),
    dim_date[MonthKey] <= MAX(dim_date[MonthKey])
  )
)
```

## Форматирование мер

```
measure 'Название меры' =
    DIVIDE([числитель], [знаменатель], 0)
    formatString: "#,##0.00"
    displayFolder: "Группа мер"
    description: "Описание для пользователя"
```

## UUID для relationships

Никогда не угадывать — генерировать через Python:
```bash
python -c "import uuid; print(uuid.uuid4())"
```

## Источники данных

Основной — MSSQL `172.16.172.102:1433/moedelo`. SQL прячется в `partition` блоке таблицы:
```
partition <name> = m
    mode: import
    source = let
        Source = Sql.Database("server", "db"),
        Query = Value.NativeQuery(Source, "SELECT ...")
    in Query
```

## Перед изменениями

1. Бэкап `relationships.tmdl` → `relationships.tmdl.bak`
2. Проверка SQL через `tools/mssql_query.py` (для renewals-powerbi)
3. После правки `.tmdl` — открыть `.pbip` в Desktop и обновить данные

## Проект renewals-powerbi

Путь: `C:\Users\User\Projects\renewals-powerbi\`
SQL утилиты: `tools/mssql_query.py`, `tools/mssql_query.ps1`
