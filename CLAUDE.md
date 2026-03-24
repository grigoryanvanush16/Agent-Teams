# Agent Teams — News Intelligence Pipeline

Мультиагентная система для мониторинга и анализа новостей из открытого интернета, с выводом в Google Sheets и PDF. Демо-проект, показывающий pipeline из 4 агентов с видимым взаимодействием в tmux.

## Обязательный режим запуска

Для этого проекта запуск `Agent Teams` через `tmux` обязателен.

- Не использовать `in-process` режим для основной демонстрации.
- Запускать lead-сессию Claude Code только внутри `tmux`.
- Все demo-сессии с агентами должны открываться в split-pane режиме.
- Если используется iTerm2, допустим запуск через `tmux -CC`.

Основание: официальная документация Claude Code по Agent Teams:

- https://code.claude.com/docs/en/agent-teams

Что важно из документации:

- `Agent Teams` являются экспериментальной функцией и требуют включения `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
- У команд есть lead и teammates, которые работают как отдельные Claude Code sessions.
- Teammates могут общаться друг с другом напрямую.
- Split-pane mode требует `tmux` или iTerm2.
- Если сессия уже запущена внутри `tmux`, Claude Code может использовать split panes для teammates.
- Каждый teammate загружает тот же проектный контекст, включая `CLAUDE.md`, skills и локальные настройки.

## Обязательные настройки проекта

- в `.claude/settings.json` должен быть включен `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- в `.claude/settings.json` должен быть установлен `teammateMode: "tmux"`

Если эти настройки отсутствуют или изменены, их нужно восстановить перед запуском demo.

## Назначение проекта

Pipeline из 4 агентов для мониторинга новостей из открытого интернета:

- `coordinator`: lead-агент, управляет pipeline и выдаёт финальный брифинг
- `scraper`: ищет новостные статьи через WebSearch + WebFetch, без внешних API
- `analyst`: оценивает релевантность, тональность, тренды, категоризирует по темам
- `reporter`: создаёт Google Sheet с графиками (Charts API) + PDF-отчёт

Роли агентов лежат в `.claude/agents/`.

## Pipeline

```
coordinator → scraper → analyst → reporter → coordinator (брифинг)
```

1. coordinator получает задание (тема, ключевые слова, языки/рынки)
2. scraper ищет статьи через WebSearch + WebFetch → `shared/raw-data.json`
3. analyst фильтрует, оценивает тональность и тренды → `shared/articles.json`
4. reporter пишет в Google Sheets + PDF → `outputs/`
5. coordinator даёт финальный брифинг → `outputs/briefing.md`

## Обязательная структура работы

Команда работает через явные артефакты и видимую коммуникацию.

- Общие рабочие файлы: `agent-runtime/shared/`
- Сообщения между агентами: `agent-runtime/messages/`
- План и статусы: `agent-runtime/state/`
- Финальные результаты: `agent-runtime/outputs/`

Каждый агент создаёт артефакт и отправляет handoff через SendMessage.

## Правила для lead и teammates

- использовать `.claude/agents/` как источник ролей
- взаимодействие агентов должно быть видно в артефактах и сообщениях
- не подменять командную работу одиночной сессией
- использовать `coordinator` как основную точку координации
- запускать cleanup только через lead

## Рекомендуемый порядок запуска

1. Открыть `tmux`:

```bash
tmux new -s claude-agent-team
```

2. Запустить Claude Code внутри `tmux`:

```bash
claude
```

3. Дать lead-инструкцию:

```text
Создай Agent Team для мониторинга новостей.
Используй роли coordinator, scraper, analyst и reporter.
Тема: [твоя тема]. Языки: EN и RU.
Пусть агенты работают через pipeline и передают данные друг другу.
```

4. После завершения работы выполнить cleanup через lead.

## Правила демонстрации

- Pipeline виден в tmux — каждый агент в своём pane
- Межагентные handoff через SendMessage видны зрителю
- Каждый этап создаёт материальный артефакт
- Финал: Google Sheet с графиками + PDF + текстовый брифинг

## Технические зависимости

- **Поиск новостей:** WebSearch (встроен в Claude) + WebFetch для полного текста статей
- **Внешние API не нужны** — только встроенные инструменты Claude Code
- **Google Sheets:** через MCP (подключен)
- **PDF:** через skill `pdf`

## Источники истины

- Главная проектная инструкция: `CLAUDE.md`
- Роли агентов: `.claude/agents/`
- Рабочий runtime: `agent-runtime/`
