# pdfdump.py <pdf> <out-dir> <prefix> [png]
# 윈도우용(맥은 pdfdump.swift). 처음 한 번: python -m pip install pymupdf
#   <out-dir>/<prefix>_글.md        쪽마다 글
#   <out-dir>/<prefix>_쪽/p001.png  png를 주면 쪽 그림(2배)
# 그림 오리기: python pdfdump.py <pdf> <out-dir> <prefix> crop <쪽번호> <x0> <y0> <x1> <y1> <저장할.png>
#   좌표는 p001.png 픽셀 기준(2배 그림), 오린 그림은 3배 해상도로 저장
import sys
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit('pymupdf가 없어요: python -m pip install pymupdf')

a = sys.argv
if len(a) < 4:
    sys.exit('사용법: python pdfdump.py <pdf> <out-dir> <prefix> [png]')
doc = fitz.open(a[1])
out, prefix = Path(a[2]), a[3]
out.mkdir(parents=True, exist_ok=True)

if len(a) > 4 and a[4] == 'crop':
    page = doc[int(a[5]) - 1]
    x0, y0, x1, y1 = (float(v) / 2 for v in a[6:10])
    page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=fitz.Rect(x0, y0, x1, y1)).save(a[10])
    print('저장:', a[10])
    sys.exit()

png = len(a) > 4
pdir = out / f'{prefix}_쪽'
if png:
    pdir.mkdir(exist_ok=True)
md = [f'# {prefix} ({Path(a[1]).name})', '']
for i, page in enumerate(doc, 1):
    n = f'p{i:03d}'
    md += [f'## {n}', '', page.get_text().strip(), '']
    if png:
        page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(pdir / f'{n}.png')
(out / f'{prefix}_글.md').write_text('\n'.join(md), encoding='utf-8')
print(f'{prefix}: {len(doc)}쪽')
