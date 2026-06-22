# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl
ET=r'C:\Users\User\Downloads\ИБ метрики v58.xlsx'
KD=r'C:\Users\User\Downloads\КД метрики v1 (формат v58).xlsx'

def headers_of_tables(path):
    wb=openpyxl.load_workbook(path, read_only=True, data_only=True)
    print('#'*60); print('FILE:', path.split(chr(92))[-1])
    for ws in wb.worksheets:
        print('  SHEET:', ws.title)
        # найти строки, похожие на заголовки таблиц (несколько непустых подряд коротких ячеек)
        for ri,row in enumerate(ws.iter_rows(values_only=True), 1):
            vals=[str(c).strip() for c in row if c is not None and str(c).strip()]
            if not vals: continue
            joined=' | '.join(vals)
            # эвристика: строка с >=4 короткими ячейками = заголовок
            short=[v for v in vals if len(v)<=22]
            if len(vals)>=4 and len(short)>=4 and ('поле' in joined or 'Метрика' in joined or 'Витрина' in joined or 'Задача' in joined or 'Дашборд' in joined or 'Ранг' in joined or 'Группа' in joined):
                print(f'    R{ri} HEADER: {joined[:160]}')
            if ri>30: break
    wb.close()

headers_of_tables(ET)
headers_of_tables(KD)
