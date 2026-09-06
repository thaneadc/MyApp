import html as htmlmod
import os
import re
import shutil
import subprocess
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


def add_candidates(text, base, candidates):
    text = htmlmod.unescape(text).replace("\\/", "/")
    patterns = [
        r'''(?:href|src)=["']([^"']+)["']''',
        r'''https?://[^\s"'<>]+''',
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.I):
            u = match if isinstance(match, str) else match[0]
            u = urllib.parse.urljoin(base, u)
            if u.startswith("http") and u not in candidates:
                candidates.append(u)
    return text


def score(u):
    s = 0
    low = u.lower()
    if "download" in low: s += 30
    if "file" in low: s += 15
    if "share" in low: s += 5
    if FILE_ID and FILE_ID in u: s += 40
    if PUBLIC_ID and PUBLIC_ID in u: s += 40
    if ".html" in low: s += 5
    if "_next/static" in low: s -= 20
    return -s


def try_candidates(candidates):
    for u in sorted(candidates, key=score):
        if u.rstrip("/") == SHARE_URL.rstrip("/"):
            continue
        try:
            body, resolved, hdr = fetch(u)
        except Exception:
            continue
        if save_if_game(body, resolved):
            return True
    return False


page, final_url, headers = fetch(SHARE_URL)
if save_if_game(page, final_url):
    sys.exit(0)

candidates = []
text = add_candidates(page.decode("utf-8", "ignore"), final_url, candidates)

# Render the share page with Chrome so client-side file links appear in the DOM.
chrome = next((shutil.which(x) for x in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"] if shutil.which(x)), None)
if chrome:
    print("Rendering share page with", chrome)
    try:
        proc = subprocess.run([
            chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
            "--disable-dev-shm-usage", "--virtual-time-budget=10000", "--dump-dom", SHARE_URL
        ], capture_output=True, text=True, timeout=45)
        rendered = proc.stdout
        print("Rendered DOM bytes:", len(rendered.encode("utf-8", "ignore")))
        text += "\n" + add_candidates(rendered, SHARE_URL, candidates)
    except Exception as e:
        print("Chrome render failed:", repr(e))
else:
    print("Chrome binary not found on runner")

# Inspect JS chunks referenced by the page for API/download routes.
script_urls = [u for u in candidates if "_next/static" in u and u.endswith(".js")]
for jsurl in script_urls[:30]:
    try:
        body, resolved, hdr = fetch(jsurl)
        js = body.decode("utf-8", "ignore")
        if any(k in js.lower() for k in ["download", "share", "file"]):
            add_candidates(js, SHARE_URL, candidates)
            # Also capture likely quoted API paths.
            for path in re.findall(r'''["'](/[^"']*(?:download|share|file)[^"']*)["']''', js, re.I):
                u = urllib.parse.urljoin(SHARE_URL, path)
                if u not in candidates:
                    candidates.append(u)
    except Exception:
        pass

# Common endpoint guesses.
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
        u = urllib.parse.urljoin(SHARE_URL, path)
        if u not in candidates:
            candidates.append(u)

if try_candidates(candidates):
    sys.exit(0)

print("Could not resolve direct file from firestorage share page.")
print("Share page bytes:", len(page))
print("Candidate URLs discovered:")
for u in sorted(candidates, key=score)[:120]:
    print(" -", u)
print("Rendered/page contains filename:", "Captains_Dash" in text)
print("Page markers:", "FILE_ID" if FILE_ID and FILE_ID in text else "", "PUBLIC_ID" if PUBLIC_ID and PUBLIC_ID in text else "")
sys.exit(2)
