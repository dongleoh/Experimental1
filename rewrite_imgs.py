# rewrite_imgs.py
from pathlib import Path
import re, shutil, urllib.parse, requests

ROOT = Path('.')
ASSETS = ROOT / 'assets' / 'images'
ASSETS.mkdir(parents=True, exist_ok=True)

IMG_RE = re.compile(r'(<img[^>]+src=")([^"]+)(")', re.IGNORECASE)

def localize(src: str) -> str:
    # 1) 원격이면 파일명만 추출
    u = urllib.parse.urlparse(src)
    if u.scheme in ('http','https'):
        name = Path(u.path).name or 'img.png'
        # 없으면 받아서 저장
        dst = ASSETS / name
        if not dst.exists():
            try:
                r = requests.get(src, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
                r.raise_for_status()
                dst.write_bytes(r.content)
            except Exception:
                return src  # 실패하면 원본 유지
        return f'assets/images/{name}'
    # 2) 상대경로인데 상위(../) 참조면 역시 파일명만
    name = Path(src).name
    return f'assets/images/{name}'

for html in ROOT.glob('*.html'):
    txt = html.read_text('utf-8')
    def rep(m):
        before, src, after = m.groups()
        return before + localize(src) + after
    new = IMG_RE.sub(rep, txt)
    # <base> 넣어두면 상대링크도 안정
    if '<base ' not in new.lower():
        new = new.replace('<head>', '<head>\n<base href="https://dongleoh.github.io/Experimental1/">', 1)
    if new != txt:
        html.write_text(new, 'utf-8')

print('done')