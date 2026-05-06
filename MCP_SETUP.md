# MCP Setup Guide

Инструкции по установке топ-MCP под профиль (DWH + аналитика + жизнь).

## Что уже работает

| MCP | Назначение | Статус |
|-----|-----------|--------|
| youtrack | Задачи в YouTrack | ⚠️ нужен токен |
| yandex-mail | Яндекс.Почта | ✅ |
| telegram | Telegram | ✅ |
| context7 | Свежая документация | ✅ |
| coingecko | Курсы крипты | ✅ |
| yahoo-finance | Котировки акций | ✅ |
| fns-ofd | Парсинг ФНС-чеков (свой) | ⚠️ нужен FNS_API_KEY или PROVERKACHEKA_TOKEN |
| tinkoff-personal | Тинькофф банк+инвест (свой) | ✅ для CSV, нужен TINKOFF_INVEST_TOKEN для портфеля |
| anki | Карточки Anki | ⚠️ требует запущенный Anki + AnkiConnect |
| obsidian | Заметки в Obsidian | ⚠️ нужно настроить путь к vault |
| apple-health | Apple Health данные | ⚠️ нужен экспорт из iOS |
| icloud | Календарь+контакты iCloud | ⚠️ нужен Apple ID + app password |

## Категория 1: Аналитика (DWH/data work)

### CoinGecko (без credentials, public API) — 🟢 ставить сразу
```bash
claude mcp add coingecko -- npx -y @coingecko/coingecko-mcp
```

### Yahoo Finance — 🟢 ставить сразу
```bash
claude mcp add yahoo-finance -- uvx yahoo-finance-mcp
```

### Hugging Face MCP — нужен HF_TOKEN
1. Получить токен: https://huggingface.co/settings/tokens
2. Добавить в `.env`: `HF_TOKEN=hf_...`
3. ```bash
   claude mcp add huggingface -- npx -y @huggingface/mcp-server
   ```

### Jupyter MCP — нужен запущенный jupyter
```bash
pip install jupyter jupyter-mcp-server
jupyter lab --no-browser --port 8888  # в отдельном терминале
claude mcp add jupyter -- npx -y @datalayer/jupyter-mcp-server
```

### Qdrant MCP — нужен Qdrant instance (Docker)
```bash
docker run -d -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
claude mcp add qdrant -- npx -y @qdrant/mcp-server
```

### Yandex Metrika MCP — нужен Yandex OAuth токен
1. https://oauth.yandex.ru/client/new — создать приложение, scope: `metrika:read`
2. Получить токен через OAuth flow
3. `.env`: `YANDEX_METRIKA_TOKEN=...`
4. ```bash
   claude mcp add yandex-metrika -- npx -y @atomkraft/yandex-metrika-mcp
   ```

### FNS Check MCP — нужен API key
1. Регистрация: https://api-fns.ru
2. Получить API key (free tier)
3. `.env`: `FNS_API_KEY=...`
4. ```bash
   claude mcp add fns-check -- uvx fns-check-mcp
   ```

### Context7 (свежая документация) — 🟢 ставить сразу, без credentials
```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

---

## Категория 2: Базы данных под DWH

### PostgreSQL Pro (Crystal DBA) — 7 БД
```bash
# Создать read-only пользователя в каждой БД:
# CREATE USER claude_reader WITH PASSWORD '...';
# GRANT CONNECT ON DATABASE backoffice_Reports TO claude_reader;
# GRANT USAGE ON SCHEMA public TO claude_reader;
# GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_reader;

claude mcp add postgres-backoffice -- uvx postgres-mcp \
  --access-mode=restricted \
  "postgresql://claude_reader:PWD@172.16.172.216:6432/backoffice_Reports"
```

Повторить для: owox, dialer, mindbox, billing, mdtech (отдельный сервер на каждый).

### Microsoft SQL MCP — для moedelo + PBIRS
```bash
# Через docker compose с Data API Builder
git clone https://github.com/Azure/data-api-builder
# Настроить config.json с подключением к 172.16.172.102:1433
docker run -e DAB_CONFIG=... mcr.microsoft.com/azure-databases/data-api-builder
```

### MySQL MCP — для crm_prod, asteriskcdrdb
```bash
claude mcp add mysql-crm -- npx -y @benborla/mcp-server-mysql \
  --host=172.16.172.199 --port=3306 --database=crm_prod \
  --user=power_bi --password=PWD
```

---

## Категория 3: dbt + Power BI

### dbt MCP (official Labs)
```bash
claude mcp add dbt -- uvx dbt-mcp \
  --project-dir "C:/Users/User/Desktop/МД/4.DWH_Production"
```

### Power BI Modeling MCP (Microsoft official)
```bash
git clone https://github.com/microsoft/powerbi-modeling-mcp
cd powerbi-modeling-mcp
# follow README
claude mcp add powerbi-modeling -- python C:/Users/User/Projects/powerbi-modeling-mcp/server.py
```

### Altimate (data engineering skills, не MCP)
```bash
/plugin marketplace add AltimateAI/data-engineering-skills
/plugin install dbt-skills@data-engineering-skills
```

---

## Категория 4: Web-разработка

### shadcn/ui MCP — без credentials
```bash
claude mcp add shadcn-ui -- npx -y @shadcn/ui-mcp
```

### Lighthouse MCP — без credentials
```bash
claude mcp add lighthouse -- npx -y lighthouse-mcp
```

### Vercel MCP — нужен OAuth (через UI)
1. https://vercel.com/account/tokens
2. `.env`: `VERCEL_TOKEN=...`
3. ```bash
   claude mcp add vercel -- npx -y @vercel/mcp
   ```

### Supabase MCP — нужен service_role key
1. Supabase project → Settings → API → service_role key
2. `.env`: `SUPABASE_URL=...`, `SUPABASE_SERVICE_KEY=...`
3. ```bash
   claude mcp add supabase -- npx -y @supabase/mcp-server
   ```

### Figma MCP — нужен Personal Access Token
1. Figma → Settings → Account → Personal Access Tokens
2. `.env`: `FIGMA_PAT=...`
3. ```bash
   claude mcp add figma -- npx -y @figma/mcp-server
   ```

---

## Категория 5: Финансы и инвестиции

### T-Invest MCP (Tinkoff) — нужен токен
1. https://www.tbank.ru/invest/settings/api/ → Sandbox или Production
2. `.env`: `TINKOFF_TOKEN=...`
3. ```bash
   git clone https://github.com/Sprytin/tinkoff-investments-mcp-server
   pip install -r requirements.txt
   claude mcp add tinkoff -- python C:/Users/User/Projects/tinkoff-mcp/server.py
   ```

### Glassnode MCP (бесплатный пока в beta)
```bash
claude mcp add glassnode -- npx -y @glassnode/mcp
```

---

## Категория 6: Жизнь

### Apple Health MCP — нужен экспорт из iOS
1. iOS app: Health → профиль → Export All Health Data
2. Скачать `export.zip`, распаковать
3. ```bash
   claude mcp add apple-health -- npx -y @neiltron/apple-health-mcp \
     --data-path "C:/Users/User/Documents/AppleHealth/export.xml"
   ```

### Aviasales MCP — нужен партнёрский токен
1. https://www.travelpayouts.com/ — регистрация
2. `.env`: `AVIASALES_TOKEN=...`
3. ```bash
   claude mcp add aviasales -- npx -y @aviasales/mcp
   ```

### Anki MCP — нужен Anki app + AnkiConnect плагин
1. Установить Anki: https://apps.ankiweb.net/
2. В Anki: Tools → Add-ons → Get Add-ons → 2055492159 (AnkiConnect)
3. ```bash
   claude mcp add anki -- npx -y anki-mcp-server
   ```

### Obsidian MCP — нужен vault path
1. Если Obsidian не установлен: https://obsidian.md/
2. `.env`: `OBSIDIAN_VAULT=C:/Users/User/Documents/Obsidian-Vault`
3. ```bash
   claude mcp add obsidian -- npx -y obsidian-mcp
   ```

### iCloud MCP (CalDAV/CardDAV) — нужен app password
1. https://appleid.apple.com/ → Sign-In and Security → App-Specific Passwords
2. `.env`: `ICLOUD_USER=...@icloud.com`, `ICLOUD_APP_PASSWORD=...`
3. ```bash
   claude mcp add icloud -- npx -y icloud-mcp-server
   ```

### Home Assistant MCP — нужен HA instance + token
1. Home Assistant → Profile → Long-Lived Access Tokens
2. `.env`: `HA_URL=http://homeassistant.local:8123`, `HA_TOKEN=...`
3. ```bash
   claude mcp add home-assistant -- npx -y @ha/mcp-server
   ```

### Last.fm MCP — нужен API key
1. https://www.last.fm/api/account/create
2. `.env`: `LASTFM_API_KEY=...`
3. ```bash
   claude mcp add lastfm -- npx -y lastfm-mcp
   ```

---

## Чек-лист перед установкой каждого MCP

1. ✅ Из официального registry или vendor-репо?
2. ✅ Read-only режим где возможно?
3. ✅ Credentials через env, не в `.mcp.json`?
4. ✅ Не превышаем 12-15 активных MCP?

## Топ-приоритет (если ставить только что-то одно)

🥇 **CoinGecko** — для трекинга крипты, public API, ставится за 30 секунд
🥈 **Context7** — против hallucinated APIs в любом коде
🥉 **dbt MCP** — критично для DWH-проекта

---

## Что добавлено 2026-05-06

### Anki MCP
Работает, если запущен Anki Desktop + установлен плагин AnkiConnect.

**Установка плагина:**
1. Открой Anki → Tools → Add-ons → Get Add-ons
2. Введи код: `2055492159`
3. Перезапусти Anki

После этого Anki MCP подцепится автоматически (URL по умолчанию `http://localhost:8765`).

### Obsidian MCP
Если у тебя нет vault — установи Obsidian (https://obsidian.md/), создай vault в `C:/Users/User/Documents/Obsidian-Vault` (или поменяй путь в `.mcp.json`).

Если vault в другом месте — обнови `OBSIDIAN_VAULT_PATH` в `.mcp.json`.

### Apple Health MCP
Нужен экспорт данных из iOS:
1. iPhone → Health → профиль → **Export All Health Data**
2. Скинь архив на ПК, распакуй
3. Положи `export.xml` в `C:/Users/User/Documents/AppleHealth/export.xml`
4. Обновляй раз в месяц

### iCloud MCP
1. https://appleid.apple.com/ → Sign-In and Security → **App-Specific Passwords**
2. Создай пароль для «Claude Code MCP»
3. Заполни в `.mcp.json`:
   ```json
   "icloud": {
     "env": {
       "ICLOUD_USERNAME": "your_email@icloud.com",
       "ICLOUD_APP_PASSWORD": "xxxx-xxxx-xxxx-xxxx"
     }
   }
   ```

### Что не нашлось на npm

Эти MCP не в публичном npm-реестре. Альтернативы:

- **Aviasales MCP** — нет публичного. Альтернатива: вызывать Travelpayouts API через WebFetch + свой Python-скрипт. Стоит ли своя обёртка — обсудим
- **Last.fm MCP** — нет публичного. Альтернатива: свой MCP через scrobbler API (~50 строк кода)
- **Hugging Face MCP** — теперь это **hosted server**, конфиг другой. Доступ через https://huggingface.co/mcp

---

## Антирекомендации (не ставить)

- `auchenberg/claude-code-mcp` — рекурсия Claude
- Любой MCP с публичного HTTP без auth (CVE-2026-26118)
- `github/github-mcp-server` — `gh` CLI быстрее в 2-4 раза
- Trade-MCP (Bybit/OKX/Tinkoff) с правом сделок — только read-only
