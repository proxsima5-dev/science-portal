# pptdump.py <pptx> <out-dir> [prefix]
# PPT 글과 그림 꺼내기. 파이썬 기본 기능만 쓴다(설치 필요 없음, 맥·윈도우 모두).
#   <out-dir>/<prefix>_글.md   슬라이드마다 글·발표자 메모·그 슬라이드의 그림 이름
#   <out-dir>/<prefix>_그림/   s03_image7.png 처럼 "슬라이드 번호_원래 이름"
# prefix 기본값: PPT
import posixpath, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/package/2006/relationships}'


def texts(xml):
    out = []
    for p in ET.fromstring(xml).iter(A + 'p'):
        line = ''.join(t.text or '' for t in p.iter(A + 't')).strip()
        if line:
            out.append(line)
    return out


def rels(z, part):
    d, f = posixpath.split(part)
    rp = posixpath.join(d, '_rels', f + '.rels')
    if rp not in z.namelist():
        return []
    res = []
    for r in ET.fromstring(z.read(rp)).iter(R + 'Relationship'):
        if r.get('TargetMode') == 'External':
            continue
        res.append((r.get('Type', '').rsplit('/', 1)[-1], posixpath.normpath(posixpath.join(d, r.get('Target', '')))))
    return res


def main():
    if len(sys.argv) < 3:
        sys.exit('사용법: python3 pptdump.py <pptx> <out-dir> [prefix]')
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    prefix = sys.argv[3] if len(sys.argv) > 3 else 'PPT'
    img_dir = out / f'{prefix}_그림'
    img_dir.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(src)
    slides = sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)),
                    key=lambda n: int(re.search(r'(\d+)', n.rsplit('/', 1)[1]).group(1)))
    md = [f'# {prefix} ({src.name})', '']
    for i, part in enumerate(slides, 1):
        md += [f'## 슬라이드 {i}', '']
        md += texts(z.read(part)) or ['(글 없음)']
        pics = []
        for kind, target in rels(z, part):
            if kind == 'notesSlide' and target in z.namelist():
                note = [t for t in texts(z.read(target)) if not t.isdigit()]
                if note:
                    md += ['', '메모: ' + ' / '.join(note)]
            elif kind in ('image', 'media', 'video') and target in z.namelist():
                name = f's{i:02d}_' + posixpath.basename(target)
                (img_dir / name).write_bytes(z.read(target))
                pics.append(name)
        if pics:
            md += ['', '그림: ' + ', '.join(pics)]
        md.append('')
    (out / f'{prefix}_글.md').write_text('\n'.join(md), encoding='utf-8')
    print(f'{prefix}: 슬라이드 {len(slides)}장, 그림 {len(list(img_dir.iterdir()))}개')


if __name__ == '__main__':
    main()
