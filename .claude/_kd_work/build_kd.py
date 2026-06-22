# -*- coding: utf-8 -*-
"""Сборка «КД метрики v1 (формат v58)» по эталону ИБ v58 / образцу Маркетинг v1."""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import kd_data as D
import kd_data2 as D2

OUT = r'C:\Users\User\Downloads\КД метрики v1 (формат v58).xlsx'

C_TITLE='1F4E78'; C_SUB='555555'; C_HEAD='1F4E78'; C_BAND='2E75B6'; C_GROUP='D6E4F0'
C_GREEN='C6EFCE'; C_YELLOW='FFEB9C'; C_BLUE='BDD7EE'; C_GRAY='D9D9D9'
C_BI='DDEBF7'; C_REBUILD='FFF2CC'; C_AUTO='E2EFDA'; C_ZEBRA='F4F7FB'; WHITE='FFFFFF'
thin=Side(style='thin', color='D0D0D0'); BORDER=Border(left=thin,right=thin,top=thin,bottom=thin)
def fill(c): return PatternFill('solid', fgColor=c)

READY_FILL={'Считаем сейчас':C_GREEN,'После новой витрины':C_YELLOW,'CH Кирилла — проверить':C_BLUE,'Нет данных (блокер)':C_GRAY}
IMPL_FILL={'BI-сторона':C_BI,'пересобрать':C_REBUILD,'авто в DWH':C_AUTO,'оставить в PBI':C_BI}

wb=openpyxl.Workbook(); wb.remove(wb.active)

def setcol(ws,w):
    for c,v in w.items(): ws.column_dimensions[c].width=v
def title(ws,t,sub,span):
    ws.merge_cells(f'A1:{get_column_letter(span)}1'); ws.merge_cells(f'A2:{get_column_letter(span)}2')
    a=ws.cell(1,1,t); a.font=Font(bold=True,size=14,color=C_TITLE)
    b=ws.cell(2,1,sub); b.font=Font(size=10,color=C_SUB); b.alignment=Alignment(wrap_text=True,vertical='top')
    ws.row_dimensions[2].height=46
def header(ws,row,cols):
    for i,h in enumerate(cols,1):
        c=ws.cell(row,i,h); c.font=Font(bold=True,size=11,color=WHITE); c.fill=fill(C_HEAD)
        c.alignment=Alignment(wrap_text=True,vertical='center'); c.border=BORDER
def band(ws,row,text,span,color=C_BAND,size=12,fc=WHITE):
    ws.merge_cells(f'A{row}:{get_column_letter(span)}{row}')
    c=ws.cell(row,1,text); c.font=Font(bold=True,size=size,color=fc)
    c.fill=fill(color); c.alignment=Alignment(wrap_text=True,vertical='center',indent=1)
def group_cell(ws,row,text):
    c=ws.cell(row,1,text); c.font=Font(bold=True,color=C_TITLE); c.fill=fill(C_GROUP)
    c.alignment=Alignment(wrap_text=True,vertical='top'); c.border=BORDER
def datarow(ws,row,vals,bold_first=True,sql_cols=(),center=()):
    for i,v in enumerate(vals,1):
        c=ws.cell(row,i,v); sz=9 if i in sql_cols else 11
        c.font=Font(size=sz,bold=(bold_first and i==1)); c.border=BORDER
        h='center' if i in center else 'general'
        c.alignment=Alignment(wrap_text=True,vertical='top',horizontal=h)
def sqlblock(ws,row,text,span):
    ws.merge_cells(f'A{row}:{get_column_letter(span)}{row}')
    c=ws.cell(row,1,text); c.font=Font(size=9,name='Consolas'); c.alignment=Alignment(wrap_text=True,vertical='top')
    nlines=text.count(chr(10))+1; ws.row_dimensions[row].height=min(14*nlines+6, 600)

# ===== Лист 1: Каталог метрик =====
ws=wb.create_sheet('Каталог метрик')
setcol(ws,{'A':18,'B':4,'C':27,'D':16,'E':46,'F':44,'G':8,'H':6,'I':6,'J':10,'K':17,'L':16,'M':32})
title(ws,'КД метрики v1 (формат v58) — Каталог метрик',
  'Все метрики Коммерческой дирекции (КД) по этапам сквозной воронки (I: лид→дозвон→квалификация→продажа→выручка), плюс юнит-экономика (II), удержание и LTV (III) и отчётность план/факт (IV). Цвет «Готовности»: зелёный - считаем сейчас (живой DAX); жёлтый - после новой витрины; синий - проверить в ClickHouse Кирилла; серый - нет данных (блокер). «Реализация в DWH»: авто в DWH / пересобрать / BI-сторона.',13)
header(ws,4,['Группа','№','Метрика','Гранулярность','Описание','Формула (методология словами)','Ед.','Приор.','KPI','Статус','Готовность','Реализация в DWH','Источник / витрина'])
ws.freeze_panes='C5'
r=5
for rec in D.CATALOG:
    if rec[0]==D.BAND:
        band(ws,r,rec[1],13); r+=1; continue
    g,n,name,gran,descr,formula,unit,prior,kpi,status,ready,impl,source=rec
    datarow(ws,r,[g,n,name,gran,descr,formula,unit,prior,kpi,status,ready,impl,source],
            sql_cols=(), center=(2,7,8,9))
    if g: group_cell(ws,r,g)
    if ready in READY_FILL: ws.cell(r,11).fill=fill(READY_FILL[ready])
    if impl in IMPL_FILL: ws.cell(r,12).fill=fill(IMPL_FILL[impl])
    if status=='GAP': ws.cell(r,10).fill=fill(C_ZEBRA)
    r+=1
band(ws,r,'Легенда «Готовность»:  Считаем сейчас · После новой витрины · CH Кирилла — проверить · Нет данных (блокер)',13,color=C_GROUP,size=10,fc=C_TITLE)

# ===== Лист 2: Roadmap витрин =====
ws=wb.create_sheet('Roadmap витрин')
setcol(ws,{'A':26,'B':24,'C':6,'D':14,'E':40,'F':15,'G':56})
title(ws,'Roadmap витрин КД',
  'Какие витрины строим под каталог метрик КД. Приоритет 0 - ядро воронки и фундамент (лиды, продажи, расход). «Источник» - из каких таблиц собирается; «Зачем нужна» - какие метрики и дашборды питает.',7)
n_metrics=sum(1 for x in D.CATALOG if x[0]!=D.BAND)
n_key=sum(1 for x in D.CATALOG if x[0]!=D.BAND and x[7]==0)
n_road=len(D2.ROADMAP); n_nobuild=sum(1 for x in D2.ROADMAP if x[5]=='BI-сторона')
for i,(lbl,val) in enumerate([('Итого метрик в каталоге',n_metrics),('Из них ключевые (приоритет 0)',n_key),
        ('Остальные (приоритет 1)',n_metrics-n_key),('Витрин/таблиц в roadmap',n_road),
        ('Из них НЕ строим как витрины (BI-сторона)',n_nobuild)]):
    ws.cell(4+i,1,lbl).font=Font(bold=True); ws.cell(4+i,2,val)
header(ws,10,['Витрина / таблица','Статус','Приор.','Ответственный','Источник (таблицы)','Реализация в DWH','Зачем нужна / что питает'])
ws.freeze_panes='A11'; r=11
for v,st,pr,ow,src,impl,purp in D2.ROADMAP:
    datarow(ws,r,[v,st,pr,ow,src,impl,purp],center=(3,))
    if impl in IMPL_FILL: ws.cell(r,6).fill=fill(IMPL_FILL[impl])
    r+=1

# ===== Лист 3: CTE =====
ws=wb.create_sheet('CTE'); setcol(ws,{'A':150})
title(ws,'CTE — бизнес-правила и сборка ядра воронки КД',
  'Логика сборки воронки КД: правила связки лид→дозвон→квалификация→продажа→выручка и полный SQL ядра dm_kd_funnel.',1)
sqlblock(ws,4,D2.CTE_RULES,1); r=5
ws.merge_cells('A6:A6'); band(ws,6,D2.CTE_SQL_TITLE,1); sqlblock(ws,7,D2.CTE_SQL,1)

# ===== Лист 4: Витрины и таблицы =====
ws=wb.create_sheet('Витрины и таблицы')
setcol(ws,{'A':24,'B':32,'C':44,'D':16,'E':6,'F':40})
title(ws,'Витрины и таблицы (структура по полям)',
  'Для каждой витрины КД: заголовок с типом, SQL сборки и поля (с колонкой sql). Грануляции и бизнес-правила - из листа «CTE».',6)
r=4
for vit in D2.VITRINY:
    band(ws,r,vit['title'],6); r+=1
    c=ws.cell(r,1,vit['table']); c.font=Font(bold=True,color=C_TITLE); r+=1
    sqlblock(ws,r,vit['sql'],6); r+=1
    header(ws,r,['поле','описание','комментарий','значения (пример)','ключ','sql']); r+=1
    for f in vit['fields']:
        datarow(ws,r,list(f),center=(5,)); r+=1
    r+=1

# ===== Лист 5: ТЗ для разработки =====
ws=wb.create_sheet('ТЗ для разработки')
setcol(ws,{'A':4,'B':26,'C':16,'D':24,'E':44,'F':30,'G':36})
title(ws,'ТЗ для разработки (DE)',
  'Задачи для команды данных. «Витрина есть?» - текущее состояние. Каждая задача разблокирует метрики из листа «Каталог метрик». Порядок = приоритет фундамента.',7)
header(ws,4,['#','Задача','Ответственный','Витрина есть?','Что построить','Какие метрики разблокирует','Источник / референс'])
ws.freeze_panes='A5'; r=5
for rec in D2.TZ:
    datarow(ws,r,list(rec),center=(1,)); r+=1

# ===== Лист 6: Реестр дашбордов =====
ws=wb.create_sheet('Реестр дашбордов')
setcol(ws,{'A':30,'B':9,'C':22,'D':6,'E':38,'F':40,'G':34,'H':15})
title(ws,'Реестр дашбордов КД',
  'Дашборды КД и смежные (PBIRS). Источники извлечены из Power Query дашборда «Сквозная отчётность». «Реализация в DWH»: авто в DWH / пересобрать / BI-сторона.',8)
header(ws,4,['Дашборд','Движок','Папка','Исп.','Назначение','Ключевые метрики','Источники данных','Реализация в DWH'])
ws.freeze_panes='A5'; r=5
for d in D2.DASH:
    datarow(ws,r,list(d),center=(4,))
    if d[7] in IMPL_FILL: ws.cell(r,8).fill=fill(IMPL_FILL[d[7]])
    r+=1

# ===== Лист 7: Топ-10 дашбордов =====
ws=wb.create_sheet('Топ-10 дашбордов')
setcol(ws,{'A':6,'B':32,'C':6,'D':9,'E':9,'F':6,'G':44,'H':32,'I':24,'J':16})
title(ws,'Топ-10 дашбордов КД для реформы',
  'Из реестра выбраны опорные дашборды для перевода на DWH. Балл = сумма трёх оценок (1-3): «Исп.» - частота просмотра; «Ценность» - влияние на решения; «Готовн.» - доступность данных в DWH-источниках. Действие: «пересобрать» - свести разрозненные меры; «авто в DWH» - перенести логику почти как есть; «оставить в PBI» - считается на BI поверх источника.',10)
header(ws,4,['Ранг','Дашборд','Исп.','Ценность','Готовн.','Балл','Почему в топе','Метрики','Витрины-источники','Действие'])
ws.freeze_panes='A5'; r=5
for rec in D2.TOP10:
    rank,name,u,v,g,sc,why,met,vit,act=rec
    datarow(ws,r,[rank,name,u,v,g,sc,why,met,vit,act],center=(1,3,4,5,6))
    if act in IMPL_FILL: ws.cell(r,10).fill=fill(IMPL_FILL[act])
    r+=1
band(ws,r,D2.TOP10_NOTE,10,color=C_GROUP,size=10,fc=C_TITLE)

wb.save(OUT)
print('SAVED:', OUT)
print('Метрик в каталоге:', n_metrics, '| ключевых:', n_key, '| витрин:', n_road)
