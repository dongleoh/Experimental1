# make_index_and_sitemap.py
import os, time
from urllib.parse import quote

BASE = "https://dongleoh.github.io/Experimental1"  # 깃허브 Pages 주소

def list_local_htmls():
    files = []
    for name in os.listdir("."):
        if not name.lower().endswith(".html"):
            continue
        if name in ("index.html", "sitemap.xml"):
            continue
        if name.startswith((".", "_")):
            continue
        if os.path.isdir(name):
            continue
        files.append(name)
    files.sort()
    return files

def write_index(files):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset='utf-8'><title>Links</title>\n")
        f.write("<h1>Mirror index</h1><ul>\n")
        for name in files:
            f.write(f"<li><a href='{name}'>{name}</a></li>\n")
        f.write("</ul>\n")

def write_sitemap(files):
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for name in files:
            # 파일명이 한글/공백이면 퍼센트 인코딩
            loc = f"{BASE}/{quote(name)}"
            f.write("  <url>\n")
            f.write(f"    <loc>{loc}</loc>\n")
            f.write(f"    <lastmod>{now}</lastmod>\n")
            f.write("    <changefreq>monthly</changefreq>\n")
            f.write("    <priority>0.6</priority>\n")
            f.write("  </url>\n")
        f.write("</urlset>\n")

if __name__ == "__main__":
    files = list_local_htmls()
    print("FOUND", len(files), "HTML")
    write_index(files)
    write_sitemap(files)
    print("WROTE index.html & sitemap.xml")