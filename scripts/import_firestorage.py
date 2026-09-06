import html as htmlmod
import json
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
UA = "Mozilla/5.0 AppleWebKit/605.1.15 Safari/605.1.15"


def fetch(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=25) as r:
        body = r.read()
        return body, r.geturl(), dict(r.headers)


def is_game(body):
    return len(body) >= MIN_SIZE and b"Captain's Dash" in body


def save_if_game(body, source):
    if not is_game(body): return False
    if EXPECTED_SHA:
        import hashlib
        got = hashlib.sha256(body).hexdigest()
        if got != EXPECTED_SHA:
            print("SHA mismatch", got, "from", source)
            return False
    open(OUT, "wb").write(body)
    print("Imported full game", len(body), "bytes from", source)
    return True


def add_url(candidates, u, base=SHARE_URL):
    if not isinstance(u, str): return
    u = htmlmod.unescape(u).replace("\\/", "/")
    if u.startswith("/"): u = urllib.parse.urljoin(base, u)
    if u.startswith("http") and u not in candidates: candidates.append(u)


def collect_strings(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str): out.append((k, v))
            collect_strings(v, out)
    elif isinstance(obj, list):
        for v in obj: collect_strings(v, out)


def add_from_text(text, candidates, base=SHARE_URL):
    text = htmlmod.unescape(text).replace("\\/", "/")
    for pat in [r'''(?:href|src)=["']([^"']+)["']''', r'''https?://[^\s"'<>]+''']:
        for m in re.findall(pat, text, flags=re.I): add_url(candidates, m, base)
    return text


def try_candidates(candidates):
    def score(u):
        low=u.lower(); s=0
        if "download" in low:s+=40
        if "file" in low:s+=15
        if FILE_ID and FILE_ID in u:s+=50
        if PUBLIC_ID and PUBLIC_ID in u:s+=50
        if "_next/static" in low:s-=30
        return -s
    for u in sorted(candidates, key=score):
        if u.rstrip("/") == SHARE_URL.rstrip("/"): continue
        try: body,resolved,h=fetch(u)
        except Exception: continue
        if save_if_game(body,resolved): return True
    return False


page, final_url, headers = fetch(SHARE_URL)
if save_if_game(page, final_url): sys.exit(0)
candidates=[]
alltext=add_from_text(page.decode("utf-8","ignore"),candidates,final_url)

# Render page so Next.js route information and filename are present.
chrome=next((shutil.which(x) for x in ["google-chrome","google-chrome-stable","chromium"] if shutil.which(x)),None)
if chrome:
    try:
        p=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--virtual-time-budget=8000","--dump-dom",SHARE_URL],capture_output=True,text=True,timeout=35)
        print("Rendered DOM bytes",len(p.stdout.encode()))
        alltext += "\n"+add_from_text(p.stdout,candidates)
    except Exception as e: print("Chrome render failed",repr(e))

# firestorage public share API discovered from its own web client.
share_id=urllib.parse.urlparse(SHARE_URL).path.rstrip("/").split("/")[-1]
for env in ["prod","dev"]:
    list_url=f"https://api.firestorage.ai/{env}/file/shares/{share_id}/files?maxResults=1000"
    try:
        body,resolved,h=fetch(list_url)
        print("File-list API",env,"status bytes",len(body))
        txt=body.decode("utf-8","ignore")
        try:
            data=json.loads(txt)
            pairs=[]; collect_strings(data,pairs)
            print("File-list string fields:")
            for k,v in pairs[:100]: print(" ",k,"=",v[:500])
            for k,v in pairs:
                lk=k.lower()
                if v.startswith("http") or v.startswith("/"):
                    add_url(candidates,v,list_url)
                # IDs/keys often combine with the API base in downloadable routes.
                if any(x in lk for x in ["download","url","href"]): add_url(candidates,v,list_url)
        except Exception:
            print("Non-JSON file list:",txt[:3000])
    except Exception as e:
        print("File-list API",env,"failed",repr(e))

# Inspect referenced JS chunks for API paths and URLs.
for jsurl in [u for u in list(candidates) if "_next/static" in u and u.endswith(".js")][:30]:
    try:
        body,resolved,h=fetch(jsurl); js=body.decode("utf-8","ignore")
        add_from_text(js,candidates)
        for path in re.findall(r'''["'](/[^"']*(?:download|shares|file)[^"']*)["']''',js,re.I): add_url(candidates,path)
    except Exception: pass

# Last-resort common endpoint guesses.
for ident in [FILE_ID,PUBLIC_ID]:
    if ident:
        for base in ["https://api.firestorage.ai/prod/file/","https://api.firestorage.ai/dev/file/","https://firestorage.ai/"]:
            for path in [f"files/{ident}/download",f"file/{ident}/download",f"download/{ident}",f"files/{ident}"]:
                add_url(candidates,urllib.parse.urljoin(base,path))

if try_candidates(candidates): sys.exit(0)
print("Could not resolve direct file. Candidates:")
for u in candidates[:150]: print(" -",u)
print("Rendered/page contains filename:","Captains_Dash" in alltext)
sys.exit(2)
