# Design: Power BI Dashboard «Продления АУТ»

**Дата:** 2026-04-14
**Автор:** Вануш
**Источник данных:** `moedelo_marts` на `172.16.172.111:1433` (MSSQL)
**Статус:** Design approved, готов к плану реализации

---

## 1. Цели и контекст

Построить интерактивный Power BI дашборд поверх витрины `moedelo_marts`, который заменит ручной Excel-процесс «Продление_отчет_*.xlsx» и даст трём ролям (руководитель продления АУТ, продуктовый менеджер модуля Cost, финансовый аналитик) единый источник правды по метрикам продления, точности автовыставления и декомпозиции выручки.

**Предпосылки:**
- В `_43_bill_cost_forecast` и `_43_bill_cost_forecast_request` уже есть 156 703 Completed-расчёта по 4 типам стоимости (Base, Cost1, Cost2, Cost3) за 18 месяцев.
- В `_23_sale` есть факты продлений OUT-ACC (~210k за тот же период).
- Excel-форма «Итог_оформлено» доказала, что декомпозиция на 8 эффектов работает на когорту фев 2026 (`Продление_форма_фев2026_v6.xlsx`).

**Цели:**
1. Единый источник метрик продления АУТ, обновляемый ежедневно.
2. Сравнение прогноза автобиллинга (Cost3) с фактом продления — для продуктовой команды.
3. Операционное управление продлением: менеджеры, отстающие когорты, апселл/даунселл — для руководителя.
4. Декомпозиция прироста по 8 эффектам (индексация, переход, скидка, обороты, апселл, сроки, сотрудники, даунселл) — для финансов.

---

## 2. Роли и страницы

### Страница 1: Обзор (для всех)

Заглавная страница, верхнеуровневые KPI и навигация.

**Элементы:**
- **KPI-карточки (5):** Клиентов в когорте, Продлившихся (шт + %), Выручка факт (млн), Cost3 прогноз (млн), Прирост vs старый тариф (млн + %)
- **Линейный график:** динамика продлений по месяцам (количество + сумма на второй оси)
- **Heat map:** когорта × месяц продления — показывает, когда клиенты каждой когорты реально продлеваются (для понимания опережающего/запаздывающего поведения)
- **Навигация** на 3 ролевые страницы (кнопки)

### Страница 2: Руководитель продления АУТ

**Элементы:**
- **Топ-N менеджеров** (горизонтальная столбчатая): сумма продлений в млн, с percentile-меткой «выше/ниже медианы команды»
- **Структура выручки по тарифам** (donut): Полный / Частичный / Зарплата / Нулевая / Спец — сумма и доля
- **Воронка:** Клиенты когорты → Подлежат продлению → Продлились → Продлились в срок → С апселлом
- **Таблица «отстающие когорты»:** когорта, клиенты, продлившихся %, средний срок задержки, топ-причина
- **Drill-down:** клик на менеджера/тариф/когорту фильтрует остальные визуалы на странице

### Страница 3: Продуктовый менеджер (Cost 1–4)

**Элементы:**
- **Scatter plot:** ось X = Cost3 прогноз, ось Y = Факт (full_sum); trend-линия y=x; точки окрашены по когорте
- **Гистограмма расхождения:** `(Cost3 − Факт) / Факт × 100%`, сегменты {<−20%, −20…−5%, −5…+5%, +5…+20%, >+20%}
- **Точность автобиллинга по когортам:** линия `% клиентов с |Cost3−Факт|<5%` по месяцам, целевая линия 80%
- **Таблица «риски автовыставления»:** клиенты с превышением лимита оборота/сотрудников, Cost2, Cost3, факт, ΔCost3–Факт — отсортировано по |Δ| DESC
- **Разложение Cost3 → Base + индексация + обороты + сотрудники + опции:** stacked bar по когортам

### Страница 4: Финансовый аналитик

Точная реплика Excel-формы «Итог_оформлено» + дополнения.

**Элементы:**
- **Матрица 1:** Когорта × Месяц продления (строки = 11 метрик: клиенты, %, старые тарифы, 8 эффектов, итого)
- **Матрица 2:** Продления АУТ (факт) × Биллинг-месяц (3 строки: общее, в других месяцах, в отчётном, %)
- **Матрица 3:** Фин. показатели продлений клиентов из всех когорт (те же 8 эффектов + даунселл по месяцам продления)
- **Waterfall:** декомпозиция «Старый тариф → +индексация → +переход → +обороты → ... → Итого Факт»
- **Multi-line chart:** 8 эффектов во времени (12 месяцев)
- **Drill-through:** клик на ячейку матрицы → раскрытие до клиентов

---

## 3. Data Model (Star Schema)

### Факты

**`fact_cost_forecast`** — один расчёт bill_cost_forecast на строку (pivoted по type)

Источник: `_43_bill_cost_forecast_request` + `_43_bill_cost_forecast` (pivoted)

Поля:
```
request_id (PK), firm_id, calculation_date_key, end_date_key,
configuration_code, product_code, status,
money_turnover_limit, employee_number_limit, cost_indexation,
base_full, base_base, base_turnover, base_option, base_employee, base_duration, base_monthly,
cost1_full, cost1_base, cost1_turnover, cost1_option, cost1_employee, cost1_duration,
cost2_full, cost2_base, cost2_turnover, cost2_option, cost2_employee, cost2_duration,
actual_money_turnover, actual_employee_number,
cost3_full, cost3_base, cost3_turnover, cost3_option, cost3_employee, cost3_duration,
exceeded_turnover_flag, exceeded_employees_flag
```

**`fact_renewals`** — факт продления OUT-ACC

Источник: `_23_sale` с фильтром `product_group = 'OUT-ACC' AND has_prev_paid_subscription = 1`

Поля:
```
payment_id (PK), firm_id, payment_date_key, renew_date_key (= cohort),
start_date_key, end_date_key,
tariff_name, prev_tariff_name, normative_period,
full_sum, payment_sum, sum_discount, month_discount,
has_autorenewal, payment_method, payment_partner_type, is_reselling,
manager_key, seller_key, cohort_month_key,
is_upsell_flag, is_downsell_flag, tariff_changed_flag
```

### Измерения

- **`dim_date`** — календарь (2025-02-01 .. 2027-12-31), year/quarter/month/month_name/is_report_month_flag
- **`dim_firm`** — уникальные клиенты: client_login, inn, opf, okved, firm_name, reg_date
- **`dim_manager`** — менеджеры: manager_fio, operator_department, operator_group, seller_login
- **`dim_tariff`** — классификация тарифов по названию:
  - Группа: Полный АУТ / Частичный АУТ / Зарплата и кадры / Нулевая отчётность / Специальный / Прочее
  - Размер клиента (по `money_turnover_limit`): ЧА (0) / Малый (<1 млн) / Средний (1–5 млн) / Большой (>5 млн)
- **`dim_configuration`** — `configuration_code` → читаемое название
- **`dim_cohort`** — когорты (месяцы с 2025-02 по +12 месяцев вперёд), для удобной фильтрации

### Связи

```
fact_cost_forecast[firm_id]              → dim_firm[firm_id]
fact_cost_forecast[end_date_key]         → dim_date[date_key]       (cohort)
fact_cost_forecast[calculation_date_key] → dim_date[date_key]       (для calc_date)
fact_cost_forecast[configuration_code]   → dim_configuration
fact_renewals[firm_id]                    → dim_firm[firm_id]
fact_renewals[payment_date_key]           → dim_date[date_key]       (когда продлился)
fact_renewals[renew_date_key]             → dim_date[date_key]       (cohort)
fact_renewals[manager_key]                → dim_manager
fact_renewals[cohort_month_key]           → dim_cohort
```

Две фактовые таблицы связаны через `dim_firm[firm_id]` — это позволяет считать матчинг Cost-прогноза с фактом продления (для Страницы 3).

---

## 4. Подключение и обновление

**Режим: Import Mode** (не DirectQuery)

Обоснование: объём данных (~400k строк факт + ~50k измерений) комфортно помещается в модель Power BI, запросы работают быстро, все DAX-функции доступны. DirectQuery нужен только для real-time сценариев, которых у нас нет.

**Источник:** MSSQL `moedelo_marts` на `172.16.172.111:1433`, учётка `dev / dev123` (внутренняя сеть MoeDelo).

**Gateway:** On-premises Data Gateway (standard) для доступа из Power BI Service к внутреннему серверу. Устанавливается на машину с постоянным доступом к `172.16.172.111`.

**Расписание обновления:**
- Ежедневно в **06:00 МСК**
- Ретенция: последние 24 месяца + весь будущий горизонт прогноза (~12 мес вперёд)
- Инкрементальное обновление: последние 90 дней каждый день, полный пересчёт раз в неделю (воскресенье)

**Power Query (M):** отдельный запрос на каждую fact/dim таблицу, с параметрами `StartDate` и `EndDate` для ретенции.

---

## 5. Ключевые DAX меры

### Базовые (7)

```dax
Клиентов в когорте =
    DISTINCTCOUNT(fact_cost_forecast[firm_id])

Продлившихся =
    CALCULATE(DISTINCTCOUNT(fact_renewals[firm_id]),
              NOT ISBLANK(fact_renewals[payment_date_key]))

Процент продлений =
    DIVIDE([Продлившихся], [Клиентов в когорте])

Выручка факт, млн =
    DIVIDE(SUM(fact_renewals[full_sum]), 1000000)

Cost3 прогноз, млн =
    DIVIDE(SUM(fact_cost_forecast[cost3_full]), 1000000)

Сумма старых тарифов, млн =
    DIVIDE(SUM(fact_cost_forecast[base_full]), 1000000)

Прирост, млн =
    [Выручка факт, млн] - [Сумма старых тарифов, млн]
```

### 8 эффектов (композитные)

```dax
Эффект индексации, млн =
    DIVIDE(SUM(cost1_full) - SUM(base_full), 1000000)

Эффект оборотов, млн =
    DIVIDE(SUM(cost2_turnover) - SUM(cost1_turnover), 1000000)

Эффект опций, млн =
    DIVIDE(SUM(cost2_option) - SUM(cost1_option), 1000000)

Эффект сотрудников, млн =
    DIVIDE(SUM(cost2_employee) - SUM(cost1_employee), 1000000)

Эффект скидки, млн =
    DIVIDE(
        (SUM(full_sum) - SUM(norm_sum_new)) -
        (SUM(full_sum_prev) - SUM(norm_sum_prev)),
        1000000
    )

Эффект перехода на тарифы, млн =
    [Прирост, млн]
  - [Эффект индексации, млн] - [Эффект оборотов, млн]
  - [Эффект опций, млн] - [Эффект сотрудников, млн]
  - [Эффект скидки, млн] - [Эффект сроков, млн]

Эффект сроков, млн =
    DIVIDE(
        SUM(fact_cost_forecast[cost3_full])
      - SUM(fact_cost_forecast[cost1_full])
      - (SUM(cost2_turnover) - SUM(cost1_turnover))
      - (SUM(cost2_employee) - SUM(cost1_employee))
      - (SUM(cost2_option)   - SUM(cost1_option)),
        1000000
    )
    -- Логика: из полного изменения (Cost3 vs Cost1 = эффекты факт. использования)
    -- вычитаем уже известные эффекты оборотов/сотрудников/опций.
    -- Остаток = изменение базовой части + срока (приблизительно срок, т.к. база меняется редко)

Эффект даунселла, млн =
    CALCULATE([Прирост, млн], fact_renewals[is_downsell_flag] = 1)
```

### Точность автобиллинга (для Страницы 3)

```dax
Клиентов с точным Cost3 =
    CALCULATE(DISTINCTCOUNT(firm_id),
              FILTER(fact_cost_forecast,
                     ABS([Cost3 прогноз] - [Выручка факт]) / [Выручка факт] <= 0.05))

Точность Cost3, % =
    DIVIDE([Клиентов с точным Cost3], [Продлившихся])

Среднее отклонение Cost3-Факт, руб =
    AVERAGEX(SUMMARIZE(fact_cost_forecast, firm_id),
             [Cost3 прогноз, руб] - [Выручка факт, руб])
```

---

## 6. Визуальный стиль

- **Тема:** Corporate Light (MoeDelo brand if provided), fallback — Power BI default Light
- **Цветовая схема для Cost-типов:**
  - Base → серый (#D9D9D9)
  - Cost1 → зелёный (#E2EFDA)
  - Cost2 → голубой (#DEEBF7)
  - Cost3 → жёлтый (#FFF2CC)
- **Положительные эффекты** → зелёный; **негативные** → красный; **нейтральные** → серый
- **Фильтры** — в sidebar слева, сквозные (синхронизированы между страницами)

---

## 7. Фазы реализации

**Фаза 1: Data layer (2 дня)**
1. Создать Power Query запросы на 2 факта + 5 измерений
2. Настроить связи и типизацию
3. Валидация: сверить агрегаты с `Продление_форма_фев2026_v6.xlsx`

**Фаза 2: DAX меры (1 день)**
1. Написать 7 базовых + 8 эффектов + 3 Cost-точности = 18 мер
2. Проверить на одной когорте (фев 2026)

**Фаза 3: Страницы (3 дня)**
1. Страница 1: Обзор — KPI + heat map (0.5 дня)
2. Страница 2: Руководитель — 4 визуала + drill-through (1 день)
3. Страница 3: Продукт (Cost) — scatter + гистограмма + точность (1 день)
4. Страница 4: Фин. аналитик — 3 матрицы + waterfall (0.5 дня)

**Фаза 4: Публикация и Gateway (0.5 дня)**
1. Установка on-premises gateway
2. Публикация в Power BI Service
3. Настройка daily refresh 06:00
4. Выдача прав ролям (read-only для менеджеров, edit для аналитика)

**Итого: ~7 дней работы**

---

## 8. Риски и митигации

| Риск | Митигация |
|------|-----------|
| Gateway недоступен / падает | Fallback: ручной refresh из Power BI Desktop + публикация .pbix |
| В `_43_bill_cost_forecast` встречаются выбросы (cost_full > 10M) | Фильтр в Power Query: `cost_full <= 10000000` |
| `_23_sale.firm_id` не матчится с `_43_bill_cost_forecast.firm_id` для 35% (v5 показал 65%) | Принять как data gap; на Странице 3 показывать только matched-клиентов, отдельный visual «Firms without forecast» |
| Классификация тарифов по `tariff_name` ломается при новых тарифах | В `dim_tariff` — fallback-группа «Прочее», мониторинг раз в месяц |
| Ретенция 24 месяца может не хватить для трендов | Параметризовать, при необходимости расширить до 36 мес. |

---

## 9. Вне скопа (не делаем в этой фазе)

- Прогнозирование / ML на основе Cost2 — только отображение прогноза, не улучшение модели
- Интеграция с email/Slack для алертов
- Export в PowerPoint / PDF (стандартный Power BI export работает, custom экспорт не нужен)
- Мобильная вёрстка (смотрим только на десктопе/Web)
- Роли Row-Level Security — все три роли видят одни и те же данные

---

## Приложение A: SQL-запросы для Power Query

### fact_cost_forecast

```sql
WITH fc AS (
    SELECT f.*, ROW_NUMBER() OVER (
        PARTITION BY f.bill_cost_forecast_request_id, f.type
        ORDER BY f.full_cost DESC
    ) AS rn
    FROM dbo._43_bill_cost_forecast f
),
fc1 AS (SELECT * FROM fc WHERE rn = 1)
SELECT
    r.id AS request_id, r.firm_id,
    r.configuration_code, r.product_code, r.status,
    CAST(r.calculation_date AS DATE) AS calculation_date_key,
    r.end_date AS end_date_key,
    r.money_turnover_limit, r.employee_number_limit, r.cost_indexation,
    -- Base
    MAX(CASE WHEN f.type='Base'  THEN f.full_cost END) AS base_full,
    MAX(CASE WHEN f.type='Base'  THEN f.base_cost END) AS base_base,
    MAX(CASE WHEN f.type='Base'  THEN f.turnover_cost END) AS base_turnover,
    MAX(CASE WHEN f.type='Base'  THEN f.option_cost END) AS base_option,
    MAX(CASE WHEN f.type='Base'  THEN f.employee_cost END) AS base_employee,
    MAX(CASE WHEN f.type='Base'  THEN f.payment_duration END) AS base_duration,
    -- Cost1
    MAX(CASE WHEN f.type='Cost1' THEN f.full_cost END) AS cost1_full,
    MAX(CASE WHEN f.type='Cost1' THEN f.turnover_cost END) AS cost1_turnover,
    MAX(CASE WHEN f.type='Cost1' THEN f.option_cost END) AS cost1_option,
    MAX(CASE WHEN f.type='Cost1' THEN f.employee_cost END) AS cost1_employee,
    -- Cost2
    MAX(CASE WHEN f.type='Cost2' THEN f.full_cost END) AS cost2_full,
    MAX(CASE WHEN f.type='Cost2' THEN f.base_cost END) AS cost2_base,
    MAX(CASE WHEN f.type='Cost2' THEN f.turnover_cost END) AS cost2_turnover,
    MAX(CASE WHEN f.type='Cost2' THEN f.option_cost END) AS cost2_option,
    MAX(CASE WHEN f.type='Cost2' THEN f.employee_cost END) AS cost2_employee,
    MAX(CASE WHEN f.type='Cost2' THEN f.actual_money_turnover END) AS actual_money_turnover,
    MAX(CASE WHEN f.type='Cost2' THEN f.actual_employee_number END) AS actual_employee_number,
    -- Cost3
    MAX(CASE WHEN f.type='Cost3' THEN f.full_cost END) AS cost3_full,
    MAX(CASE WHEN f.type='Cost3' THEN f.base_cost END) AS cost3_base,
    MAX(CASE WHEN f.type='Cost3' THEN f.turnover_cost END) AS cost3_turnover,
    MAX(CASE WHEN f.type='Cost3' THEN f.option_cost END) AS cost3_option,
    MAX(CASE WHEN f.type='Cost3' THEN f.employee_cost END) AS cost3_employee,
    CASE WHEN MAX(CASE WHEN f.type='Cost2' THEN f.actual_money_turnover END) > r.money_turnover_limit
              AND r.money_turnover_limit > 0 THEN 1 ELSE 0 END AS exceeded_turnover_flag
FROM dbo._43_bill_cost_forecast_request r
INNER JOIN fc1 f ON r.id = f.bill_cost_forecast_request_id
WHERE r.status = 'Completed'
  AND r.calculation_date >= DATEADD(MONTH, -24, GETDATE())
GROUP BY r.id, r.firm_id, r.configuration_code, r.product_code, r.status,
         r.calculation_date, r.end_date, r.money_turnover_limit,
         r.employee_number_limit, r.cost_indexation
```

### fact_renewals

```sql
SELECT
    s.payment_id, s.firm_id,
    s.payment_date AS payment_date_key,
    s.renew_date AS renew_date_key,
    s.start_date AS start_date_key,
    s.end_date AS end_date_key,
    s.tariff_name, s.prev_tariff_name, s.normative_period,
    s.full_sum, s.payment_sum, s.sum_discount, s.month_discount,
    s.has_autorenewal, s.payment_method, s.payment_partner_type, s.is_reselling,
    s.manager, s.seller_fio, s.seller_login,
    s.operator_department, s.operator_group,
    FORMAT(s.renew_date, 'yyyy-MM') AS cohort_month_key
    -- ВАЖНО: флаги is_upsell_flag / is_downsell_flag вычисляются НЕ в SQL,
    -- а в DAX после join с fact_cost_forecast:
    --   is_upsell   = full_sum > base_full * 1.05 (с учётом 5% порога на индексацию)
    --   is_downsell = full_sum < base_full * 0.95
    -- Бизнес-правила нужно подтвердить с product owner модуля Cost.
FROM dbo._23_sale s
WHERE s.product_group = 'OUT-ACC'
  AND s.has_prev_paid_subscription = 1
  AND s.payment_date >= DATEADD(MONTH, -24, GETDATE())
  AND s.is_deleted = 0
```

---

**Reference files:**
- `C:\Users\User\Downloads\Продление_форма_фев2026_v6.xlsx` — рабочая Excel-форма (reference для валидации)
- `C:\Users\User\Downloads\build_form_final.py` — Python-скрипт с логикой агрегации (основа для DAX)
- `C:\Users\User\.claude\renewals\kpi_renewed\logic.md` — декодинг 29 метрик из DataLens
- `C:\Users\User\Desktop\МД\2.DWH\TZ\TZ_Moedelo_Inventory.md` — полный каталог таблиц MSSQL
