import html as htmlmod
import os
import re
import sys
import urllib.parse
import urllib.request

SHARE_URL = os.environ["SHARE_URL"]
FILE_ID = os.environ.get("FILE_ID", "")
PUBLIC_ID = os.environ.get("PUBLIC_ID", "")
EXPECTED_SHA = os.environ.get("EXPECTED_SHA", "")
MIN_SIZE = int(os.environ.get("MIN_SIZE", "4000000"))
OUT = os.environ.get("OUT", "index.html")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"


def fetch(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read()
        return body, r.geturl(), dict(r.headers)


def is_game(body):
    return len(body) >= MIN_SIZE and (b"Captain's Dash" in body or b"Captain&#39;s Dash" in body)


def save_if_game(body, source):
    if not is_game(body):
        return False
    if EXPECTED_SHA:
        import hashlib
        got = hashlib.sha256(body).hexdigest()
        if got != EXPECTED_SHA:
            print(f"Large candidate from {source} had SHA {got}, expected {EXPECTED_SHA}")
            return False
    with open(OUT, "wb") as f:
        f.write(body)
    print(f"Imported full game: {len(body)} bytes from {source}")
    return True


page, final_url, headers = fetch(SHARE_URL)
if save_if_game(page, final_url):
    sys.exit(0)

text = page.decode("utf-8", "ignore")
text = htmlmod.unescape(text).replace("\\/", "/")
base = final_url

candidates = []
for pattern in [r'''href=["']([^"']+)["']''', r'''https?://[^\s"'<>]+''']:
    for match in re.findall(pattern, text, flags=re.I):
        u = match if isinstance(match, str) else match[0]
        u = urllib.parse.urljoin(base, u)
        if u.startswith("http") and u not in candidates:
            candidates.append(u)

# Common direct-download endpoint guesses. Harmless if absent.
for ident in [FILE_ID, PUBLIC_ID]:
    if not ident:
        continue
    for path in [
        f"/api/files/{ident}/download",
        f"/api/file/{ident}/download",
        f"/api/download/{ident}",
        f"/download/{ident}",
        f"/files/{ident}/download",
    ]:
        u = urllib.parse.urljoin(base, path)
        if u not in candidates:
            candidates.append(u)

# Prefer links that look like file/download links.
def score(u):
    s = 0
    low = u.lower()
    if "download" in low: s += 20
    if "file" in low: s += 10
    if FILE_ID and FILE_ID in u: s += 30
    if PUBLIC_ID and PUBLIC_ID in u: s += 30
    if ".html" in low: s += 5
    return -s

for u in sorted(candidates, key=score):
    if u.rstrip("/") == SHARE_URL.rstrip("/"):
        continue
    try:
        body, resolved, hdr = fetch(u)
    except Exception as e:
        continue
    if save_if_game(body, resolved):
        sys.exit(0)

print("Could not resolve direct file from firestorage share page.")
print("Share page bytes:", len(page))
print("Candidate URLs discovered:")
for u in sorted(candidates, key=score)[:80]:
    print(" -", u)
print("Page markers:", "FILE_ID" if FILE_ID and FILE_ID in text else "", "PUBLIC_ID" if PUBLIC_ID and PUBLIC_ID in text else "")
sys.exit(2)
