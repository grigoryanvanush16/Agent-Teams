# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl
DL = r'C:\Users\User\Downloads'

def dump(fname, outname):
    p = os.path.join(DL, fname)
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        out.append('#'*80)
        out.append('SHEET: ' + ws.title)
        out.append('#'*80)
        for r in ws.iter_rows(values_only=True):
            # skip fully empty rows
            if all(c is None for c in r):
                continue
            cells = []
            for c in r:
                if c is None:
                    cells.append('')
                else:
                    s = str(c).replace('\n',' / ').strip()
                    cells.append(s)
            out.append(' | '.join(cells).rstrip(' |'))
    wb.close()
    with open(outname, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('wrote', outname, len(out), 'lines')

dump('Описание метрик КД.xlsx', 'opisanie_kd.txt')
dump('Дашборды для КД(1).xlsx', 'dashboards_kd.txt')
dump('ИБ метрики v58.xlsx', 'etalon_ib_v58.txt')
dump('Маркетинг метрики v1 (формат v58).xlsx', 'obrazec_mrkt_v1.txt')
