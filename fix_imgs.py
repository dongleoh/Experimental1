# fix_imgs.py  (레포 루트: Experimental1/ 에 두고 실행)
from pathlib import Path
from bs4 import BeautifulSoup
import requests, re, urllib.parse, shutil

ROOT = Path(".")
ASSETS = ROOT / "assets" / "images"
ASSETS.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
ORIGIN_HOST_RE = re.compile(r"^https://www\.sweeper\.or\.kr/etc/manual/", re.I)

def find_origin_url(soup: BeautifulSoup) -> str | None:
    # 문서 상단에 제가 만들었던 “원문:” 또는 “Source:” 링크가 있으니 그걸 origin으로 사용
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if ORIGIN_HOST_RE.match(href):
            return href
    return "https://www.sweeper.or.kr/etc/manual/"  # 최후의 기본값

def url_join(base: str, rel: str) -> str:
    return urllib.parse.urljoin(base, rel)

def dl(remote: str, referer: str, dest: Path) -> bool:
    if dest.exists():
        return True
    headers = {
        "User-Agent": UA,
        "Referer": referer,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    try:
        r = requests.get(remote, headers=headers, timeout=20)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception:
        return False

def sanitize_name(url_path: str) -> str:
    # 쿼리스트링 제거, 파일명만 추출
    p = urllib.parse.urlparse(url_path)
    name = Path(p.path).name or "img.png"
    return name

changed_files = 0
for html in sorted(ROOT.glob("*.html")):
    txt = html.read_text("utf-8", errors="ignore")
    soup = BeautifulSoup(txt, "lxml")

    origin = find_origin_url(soup)

    updated = False
    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        if not src:
            continue
        # 이미 로컬로 바뀐 경우(assets/images/…)는 스킵
        if src.lower().startswith("assets/images/"):
            continue

        # 원격 URL 계산(상대경로면 origin을 기준으로 합성)
        remote = src if re.match(r"^https?://", src, re.I) else url_join(origin, src)
        fname = sanitize_name(remote)
        # 이름 충돌 피하려면 페이지명 접두어를 붙여도 됨
        dest = ASSETS / fname

        if dl(remote, referer=origin, dest=dest):
            img["src"] = f"assets/images/{fname}"
            updated = True
        # 실패하면 그대로 두되, 나중에 다시 돌릴 수 있게 함

    # 내부 링크 안정화를 위해 base 태그도 넣어두면 좋음(상대 링크 → 레포 루트 기준)
    head = soup.find("head")
    if head and not soup.find("base"):
        base = soup.new_tag("base", href="https://dongleoh.github.io/Experimental1/")
        head.insert(0, base)
        updated = True

    if updated:
        html.write_text(str(soup), "utf-8")
        changed_files += 1

print(f"updated HTML files: {changed_files}")
print("done")